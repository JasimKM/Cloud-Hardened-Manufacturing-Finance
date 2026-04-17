# Project Proposal: ManufacturingVault — Secure Industrial File Encryption Platform

---

## I. Title of the Project

**ManufacturingVault: A Secure Industrial File Encryption and Decryption Web Application with Cloud-Native WAF Protection**

---

## II. Statement of the Problem

Manufacturing organizations generate and exchange sensitive industrial data daily — ranging from CNC machining programs (G-code), programmable logic controller (PLC) ladder logic exports, SCADA configuration files, engineering drawings (DWG), and compliance audit logs. When these files are transmitted across networks or stored on shared servers, they are exposed to unauthorized access, industrial espionage, and cyber sabotage.

Traditional file storage methods in manufacturing environments are inadequately protected. Files are often shared over unencrypted channels, stored with weak access controls, or passed through unsecured web portals that are vulnerable to common web attacks such as SQL Injection and Cross-Site Scripting (XSS). A single breach of such sensitive files can compromise production lines, reveal proprietary manufacturing processes, or create life-safety hazards in plant environments.

The problem, therefore, is to build a secure, web-accessible file encryption and decryption platform specifically designed for industrial manufacturing data, using Python and Flask on a hardened Azure cloud infrastructure, protected by an industry-standard Web Application Firewall, and implementing cryptographically strong AES-256-GCM encryption so that sensitive manufacturing files may be safely transmitted and stored even in hostile network environments.

---

## III. Why This Particular Topic Chosen?

Manufacturing cybersecurity is a rapidly growing field driven by the global adoption of Industry 4.0, where operational technology (OT) systems are increasingly connected to information technology (IT) networks. This convergence creates significant new attack surfaces that traditional enterprise security tools are not designed to address.

The topic was chosen because:

Manufacturing environments handle uniquely sensitive data categories — proprietary machine programs, formulation recipes, and safety system configurations — that require encryption beyond standard enterprise data protection. Industrial cybersecurity standards such as IEC 62443 and the NIST Cybersecurity Framework for OT environments specifically mandate encryption of sensitive industrial data and network segmentation following the Purdue Model.

Additionally, web-accessible industrial tools are increasingly common for engineers working remotely or across facilities, making secure web interfaces for file operations a practical and urgent requirement. By combining strong cryptography (AES-256-GCM with Argon2id key derivation) with a cloud-native Web Application Firewall and Purdue Model network architecture, this project addresses a real-world industrial security challenge that bridges academic cryptography with practical cloud security engineering.

---

## IV. Objective and Scope

**Objective:**
To develop a production-grade, web-based file encryption and decryption platform for industrial manufacturing environments. The platform must implement AES-256-GCM authenticated encryption with Argon2id key derivation, deploy on a hardened Azure cloud infrastructure segmented according to the Purdue Model (IEC 62443 compliant), and protect all web traffic through an Azure Web Application Firewall operating in Prevention mode.

**Scope:**
The system includes the following capabilities and boundaries:

- A Flask web application providing a user-friendly Tactical Dashboard interface for file encryption and decryption operations.
- Support for industrial file types including G-code, L5X (Allen-Bradley), STL, DWG, PDF, CSV, log files, and binary data files.
- AES-256-GCM authenticated encryption ensuring both confidentiality and integrity of encrypted files.
- Argon2id memory-hard key derivation preventing brute-force and GPU-based password cracking attacks.
- Azure cloud infrastructure provisioned through Terraform, including a four-tier Purdue Model virtual network, Application Gateway with WAF v2, and isolated VM compute resources.
- OWASP 3.2 managed rule set enforcement through the WAF, blocking SQL Injection, Cross-Site Scripting, Remote File Inclusion, and other common web attacks.
- The scope does not include real-time SCADA/PLC protocol monitoring, MFA implementation, or integration with enterprise ERP systems.

---

## V. Methodology

The project follows a layered, incremental development approach structured around two primary security layers:

**Infrastructure Layer First:** The Azure cloud infrastructure is designed and provisioned using Terraform before any application code is deployed. This ensures the hardened network environment is established as the foundation, enforcing the principle that security must be built into the architecture rather than added afterward.

**Application Layer Second:** The Flask web application, cryptographic utilities, and reverse proxy configuration (Nginx + Gunicorn) are developed and tested locally before being deployed to the hardened VM. Each functional module — file ingestion, encryption, download, decryption — is tested independently for correctness before integration.

**Security Testing and Validation:** After full deployment, attack simulations are performed against the public endpoint to verify WAF effectiveness. Encryption correctness is validated through round-trip encrypt-then-decrypt testing with both correct and incorrect passwords, as well as file tampering detection tests.

---

## VI. Process Description

**File Ingestion Module:** The user uploads an industrial file through the web interface. The file is received by the Flask application in memory and validated against an allowlist of permitted file extensions. No file is written to disk unencrypted at any point.

**Cryptographic Processing Module:** The encryption process derives a 256-bit AES key from the user's passphrase using Argon2id with a random 16-byte salt. A random 12-byte nonce is generated for AES-GCM mode. The encrypted output binary is structured as: salt (16 bytes) + nonce (12 bytes) + GCM authentication tag (16 bytes) + ciphertext. This authenticated encryption format ensures that any tampering with the encrypted file is detected during decryption.

**Secure Download Module:** The encrypted file is streamed directly to the user's browser as a file download with RFC 8187 compliant Content-Disposition headers. The filename is preserved with a `.enc` extension appended. No encrypted data is persisted on the server.

**Decryption Module:** The user uploads a `.enc` file and provides the original passphrase. The application extracts the salt, nonce, and authentication tag from the binary header, re-derives the AES key using Argon2id, and decrypts the ciphertext. If the password is incorrect or the file has been tampered with, GCM authentication fails and the operation is rejected. The original file is streamed back to the user.

**Web Application Firewall Layer:** All HTTP requests pass through the Azure Application Gateway WAF before reaching the Flask application. In Prevention mode, the WAF inspects request parameters, headers, and body content. Any request matching OWASP Core Rule Set rules for SQLi, XSS, Remote File Inclusion, or other attack patterns is blocked with a 403 Forbidden response before it reaches the application server.

**Infrastructure Orchestration:** The entire Azure infrastructure — including the virtual network, subnets, NSGs, Application Gateway, WAF policy, and VM resources — is defined as Terraform Infrastructure as Code and can be provisioned or destroyed repeatably and consistently.

---

## VII. Resources and Limitations

**Hardware:**
- Development: Standard workstation with internet access for Terraform and Azure CLI operations.
- Production: Azure Standard_B2s_v2 virtual machine (2 vCPU, 4 GiB RAM, Ubuntu Server 22.04 LTS).
- Azure Application Gateway WAF_v2 (managed, serverless).

**Software:**
- Python 3.10, Flask, Gunicorn, Nginx.
- Python libraries: `cryptography`, `argon2-cffi`, `werkzeug`.
- Azure CLI, Terraform 1.5+.
- Bootstrap 5 (frontend framework), JetBrains Mono and Outfit (Google Fonts).

**Limitations:**
- The project implements symmetric encryption; key management (secure sharing of passphrases between authorized parties) is outside scope.
- The system does not implement multi-factor authentication or Role-Based Access Control for the web interface.
- The WAF operates at Layer 7 only; encrypted binary payloads (the `.enc` files) cannot be deeply inspected by the WAF.
- No persistent file storage or audit log is maintained on the server; once a session ends, no trace of the file operation remains.
- The project does not include SCADA protocol simulation or real PLC connectivity.

---

## VIII. Testing Technologies Used

**Black Box Testing:** The encrypted web endpoint is tested as a real-world attacker would approach it. SQL Injection payloads (e.g., `OR 1=1 --`) and Cross-Site Scripting payloads (e.g., `<script>alert(1)</script>`) are submitted as URL query parameters to confirm that the WAF returns HTTP 403 Forbidden for all attack attempts. Normal traffic is confirmed to receive HTTP 200 OK.

**White Box Testing:** The cryptographic module is tested at the unit level. A known plaintext file is encrypted, and the encrypted binary structure is inspected to verify the presence of the correct salt, nonce, and GCM tag positions. A decryption test using the correct password verifies exact byte-for-byte plaintext restoration. A decryption test with an incorrect password verifies that `InvalidTag` exception is raised by the AESGCM library, preventing any plaintext output.

**Integration Testing:** End-to-end testing is performed through the deployed web application: uploading a real manufacturing test file (`.gcode`, `.pdf`), downloading the `.enc` file, re-uploading it to the decryption facility, entering the passphrase using the Two-Factor Lever authorization interface, and verifying the downloaded file matches the original by checksum.

**Infrastructure Testing:** Terraform plan and apply outputs are inspected to verify all NSG rules, subnet associations, WAF policy assignments, and backend pool configurations are deployed as designed.

---

## IX. Conclusion

ManufacturingVault demonstrates how modern cryptographic principles and cloud-native security architecture can be combined to address the real-world cybersecurity challenges faced by industrial manufacturing organizations. The project implements authenticated encryption (AES-256-GCM), memory-hard key derivation (Argon2id), network segmentation following the Purdue Model (IEC 62443), and web application attack prevention (OWASP WAF) as an integrated security platform.

The project provides a strong foundation for understanding the intersection of applied cryptography, industrial cybersecurity standards, and cloud infrastructure security. Future enhancements could include Multi-Factor Authentication, Role-Based Access Control for different manufacturing roles, SCADA protocol monitoring integration, audit logging dashboards, and transition to a full Zero-Trust Architecture aligned with IEC 62443 Security Levels 2 and 3.
