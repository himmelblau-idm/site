# Configuration

## Overview

Himmelblau is configured primarily through a single file: [`/etc/himmelblau/himmelblau.conf`](reference/himmelblau-conf.md). This file controls authentication behavior, domain bindings, environment setup, policy enforcement, and more.

This page also describes required system integration steps, including PAM and NSS configuration.

---

## Config File: [`/etc/himmelblau/himmelblau.conf`](reference/himmelblau-conf.md)

To enable authentication, you must configure the `domain` option in the [`/etc/himmelblau/himmelblau.conf`](reference/himmelblau-conf.md) file. This setting determines which tenant/domain is permitted to authenticate to the host. You SHOULD specify the primary domain for the tenant.
All other configuration options are optional.

### Format

The file uses an INI-like syntax with support for `[global]` and per-domain sections:

```ini
[global]
domain = example.com

[example.com]
app_id = 00000000-1111-2222-3333-444444444444
```

### Key Options

| Key                   | Description|
| --------------------- | ------------------------------------------------------------- |
| `domain`		        | The allowed Entra ID domain                                   |
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

> ⚠️**Important**: To require full TPM-backed security, set `hsm_type = tpm` **before authenticating or enrolling this device**. By default, Himmelblau uses `tpm_bound_soft_if_possible` (software HSM with a TPM-bound top key when available). [Learn how to configure TPM »](advanced/Configuring-a-Hardware-TPM-for-Secure-Key-Storage.md).

---

## PAM Configuration

To allow users to authenticate with Azure Entra ID, Himmelblau must be integrated into your system’s PAM (Pluggable Authentication Module) stack. This directs authentication requests to the `pam_himmelblau.so` module.

---

### Preferred Configuration Methods

Use one of the following automated tools to insert Himmelblau into the appropriate PAM files.

* **Ubuntu / Debian:**

  PAM configuration is handled automatically by the packages. No manual steps are required.

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

* Place `pam_himmelblau.so` after `pam_localuser.so` and before `pam_unix.so`
* Always include `ignore_unknown_user`
* Ensure `pam_deny.so` is placed last

---

#### Example: `/etc/pam.d/common-auth`

```pam
auth        required      pam_env.so
auth        [default=1 ignore=ignore success=ok] pam_localuser.so
auth        sufficient    pam_himmelblau.so ignore_unknown_user
auth        sufficient    pam_unix.so nullok try_first_pass
auth        required      pam_deny.so
```

> 💡 To avoid fallback password prompts, keep `pam_himmelblau.so` above `pam_unix.so` in the pam **auth** stack.

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

## Disabling Linux Hello PIN

Linux Hello authentication is enabled by default. To disable it:

```ini
[global]
enable_hello = false
```

---

### Changing a Hello PIN

To change an existing Hello PIN, run `passwd` as the user. When `pam_himmelblau.so` is present in the system password stack, `passwd` updates the Hello PIN instead of (or in addition to) a local password.

```bash
passwd
```

---

### PIN lifetime and cache behavior

A Hello PIN can last indefinitely. It is only constrained by the lifetime of the cached PRT or refresh token (depending on the environment). If the host is offline longer than the cached PRT validity (often around 14 days, but tenant policy can differ), the Hello credentials expire and an online sign-in is required. At present, that online sign-in results in creating a new PIN; a future update will allow re-associating refreshed credentials with the existing PIN.

---

## Debug Logging

Enable debug logs for troubleshooting:

```ini
[global]
debug = true
```

Logs are written to:

* `journalctl -u himmelblaud -u himmelblaud-tasks`
