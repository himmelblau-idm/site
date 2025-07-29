# Device Registration with Azure Entra ID

## Overview

Himmelblau supports automatic device registration with Azure Entra ID as part of its first-login flow. This enables conditional access, device-based compliance enforcement, and visibility in the Microsoft Entra admin center.

Device registration is mandatory for:

- Intune integration
- Device-scoped Conditional Access policies

---

## When Registration Occurs

Device registration is initiated automatically when:

- A user authenticates with a domain configured in `himmelblau.conf`
- The device has no cached registration or device identity

This typically happens during the first successful login for each Entra ID–enabled domain. You can enforce registration immediately by running `aad-tool auth-test`.

---

## Registration Workflow

### Step-by-Step

1. **Check for Existing Identity**

    Himmelblau checks whether the device is already registered. This is done by:

    - Looking for sealed credentials in the himmelblau cache.
    - Checking configuration for a `device_id`


2. **Enroll Device**

    If not already registered:

    - Himmelblau contacts the Entra Id `/device` endpoint
    - Uses device credentials (TPM-backed or SoftHSM-backed key)

    For more details, view the [enrollment documentation](https://github.com/himmelblau-idm/aad-join-spec/blob/main/aad-join-spec.md#33-device-join-service).

3. **Store Device Identity**

    Upon successful registration:

    - The device ID and related certificate are stored securely
    - Future token requests include device context

4. **Intune Enroll Device (Optional)**
    Registering the device with Intune is a separate process:

    - Himmelblau contacts the Intune `/enroll` endpoint
    - Uses device credentials from Entra Id enrollment to authenticate

    For more details, view the [Intune enrollment documentation](https://github.com/himmelblau-idm/intune-spec/blob/main/intune-spec.md#211-enroll).

5. **Store Intune Device Identity**

    Upon successful registration:

    - The device ID and related certificate are stored securely
    - Intune and Conditional Access can now recognize the device

---

## Security Considerations

- Registration keys are sealed to the TPM when available
- Device identity is bound to the machine and cannot be reused elsewhere

---

## Managing Registered Devices

Once registered, the device can be managed through the Entra admin portal or Microsoft Intune:

- View device metadata, compliance status, and last check-in
- Enforce policies
- Remove stale entries manually if a device is decommissioned
