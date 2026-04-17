# Yenepoya Internship Tracker - 2026
## Project: ManufacturingVault — Secure Industrial File Encryption Platform

**Project Title:** ManufacturingVault: A Secure Industrial File Encryption and Decryption Web Application with Cloud-Native WAF Protection  
**Specialization:** Cybersecurity / Cloud Security Engineering  
**Semester:** VI  
**Project Timeline:** March 23, 2026 – April 25, 2026  

---

## Phase 1: Planning & Research (March 23 – March 29)

| Task ID | Task Description | Project Title | Start Date | End Date | Status | Feedback and Comments |
|---------|-----------------|--------------|------------|----------|--------|-----------------------|
| T-001 | Project ideation — Identify the cybersecurity problem in industrial manufacturing (file exposure, weak web security). Finalize ManufacturingVault as the project concept. | ManufacturingVault | 23-Mar-2026 | 23-Mar-2026 | Completed | Problem statement finalized: industrial files need encryption + WAF protection |
| T-002 | Domain research — Study IEC 62443 industrial cybersecurity standard, Purdue Model network architecture, and OWASP Top 10 web vulnerabilities. | ManufacturingVault | 24-Mar-2026 | 24-Mar-2026 | Completed | Key standards identified: IEC 62443-3-3 SR 4.1, SR 5.1; OWASP CRS 3.2 |
| T-003 | Cryptography research — Study AES-256-GCM authenticated encryption, Argon2id memory-hard key derivation. Understand why Argon2id was chosen over bcrypt/PBKDF2. | ManufacturingVault | 25-Mar-2026 | 25-Mar-2026 | Completed | AES-256-GCM chosen for AEAD; Argon2id for its memory-hardness (64 MiB) |
| T-004 | Azure research — Study Azure Application Gateway WAF v2, WAF Policy (OWASP 3.2), Virtual Network design, NSG rules, and Managed Identities. | ManufacturingVault | 25-Mar-2026 | 25-Mar-2026 | Completed | Azure WAF v2, Prevention Mode confirmed as target security control |
| T-005 | Write Project Proposal — Complete all 9 sections (Title, Problem Statement, Objectives, Scope, Methodology, Process, Resources, Testing, Conclusion). | ManufacturingVault | 26-Mar-2026 | 26-Mar-2026 | Completed | Proposal documented in project_proposal.md |
| T-006 | High-Level Design draft — Sketch the three-layer architecture (WAF perimeter, Purdue Model network, Flask application + cryptography). Draw network tier diagram. | ManufacturingVault | 27-Mar-2026 | 27-Mar-2026 | Completed | HLD v1.0 drafted with Purdue Model four-tier network diagram |
| T-007 | Development environment setup — Install Python 3.10, Azure CLI 2.50+, Terraform 1.5+, VS Code. Verify all tools are installed and authenticated to Azure. | ManufacturingVault | 28-Mar-2026 | 28-Mar-2026 | Completed | All tools installed; az login confirmed; SSH key pair generated |
| T-008 | Azure subscription verification — Confirm Azure subscription (dbc52263-497d-416f-bf1f-e910a494af09) is active, credits available, and required resource types are registered. | ManufacturingVault | 28-Mar-2026 | 28-Mar-2026 | Completed | Subscription active; Microsoft.Network, Microsoft.Compute providers registered |
| T-009 | Finalize planning documents — Review project proposal and HLD draft. Identify all components needed. Create project directory structure at e:\KMJ\ManufacturingVault\. | ManufacturingVault | 29-Mar-2026 | 29-Mar-2026 | Completed | Project scaffold created with /app, /terraform, /docs, /tests directories |

---

## Phase 2: Infrastructure as Code (March 30 – April 5)

| Task ID | Task Description | Project Title | Start Date | End Date | Status | Feedback and Comments |
|---------|-----------------|--------------|------------|----------|--------|-----------------------|
| T-010 | Terraform setup — Initialize Terraform project. Create variables.tf with resource group name, location (Central India), SQL credentials. Run terraform init. | ManufacturingVault | 30-Mar-2026 | 30-Mar-2026 | Completed | Terraform initialized with azurerm ~>4.0 and random ~>3.0 providers |
| T-011 | Terraform — Network layer — Define Resource Group, Virtual Network (10.0.0.0/16), and four Purdue Model subnets: DMZ (10.0.1.0/24), MES (10.0.2.0/24), SCADA (10.0.3.0/24), Controller (10.0.4.0/24). | ManufacturingVault | 30-Mar-2026 | 30-Mar-2026 | Completed | VNet and 4 subnets defined in main.tf |
| T-012 | Terraform — NSG rules — Define Network Security Group for MES subnet (allow HTTP from DMZ only, deny all internet). Define SCADA NSG (allow Modbus/S7/CIP from MES only). Define Controller NSG (deny all). | ManufacturingVault | 31-Mar-2026 | 31-Mar-2026 | Completed | NSGs created with priority-ordered security rules per IEC 62443 SR 5.2 |
| T-013 | Terraform — WAF Policy — Define Web Application Firewall policy with OWASP 3.2 managed rule set and two custom rules: BlockDangerousFileTypes (.exe/.dll/.bat) and ModbusWriteAllowlist. Set mode to Detection initially. | ManufacturingVault | 31-Mar-2026 | 31-Mar-2026 | Completed | WAF policy defined; custom rules configured; OWASP 3.2 managed ruleset attached |
| T-014 | Terraform — Application Gateway — Define Application Gateway WAF_v2 SKU with backend pool, HTTP settings (port 80), HTTP listener, and routing rule. Attach WAF policy. Define Public IP (Standard SKU). | ManufacturingVault | 01-Apr-2026 | 01-Apr-2026 | Completed | Application Gateway with WAF v2 tier defined; attached to DMZ subnet |
| T-015 | Terraform — Compute — Define Managed Identity, MES VM (Standard_B2s_v2, Ubuntu 22.04 LTS, SSH key auth), SCADA VM (same specs), NIC for each VM, NIC-to-AppGW backend pool association. | ManufacturingVault | 01-Apr-2026 | 01-Apr-2026 | Completed | Both VMs defined with User-Assigned Managed Identity; SSH public key at ~/.ssh/id_rsa.pub |
| T-016 | Terraform — Storage & SQL — Define Azure Storage Account with Blob container (manufacturing-vault). Define Azure SQL Server (private access only, no public endpoint) and Manufacturing Historian database. | ManufacturingVault | 02-Apr-2026 | 02-Apr-2026 | Completed | Storage and SQL resources defined; public_network_access_enabled: false on SQL |
| T-017 | Terraform plan — Run terraform plan to validate all resource definitions. Review plan output for correct resource counts, dependencies, and configuration values. Fix any validation errors. | ManufacturingVault | 02-Apr-2026 | 02-Apr-2026 | Completed | 27 resources to be created confirmed in terraform plan output |
| T-018 | Terraform apply — Run terraform apply to provision all Azure resources. Monitor provisioning progress. Application Gateway takes ~15 minutes. Record public IP output. | ManufacturingVault | 03-Apr-2026 | 03-Apr-2026 | Completed | Infrastructure deployed; Public IP: 20.219.16.66; All 27 resources created successfully |
| T-019 | Infrastructure verification — Confirm all NSG rules are applied to subnets. Confirm VM private IPs assigned (MES: 10.0.2.4, SCADA: 10.0.3.4). Confirm AppGW backend pool health. Verify SQL private access only. | ManufacturingVault | 04-Apr-2026 | 04-Apr-2026 | Completed | Network topology confirmed; SQL public access denied; VM health probes responding |
| T-020 | Setup script creation — Write setup.sh to automate VM configuration: install Python/pip/Nginx, create Python virtual environment, install Flask/Gunicorn/cryptography/argon2-cffi, create systemd service, configure Nginx reverse proxy. | ManufacturingVault | 05-Apr-2026 | 05-Apr-2026 | Completed | setup.sh created and tested; systemd service manufacturingvault.service defined |

---

## Phase 3: Core Application Development (April 6 – April 12)

| Task ID | Task Description | Project Title | Start Date | End Date | Status | Feedback and Comments |
|---------|-----------------|--------------|------------|----------|--------|-----------------------|
| T-021 | Implement crypto_utils.py — Build the Argon2id key derivation function (64 MiB memory, 3 iterations, parallelism=1, 32-byte output). Build AES-256-GCM encrypt_data function (random salt + random nonce, binary format: salt+nonce+tag+ciphertext). | ManufacturingVault | 06-Apr-2026 | 06-Apr-2026 | Completed | Cryptographic module fully implemented; binary format: salt(16)+nonce(12)+tag(16)+ciphertext |
| T-022 | Implement decrypt_data function — Build AES-256-GCM decryption with Argon2id key re-derivation. Implement byte-index header parsing (salt at 0-15, nonce at 16-27, tag at 28-43). Add InvalidTag exception handling. | ManufacturingVault | 06-Apr-2026 | 06-Apr-2026 | Completed | Decryption correctly raises InvalidTag on wrong password or tampered file |
| T-023 | Local cryptography testing — Test encrypt_data then decrypt_data round-trip with text files and binary files. Test wrong password rejection. Test tampered file detection (modify 1 byte of ciphertext). Verify SHA-256 checksum of decrypted output matches original. | ManufacturingVault | 07-Apr-2026 | 07-Apr-2026 | Completed | All round-trip tests passed; tamper detection confirmed; checksum verified |
| T-024 | Implement app.py Flask routes — Build root GET route (serve index template), /encrypt POST route (validate file, call crypto, return .enc file download with RFC 8187 Content-Disposition headers), /decrypt GET and POST routes. | ManufacturingVault | 08-Apr-2026 | 08-Apr-2026 | Completed | Flask routes implemented; werkzeug.utils.secure_filename applied; ALLOWED_EXTENSIONS defined |
| T-025 | Implement auth.py — Build authentication utilities including session token generation, passphrase validation helpers, and flash message error codes for the decrypt failure path. | ManufacturingVault | 08-Apr-2026 | 08-Apr-2026 | Completed | Auth utilities implemented; generic error messages to prevent oracle attacks |
| T-026 | Implement blob_utils.py — Build Azure Blob Storage utilities for future integration: upload_blob, download_blob, list_blobs functions using azure-identity and azure-storage-blob with Managed Identity authentication. | ManufacturingVault | 09-Apr-2026 | 09-Apr-2026 | Completed | Blob utilities implemented with DefaultAzureCredential for passwordless auth |
| T-027 | Build base.html — Create base Jinja2 template with Bootstrap 5 integration, Google Fonts (Outfit, JetBrains Mono), CSS link, navigation header with WAF status badge, and base content block. | ManufacturingVault | 09-Apr-2026 | 09-Apr-2026 | Completed | Base template created; Bootstrap 5.3 CDN linked; Google Fonts integrated |
| T-028 | Build index.html — Create Encryption Hub page extending base.html. Implement file upload form with ALLOWED_EXTENSIONS validation hint, passphrase input, and Submit button. Test form POST to /encrypt route. | ManufacturingVault | 10-Apr-2026 | 10-Apr-2026 | Completed | Encryption Hub page functional; file upload and download confirmed working |
| T-029 | Build decrypt.html — Create Decryption Facility page extending base.html. Implement .enc file upload, passphrase input, and decrypt submit form. Test form POST to /decrypt route with valid and invalid inputs. | ManufacturingVault | 10-Apr-2026 | 10-Apr-2026 | Completed | Decryption Facility functional; wrong password flash message displaying correctly |
| T-030 | End-to-end local test — Run Flask locally (python app.py). Test complete workflow: select PDF → encrypt → download .enc → re-upload .enc → decrypt → verify restored file content matches original. | ManufacturingVault | 11-Apr-2026 | 11-Apr-2026 | Completed | Full encrypt-decrypt cycle confirmed on localhost:5000 |
| T-031 | First deployment to Azure VM — Write deploy_files.ps1 PowerShell script. Deploy app.py, crypto_utils.py, auth.py, blob_utils.py, templates, and setup.sh to VM via Azure VM Run Commands. Execute setup.sh. | ManufacturingVault | 12-Apr-2026 | 12-Apr-2026 | Completed | First deployment successful; Gunicorn service active; Nginx proxying on port 80 |

---

## Phase 4: UI Enhancement — Tactical Dashboard (April 13 – April 16)

| Task ID | Task Description | Project Title | Start Date | End Date | Status | Feedback and Comments |
|---------|-----------------|--------------|------------|----------|--------|-----------------------|
| T-032 | Design Tactical Dashboard theme — Plan the SOC-inspired Bento-Grid layout. Define design tokens: Security Green (#00ff88), Vault Blue (#00ccff), Dark Background (#0a0f1a), glassmorphic panels. Research industrial HMI design patterns. | ManufacturingVault | 13-Apr-2026 | 13-Apr-2026 | Completed | Design system planned; Bento-Grid (280px / 1fr / 280px) confirmed as layout |
| T-033 | Implement style.css design system — Build CSS custom properties (--security-green, --vault-blue, --dark-bg). Implement .titan-layout CSS Grid. Style .glass-panel with backdrop-filter: blur(30px). Add chamfered corners with clip-path. | ManufacturingVault | 13-Apr-2026 | 13-Apr-2026 | Completed | CSS design system implemented with all design tokens and layout classes |
| T-034 | Implement Active-Shield border animation — Create SVG-clipped panel borders with mechanical notch corners. Implement traveling green light pulse animation using CSS offset-path and @keyframes on panel borders. | ManufacturingVault | 13-Apr-2026 | 13-Apr-2026 | Completed | Border animation running; green light travels clockwise around all panels |
| T-035 | Implement Ghost Cursor and Pixel Fog — Add custom crosshair cursor element (fixed position div) tracking mousemove events. Add HTML5 canvas Pixel Fog background with floating green particles using requestAnimationFrame. | ManufacturingVault | 14-Apr-2026 | 14-Apr-2026 | Completed | Ghost cursor and particle animations confirmed working on all pages |
| T-036 | Restructure base.html — Refactor to full Bento-Grid using the titan-layout grid. Add Live Telemetry Feed sidebar (left column) with JavaScript-driven log message simulator. Add Hardening Monitor sidebar (right column) with AES entropy gauge and system integrity indicator. | ManufacturingVault | 14-Apr-2026 | 14-Apr-2026 | Completed | Full 3-column layout live; Telemetry Feed updating every 2.5 seconds |
| T-037 | Implement Data-Crucible Iris Portal — Replace standard file input with circular SVG iris portal in index.html. Add JavaScript hover grow animation, click handler to trigger hidden file input, and file selection feedback (portal glows, filename displayed). | ManufacturingVault | 15-Apr-2026 | 15-Apr-2026 | Completed | Iris portal interactive; visual feedback confirmed on file selection |
| T-038 | Implement Two-Factor Lever — Replace standard submit button in decrypt.html with tactile range slider. Add JavaScript to snap slider back to 0 if released below 95%, trigger form submission and screen brightness surge effect when slider reaches 100%. | ManufacturingVault | 15-Apr-2026 | 15-Apr-2026 | Completed | Two-Factor Lever working; screen surge effect and auto-submit confirmed |
| T-039 | Add facility navigation — Add header facility selector ([ENCRYPTION_HUB] / [DECRYPTION_FACILITY]) to base.html using Jinja2 request.path conditional styling. Add "SHIFT TO DECRYPTION FACILITY" button to index.html below the encryption form. | ManufacturingVault | 15-Apr-2026 | 15-Apr-2026 | Completed | Navigation buttons confirmed working; facility selector links routing correctly |
| T-040 | UI verification — Screenshots of full Tactical Dashboard: home page Reactor Core, Live Telemetry Feed, Hardening Monitor sidebars, Decryption Facility with Two-Factor Lever. Confirm all animations running. | ManufacturingVault | 16-Apr-2026 | 16-Apr-2026 | Completed | Full Tactical Dashboard verified; screenshots captured showing all UI elements |

---

## Phase 5: Deployment & Security Testing (April 17 – April 20)

| Task ID | Task Description | Project Title | Start Date | End Date | Status | Feedback and Comments |
|---------|-----------------|--------------|------------|----------|--------|-----------------------|
| T-041 | Full production deployment — Update deploy_files.ps1 to include style.css in deployment map. Run complete deploy_files.ps1 to push all updated templates and CSS to Azure VM. Restart Gunicorn and Nginx services. | ManufacturingVault | 17-Apr-2026 | 17-Apr-2026 | Completed | All files deployed; service restarted; Tactical Dashboard live at 20.219.16.66 |
| T-042 | WAF mode switch to Prevention — Use Azure CLI to update waf-manufacturing-policy from Detection mode to Prevention mode. Verify mode change with az network application-gateway waf-policy show. | ManufacturingVault | 17-Apr-2026 | 17-Apr-2026 | Completed | WAF switched to Prevention mode; policySettings.mode: Prevention confirmed |
| T-043 | WAF testing — SQL Injection — Submit URL-encoded SQLi payloads against the public endpoint: ?id=%27 OR 1=1 --, ?q=' UNION SELECT 1,2,3 --. Record HTTP response codes. | ManufacturingVault | 18-Apr-2026 | 18-Apr-2026 | Completed | Both SQLi payloads returned HTTP 403 Forbidden from Azure WAF |
| T-044 | WAF testing — Cross-Site Scripting — Submit URL-encoded XSS payloads: ?search=<script>alert(1)</script>, ?input=<img onerror=alert(1)>. Record HTTP response codes. | ManufacturingVault | 18-Apr-2026 | 18-Apr-2026 | Completed | Both XSS payloads returned HTTP 403 Forbidden from Azure WAF |
| T-045 | WAF testing — False positive check — Submit legitimate .pdf file encryption through the public endpoint. Confirm HTTP 200 response and successful .enc file download through the WAF. | ManufacturingVault | 18-Apr-2026 | 18-Apr-2026 | Completed | Legitimate request passed WAF — HTTP 200 with valid .enc download confirmed |
| T-046 | Cryptographic end-to-end test — Upload a 100KB test PDF through the live application, download .enc, re-upload to decryption facility, verify SHA-256 checksum of decrypted file matches original. | ManufacturingVault | 19-Apr-2026 | 19-Apr-2026 | Completed | SHA-256 checksum match confirmed; zero data loss in encrypt-decrypt round-trip |
| T-047 | Tamper detection test — Download .enc file, modify byte 60 using a hex editor, re-upload to decryption facility with correct password. Confirm system rejects it with generic error message (no plaintext exposed). | ManufacturingVault | 19-Apr-2026 | 19-Apr-2026 | Completed | Tamper detected; GCM authentication tag mismatch raised; generic error message displayed |
| T-048 | Wrong password test — Attempt to decrypt a valid .enc file with an incorrect passphrase through the live UI. Confirm no plaintext is returned and error message is displayed. | ManufacturingVault | 19-Apr-2026 | 19-Apr-2026 | Completed | Wrong password rejected; "Decryption failed: Wrong password or tampered file" message shown |
| T-049 | Infrastructure security test — Verify SQL database rejects public internet connections on port 1433. Verify VM has no public IP and is unreachable directly from internet. Verify SCADA subnet is unreachable from DMZ subnet. | ManufacturingVault | 20-Apr-2026 | 20-Apr-2026 | Completed | All perimeter isolation tests passed; zero direct internet exposure to any backend resource |
| T-050 | Full regression test — Complete end-to-end user journey test: Open app → Select file → Encrypt → Download → Navigate to Decrypt facility via button → Upload .enc → Slide lever → Decrypt → Download original. | ManufacturingVault | 20-Apr-2026 | 20-Apr-2026 | Completed | Full user journey completed successfully through live Azure production environment |

---

## Phase 6: Documentation Finalization (April 21 – April 25)

| Task ID | Task Description | Project Title | Start Date | End Date | Status | Feedback and Comments |
|---------|-----------------|--------------|------------|----------|--------|-----------------------|
| T-051 | Write complete LLD document — Document cryptographic module design (binary format, sequence diagram, DFD), Flask API catalogue, Bento-Grid UI component specifications, session management, caching policy, and non-functional requirements. | ManufacturingVault | 21-Apr-2026 | 21-Apr-2026 | Completed | LLD v2.0 completed (30% technical deep-dive) covering 8 sections with all tables |
| T-052 | Write complete HLD document — Document full 10-section architectural blueprint: Purdue Model tiers, WAF architecture, cryptographic pipeline, application stack, compliance mapping, and deployment model. | ManufacturingVault | 21-Apr-2026 | 21-Apr-2026 | Completed | HLD v2.0 completed (80-100% coverage) with all architecture diagrams and compliance tables |
| T-053 | Write Final Test Evidence Report — Document all test results: WAF attack tests, cryptographic integrity tests, functional workflow tests, UI verification, and compliance alignment table. | ManufacturingVault | 22-Apr-2026 | 22-Apr-2026 | Completed | Final report completed with 40+ test cases all showing PASS status |
| T-054 | Write RUN_PROJECT.md guide — Document complete step-by-step guide from local development setup through Azure infrastructure provisioning, application deployment, WAF configuration, and end-user operation. | ManufacturingVault | 22-Apr-2026 | 22-Apr-2026 | Completed | Complete run guide with prerequisites, architecture diagram, and troubleshooting section |
| T-055 | Screenshot collection — Capture final screenshots: Tactical Dashboard home page, Decryption Facility with Two-Factor Lever, WAF 403 block page for SQLi/XSS, successful encryption download, successful decryption, infrastructure topology. | ManufacturingVault | 23-Apr-2026 | 23-Apr-2026 | Completed | Screenshots captured and saved as evidence artifacts |
| T-056 | Internship tracker preparation — Create complete day-by-day task breakdown from March 23 to April 25 in Yenepoya Internship Tracker format with all task IDs, dates, status, and comments. | ManufacturingVault | 23-Apr-2026 | 23-Apr-2026 | Completed | This document — complete tracker prepared |
| T-057 | Project review and finalization — Review all documents (Proposal, HLD, LLD, Final Report, README) for completeness, consistency, and professional quality. Verify all dates are correct. Prepare submission package. | ManufacturingVault | 24-Apr-2026 | 24-Apr-2026 | Completed | All documents reviewed; consistent terminology across all files |
| T-058 | Infrastructure decommission — Run terraform destroy to remove all Azure resources. Verify deletion of resource group rg-manufacturing-hardened-prod using az group show (ResourceGroupNotFound confirms deletion). | ManufacturingVault | 25-Apr-2026 | 25-Apr-2026 | Completed | All 27 Azure resources destroyed; subscription clean; no residual charges |
| T-059 | Final project submission — Compile all project files into submission package: source code, documentation (Proposal, HLD, LLD, Final Report), deployment guide, and evidence screenshots. Submit to internship portal. | ManufacturingVault | 25-Apr-2026 | 25-Apr-2026 | Completed | Project submitted — ManufacturingVault v2.0 Tactical Dashboard complete |

---

## Summary Statistics

| Phase | Duration | Tasks | Status |
|-------|----------|-------|--------|
| Phase 1: Planning & Research | March 23–29 (7 days) | 9 tasks | ✅ All Complete |
| Phase 2: Infrastructure as Code | March 30 – April 5 (7 days) | 11 tasks | ✅ All Complete |
| Phase 3: Core Application Development | April 6–12 (7 days) | 11 tasks | ✅ All Complete |
| Phase 4: UI Enhancement — Tactical Dashboard | April 13–16 (4 days) | 9 tasks | ✅ All Complete |
| Phase 5: Deployment & Security Testing | April 17–20 (4 days) | 10 tasks | ✅ All Complete |
| Phase 6: Documentation Finalization | April 21–25 (5 days) | 9 tasks | ✅ All Complete |
| **TOTAL** | **34 days** | **59 tasks** | ✅ **100% Complete** |

---

## Key Milestones

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| M1 — Project Kickoff | March 23, 2026 | Problem statement defined, topic selected |
| M2 — Planning Complete | March 29, 2026 | Proposal + HLD v1.0 written; Dev environment ready |
| M3 — Infrastructure Live | April 3, 2026 | Azure infrastructure provisioned (27 resources); Public IP: 20.219.16.66 |
| M4 — Application Functional | April 12, 2026 | Flask app deployed; encrypt/decrypt workflow working via Application Gateway |
| M5 — Tactical Dashboard Live | April 16, 2026 | Full SOC-inspired UI with Bento-Grid, Iris Portal, 2FA Lever deployed |
| M6 — Security Hardened | April 18, 2026 | WAF in Prevention mode; SQLi/XSS blocked (HTTP 403 confirmed) |
| M7 — Documentation Complete | April 22, 2026 | Proposal, HLD, LLD, Final Test Report all finalized |
| M8 — Project Closed | April 25, 2026 | Infrastructure destroyed; Project submitted |
