# Introduction to Himmelblau

## What is Himmelblau?

Himmelblau is an open-source project that brings Azure Entra ID (formerly Azure Active Directory) authentication to Linux systems. It enables:

- Single Sign-On (SSO)
- Multi-Factor Authentication (MFA)
- Secure token handling

The project bridges the gap between Microsoft’s identity solutions and Linux environments through modular components for authentication, registration, and identity management.

> 💡 Himmelblau means "sky blue" in German — a nod to Microsoft Azure.

## Why Integrate Azure Entra ID with Linux?

Hybrid IT environments are increasingly common, and Entra ID is central to identity and access management in Microsoft ecosystems. Linux systems often lack first-class support.

Himmelblau addresses this by:

- Providing unified credentials across Windows and Linux
- Enabling Azure MFA (FIDO2, SMS, Authenticator app)
- Supporting browser SSO (via Siemens’ `linux-entra-sso`)
- Meeting compliance requirements
- Scaling across small and large deployments

## Open Source Advantage

As an open-source solution, Himmelblau offers:

- Customizable workflows
- Community-driven development
- No vendor lock-in
