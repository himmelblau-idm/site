# Device Compliance Settings for Linux in Intune with Himmelblau

Himmelblau supports Microsoft Intune compliance policies for Linux by interpreting and enforcing policy settings locally—without requiring the Microsoft Intune app. This enables Linux systems to participate in compliance workflows while maintaining digital sovereignty and compatibility with a wide variety of distributions.

> ⚠️ **Critical Behavior Difference:**
> In Himmelblau, **non-compliance results in immediate authentication failure**.
> If a device does not meet compliance requirements, login is denied.
> This is different from Microsoft Intune, where non-compliance typically results in a policy flag or limited access. Plan and test your policies accordingly.

Himmelblau policies are configured using the Microsoft Intune Settings Catalog. When creating a compliance policy, select the desired settings as you would for other platforms.

---

## Policy Enforcement in Himmelblau

To enable policy enforcement, you must set the following global configuration in `himmelblau.conf`:

```ini
apply_policy = true
```

Without this setting, compliance policies will not be evaluated or enforced.

---

## Linux Settings Categories

### Allowed Distributions

Define minimum and maximum OS versions for specific distributions. Devices outside the allowed range will be marked non-compliant.

> ⚠️ **Warning:** Enforcing this setting may prevent some Himmelblau systems from authenticating.
> While Intune only supports Ubuntu and RedHat, Himmelblau is compatible with many more Linux distributions. If a user attempts to log in from an unsupported or disallowed distro, authentication will fail.

### Custom Compliance

Custom compliance settings are currently **experimental** in Himmelblau. You must explicitly enable them:

```ini
enable_experimental_intune_custom_compliance = true
```

Once enabled, Himmelblau will attempt to evaluate any custom compliance rules defined in your Intune policy. These are executed locally, and any failure results in blocked authentication.

See [Microsoft's documentation](https://learn.microsoft.com/en-us/intune/intune-service/protect/compliance-use-custom-settings) for guidance on policy creation.

> ⚠️ **Note:** The Custom Compliance status is **not reliably reported to Intune**.

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
