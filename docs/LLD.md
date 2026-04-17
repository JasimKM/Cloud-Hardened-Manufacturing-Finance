# Technical Implementation Guide (LLD): ManufacturingVault
### Secure Industrial File Encryption Platform — Full Technical Specifications

**Document Version:** 2.0  
**Coverage:** Production-Ready Implementation (100% Scope)  
**Audience:** Developers, Security Engineers, Infrastructure Teams

---

## Table of Contents

1. Introduction
   - 1.1 Scope of the Document
   - 1.2 Intended Audience
   - 1.3 System Overview
2. System Design
   - 2.1 Application Architecture Diagram
   - 2.2 Process Flow (Encryption Lifecycle) — Sequence Diagram
   - 2.3 Information Flow (Cryptographic Engine) — Data Flow Diagram
   - 2.4 Components Design (Detailed)
   - 2.5 Key Design Considerations
   - 2.6 API Catalogue
3. Data Design
   - 3.1 Encrypted Binary Format (Schema)
   - 3.2 Data Model (Schema & Encryption)
   - 3.3 Data Access Mechanism
   - 3.4 Data Retention & Archival Policies
   - 3.5 Data Migration & Seeding
4. Interfaces
   - 4.1 User Interface Layout
   - 4.2 API Contracts (Request/Response Structure)
5. State and Session Management
6. Caching Strategy
7. Non-Functional Requirements
   - 7.1 Security Aspects
   - 7.2 Performance Aspects
8. Conclusion

---

## 1. Introduction

### 1.1 Scope of the Document

This Technical Implementation Guide provides a comprehensive deep-dive into the core modules of ManufacturingVault: the cryptographic processing module, the Flask application routing layer, and the Azure infrastructure configuration. This document covers the complete system architecture and implementation details required for a secure production-grade deployment.

### 1.2 Intended Audience

This document is intended for software developers implementing or auditing the cryptographic module, security engineers reviewing the WAF configuration and network controls, infrastructure engineers working with the Terraform configurations, and technical reviewers assessing compliance with IEC 62443 and OWASP standards.

### 1.3 System Overview

ManufacturingVault is a Flask-based web application that provides AES-256-GCM authenticated file encryption and decryption as a web service. It is deployed on a hardened Ubuntu VM (Standard_B2s_v2) in a four-tier Azure Virtual Network following the Purdue Model, fronted by an Application Gateway WAF v2 in Prevention mode. The application runs under Gunicorn (3 workers) behind Nginx acting as reverse proxy. All cryptographic operations occur in memory; no plaintext data touches disk.

---

## 2. System Design

### 2.1 Application Architecture Diagram

The system is organized as a layered request pipeline. All inbound HTTP requests originate from the internet and first arrive at the Azure Application Gateway. The WAF inspects the request. If it passes inspection, the gateway forwards it to the MES VM's Nginx process on port 80. Nginx proxies the request to Gunicorn on localhost port 5000. Gunicorn invokes the Flask WSGI application, which processes the request, invokes the cryptographic module if needed, and returns a response. The response traverses the same path in reverse back to the user's browser.

Within the Flask application, the request routing layer dispatches to one of three handlers: the index handler (serves the Encryption Hub), the encrypt handler (processes file encryption), or the decrypt handler (serves the facility page and processes decryption). The encrypt and decrypt handlers directly invoke the cryptographic utilities module, which contains the Argon2id key derivation and AES-256-GCM cipher operations.

### 2.2 Process Flow (Encryption Lifecycle) — Sequence Diagram

The encryption lifecycle proceeds as follows:

Step 1 — The user opens the web browser and navigates to the ManufacturingVault home page. The browser sends a GET request.

Step 2 — The request traverses the WAF (no attack patterns present), reaches Nginx, is proxied to Gunicorn, and Flask renders the Tactical Dashboard index template with the Reactor Core encryption form.

Step 3 — The user selects an industrial file (e.g., machine.gcode) using the Data-Crucible portal interface and enters a strong passphrase. The portal's JavaScript validates the file is selected and updates the UI status.

Step 4 — The user clicks "EXECUTE ENCRYPTION." The browser sends an HTTP POST request with the file as multipart/form-data and the passphrase in the request body.

Step 5 — WAF inspects the request headers and body. The Content-Disposition header is checked against the dangerous file types custom rule. Since .gcode is not on the blocklist, the request is permitted.

Step 6 — Flask receives the POST, reads the uploaded file bytes entirely into memory, and validates the file extension against the ALLOWED_EXTENSIONS set.

Step 7 — Flask invokes encrypt_data(data, password). The function generates a 16-byte random salt using os.urandom(16), then invokes Argon2id to derive a 32-byte AES key from the passphrase and salt.

Step 8 — A 12-byte random nonce is generated. The AES-256-GCM cipher is instantiated with the derived key. The plaintext is encrypted, producing ciphertext and a 16-byte GCM authentication tag appended to the ciphertext.

Step 9 — The function constructs the encrypted binary output as salt + nonce + tag + ciphertext and returns it to Flask.

Step 10 — Flask constructs a streaming HTTP response with Content-Disposition: attachment; filename="machine.gcode.enc" and Cache-Control: no-cache, no-store headers. The encrypted binary is sent directly to the browser as a file download.

Step 11 — The browser downloads the .enc file. No data has been written to disk on the server. The in-memory buffer is garbage collected.

### 2.3 Information Flow (Cryptographic Engine) — Data Flow Diagram

**Inputs to the Cryptographic Module:**
- Raw file bytes (plaintext): The complete binary content of the uploaded industrial file, held entirely in a Python bytes object.
- User passphrase (string): The encryption key material entered by the user, received as a POST parameter and held in Python memory only.

**Internal Data Transformations:**

Stage 1 — Salt generation: os.urandom(16) generates 16 cryptographically unpredictable bytes from the operating system's entropy source. This salt ensures that the same passphrase produces a different AES key on every encryption operation.

Stage 2 — Key derivation: Argon2id processes the passphrase and salt. The hash_secret_raw function from argon2-cffi occupies 64,000 KB of memory for 3 passes with parallelism of 1, producing a deterministic 32-byte output. This operation takes approximately 200–500ms, which is intentionally slow to resist brute-force attacks.

Stage 3 — Nonce generation: os.urandom(12) generates 12 bytes for the AES-GCM nonce. The nonce is unique per encryption operation, ensuring that the same key with the same plaintext produces different ciphertext.

Stage 4 — AES-256-GCM encryption: The AESGCM object is instantiated with the 32-byte derived key. The encrypt method processes the plaintext with the nonce and produces ciphertext || GCM_tag (the last 16 bytes of the output are the authentication tag).

Stage 5 — Output packing: The final output is assembled as the concatenation of salt (16), nonce (12), tag (16), and ciphertext (variable length). This binary blob is entirely self-contained for decryption except for the passphrase.

**Outputs from the Cryptographic Module:**
- Encrypted binary bytes: The packed binary blob ready for HTTP response transmission.

### 2.4 Components Design (Detailed)

**Component: crypto_utils.py — Cryptographic Utilities Module**

This module is the most security-critical component in the entire system. It contains three primary functions:

derive_key(password, salt) accepts a plaintext password string and a 16-byte salt, invokes Argon2id with the specified parameters, and returns a 32-byte derived key. This function never returns the intermediate hash state and does not log or print the password or derived key under any circumstances.

encrypt_data(data, password) is the primary encryption function. It calls derive_key to obtain the AES key, generates a random nonce, creates an AESGCM cipher instance, encrypts the data, splits the tag from the ciphertext, and returns the complete binary blob. All intermediate objects (key, nonce, plaintext) exist only within the function's local scope and are not returned or stored.

decrypt_data(encrypted_data, password) is the primary decryption function. It validates that the input is at least 44 bytes (16+12+16 minimum, meaning a zero-length plaintext). It extracts salt, nonce, and tag by byte index slicing. It calls derive_key to re-derive the AES key. It reassembles ciphertext+tag as expected by AESGCM.decrypt. If the authentication tag does not match (wrong password or tampered file), the library raises an InvalidTag exception, which Flask catches and converts to a generic user-facing error message. This design prevents oracle attacks — the user learns only that decryption failed, not why.

**Component: app.py — Flask Application**

The Flask application contains three route handlers. The index handler simply renders the index template and requires no input validation. The encrypt handler validates that the request contains a file part and a non-empty passphrase, invokes secure_filename on the uploaded filename to prevent path traversal attacks, validates the file extension against ALLOWED_EXTENSIONS, reads the file bytes, calls encrypt_data, constructs an RFC 8187 compliant Content-Disposition header with both ASCII and UTF-8 encoded filename variants, and returns a streaming binary Response. The decrypt handler performs the same validation on the .enc file upload, reads the encrypted bytes, calls decrypt_data, handles InvalidTag exceptions with a generic flash message, and returns the decrypted file with the original filename restored.

**Component: base.html — Tactical Dashboard Layout**

The base template implements a CSS Grid layout (display: grid, 3 columns: 280px 1fr 280px) that creates the Bento-Grid Tactical Dashboard. It includes inline JavaScript for three cross-page behaviors: the Ghost Cursor (a custom crosshair cursor element positioned via mousemove events), the Live Telemetry Feed (a setInterval function that prepends timestamped log messages to the sidebar), and the Pixel Fog (a canvas-based particle animation on the background layer). These visual elements use no external JavaScript libraries or CDN dependencies, ensuring that the application has no third-party JavaScript attack surface.

### 2.5 Key Design Considerations

**Memory safety:** File bytes are read into Python memory, processed, and returned as streaming responses. Python's garbage collector automatically reclaims the memory after each request. There is no mechanism for the application to write plaintext to disk under any normal operation path.

**Filename handling:** The werkzeug.utils.secure_filename function strips path separators, doubly-encoded sequences, and OS-reserved characters from uploaded filenames. This prevents path traversal attacks where a malicious filename like ../../etc/passwd.enc could otherwise direct the application to write to an unintended location.

**No persistent user state:** The application has no user accounts, no database of uploaded files, and no server-side session data. Each request is entirely stateless. This dramatically reduces the attack surface — there is no credential store to steal, no session token to hijack, and no file store to enumerate.

**RFC 8187 Content-Disposition:** Download filenames are encoded using both the legacy ASCII format and the RFC 8187 UTF-8 percent-encoded format (filename*=UTF-8''encoded_name) to ensure that filenames with non-ASCII characters (common in multilingual manufacturing environments) are correctly preserved across all modern browsers.

### 2.6 API Catalogue

**GET /** — Encryption Hub
- Description: Returns the main Tactical Dashboard encryption interface.
- Authentication: None required.
- Response: 200 OK with HTML content.
- Flash Messages: Displayed if a previous encrypt/decrypt operation produced an error.

**POST /encrypt** — File Encryption
- Description: Accepts a file upload and passphrase, returns the AES-256-GCM encrypted binary file.
- Request: multipart/form-data with fields: file (binary, required), encryption_password (string, required).
- Validation: File must be present and non-empty. Password must be non-empty. File extension must be in ALLOWED_EXTENSIONS.
- Response on success: 200 OK, Content-Type: application/octet-stream, Content-Disposition: attachment with .enc filename.
- Response on failure: 302 Redirect to / with flash message.

**GET /decrypt** — Decryption Facility
- Description: Returns the Decryption Facility page with the Two-Factor Lever authorization interface.
- Authentication: None required.
- Response: 200 OK with HTML content.

**POST /decrypt** — File Decryption
- Description: Accepts an .enc file upload and passphrase, attempts AES-256-GCM authenticated decryption, returns original file.
- Request: multipart/form-data with fields: file (binary .enc file, required), password (string, required).
- Validation: File must be present. Password must be non-empty. Encrypted data must be at least 44 bytes.
- Response on success: 200 OK, Content-Type: application/octet-stream, Content-Disposition: attachment with original filename.
- Response on failure: 302 Redirect to /decrypt with generic error flash message. No information about failure reason is exposed.

---

## 3. Data Design

### 3.1 Encrypted Binary Format (Schema)

The ManufacturingVault encrypted file format is a self-contained binary container. The format is designed to be forward-compatible: all information required for decryption, except the passphrase, is embedded in the file header.

| Field | Byte Position | Length | Description |
|-------|-------------|--------|-------------|
| Salt | 0–15 | 16 bytes | Random salt for Argon2id key derivation. Unique per file. |
| Nonce | 16–27 | 12 bytes | Random AES-GCM nonce. Unique per encryption operation. |
| GCM Authentication Tag | 28–43 | 16 bytes | Cryptographic integrity proof. Fails if key or ciphertext is wrong. |
| Ciphertext | 44 – EOF | Variable | AES-256-GCM encrypted file content. |

Minimum valid encrypted file size: 44 bytes (for a zero-length plaintext). Any file shorter than 44 bytes is rejected by the decryption module as malformed.

### 3.2 Data Model (Schema & Encryption)

ManufacturingVault does not use a database for file storage. The design decision to avoid database persistence is intentional and security-motivated: storing encrypted files server-side creates a high-value target, requires access control implementation, and introduces compliance complexity under GDPR (right to erasure) and manufacturing data sovereignty requirements.

The only data model in the system is the in-memory representation of the encryption parameters, which exists only during the scope of a single request handler invocation.

The Azure SQL Database resource (db-manufacturing-historian) provisioned in the infrastructure represents the Manufacturing Historian database for future integration with production data logging systems. It is not used by the current application version.

### 3.3 Data Access Mechanism

File data is accessed in two phases. During upload, the werkzeug FileStorage object provides a read() method that returns the complete file bytes as a Python bytes object from the multipart/form-data request body. During download, the encrypted bytes or decrypted bytes are wrapped in a Flask Response object using Python's bytes directly as the response body. No intermediate file system writes occur at any stage.

### 3.4 Data Retention & Archival Policies

Because ManufacturingVault performs all operations in memory without persistence, the data retention policy is automatically enforced by the application's stateless design:

Plaintext data retention: Zero. Plaintext exists only during the request processing window (typically milliseconds to a few seconds depending on file size).

Encrypted data retention: Zero on the server. The encrypted file exists only in the HTTP response buffer as it is streamed to the user's browser.

User passphrase retention: Zero. The passphrase exists as a Python string within the request handler scope and is not stored, logged, or persisted in any form.

Application log retention: The application logs basic metadata (filename, encrypted size, operation type) to stderr via Gunicorn for operational monitoring. These logs contain no passphrase or file content information.

### 3.5 Data Migration & Seeding

Not applicable. The stateless, persistence-free design means there is no data migration requirement. When new versions of the application are deployed, there is no database schema migration or data seeding step required. The only persistent state in the system is the infrastructure itself (VMs, networking), which is managed by Terraform state files.

---

## 4. Interfaces

### 4.1 User Interface Layout

The Tactical Dashboard implements a three-column Bento-Grid layout for the primary application screen:

**Left Column — Live Telemetry Panel (280px wide):**
A vertical panel with a dark glass background displays scrolling system log messages in JetBrains Mono monospace font, colored in Security Green. New messages are prepended every 2.5 seconds by a JavaScript timer. The panel has a traveling green light pulse animation on its decorative border, implemented using CSS offset-path animation, to give the appearance of an active security monitoring system.

**Center Column — Reactor Core (flexible width):**
The primary operational panel. On the Encryption Hub, it contains the Data-Crucible iris portal (a circular graphic that activates on file selection), a hidden file input that triggers on portal click, a passphrase input field, and the EXECUTE ENCRYPTION submit button. On the Decryption Facility, it contains the encrypted file input, the passphrase input, and the Two-Factor Lever — a styled range input slider that must reach its maximum position to trigger form submission. The panel background uses backdrop-filter: blur(30px) for a layered glass depth effect, making it visually distinct from the sidebar panels.

**Right Column — Hardening Monitor Panel (280px wide):**
A vertical panel displaying security posture metrics: an Encryption Entropy progress bar (representing AES-256 strength), a Memory Isolation indicator (representing encrypted swap status), and a System Integrity badge. These are static visual indicators in the current version, designed as placeholders for future integration with real system monitoring APIs.

**Header Bar (full width):**
Spans all three columns. Contains the MANUFACTURING VAULT brand name on the left, navigation facility selectors ([ENCRYPTION_HUB] and [DECRYPTION_FACILITY]) in the center, and the WAF Status indicator (green pulsing dot + "SHIELDED" / "v2.0.4-TACTICAL") on the right.

**Footer Bar (full width):**
Spans all three columns. Displays copyright attribution on the left and compliance standards badges (ISO 27001 / IEC 62443 / NIST COMPLIANT) on the right.

**Custom Cursor:**
A fixed-position div using CSS clip-path cross lines creates a ghost crosshair cursor that replaces the default browser cursor. It expands and changes color when hovering over interactive elements, providing tactile affordance without relying on standard browser cursor icons.

### 4.2 API Contracts (Request/Response Structure)

**POST /encrypt — Request Contract:**
Content-Type: multipart/form-data
Required fields: file (FileStorage, binary), encryption_password (string, min 1 character, not validated for complexity at application level — enforcement is user responsibility).
File extension must match one of: .nc, .gcode, .l5x, .stl, .dwg, .pdf, .log, .csv, .bin (configurable via ALLOWED_EXTENSIONS environment variable).

**POST /encrypt — Success Response Contract:**
Status: 200 OK
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="original.ext.enc"; filename*=UTF-8''original.ext.enc
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Expires: 0
Access-Control-Expose-Headers: Content-Disposition
X-Content-Type-Options: nosniff
Body: Raw binary bytes of encrypted vault file.

**POST /decrypt — Request Contract:**
Content-Type: multipart/form-data
Required fields: file (FileStorage, binary .enc file), password (string).
The file must be a validly formatted ManufacturingVault .enc binary (44+ bytes with correct header structure).

**POST /decrypt — Success Response Contract:**
Same headers as /encrypt success response except the filename is the original filename with the .enc extension stripped.
Body: Raw binary bytes of decrypted original file.

**POST /decrypt — Failure Response Contract:**
Status: 302 Found
Location: /decrypt
The response sets a flash message "Decryption failed: Wrong password or tampered file." No additional diagnostic information is returned.

---

## 5. State and Session Management

ManufacturingVault is a deliberately stateless application. It does not implement HTTP sessions, user authentication tokens, or server-side state stores of any kind. 

Flask's session mechanism (cookie-based, signed with the application's secret key) is used only in one limited way: to pass flash messages between POST handlers and their redirect targets. Flash messages contain only user-facing error strings (e.g., "File type not allowed") and contain no sensitive data. The Flask secret key is generated at application startup using os.urandom(24), meaning it changes on every Gunicorn restart and flash messages do not persist across restarts.

Because there are no user accounts and no file storage, there is no concept of a logged-in user, no authorization token, and no resource ownership to manage. Each HTTP request is entirely self-contained and independently authorized (or rejected by the WAF).

---

## 6. Caching Strategy

ManufacturingVault applies a strict no-cache policy for all dynamic responses. Every response from the /encrypt and /decrypt routes includes Cache-Control: no-cache, no-store, must-revalidate, Pragma: no-cache, and Expires: 0 headers. This prevents browsers from caching encrypted or decrypted file downloads, protecting against scenarios where a shared computer might allow a subsequent user to retrieve a previously downloaded file from the browser cache.

Static assets (CSS files, served from the Flask /static/ route through Nginx) are served with default Nginx caching headers. Since the CSS contains no sensitive data, caching of static assets is acceptable and beneficial for page load performance.

The WAF and Application Gateway do not perform any response caching. They operate as pass-through proxies for all dynamic requests.

---

## 7. Non-Functional Requirements

### 7.1 Security Aspects

**Authentication Tag Verification:** Every decryption attempt verifies the AES-GCM authentication tag before producing any plaintext output. This is enforced by the AESGCM.decrypt method of the cryptography library, which raises an exception (and produces no output) if the tag is invalid. This is a core requirement: partial decryption or unverified plaintext output is never permissible.

**Side-Channel Resistance:** Argon2id's memory-hard design makes the key derivation process resistant to timing-based side-channel attacks by ensuring the operation always consumes a fixed amount of time and memory regardless of the input. The cryptography library's AESGCM implementation uses constant-time authentication tag comparison to prevent oracle attacks.

**File Type Restriction:** Only explicitly allowlisted file extensions are accepted for encryption. This is enforced at the application level in addition to the WAF-level Content-Disposition inspection, implementing defense-in-depth for file upload security.

**No File Disclosure:** The application never reveals server-side file paths, stack traces, or detailed error information to users. All exceptions in the encrypt and decrypt handlers are caught and converted to generic flash messages.

**WAF Prevention Mode Requirement:** The application is designed to operate exclusively behind a WAF in Prevention mode. Operating in Detection mode only means attack payloads reach the Flask application, which has no WAF-equivalent layer of its own for query parameter inspection.

### 7.2 Performance Aspects

**Argon2id Latency:** The intentional memory-hardness of Argon2id creates an operation latency of approximately 200–500ms per key derivation on the Standard_B2s_v2 VM. This is acceptable for interactive use (a user encrypting or decrypting a file does not notice a half-second delay) while making brute-force attacks computationally impractical. A single brute-force attempt requires 64 MiB of memory and 200-500ms per guess.

**File Size Limits:** The Flask application reads uploaded files entirely into memory before processing. The maximum practical file size is limited by:
- Nginx's client_max_body_size directive (default not configured, inherits from request).
- The WAF's maxRequestBodySizeInKb setting, configured to 2000 KB (2 MB) for request body inspection.
- The VM's available RAM (4 GiB on Standard_B2s_v2, with 3 Gunicorn workers, leaving substantial headroom for files up to hundreds of MB).

For production deployment handling very large industrial files (e.g., large CNC program archives, full DWG assemblies), file size limits should be explicitly configured and tested.

**Gunicorn Workers:** Three Gunicorn workers allow the application to handle up to three concurrent encryption/decryption requests simultaneously. Each Argon2id operation consumes 64 MiB of RAM, so three concurrent operations consume approximately 192 MiB of additional RAM in addition to the baseline Flask application memory. This is well within the 4 GiB VM RAM allocation.

---

## 8. Conclusion

This Low-Level Design document has provided detailed technical specifications for the three most security-critical modules of ManufacturingVault: the AES-256-GCM / Argon2id cryptographic processing pipeline, the Flask application routing and validation layer, and the Tactical Dashboard user interface component architecture.

The key design principle throughout all modules is that security properties are enforced structurally wherever possible, rather than through procedural checks. The stateless design eliminates credential and session management vulnerabilities. The binary format enforces authentication before decryption. The ALLOWED_EXTENSIONS validation enforces file type restrictions before cryptographic processing. The no-store cache policy enforces sensitive data lifecycle management at the HTTP response layer.

Future development iterations should address the currently out-of-scope areas: Multi-Factor Authentication integration, Role-Based Access Control with manufacturing operational roles (Operator, Engineer, Security Officer), server-side audit logging with tamper-evident log storage, and scaling the application to cluster deployment with a shared distributed cache for flash message state instead of the current cookie-based approach.
