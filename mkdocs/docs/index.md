# Quickstart

**Himmelblau** is an open-source authentication framework that brings Microsoft Entra ID login, policy enforcement, and Hello PIN support to Linux systems. This documentation will guide you through installation, configuration, and best practices for integrating Himmelblau into your environment.

## Get Started

- 📥 [Installation Guide](installation.md)
- ⚙️ [Configuration Reference](configuration.md)
- 🔐 [NSS and PAM Setup](configuration.md#pam-configuration)
- 🧠 [Understanding Enrollment](registration.md)

## TL;DR

Himmelblau is designed with sensible defaults to make initial setup fast and simple. If you're eager to get started without reading all the details, follow these basic steps:

1. 📦 **[Download and install the packages](https://himmelblau-idm.org/downloads.html)**

   (Choose the appropriate DEB or RPM for your system and install them.)

2. ✏️ **Edit your config:**  

   Set the primary domain of your Entra ID tenant in `/etc/himmelblau/himmelblau.conf`:

```conf
[global]
domain = example.onmicrosoft.com
```

   To enforce MDM Intune compliance, enable it:

```conf
[global]
apply_policy = true
```

3. 🔐 **[Configure PAM](configuration.md#pam-configuration)**

   On Debian based distros, PAM configuration happens automatically when you install Himmelblau.

   On openSUSE or SUSE Linux Enterprise:

```
sudo pam-config --add --himmelblau
```

   On all other distros, you can run the manual config utility bundled with Himmelblau:

```
sudo aad-tool configure-pam
```

4. 👥 **[Configure NSS](configuration.md#nss-configuration)**

   Add `himmelblau` to your `/etc/nsswitch.conf` to resolve Entra ID users and groups.

```conf
passwd:     files himmelblau
group:      files himmelblau
```

5. 🚀 **Start the daemons:**

```
sudo systemctl enable himmelblaud himmelblaud-tasks
sudo systemctl restart himmelblaud himmelblaud-tasks
```

You’re now ready to log in with your Entra ID credentials!
