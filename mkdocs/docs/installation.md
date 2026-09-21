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

Choose **Stable Repositories** for maintained, versioned release packages, **Community Nightly** for free development packages, or **Vendor Packages** where available. Stable access does not include technical support.

### Stable Repositories

[Subscribe through Open Collective](https://himmelblau-idm.org/stable-repositories/) using Personal or Organization contributions, monthly or yearly. All four choices provide identical access to both 3.x and 4.x, with no per-host limits or feature restrictions. Amounts are shown at checkout and contributions use the honor system.

You should receive separate entitlement tokens for both streams automatically by email. In the installer, choose Stable Repositories and paste the token for the stream you want. The installer identifies the authorized repository automatically; use the 4.x token for new deployments unless you specifically need 3.x. The token is masked in the terminal and omitted from installer logs. Keep it private.

If your email does not arrive, contact [dmulder@himmelblau-idm.org](mailto:dmulder@himmelblau-idm.org) with proof of subscription. You should receive a response within one business day. This assistance concerns repository access; technical support is not included.

The installer checks the token against the known stable streams and verifies package availability for your distribution and architecture before configuring signed packages with `apt`, `dnf`, or `zypper`. An invalid token or unavailable repository produces an error; it does not silently switch to Nightly. Rawhide is available through Nightly; NixOS uses a separate source-build path.

For upgrades and repairs, the installer reuses the entitlement token from the configured stable repository. Downgrading from a newer installed major release remains blocked and requires manual migration.

#### Automated installation

Save the selected stream's entitlement token in a private file readable by the installer, then run:

```sh
chmod 600 /path/to/entitlement-token
curl -fsSL https://himmelblau-idm.org/install | sh -s -- \
  --channel stable --entitlement-token-file /path/to/entitlement-token
```

Use the token issued for 3.x when that stream is required. The token is read from the file rather than supplied as a command-line argument, keeping it out of shell history and process listings. Automated installation installs packages without changing identity provider configuration.

For a new free development installation, explicitly select Nightly:

```sh
curl -fsSL https://himmelblau-idm.org/install | sh -s -- --channel nightly
```

Use `--channel vendor` for distribution packages where available. A new noninteractive installation without a selected channel stops with guidance. An existing stable subscription can be reused without supplying its URL again.

#### Manual configuration management

Use the installer with the entitlement token issued for the required stream. It determines the distribution-specific repository, installs the repository signing key, and retains signature verification. Each stream has a separate access credential.

Configuration management can run the installer with `--channel stable` and a protected `--entitlement-token-file` as shown above. No entitlement token needs to be entered into the website.

---

### Manual Repository Setup (Advanced)

Use the manual repository instructions if you manage repositories with configuration management, need to audit each command before running it, want to install optional packages explicitly, or need vendor-supported distribution packages.

➡️ **[Visit the Downloads page](https://himmelblau-idm.org/downloads)** and expand **Advanced manual package repository instructions** to:

- Select your distribution and release channel
- View the correct repository setup commands for your system
- Copy package-manager commands for `apt`, `dnf`, or `zypper`

The downloads page uses the support matrix shared with the bootstrap installer. Stable setup requires the entitlement token for your chosen major stream.

---

### Building from Source (Advanced / Developer Use)

If you prefer to build Himmelblau locally — for testing, development, or packaging validation — use the included `Makefile`.  
The build system automatically detects your host distribution and uses either Podman or Docker for reproducible container builds.

#### Steps

##### 1. Clone the repository:

```
git clone https://github.com/himmelblau-idm/himmelblau
cd himmelblau
git checkout stable-4.x
```

Choose `stable-3.x` instead for the 3.x source stream, or `main` for development builds. Building from source remains freely available.

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
