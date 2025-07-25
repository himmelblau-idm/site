# The Himmelblau Ecosystem

## Overview

Himmelblau is more than just a login module — it’s a full ecosystem for managing identity integration between Azure Entra ID and Linux systems.

---

## Core Features and Benefits

### Azure Entra ID Integration

Himmelblau supports modern Azure Entra ID authentication flows:

- OAuth2 authorization with MS-OAPX and OAPXBC extensions
- Primary Refresh Token (PRT) issuance and renewal
- Support for multi-factor authentication (MFA), including:
    - Microsoft Authenticator
    - FIDO2 hardware keys
    - One-time passwords via SMS
    - Temporary Access Pass

### Secure Token Storage and Device Registration

- All credentials and issued tokens are stored in encrypted, machine-bound storage
- SoftHSM and TPM backends are supported
- Seamless device registration with Azure Entra ID during first login

### Kerberos Support

Himmelblau retrieves and caches Ticket Granting Tickets (TGTs) from Azure’s cloud KDC, enabling:

- Secure SSO access to Kerberos-based applications
- Hybrid workflows that combine cloud and on-prem AD Kerberos services

### Single Sign-On (SSO)

Via integration with Siemens' `linux-entra-sso`, Himmelblau enables:

- Firefox/Chrome Browser SSO for Microsoft 365 and Entra ID–protected apps
- Secure, refreshable token storage for long-lived sessions

---

## Supported Linux Distributions

Himmelblau supports a broad range of Linux distributions, including:

**Enterprise-focused:**

- SUSE Linux Enterprise (SLE)
- Red Hat Enterprise Linux (RHEL)
- Rocky Linux

**Community-driven:**

- Ubuntu
- Debian
- Fedora
- openSUSE
- NixOS

---

## Interoperability with Microsoft Services

By emulating Windows authentication flows and integrating directly with Microsoft APIs, Himmelblau enables Linux clients to:

- Authenticate to Microsoft 365 services (Exchange, SharePoint, Teams)
- Access Azure-based applications protected by Entra ID Conditional Access
- Report device state and compliance to Microsoft Intune (optional)
- Function in hybrid environments with both on-prem and cloud resources
