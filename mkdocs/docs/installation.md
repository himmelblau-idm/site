# Installing Himmelblau

## Overview

Himmelblau is packaged for a wide range of Linux distributions and supports multiple installation methods, including `.deb` and `.rpm` packages, container builds, and manual source compilation.

This page covers how to install Himmelblau on Ubuntu, Debian, RHEL, Rocky, SUSE, and other distributions.

---

## Supported Distributions

<div id="supported-distros">
  Loading supported distributions...
</div>

---

## Installation from Prebuilt Packages

### Debian & Ubuntu

1. [Download](https://himmelblau-idm.org/downloads.html) the `.deb` packages.

2. Install:

```bash
sudo apt install -y ./himmelblau_<version>-<distro>_amd64.deb ./himmelblau-sshd-config_<version>-<distro>_amd64.deb ./himmelblau-sso_<version>-<distro>_amd64.deb ./nss-himmelblau_<version>-<distro>_amd64.deb ./pam-himmelblau_<version>-<distro>_amd64.deb ./himmelblau-qr-greeter_<version>-<distro>_amd64.deb 
```

### RHEL, Rocky, Fedora

1. [Download](https://himmelblau-idm.org/downloads.html) the `.rpm` packages.

2. Install:

```bash
sudo rpm --import https://himmelblau-idm.org/himmelblau.asc
sudo dnf install ./himmelblau-<version>-1.x86_64-<distro>.rpm ./himmelblau-sshd-config-<version>-1.x86_64-<distro>.rpm ./himmelblau-sso-<version>-1.x86_64-<distro>.rpm ./nss-himmelblau-<version>-1.x86_64-<distro>.rpm ./pam-himmelblau-<version>-1.x86_64-<distro>.rpm ./himmelblau-qr-greeter-<version>-1.x86_64-<distro>.rpm
```

### SUSE Linux Enterprise (SLE) / openSUSE

1. [Download](https://himmelblau-idm.org/downloads.html) the `.rpm` packages.

2. Install:

```bash
sudo rpm --import https://himmelblau-idm.org/himmelblau.asc
sudo zypper install ./himmelblau-<version>-1.x86_64-<distro>.rpm ./himmelblau-sshd-config-<version>-1.x86_64-<distro>.rpm ./himmelblau-sso-<version>-1.x86_64-<distro>.rpm ./nss-himmelblau-<version>-1.x86_64-<distro>.rpm ./pam-himmelblau-<version>-1.x86_64-<distro>.rpm ./himmelblau-qr-greeter-<version>-1.x86_64-<distro>.rpm 
```

---

### From Source

If you prefer to build Himmelblau from source, you can use the provided `Makefile` to produce native packages for your target distribution.

### Steps:

1. Clone the repository:

```bash
git clone https://github.com/himmelblau-idm/himmelblau
cd himmelblau
```

2. Build packages for your distro:

```bash
make ubuntu24.04         # Replace with your target distro
```

   Available distro targets:

```
ubuntu22.04  ubuntu24.04  debian12
rocky8       rocky9       rocky10
sle15sp6     sle15sp7     tumbleweed
fedora41     fedora42     rawhide
```

3. Find the resulting `.deb` or `.rpm` packages in:

```
./packages/
```

You can then install the generated package as normal using your system's package manager (e.g., `dpkg`, `dnf`, or `zypper`).

> 💡 This method ensures proper packaging with dependencies and systemd service files — ideal for testing or contributing to Himmelblau.
