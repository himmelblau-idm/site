# Installing Himmelblau

## Overview

Himmelblau is packaged for a wide range of Linux distributions and supports multiple installation methods, including `.deb` and `.rpm` packages, container builds, and manual source compilation.

This page covers how to install Himmelblau on Ubuntu, Debian, RHEL, Rocky, SUSE, and other distributions.

---

## Supported Distributions

<div id="supported-distros">
<p>The following distributions are currently packaged by the Himmelblau project:</p>
<table>
  <thead>
    <tr><th>Distribution</th><th>Version</th></tr>
  </thead>
  <tbody>
    <tr><td>Fedora</td><td>41</td></tr>
    <tr><td>Fedora</td><td>42</td></tr>
    <tr><td>Fedora</td><td>43</td></tr>
    <tr><td>Fedora</td><td>Rawhide</td></tr>
    <tr><td>Rocky Linux</td><td>8</td></tr>
    <tr><td>Rocky Linux</td><td>9</td></tr>
    <tr><td>Rocky Linux</td><td>10</td></tr>
    <tr><td>Red Hat Enterprise Linux</td><td>8</td></tr>
    <tr><td>Red Hat Enterprise Linux</td><td>9</td></tr>
    <tr><td>Red Hat Enterprise Linux</td><td>10</td></tr>
    <tr><td>Oracle Linux</td><td>8</td></tr>
    <tr><td>Oracle Linux</td><td>9</td></tr>
    <tr><td>Oracle Linux</td><td>10</td></tr>
    <tr><td>SUSE Linux Enterprise</td><td>15 SP6</td></tr>
    <tr><td>SUSE Linux Enterprise</td><td>15 SP7</td></tr>
    <tr><td>SUSE Linux Enterprise</td><td>16</td></tr>
    <tr><td>openSUSE Leap</td><td>15.6</td></tr>
    <tr><td>openSUSE Leap</td><td>16</td></tr>
    <tr><td>openSUSE Tumbleweed</td><td></td></tr>
    <tr><td>Debian</td><td>12</td></tr>
    <tr><td>Debian</td><td>13</td></tr>
    <tr><td>Ubuntu</td><td>22.04</td></tr>
    <tr><td>Ubuntu</td><td>24.04</td></tr>
    <tr><td>Linux Mint</td><td>21.3</td></tr>
    <tr><td>Linux Mint</td><td>22</td></tr>
    <tr><td>NixOS</td><td></td></tr>
  </tbody>
</table>
</div>

---

## Installation

### Bootstrap Installer (Recommended)

For most users, install Himmelblau with the bootstrap installer:

```sh
curl -fsSL https://himmelblau-idm.org/install | sh
```

The bootstrapper detects your distribution, offers the supported package sources, adds the trusted Himmelblau repository when needed, installs packages with your native package manager, and asks whether to configure Microsoft Entra ID or a generic OIDC provider such as Google Workspace, Okta, or Keycloak.

For Entra ID, it writes a `domain` setting. For generic OIDC, it writes `oidc_issuer_url` and `app_id`. If `/etc/himmelblau/himmelblau.conf` already contains a complete identity provider configuration, the bootstrapper treats it as an upgrade or repair install and leaves the file unchanged.

After package installation and configuration, the bootstrapper enables and starts both `himmelblaud` and `himmelblaud-tasks`.

The bootstrapper does **not** download or install Himmelblau binaries directly. It delegates installation to `apt`, `dnf`, or `zypper`, and relies on package repositories and package signatures.

> This is the **recommended** installation method for production systems and most users.

---

### Manual Repository Setup (Advanced)

Use the manual repository instructions if you manage repositories with configuration management, need to audit each command before running it, want to install optional packages explicitly, or need vendor-supported distribution packages.

➡️ **[Visit the Downloads page](https://himmelblau-idm.org/downloads)** and expand **Advanced manual package repository instructions** to:

- Select your distribution and release channel
- View the correct repository setup commands for your system
- Copy package-manager commands for `apt`, `dnf`, or `zypper`

The downloads page is kept in sync with the latest release metadata and support matrix used by the bootstrap installer.

---

### Building from Source (Advanced / Developer Use)

If you prefer to build Himmelblau locally — for testing, development, or packaging validation — use the included `Makefile`.  
The build system automatically detects your host distribution and uses either Podman or Docker for reproducible container builds.

#### Steps

##### 1. Clone the repository:

```
git clone https://github.com/himmelblau-idm/himmelblau
cd himmelblau
```

##### 2. Build packages:

```
make               # auto-detects host distro and builds matching packages
```

   or build explicitly for a target:

```
make ubuntu24.04   # or debian13, rocky9, sle16, etc.
```

Run `make help` for the full list of available targets.

##### 3. Install on your current host:

```
sudo make install
```

This installs the locally built packages using the native package manager (apt / dnf / zypper).

---

### Need another distro?

If your environment isn’t listed on the [Supported Distributions](#supported-distributions) table, please [open an issue](https://github.com/himmelblau-idm/himmelblau/issues) or contact a maintainer — we’re happy to help add new targets.
