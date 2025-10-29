/***** STATIC REPO SUPPORT MATRIX ******************************************
 * Leave "include" empty to mean "all distros in your selector are supported"
 * and just list exceptions in "exclude". If you prefer strict allow-lists,
 * put distros in "include" and set "exclude" to [].
 **************************************************************************/
const REPO_SUPPORT = {
  stable: {
    include: [],
    exclude: ['rawhide', 'debian13', 'sle16'],
  },
  nightly: {
    include: [],
    exclude: [],
  },
};

function isDeb(d) { return d.startsWith('ubuntu') || d.startsWith('debian'); }

function baseUrlFor(channel) {
  return channel === 'nightly'
    ? 'https://packages.himmelblau-idm.org/nightly/latest'
    : 'https://packages.himmelblau-idm.org/stable/latest';
}

function isSupported(channel, distro) {
  const cfg = REPO_SUPPORT[channel] || { include: [], exclude: [] };
  // If include list is populated, only those are supported.
  if (cfg.include.length > 0) {
    return cfg.include.includes(distro);
  }
  // Otherwise everything is supported except explicit exclusions.
  return !cfg.exclude.includes(distro);
}

function addCopyButtons() {
  document.querySelectorAll('#download-links pre').forEach((pre) => {
    if (pre.parentElement.classList.contains('code-block')) return;

    const wrapper = document.createElement('div');
    wrapper.classList.add('code-block');
    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(pre);

    const button = document.createElement('button');
    button.className = 'copy-btn';
    button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path d="M10 1.5A1.5 1.5 0 0 1 11.5 3v9A1.5 1.5 0 0 1 10 13.5H4A1.5 1.5 0 0 1 2.5 12V3A1.5 1.5 0 0 1 4 1.5h6zm0 1H4a.5.5 0 0 0-.5.5v9c0 .28.22.5.5.5h6a.5.5 0 0 0 .5-.5V3a.5.5 0 0 1 .5-.5zM13.5 4a.5.5 0 0 1 .5.5v8A1.5 1.5 0 0 1 12.5 14h-6a.5.5 0 0 1 0-1h6a.5.5 0 0 0 .5-.5v-8a.5.5 0 0 1 .5-.5z"/></svg>';
    wrapper.appendChild(button);

    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(pre.textContent.trim());
        button.classList.add('copied');
        setTimeout(() => button.classList.remove('copied'), 2000);
      } catch (err) {
        console.error('Copy failed:', err);
      }
    });
  });
}

async function provideRepoInstructions() {
  const distroEl = document.getElementById('linux-distro');
  const channelEl = document.getElementById('channel');
  const linksContainer = document.getElementById('download-links');

  const distro = distroEl ? distroEl.value : '';
  const requestedChannel = channelEl && channelEl.value ? channelEl.value : 'stable';

  linksContainer.innerHTML = '';

  if (!distro) {
    linksContainer.textContent = 'Please select a valid distribution.';
    return;
  }

  // Resolve effective channel using static matrix + fallback rule
  let channel = requestedChannel;
  let fallback = null;

  if (!isSupported(requestedChannel, distro)) {
    const alt = requestedChannel === 'nightly' ? 'stable' : 'nightly';
    if (isSupported(alt, distro)) {
      channel = alt;
      fallback = { from: requestedChannel, to: alt };
    } else {
      // neither supported; keep requested but flag a hard note
      fallback = { from: requestedChannel, to: null };
    }
  }

  const gpgKeyUrl = 'https://packages.himmelblau-idm.org/himmelblau.asc';
  const baseUrl = baseUrlFor(channel);

  const title = document.createElement('h2');
  title.textContent = `Installing Himmelblau (${channel})`;
  linksContainer.appendChild(title);

  const intro = document.createElement('p');
  intro.textContent =
    channel === 'nightly'
      ? 'Nightly builds include the latest changes and may support more distributions.'
      : 'Stable builds are recommended for most users and track tested releases.';
  linksContainer.appendChild(intro);

  // 1) Update
  const updateSection = document.createElement('h3');
  updateSection.textContent = '1. Update your system';
  linksContainer.appendChild(updateSection);

  let updateCmd = '';
  if (isDeb(distro)) {
    updateCmd = 'sudo apt update && sudo apt upgrade';
  } else if (distro.startsWith('sle') || distro === 'tumbleweed') {
    updateCmd = 'sudo zypper update';
  } else {
    updateCmd = 'sudo dnf update';
  }
  linksContainer.appendChild(Object.assign(document.createElement('pre'), { textContent: updateCmd }));

  // 2) Add repo + key
  const repoSection = document.createElement('h3');
  repoSection.textContent = '2. Add the Himmelblau repository and import the signing key';
  linksContainer.appendChild(repoSection);

  if (isDeb(distro)) {
    [
      `curl -fsSL ${gpgKeyUrl} | gpg --dearmor | sudo tee /usr/share/keyrings/himmelblau.gpg > /dev/null`,
      `echo "deb [signed-by=/usr/share/keyrings/himmelblau.gpg] ${baseUrl}/deb/${distro} ./ " | sudo tee /etc/apt/sources.list.d/himmelblau.list`,
      'sudo apt update'
    ].forEach(cmd => linksContainer.appendChild(Object.assign(document.createElement('pre'), { textContent: cmd })));
  } else if (distro.startsWith('sle') || distro === 'tumbleweed') {
    [
      `sudo rpm --import ${gpgKeyUrl}`,
      `sudo zypper addrepo ${baseUrl}/rpm/${distro} himmelblau-${channel}`,
      'sudo zypper refresh'
    ].forEach(cmd => linksContainer.appendChild(Object.assign(document.createElement('pre'), { textContent: cmd })));
  } else {
    [
      `sudo rpm --import ${gpgKeyUrl}`,
      `sudo dnf config-manager --add-repo=${baseUrl}/rpm/${distro}`,
      'sudo dnf makecache'
    ].forEach(cmd => linksContainer.appendChild(Object.assign(document.createElement('pre'), { textContent: cmd })));
  }

  // 3) Install
  const installSection = document.createElement('h3');
  installSection.textContent = '3. Install Himmelblau';
  linksContainer.appendChild(installSection);

  const installPre = document.createElement('pre');
  installPre.textContent = isDeb(distro)
    ? 'sudo apt install -y himmelblau pam-himmelblau nss-himmelblau'
    : (distro.startsWith('sle') || distro === 'tumbleweed')
      ? 'sudo zypper in -y himmelblau pam-himmelblau nss-himmelblau'
      : 'sudo dnf install -y himmelblau pam-himmelblau nss-himmelblau';
  linksContainer.appendChild(installPre);

  const opt = document.createElement('p');
  opt.textContent =
    channel === 'nightly'
      ? 'Optional packages: himmelblau-sshd-config (for SSH integration), himmelblau-qr-greeter (for DAG QR integration in GDM), himmelblau-sso (for browser single sign-on), o365 (Office 365 web apps), and himmelblau-selinux (SELinux module).'
      : 'Optional packages: himmelblau-sshd-config (for SSH integration), himmelblau-qr-greeter (for DAG QR integration in GDM), and himmelblau-sso (for browser single sign-on).';
  linksContainer.appendChild(opt);

  addCopyButtons();
}

// Listeners
document.getElementById('linux-distro').addEventListener('change', provideRepoInstructions);
const channelEl = document.getElementById('channel');
if (channelEl) channelEl.addEventListener('change', provideRepoInstructions);
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('linux-distro')) provideRepoInstructions();
});
