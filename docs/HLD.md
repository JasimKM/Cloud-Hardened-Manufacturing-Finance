# High-Level Design (HLD): ManufacturingVault
### Hardened Cloud Infrastructure for Industrial Data Protection — Architectural Blueprint

**Document Version:** 2.0  
**Coverage:** Complete Architectural Blueprint (100% Scope)  
**Audience:** Chief Technology Officers, Infrastructure Architects, Compliance Officers, Security Leads

---

## Table of Contents

1. Introduction
   - 1.1 Scope of the Document
   - 1.2 Intended Audience
   - 1.3 System Overview
2. System Architecture
   - 2.1 Layered Defense Strategy (Defense-in-Depth)
   - 2.2 Purdue Model Network Segmentation (Zones & Conduits)
   - 2.3 Cloud Infrastructure Component Graph
   - 2.4 Software Stack Selection
   - 2.5 Deployment Model
   - 2.6 Scalability and Availability
3. Data Strategy
   - 3.1 Data Categorization (OT vs. IT Data)
   - 3.2 Cryptographic Governance (AES-256-GCM Standards)
   - 3.3 Storage Privacy Policy (Blob vs. In-Memory)
   - 3.4 Data Retention and Compliance Requirements
   - 3.5 Backup and Recovery Strategy
4. System Interfaces
   - 3.1 External Connectivity (Internet Edge)
   - 3.2 Internal Cross-Subnet Communication
5. System State and Lifecycle Management
6. Performance and Optimization Strategy
7. Non-Functional Requirements (Compliance & Security)
   - 7.1 Security Policy (IEC 62443 Compliance)
   - 7.2 Reliability and Fault Tolerance
8. Conclusion

---

## 1. Introduction

### 1.1 Scope of the Document

This High-Level Design (HLD) document defines the architectural blueprint for ManufacturingVault. It provides a macro-level overview of the entire system, including the Azure infrastructure environment, the network segmentation following the Purdue Reference Model, the application gateway security policy, and the overarching data governance strategy. This document covers approximately 80%–100% of the system architecture, serving as the primary reference for infrastructure deployment and compliance auditing.

Technical implementation details of individual software modules and internal data schemas are deferred to the Low-Level Design (LLD) document.

### 1.2 Intended Audience

This document is intended for executive leadership overseeing digital transformation, infrastructure architects designing the Azure environment, compliance officers assessing IEC 62443 alignment, and lead engineers responsible for the end-to-end integration of OT (Operational Technology) and IT security.

### 1.3 System Overview

ManufacturingVault is a secure industrial file encryption platform designed to protect sensitive manufacturing intellectual property (CNC programs, CAD models, PLC logic) from external threats and unauthorized access. The system combines a hardened "Tactical Dashboard" web interface with a multi-tier cloud infrastructure that enforces strict network isolation between the public internet and industrial data assets.

---

## 2. System Architecture

### 2.1 Layered Defense Strategy (Defense-in-Depth)

The architecture follows a Defense-in-Depth (DiD) model where security is enforced at four distinct layers:
1. **Perimeter Layer:** Azure WAF v2 in Prevention Mode blocks web-based attacks (SQLi, XSS) before they reach the internal network.
2. **Network Layer:** A four-tier Virtual Network (VNet) segments the environment into functional zones (DMZ, MES, SCADA, Controller) using Network Security Groups (NSGs).
3. **Compute Layer:** Hardened Linux nodes running on Managed Identities, with zero-trust access to storage and databases.
4. **Data Layer:** Authenticated encryption (AES-256-GCM) ensures that even if infrastructure is compromised, data remains unreadable without the correct cryptographic material.

### 2.2 Purdue Model Network Segmentation (Zones & Conduits)

Following IEC 62443 standards, the network is segmented into tiers representing the Purdue Reference Model:
- **Level 4 (DMZ Subnet):** Hosts the Application Gateway (WAF). This is the only zone reachable from the public internet.
- **Level 3 (MES Subnet):** Hosts the Application Server (Manufacturing Execution System). It can communicate only with the DMZ (port 80) and Level 2 (port 502/TCP).
- **Level 2 (SCADA Subnet):** Hosts industrial simulators and monitoring tools. It is completely isolated from the internet and the DMZ.
- **Level 0-1 (Controller Subnet):** The most isolated zone, representing physical controllers. Strictly no inbound traffic from higher levels.

### 2.3 Cloud Infrastructure Component Graph

The infrastructure is provisioned as a single resource group containing:
- **Azure Application Gateway:** Functioning as an L7 Load Balancer and WAF v2.
- **VNet (10.0.0.0/16):** With four subnets (DMZ, MES, SCADA, Controller) and dedicated NSGs.
- **MES VM (Standard_B2s_v2):** 2 vCPUs, 4GB RAM, running the core Encryption Hub.
- **Managed Identities:** Eliminating the need for connection strings or passwords to be stored in code.
- **Private Storage Accounts:** Using Private Endpoints to ensure blob data is never exposed to the public internet.

### 2.4 Software Stack Selection

- **Application Logic:** Python 3.10 with Flask 3.0.
- **WSGI Server:** Gunicorn with 3 sync workers for balanced responsiveness.
- **Reverse Proxy:** Nginx for TLS termination and static asset serving.
- **Infrastructure:** Microsoft Azure with Terraform 1.5+ for predictable deployments.
- **Cryptography:** OpenSSL-backed Python `cryptography` library for FIPS-compliant algorithms.

### 2.5 Deployment Model

The system uses a "Blueprints-First" deployment model. All infrastructure is defined as code (Terraform), followed by an automated configuration script (`setup.sh`) that hardens the OS, installs dependencies, and initializes the service. Code deployment is handled via secure synchronization to the MES VM, followed by a zero-downtime service restart.

### 2.6 Scalability and Availability

While the current deployment is a single-node setup for audit verification, the architecture is "Scale-Out Ready." The Application Gateway can be configured with an Autoscale policy, and the MES VMs can be placed behind a Scale Set to handle high-volume industrial file processing across multiple manufacturing sites.

---

## 3. Data Strategy

### 3.1 Data Categorization (OT vs. IT Data)

The system distinguishes between two data classes:
- **Transient Operational Data:** Passphrases and file bytes processed in-memory. Retention = 0.
- **Persistent Compliance Data:** System logs and telemetry displayed on the Tactical Dashboard. Retention = 30 days.

### 3.2 Cryptographic Governance (AES-256-GCM Standards)

All industrial files are protected using the AES-256-GCM standard. Argon2id is the mandatory key derivation function, configured with 64MiB of memory to prevent GPU-accelerated brute-force attacks. This standard ensures that even a partial server compromise does not expose the manufacturing secret keys.

### 3.3 Storage Privacy Policy (Blob vs. In-Memory)

By design, the Encryption Hub is stateless. Plaintext data is never written to the VM's disk. Secure file downloads are generated as streaming responses, ensuring zero leakage of plaintext to permanent server storage.

### 3.4 Data Retention and Compliance Requirements

ManufacturingVault aligns with the **IEC 62443-3-3** requirements for data integrity and confidentiality. All operations are logged for audit purposes but cleansed of any sensitive file content or metadata to comply with industrial privacy standards.

### 3.5 Backup and Recovery Strategy

The HLD assumes a "Recovery from Code" strategy. Since no persistent state is maintained on the web server, recovery involves redeploying the infrastructure via Terraform and syncing the application files, resulting in a 100% clean, verified state in under 15 minutes.

---

## 4. System Interfaces

### 3.1 External Connectivity (Internet Edge)

The only entry point is HTTPS (443) on the Application Gateway IP. All other ports (22, 5000, 80) are blocked at the perimeter.

### 3.2 Internal Cross-Subnet Communication

Traffic between the MES subnet and SCADA subnet is strictly limited to authorized protocol conduits (Modbus TCP/502). All other internal traffic is dropped by the NSG "Deny-All" default rule.

---

## 5. System State and Lifecycle Management

The system follows a stateless operational lifecycle. State is maintained solely on the client-side (browser) during the encryption session. The server-side VM exists in a "Read-Only" operational state, where only the running Gunicorn process holds the transient file buffers.

---

## 6. Performance and Optimization Strategy

To maintain performance on industrial networks, the system implements:
- **Stateless responses:** Reducing server-side memory pressure.
- **Nginx static caching:** Speeding up the delivery of the Tactical Dashboard UI.
- **Resource capping:** Limiting Argon2id threads to prevent CPU starvation during peak upload periods.

---

## 7. Non-Functional Requirements (Compliance & Security)

### 7.1 Security Policy (IEC 62443 Compliance)

The system maps directly to the following security requirements:
- **SR 3.1 (Communication Integrity):** Handled by AES-GCM tags.
- **SR 4.1 (Data Confidentiality):** Handled by AES-256 encryption.
- **SR 5.2 (Resource Isolation):** Handled by Purdue VNet segmentation.

### 7.2 Reliability and Fault Tolerance

Fault tolerance is provided at the Azure platform level. The Managed SQL Historian and Application Gateway provide 99.95% SLAs, ensuring that the security boundary remains active even during underlying hardware maintenance.

---

## 8. Conclusion

This High-Level Design defines a robust, industrial-grade architecture for protected manufacturing data. By combining a hardened cloud perimeter (WAF) with strict zone isolation (Purdue Model) and mathematical encryption (AES-256-GCM), ManufacturingVault provides a scalable and compliant foundation for modern smart-factory security.

---
