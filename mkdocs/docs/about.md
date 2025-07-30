# About Himmelblau

**Himmelblau** is an open-source authentication framework for Linux that integrates securely with **Microsoft Entra ID** (formerly Azure Active Directory). It bridges the long-standing gap between modern cloud identity and traditional Unix authentication (PAM/NSS), bringing MFA, device compliance, and policy enforcement to Linux — without proprietary agents or extra infrastructure.

> *Himmelblau* is German for “sky blue” — a nod to Microsoft’s Azure cloud and our mission to bring seamless cloud identity to Linux.

---

## Origins & Mission

Himmelblau was conceived to address the growing need for **seamless integration between Linux environments and Microsoft Entra ID**. Originating as a **fork of the Kanidm OAuth2 client** led by **William Brown** (SUSE), Himmelblau tailors Kanidm’s proven, security-focused foundations to the specifics of Entra ID, while pushing deeper into **Intune policy enforcement, compliance reporting, and Hello for Business flows**.

Our mission is simple:

- **Parity with Windows** for authentication security and ease.
- **First-class cloud identity on Linux** — with open code, auditable flows, and a modern Rust codebase.
- **Pragmatic interoperability** with existing enterprise tooling.

---

## Key Features

- **Microsoft Entra ID integration**  
  Native support for interactive and brokered OAuth 2.0 / OIDC flows, MFA, SSO, secure token management, and modern enterprise identity standards.

- **(Optional / hybrid) Kerberos compatibility**  
  Extends Entra ID scenarios to Kerberos-backed environments for cloud and on-premises hybrid use cases.

- **Intune policy & compliance**  
  Apply and report Linux Intune compliance results; cache and enforce password/PIN policies locally.

- **Passwordless & FIDO2**  
  Early support for passwordless authentication paths.

- **Rust-first, modular architecture**  
  A systemd daemon (`himmelblaud`) plus PAM/NSS modules and CLI tooling — designed for reliability, memory safety, and maintainability.

- **Open source & community-driven**  
  Built in the open, with transparent design, rigorous logging, and well-defined extension points.

---

## Supported Platforms

Himmelblau targets a wide range of enterprise and community Linux distributions, including:

- **SUSE / SLES**
- **Rocky Linux / RHEL**
- **Fedora**
- **Ubuntu**
- **Debian**
- **NixOS**

(We actively maintain cross-distro build pipelines and packaging; contributions for additional platforms are welcome.)

---

## Who’s Behind It?

Himmelblau is created and primarily maintained by **[David Mulder](mailto:dmulder@himmelblau-idm.org)**, with key contributions from **William Brown** and support from **SUSE engineers** and a growing community of open-source contributors.

---

## Get Involved

We welcome contributors of all kinds — code, docs, packaging, testing, and real-world deployment feedback:

- **Source & issues**: [Github](https://github.com/himmelblau-idm/himmelblau)
- **Discuss / report bugs / request features**: Open a [GitHub issue](https://github.com/himmelblau-idm/himmelblau/issues/new/choose) or [PR](https://github.com/himmelblau-idm/himmelblau/compare)
- **Sponsorship / support**: [Reach out](https://matrix.to/#/#himmelblau:matrix.org) to discuss enterprise needs, or [sponsor the project](https://himmelblau-idm.org/backers.html).

---

## License

Himmelblau is released under the **GPLv3 (or later)** — ensuring the code remains free, auditable, and community-owned.

---
