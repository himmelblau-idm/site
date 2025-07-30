# Understanding Himmelblau Architecture

## Overview

Himmelblau’s architecture is modular, scalable, and designed to integrate deeply with both Linux system services and Microsoft Azure Entra ID. Its core components work together to authenticate users, manage tokens, provide session services, and bridge cloud-based identity with traditional POSIX environments.

---

## Key Components

### `himmelblaud`: Authentication Daemon

The central daemon responsible for:

- Initiating and processing Entra Id authentication flows
- Requesting Primary Refresh Tokens (PRTs) and access tokens
- Managing token lifecycles: storage, renewal, expiration
- Securely communicating with other services via UNIX sockets
- Integrating with:
	- PAM (authentication/account/session/password stacks)
	- NSS (for user/group resolution)

All authentication events funnel through `himmelblaud`, whether invoked via login, SSH, or user switching.

---

### `himmelblau-broker`: SSO Interface

A DBus-based service that:

- Exposes authentication tokens to applications and browser plugins
- Supports automatic token refresh for SSO continuity
- Bridges the gap between system-level login and application-level authentication

Used primarily in desktop environments or with SSO-capable CLI tools.

---

### `himmelblaud-tasks`: Background Worker

This helper service performs actions that are triggered post-authentication:

- Requests cloud-based Kerberos TGTs and stores them in `krb5cc` caches
- Creates and initializes user home directories
- Enforces Intune policies (if enabled).

It runs as a system service alongside `himmelblaud`.

---

### `/etc/himmelblau/himmelblau.conf`: Configuration File

Defines the global and per-domain settings used by Himmelblau:

- Entra ID domains (automatically associated with tenants)
- Logging and debugging options
- POSIX mapping preferences
- Allowed groups for login authorization
- Session environment behavior

Example:

```ini
[global]
domains = example.com
pam_allow_groups = 00000000-1111-2222-3333-444444444444
home_attr = CN
use_etc_skel = true
```

> 📘 **See Also:**
>
> * The himmelblau.conf man page for detailed configuration options
> * The `aad-tool` man page for command-line configuration and diagnostics
