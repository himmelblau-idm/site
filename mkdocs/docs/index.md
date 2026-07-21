# Quickstart

**Himmelblau** brings Microsoft Entra ID and OIDC (Google Workspace, Okta, Keycloak, etc) login, policy enforcement, and Hello PIN support to Linux.

## Install Himmelblau

Run the bootstrap installer:

```sh
curl -fsSL https://himmelblau-idm.org/install | sh
```

For most systems, that is all you need. The installer uses your native package manager, prompts for Microsoft Entra ID or generic OIDC settings, configures PAM and NSS, and starts the Himmelblau services.

<details class="hb-advanced-install">
<summary>What the installer does</summary>

The bootstrap installer detects your distribution, offers the supported package sources, adds the trusted Himmelblau repository when needed, and installs packages with `apt`, `dnf`, or `zypper`.<br>

It asks whether to configure Microsoft Entra ID or a generic OIDC provider such as Google Workspace, Okta, or Keycloak.<br>

For Entra ID, it writes a `domain` setting. For generic OIDC, it writes `oidc_issuer_url` and `app_id`. If `/etc/himmelblau/himmelblau.conf` already contains a complete identity provider configuration, the installer treats the run as an upgrade or repair install and leaves the file unchanged.<br>

After package installation and configuration, it enables and starts `himmelblaud` and `himmelblaud-tasks`.<br>

The installer delegates package installation to your system package manager. It does not download or install Himmelblau binaries directly.<br>

For manual repository setup or source builds, see <a href="installation">Installing Himmelblau</a>.<br>

</details>

After installation, log in with your Entra ID or OIDC credentials.

<details class="hb-advanced-install">
<summary>Optional: manual config, PAM, NSS, and service restart</summary>

<details class="hb-advanced-install">
<summary>If you need to edit configuration</summary>

The installer normally writes `/etc/himmelblau/himmelblau.conf` for you. Edit it manually only if the installer did not prompt for your identity provider settings, or if you need to change them later.<br>

The `himmelblau.conf` configuration file uses the <a href="https://en.wikipedia.org/wiki/INI_file">INI file format</a>.<br>

Set the primary domain of your Entra ID tenant in `/etc/himmelblau/himmelblau.conf`:

```conf
[global]
domain = example.onmicrosoft.com
```

For generic OIDC providers such as Google Workspace, Okta, or Keycloak, set the issuer URL and client ID:

```conf
[global]
oidc_issuer_url = https://keycloak.example.com/realms/himmelblau
app_id = himmelblau-login
```

To enforce MDM Intune compliance, enable it:

```conf
[global]
apply_policy = true
```

For additional configuration options, see the <a href="reference/himmelblau-conf">himmelblau.conf man page</a>.

</details>

<details class="hb-advanced-install">
<summary>If PAM was not configured automatically</summary>

On most Linux distributions, PAM configuration happens automatically when you install Himmelblau. If you use distribution-provided packages, you may need to configure PAM manually.<br>

On openSUSE or SUSE Linux Enterprise:

```
sudo pam-config --add --himmelblau
```

On all other distros, you can run the manual config utility bundled with Himmelblau:

```
sudo aad-tool configure-pam
```

For more detail, see <a href="configuration#pam-configuration">PAM configuration</a>.

</details>

<details class="hb-advanced-install">
<summary>If NSS was not configured automatically</summary>

On most Linux distributions, NSS configuration happens automatically when you install Himmelblau.<br>

Add `himmelblau` to your `/etc/nsswitch.conf` to resolve Entra ID users and groups.

```conf
passwd:     files himmelblau
group:      files himmelblau
```

For more detail, see <a href="configuration#nss-configuration">NSS configuration</a>.

</details>

<details class="hb-advanced-install">
<summary>If you changed configuration manually</summary>

The Himmelblau installer normally enables and starts the daemons for you. If you edit configuration manually, restart them:

```
sudo systemctl enable himmelblaud himmelblaud-tasks
sudo systemctl restart himmelblaud himmelblaud-tasks
```

</details>
</details>
