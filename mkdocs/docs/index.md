# Quickstart

**Himmelblau** is an open-source authentication framework that brings Microsoft Entra ID login, policy enforcement, and Hello PIN support to Linux systems. This documentation will guide you through installation, configuration, and best practices for integrating Himmelblau into your environment.

## Get Started

- 📥 [Installation Guide](#installing-himmelblau)
- ⚙️ [Configuration Reference](#configuring-himmelblau)
- 🔐 [NSS and PAM Setup](#setup-nss)
- 🧠 [Understanding Hello PIN and Enrollment](#enrolling-the-device-and-hello-pin)

## Supported Linux Distributions

<div id="supported-distros">
  Loading supported distributions...
</div>

The following distributions have packages upstream:

| Distribution | Version |
| --- | --- |
| openSUSE | Tumbleweed |
| SUSE Linux Enterprise | 15 SP7 |

## Installing Himmelblau

Himmelblau provides the necessary tools and utilities to enable authentication with Azure Entra ID.

[Download the packages for your distribution](https://himmelblau-idm.org/downloads.html), and install them using your flavor of package manager:

---

### Fedora and Rocky Linux:
```bash
sudo dnf install ./himmelblau-0.8.0-1.x86_64-fedora41.rpm \
                 ./himmelblau-sshd-config-0.8.0-1.x86_64-fedora41.rpm \
                 ./himmelblau-sso-0.8.0-1.x86_64-fedora41.rpm \
                 ./nss-himmelblau-0.8.0-1.x86_64-fedora41.rpm \
                 ./pam-himmelblau-0.8.0-1.x86_64-fedora41.rpm
```

---

### openSUSE/SUSE Linux Enterprise:
```bash
sudo zypper install ./himmelblau-0.8.0-1.x86_64-sle15sp6.rpm \
                    ./himmelblau-sshd-config-0.8.0-1.x86_64-sle15sp6.rpm \
                    ./himmelblau-sso-0.8.0-1.x86_64-sle15sp6.rpm \
                    ./nss-himmelblau-0.8.0-1.x86_64-sle15sp6.rpm \
                    ./pam-himmelblau-0.8.0-1.x86_64-sle15sp6.rpm
```

---

### Debian/Ubuntu:
```bash
sudo apt install ./himmelblau_0.8.0-debian12_amd64.deb \
                 ./himmelblau-sshd-config_0.8.0-debian12_amd64.deb \
                 ./himmelblau-sso_0.8.0-debian12_amd64.deb \
                 ./nss-himmelblau_0.8.0-debian12_amd64.deb \
                 ./pam-himmelblau_0.8.0-debian12_amd64.deb
```

---

## Configuring Himmelblau

To enable authentication, you must configure the `domains` option in the `/etc/himmelblau/himmelblau.conf` file. This setting determines which domains are permitted to authenticate to the host. You MUST only specify the primary domain from each tenant.
All other configuration options are optional.

```ini
[global]
domains = contoso.onmicrosoft.com
```

**Note:** Leaving the `pam_allow_groups` option unset in the `/etc/himmelblau/himmelblau.conf` file _permits all users to authenticate_.

**Note:** On Ubuntu, you should additionally set `use_etc_skel` to `true` and configure `home_attr` and `home_alias` to match (I recommend using the `CN` attribute). These parameters are necessary, otherwise Ubuntu's snaps will fail to execute. These settings are set by default using the Himmelblau project Debian/Ubuntu packages.

```ini
[global]
home_attr = CN
home_alias = CN
use_etc_skel = true
```

### Run the daemon

Enable and start the `himmelblaud` and `himmelblaud-tasks` daemons. The `himmelblaud` daemon communicates with Entra ID and facilitates device, Hello PIN enrollment, and authentication. The `himmelblaud-tasks` daemon is responsible for authenticated tasks, such as creating the users home directory.

```bash
systemctl enable himmelblaud himmelblaud-tasks
systemctl start himmelblaud himmelblaud-tasks
```

### Disable nscd

It is recommended that the Name Service Cache daemon (`nscd`) be disabled.

The nscd daemon caches name service lookups, including user and group information obtained from sources like `/etc/passwd` and `/etc/group`. When integrating with Azure Entra ID, it's important to ensure that the most up-to-date user and group information is consistently retrieved from the directory. Disabling nscd helps avoid potential inconsistencies that may arise from cached data not reflecting changes made in Azure Entra ID.

```bash
systemctl stop nscd
systemctl disable nscd
systemctl mask nscd
```

### Setup NSS

Configuring NSS (Name Service Switch) is essential in integrating Linux hosts with Azure Entra ID using Himmelblau. By configuring NSS to include `himmelblau` alongside sources such as `compat`, `systemd`, etc., the system knows to query Azure Entra ID for user and group information.

The NSS configuration file is found at `/etc/nsswitch.conf`. The `himmelblau` NSS module name should be appended to the `passwd`, `group` and `shadow` entries.

```conf
passwd:     compat systemd himmelblau
group:      compat systemd himmelblau
shadow:     compat systemd himmelblau
```

### Setup PAM

PAM enables flexible authentication mechanisms by allowing administrators to define authentication policies through modular components. Configuring PAM for Azure Entra ID that users can authenticate using their Azure Entra ID credentials. By configuring PAM to include the Himmelblau module, authentication requests are directed to Azure Entra ID.

To configure Himmelblau for PAM on openSUSE Tumbleweed, simply use pam-config:

```bash
pam-config --add --himmelblau
```

To configure Himmelblau for PAM on Ubuntu/Debian distros:

```bash
sudo pam-auth-update
```

Then ensure the `Azure authentication` checkbox is set.

Check the pam files afterward to ensure the configuration was successful.

Otherwise configure pam manually:

In `/etc/pam.d/common-auth`, ensure that the `pam_himmelblau.so` module is placed after other authentication methods (such as `pam_unix.so`). Ensure that other authentication modules are not set to `required`, as this could cause authentication to fail prior to PAM communicating with Entra ID. Include the `ignore_unknown_user` option for Himmelblau. Ensure `pam_deny.so` is placed after all modules, so that unknown users are not implicitly allowed.

**Note:** If you intend to use Hello or Passwordless authentication, it's recommended that `pam_himmelblau.so` be placed before `pam_unix.so` in the pam `auth` stack (but always after `pam_localuser.so`), otherwise `pam_unix` will unnecessarily prompt for a password.

```pam
auth        required      pam_env.so
auth        [default=1 ignore=ignore success=ok] pam_localuser.so
auth        sufficient    pam_unix.so nullok try_first_pass
auth        sufficient    pam_himmelblau.so ignore_unknown_user
auth        required      pam_deny.so
```

Configure `/etc/pam.d/common-account` in a similar manner.

```pam
account    [default=1 ignore=ignore success=ok] pam_localuser.so
account    sufficient    pam_unix.so
account    sufficient    pam_himmelblau.so ignore_unknown_user
account    required      pam_deny.so
```

In `/etc/pam.d/common-session`, set `pam_himmelblau.so` as an optional module.

```pam
session optional    pam_systemd.so
session required    pam_limits.so
session optional    pam_unix.so try_first_pass
session optional    pam_umask.so
session optional    pam_himmelblau.so
session optional    pam_env.so
```

In `/etc/pam.d/common-password`, set `pam_himmelblau.so` as sufficient.

```pam
password	sufficient	pam_himmelblau.so ignore_unknown_user
password        optional        pam_gnome_keyring.so    use_authtok
password	sufficient	pam_unix.so	use_authtok nullok shadow try_first_pass 
password	required	pam_deny.so
```

## Enrolling the Device and Hello PIN

A Windows Hello PIN offers a secure and convenient authentication method by leveraging strong encryption, local authentication capabilities, and integration with Entra ID. By setting a PIN on a soft TPM object and unlocking it securely, users can authenticate to their devices and Azure services with confidence in the security of their credentials.

If you're coming from using Active Directory, you're familiar with a device join. In Azure Entra ID, enrollment (device join) is performed by individual users who can enroll a [maximum of 50 devices each (by default)](https://learn.microsoft.com/en-us/mem/intune/enrollment/device-limit-intune-azure#microsoft-entra-device-limit). Instead of being performed as an administrative action, enrollment happens at authentication time, and the first user to authenticate to a device becomes the owner of the device in Entra ID. Subsequent users who are authorized may authenticate to the device, but will not _own_ the device. In a workplace setting, administrators would be responsible for configuring the himmelblau.conf file, as well as pam and nss, but enrollment would be performed by the user when they receive the device.

```
opensuse-himmelblau login: tux@contoso.onmicrosoft.com
Password: 
Please type in the code displayed on your authenticator app from your device:
Code: 
Set up a PIN
 A Hello PIN is a fast, secure way to signin to your device, apps, and services.
New PIN: 
Confirm PIN: 
Have a lot of fun...
tux@contoso.onmicrosoft.com@opensuse-himmelblau:~>
```

To enroll your device in Entra ID:

1. Login:
    * At the login prompt, enter your username in the format tux@contoso.onmicrosoft.com.
    * Enter your password when prompted.
2. MFA:
    * You'll be prompted to provide multi-factor authentication, using your prefered method.
    * Your device is now enrolled in Entra ID.
3. Set up a PIN:
    * You'll be prompted to set up a PIN for Windows Hello. This PIN serves as a fast and secure way to sign in to your device, apps, and services.
    * Your PIN must be between 6 and 32 characters in length.
    * Enter a new PIN of your choice when prompted.
    * Confirm the new PIN by entering it again.
4. Completion:
    * You are now enrolled in Windows Hello PIN authentication.

Ensure that you choose a strong and memorable PIN to maintain the security of your device. Additionally, keep your PIN confidential and do not share it with others to prevent unauthorized access to your device and associated services. Your PIN is unique to this host, and will not effect authentication to other hosts and Azure services.

You can now use your newly set up PIN to authenticate and access your device.
