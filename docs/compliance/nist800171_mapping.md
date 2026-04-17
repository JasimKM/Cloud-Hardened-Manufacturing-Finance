# Compliance Mapping: NIST SP 800-171
### Protecting Controlled Unclassified Information (CUI) in Non-Federal Systems

ManufacturingVault provides the following technical controls aligned with the **NIST SP 800-171 Rev. 2** standard for protecting sensitive high-value industrial data.

| NIST 800-171 Control | Description | Implementation Detail | Status |
|:---|:---|:---|:---|
| **3.1.3** | Control CUI flow | Purdue Model VNet segmentation prevents unauthorized data movement. | ✅ PASS |
| **3.3.1** | Audit logs | Gunicorn/Nginx logs capture all transaction attempts. | ✅ PASS |
| **3.13.10** | Cryptography at rest | AES-256-GCM authenticated encryption for all files. | ✅ PASS |
| **3.13.11** | FIPS compliance | Uses cryptographic primitives compatible with FIPS 140-2. | ✅ PASS |
| **3.14.6** | Monitor indicators | WAF v2 alerts on suspicious activity (SQLi, XSS). | ✅ PASS |

---
*Note: This mapping addresses the Technical Controls category. Administrative and Physical controls are the responsibility of the manufacturing facility operator.*
