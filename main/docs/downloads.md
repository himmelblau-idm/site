---
hide:
  - navigation
  - toc
---

# Linux Cloud Authentication

<div class="hb-install-page">

<div class="hb-install-panel">
  <p>Run this in your terminal, then follow the onscreen instructions.</p>

  <pre>curl -fsSL https://himmelblau-idm.org/install | sh</pre>

  <p class="hb-install-note">Uses your native package manager and signed Himmelblau packages. <a href="https://himmelblau-idm.org/install">Review the installer</a>.</p>
</div>

<p class="hb-install-help">Need manual repository commands? Use the advanced section below.</p>

<details class="hb-advanced-install">
<summary>Advanced manual package repository instructions</summary>

Use these instructions if you manage repositories with configuration management, need to review every command before running it, want to install optional packages manually, or prefer vendor-supported distribution packages where available.

<div class="download-selector">
<div id="channel-buttons" class="channel-buttons">
  <button data-value="subscription" class="channel-btn active">Vendor Supported<sup class="footnote-mark">*</sup></button>
  <button data-value="stable" class="channel-btn">Community Stable</button>
  <button data-value="nightly" class="channel-btn">Community Nightly</button>
</div>
<select id="linux-distro" class="linux-distro-select">
    <option value="" selected>Select a distribution</option>
    <option value="sle15sp6">SUSE Linux Enterprise 15 SP6</option>
    <option value="sle15sp7">SUSE Linux Enterprise 15 SP7</option>
    <option value="sle16">SUSE Linux Enterprise 16</option>
    <option value="sle15sp6">openSUSE Leap 15.6</option>
    <option value="sle16">openSUSE Leap 16</option>
    <option value="tumbleweed">openSUSE Tumbleweed</option>
    <option value="rocky8">Rocky Linux 8</option>
    <option value="rocky9">Rocky Linux 9</option>
    <option value="rocky10">Rocky Linux 10</option>
	<option value="fedora42">Fedora 42</option>
    <option value="fedora43">Fedora 43</option>
    <option value="fedora44">Fedora 44</option>
	<option value="rawhide">Fedora Rawhide</option>
	<option value="rocky8">Red Hat Enterprise Linux 8</option>
	<option value="rocky9">Red Hat Enterprise Linux 9</option>
	<option value="rocky10">Red Hat Enterprise Linux 10</option>
	<option value="rocky8">Oracle Linux 8</option>
    <option value="rocky9">Oracle Linux 9</option>
	<option value="rocky10">Oracle Linux 10</option>
    <option value="rocky8">AlmaLinux 8</option>
    <option value="rocky9">AlmaLinux 9</option>
    <option value="rocky10">AlmaLinux 10</option>
    <option value="amzn2023">Amazon Linux 2023</option>
	<option value="debian12">Debian 12</option>
    <option value="debian13">Debian 13</option>
	<option value="ubuntu22.04">Ubuntu 22.04</option>
	<option value="ubuntu24.04">Ubuntu 24.04</option>
    <option value="ubuntu25.10">Ubuntu 25.10</option>
    <option value="ubuntu26.04">Ubuntu 26.04</option>
	<option value="ubuntu22.04">Linux Mint 21.3</option>
	<option value="ubuntu24.04">Linux Mint 22</option>
    <option value="ubuntu26.04">Linux Mint 23</option>
    <option value="nixos">NixOS</option>
</select>
</div>
<select id="channel" style="display:none;">
    <option value="subscription" selected>Vendor Supported</option>
    <option value="stable">Community Stable</option>
    <option value="nightly">Community Nightly</option>
</select>
<div id="download-links" style="margin-top: 20px;"></div>
<div id="configuration" style="display: none;"></div>
<script src="../js/install.js"></script>

<p class="footnote">
  <span class="footnote-mark">*</span>
  Vendor-supported packages are installed using your distribution’s subscription channels (e.g. SLE, Rocky Linux).
</p>

</details>

</div>
