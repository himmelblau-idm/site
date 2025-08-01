# Configuring a Hardware TPM for Secure Key Storage

Himmelblau supports the use of a **hardware TPM (Trusted Platform Module)** to securely store cryptographic secrets, including Hello PIN keys, device credentials, and the Primary Refresh Token (PRT). By default, Himmelblau uses a **software HSM**, which provides no hardware-backed security. If your system includes a TPM, we strongly recommend configuring Himmelblau to use it **before enrolling the device**.

> ⚠️ **Warning:** TPM support must be configured **before** authenticating to Entra ID or enrolling the device. If you've already enrolled, you'll need to **reset the local cache** and re-enroll in order to switch to TPM.

---

## When Should I Use TPM?

You should configure Himmelblau to use TPM if:

* Your system includes a TPM 2.0 chip
* You want hardware-backed protection for Hello PIN credentials
* You want secure key binding tied to the physical machine (e.g., protection against disk cloning)
* You're deploying to security-sensitive environments (e.g., laptops, remote workers)

---

## 🛠️ TPM Setup Instructions

### 1. Ensure the TPM Is Available and Functional

Check whether a TPM is exposed on your system by running:

```bash
ls /dev/tpmrm0
```

If that file exists, you likely have a usable TPM. For further inspection, you can optionally install TPM tools:

* On **openSUSE**:

  ```bash
  sudo zypper install tpm2.0-tools
  ```
* On **Debian/Ubuntu**:

  ```bash
  sudo apt install tpm2-tools
  ```

Then run:

```bash
sudo tpm2_getcap properties-fixed
```

This should output a list of TPM capabilities. If not, verify:

* TPM is **enabled** in BIOS/UEFI
* Kernel drivers (`tpm_crb`, `tpm_tis`) are loaded

---

### 2. Configure `himmelblau.conf`

Open `/etc/himmelblau/himmelblau.conf` and change the `hsm_type` setting:

```ini
hsm_type = tpm
```

If you want to fall back to software HSM on systems without a TPM:

```ini
hsm_type = tpm_if_possible
```

> ℹ️ You **do not need to set** `tpm_tcti_name` unless your TPM is exposed through a nonstandard interface. By default, Himmelblau uses:
>
> ```ini
> tpm_tcti_name = device:/dev/tpmrm0
> ```

---

### 3. Restart Himmelblau Services

```bash
sudo systemctl restart himmelblaud
sudo systemctl restart himmelblaud-tasks
```

---

### 4. Enroll the Device

Once TPM is configured, proceed with Entra ID authentication and device enrollment. All future key material will be generated and bound to the TPM.

---

## Switching to TPM After Enrollment

If you've already enrolled the device using `hsm_type = soft`, you can still switch to TPM, but you'll need to **reset the local key cache** and re-enroll:

```bash
sudo aad-tool cache-clear --full
```

Then update `himmelblau.conf` to use `hsm_type = tpm`, restart services, and begin re-enrollment.

---

## Verifying TPM Usage

Check the logs for TPM initialization:

```bash
journalctl -u himmelblaud | grep -i tpm
```

You should see messages indicating successful communication with the TPM and key creation/binding.

---

## Summary

| Feature         | Default              | Recommended for TPM        |
| --------------- | -------------------- | -------------------------- |
| `hsm_type`      | `soft` (no TPM)      | `tpm` or `tpm_if_possible` |
| `tpm_tcti_name` | `device:/dev/tpmrm0` | (usually don't change)     |

**Remember:** TPM must be configured before enrollment. Switching afterward requires clearing the secure key cache.
