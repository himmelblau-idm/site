---
title: Alternatives
hide:
  - navigation
  - toc
---

## Feature Comparison

Several solutions provide Linux integration with Microsoft Entra ID and Intune, but they differ significantly in their authentication, compliance, and device management capabilities. The table below highlights the features most commonly evaluated by Linux administrators.

| Capability | Himmelblau | Authd | SSSD | Microsoft Intune for Linux |
|------------|------------|--------|--------|--------|
| Linux Login with Entra ID | <span class="yes">✓</span> | <span class="yes">✓</span> | <span class="yes">✓</span> | <span class="no">✗</span> |
| **Native MFA Login**¹ | <span class="yes">✓</span> | <span class="no">✗</span> | <span class="no">✗</span> | <span class="no">✗</span> |
| **Passwordless Login**² | <span class="yes">✓</span> | <span class="no">✗</span> | <span class="no">✗</span> | <span class="no">✗</span> |
| **Hello for Business Authentication**³ | <span class="yes">✓</span> | <span class="no">✗</span> | <span class="no">✗</span> | <span class="no">✗</span> |
| Browser Single Sign-On | <span class="yes">✓</span> | <span class="no">✗</span> | <span class="no">✗</span> | <span class="yes">✓</span> |
| Device Registration | <span class="yes">✓</span> | <span class="yes">✓</span> | <span class="no">✗</span> | <span class="yes">✓</span> |
| Conditional Access | <span class="yes">✓</span> | <span class="no">✗</span> | <span class="no">✗</span> | <span class="yes">✓</span> |
| Cloud Kerberos | <span class="yes">✓</span> | <span class="no">✗</span> | <span class="no">✗</span> | <span class="no">✗</span> |
| Intune Compliance Integration | <span class="yes">✓</span> | <span class="no">✗</span> | <span class="no">✗</span> | <span class="yes">✓</span> |
| TPM-backed Credentials | <span class="yes">✓</span> | <span class="no">✗</span> | <span class="no">✗</span> | <span class="no">✗</span> |
| OIDC Providers Beyond Entra ID | <span class="yes">✓</span> | <span class="yes">✓</span> | <span class="yes">✓</span> | <span class="no">✗</span> |

¹ Graphical login, terminal login, and SSH sessions without requiring a browser-based Device Authorization Grant/QR-code flow.

² Allows users to sign in by approving a request in Microsoft Authenticator without entering a password.

³ Uses Microsoft's Hello for Business protocols.
