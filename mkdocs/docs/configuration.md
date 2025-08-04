# Configuration

## Overview

Himmelblau is configured primarily through a single file: [`/etc/himmelblau/himmelblau.conf`](reference/himmelblau-conf.md). This file controls authentication behavior, domain bindings, environment setup, policy enforcement, and more.

This page also describes required system integration steps, including PAM and NSS configuration.

---

## Config File: [`/etc/himmelblau/himmelblau.conf`](reference/himmelblau-conf.md)

To enable authentication, you must configure the `domains` option in the [`/etc/himmelblau/himmelblau.conf`](reference/himmelblau-conf.md) file. This setting determines which domains are permitted to authenticate to the host. You MUST only specify the primary domain from each tenant.
All other configuration options are optional.

### Format

The file uses an INI-like syntax with support for `[global]` and per-domain sections:

```ini
[global]
domains = example.com

[example.com]
app_id = 00000000-1111-2222-3333-444444444444
```

### Key Options

| Key                   | Description|
| --------------------- | ------------------------------------------------------------- |
| `domains`		        | Comma-separated list of allowed Entra ID domains				|
| `pam_allow_groups`    | Group object IDs and user UPNs allowed to authenticate        |
| `enable_hello`        | Enables Linux Hello PIN support                               |

**Note:** Leaving the `pam_allow_groups` option unset in the `/etc/himmelblau/himmelblau.conf` file _permits all users to authenticate_.

**Note:** On Ubuntu, you should additionally set `use_etc_skel` to `true` and configure `home_attr` and `home_alias` to match (I recommend using the `CN` or `SPN` attributes). These parameters are necessary, otherwise Ubuntu's snaps will fail to execute. These settings are set by default using the Himmelblau project Debian/Ubuntu packages.

```ini
[global]
home_attr = CN
home_alias = CN
use_etc_skel = true
```

Refer to the [himmelblau.conf](reference/himmelblau-conf.md) man page for a full list of options.

> ⚠️**Important**: To enable hardware-backed security, you must configure TPM support **before authenticating or enrolling this device**. It is disabled by default. [Learn how to configure TPM »](advanced/Configuring-a-Hardware-TPM-for-Secure-Key-Storage.md).

---

## PAM Configuration

To allow users to authenticate with Azure Entra ID, Himmelblau must be integrated into your system’s PAM (Pluggable Authentication Module) stack. This directs authentication requests to the `pam_himmelblau.so` module.

---

### Preferred Configuration Methods

Use one of the following automated tools to insert Himmelblau into the appropriate PAM files.

* **Ubuntu / Debian:**

```bash
sudo pam-auth-update
```

  Then check the box labeled **Azure authentication**.

* **openSUSE / Tumbleweed:**

```bash
sudo pam-config --add --himmelblau
```

* **All systems (manual file editing):**

```bash
sudo aad-tool configure-pam
```

This directly modifies PAM config files such as:

* `/etc/pam.d/common-auth`

> ℹ️ This tool is safe to use as a starting point, and allows fine-grained control later if needed.

---

### Manual Configuration (Advanced)

If the above tools don’t produce the desired result or you require precise control over module ordering and behavior, you may manually edit your PAM stack.

**Guidelines:**

* Place `pam_himmelblau.so` after `pam_localuser.so`
* If using Linux Hello or Passwordless, place Himmelblau *before* `pam_unix.so` to avoid password prompts
* Always include `ignore_unknown_user`
* Ensure `pam_deny.so` is placed last

---

#### Example: `/etc/pam.d/common-auth`

```pam
auth        required      pam_env.so
auth        [default=1 ignore=ignore success=ok] pam_localuser.so
auth        sufficient    pam_unix.so nullok try_first_pass
auth        sufficient    pam_himmelblau.so ignore_unknown_user
auth        required      pam_deny.so
```

> 💡 For Passwordless login, move Himmelblau **above** `pam_unix.so` to avoid fallback password prompts.

---

#### Example: `/etc/pam.d/common-account`

```pam
account     [default=1 ignore=ignore success=ok] pam_localuser.so
account     sufficient    pam_unix.so
account     sufficient    pam_himmelblau.so ignore_unknown_user
account     required      pam_deny.so
```

---

#### Example: `/etc/pam.d/common-session`

```pam
session optional    pam_systemd.so
session required    pam_limits.so
session optional    pam_unix.so try_first_pass
session optional    pam_umask.so 
session optional    pam_himmelblau.so
session optional    pam_env.so
```

---

#### Example: `/etc/pam.d/common-password`

```pam
password    sufficient  pam_himmelblau.so ignore_unknown_user
password    optional    pam_gnome_keyring.so use_authtok
password    sufficient  pam_unix.so use_authtok nullok shadow try_first_pass
password    required    pam_deny.so
```

## NSS Configuration

To ensure system tools can resolve Entra ID users and groups:

1. Edit `/etc/nsswitch.conf`

	Find the `passwd` and `group` lines and modify them to include `himmelblau`, for example:

```conf
passwd:     files himmelblau
group:      files himmelblau
```

---

## Using Multiple Tenants

You can support multiple Azure Entra ID tenants by listing their primary domain names in the global `domains` key:

```ini
[global]
domains = example.com,contoso.com

[example.com]
home_attr = CN

[contoso.com]
app_id = 1111-2222-3333-4444
```

Only the **primary** domain need be listed in the `domains` key. Other domains associated with the same tenant will be configured automatically.

Each domain block may override options like `app_id`, `idmap_range`, or `shell`. Refer to the `himmelblau.conf` man page for a full list of options.

---

## Disabling Linux Hello PIN

Linux Hello authentication is enabled by default. To disable it:

```ini
[global]
enable_hello = false
```

---

## Debug Logging

Enable debug logs for troubleshooting:

```ini
[global]
debug = true
```

Logs are written to:

* `journalctl -u himmelblaud -u himmelblaud-tasks`
