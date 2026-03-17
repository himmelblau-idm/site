# Device Compliance Settings for Linux in Intune with Himmelblau

Himmelblau supports Microsoft Intune compliance policies for Linux by interpreting and enforcing policy settings locally—without requiring the Microsoft Intune app. This enables Linux systems to participate in compliance workflows while maintaining digital sovereignty and compatibility with a wide variety of distributions.

Himmelblau policies are configured using the Microsoft Intune Settings Catalog. When creating a compliance policy, select the desired settings as you would for other platforms.

---

## Policy Enforcement in Himmelblau

To enable policy enforcement, you must set the following global configuration in `himmelblau.conf`:

```ini
[global]
apply_policy = true
```

Then restart the daemons:

```bash
sudo systemctl restart himmelblaud himmelblaud-tasks
```

Without this setting, compliance policies will not be evaluated or enforced.

In Himmelblau 2.x, policy evaluation is applied only to the first user who signs in on a Linux client. Other users can still authenticate, but policy settings are not applied to them.

---

## Linux Settings Categories

### Allowed Distributions

Define minimum and maximum OS versions for specific distributions. Devices outside the allowed range will be marked non-compliant.

> ⚠️ **Warning:** Enforcing this setting may cause some Himmelblau systems to be reported as non-compliant.
> While Intune only supports Ubuntu and RedHat, Himmelblau is compatible with many more Linux distributions. If a device uses an unsupported or disallowed distro, it may be reported as non-compliant. If distro version compliance is necessary, use a **Custom Compliance** policy instead.

### Custom Compliance

Himmelblau evaluates any custom compliance rules defined in your Intune policy locally and reports the resulting compliance state.

See [Microsoft's documentation](https://learn.microsoft.com/en-us/intune/intune-service/protect/compliance-use-custom-settings) for guidance on policy creation.

### Device Encryption

Enforce disk encryption using dm-crypt (typically via LUKS and `cryptsetup`). Himmelblau checks for encrypted fixed writable volumes.

> 💡 For best results, enable encryption during OS installation. Post-install encryption may be time-consuming and complex.

### Password Policy

These settings apply **to the Linux Hello PIN**, not the user's system password.

> ⚠️ **Important:**
> Enforcing certain complexity rules (e.g., uppercase, symbols) will prevent numeric-only PINs. This may confuse users expecting a simple PIN login experience.

Supported rules:

* Minimum Lowercase
* Minimum Uppercase
* Minimum Symbols
* Minimum Length
* Minimum Digits

> Users supplying non-compliant PINs will be **denied PIN enrollment**.

---

## Refreshing Compliance Status

Compliance is checked during login. To force re-evaluation, simply re-authenticate.
