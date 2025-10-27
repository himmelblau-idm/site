function addCopyButtons() {
  document.querySelectorAll('#download-links pre').forEach((pre) => {
    // Skip if already wrapped
    if (pre.parentElement.classList.contains('code-block')) return;

    // Create wrapper
    const wrapper = document.createElement('div');
    wrapper.classList.add('code-block');
    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(pre);

    // Create copy button
    const button = document.createElement('button');
    button.className = 'copy-btn';
    button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path d="M10 1.5A1.5 1.5 0 0 1 11.5 3v9A1.5 1.5 0 0 1 10 13.5H4A1.5 1.5 0 0 1 2.5 12V3A1.5 1.5 0 0 1 4 1.5h6zm0 1H4a.5.5 0 0 0-.5.5v9c0 .28.22.5.5.5h6a.5.5 0 0 0 .5-.5V3a.5.5 0 0 0-.5-.5zM13.5 4a.5.5 0 0 1 .5.5v8A1.5 1.5 0 0 1 12.5 14h-6a.5.5 0 0 1 0-1h6a.5.5 0 0 0 .5-.5v-8a.5.5 0 0 1 .5-.5z"/></svg>';
    wrapper.appendChild(button);

    // Copy logic
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

document.getElementById('linux-distro').addEventListener('change', function () {
  provideRepoInstructions();
});

function provideRepoInstructions() {
  const distro = document.getElementById('linux-distro').value;
  const linksContainer = document.getElementById('download-links');
  linksContainer.innerHTML = ''; // clear previous content

  if (!distro) {
    linksContainer.innerHTML = 'Please select a valid distribution.';
    return;
  }

  const baseUrl = 'https://packages.himmelblau-idm.org/stable/latest';
  const gpgKeyUrl = 'https://packages.himmelblau-idm.org/himmelblau.asc';

  const title = document.createElement('h2');
  title.textContent = 'Installing Himmelblau';
  linksContainer.appendChild(title);

  const intro = document.createElement('p');
  intro.textContent =
    'Himmelblau can be installed directly from the official repositories. These repositories provide the latest stable builds for your Linux distribution.';
  linksContainer.appendChild(intro);

  const updateSection = document.createElement('h3');
  updateSection.textContent = '1. Update your system';
  linksContainer.appendChild(updateSection);

  let updateCmd = '';
  if (distro.startsWith('ubuntu') || distro.startsWith('debian')) {
    updateCmd = 'sudo apt update && sudo apt upgrade';
  } else if (distro.startsWith('rocky') || distro.startsWith('fedora') || distro === 'rawhide') {
    updateCmd = 'sudo dnf update';
  } else if (distro.startsWith('sle') || distro === 'tumbleweed') {
    updateCmd = 'sudo zypper update';
  }

  const updatePre = document.createElement('pre');
  updatePre.textContent = updateCmd;
  linksContainer.appendChild(updatePre);

  const repoSection = document.createElement('h3');
  repoSection.textContent = '2. Add the Himmelblau repository and import the signing key';
  linksContainer.appendChild(repoSection);

  if (distro.startsWith('ubuntu') || distro.startsWith('debian')) {
    const steps = [
      `curl -fsSL ${gpgKeyUrl} | gpg --dearmor | sudo tee /usr/share/keyrings/himmelblau.gpg > /dev/null`,
      `echo "deb [signed-by=/usr/share/keyrings/himmelblau.gpg] ${baseUrl}/deb/${distro} ./ " | sudo tee /etc/apt/sources.list.d/himmelblau.list`,
      'sudo apt update'
    ];
    steps.forEach((cmd) => {
      const pre = document.createElement('pre');
      pre.textContent = cmd;
      linksContainer.appendChild(pre);
    });
  } else if (distro.startsWith('rocky') || distro.startsWith('fedora') || distro === 'rawhide') {
    const cmd1 = `sudo rpm --import ${gpgKeyUrl}`;
    const cmd2 = `sudo dnf config-manager --add-repo=${baseUrl}/rpm/${distro}`;
    const cmd3 = 'sudo dnf makecache';
    [cmd1, cmd2, cmd3].forEach((cmd) => {
      const pre = document.createElement('pre');
      pre.textContent = cmd;
      linksContainer.appendChild(pre);
    });
  } else if (distro.startsWith('sle') || distro === 'tumbleweed') {
    const cmd1 = `sudo rpm --import ${gpgKeyUrl}`;
    const cmd2 = `sudo zypper addrepo ${baseUrl}/rpm/${distro} himmelblau`;
    const cmd3 = 'sudo zypper refresh';
    [cmd1, cmd2, cmd3].forEach((cmd) => {
      const pre = document.createElement('pre');
      pre.textContent = cmd;
      linksContainer.appendChild(pre);
    });
  }

  const installSection = document.createElement('h3');
  installSection.textContent = '3. Install Himmelblau';
  linksContainer.appendChild(installSection);

  const installCmd = document.createElement('pre');
  if (distro.startsWith('ubuntu') || distro.startsWith('debian')) {
    installCmd.textContent =
      'sudo apt install -y himmelblau pam-himmelblau nss-himmelblau himmelblau-qr-greeter';
  } else if (distro.startsWith('sle') || distro.startsWith('tumbleweed')) {
    installCmd.textContent =
      'sudo zypper in -y himmelblau pam-himmelblau nss-himmelblau himmelblau-qr-greeter';
  } else {
    installCmd.textContent =
      'sudo dnf install -y himmelblau pam-himmelblau nss-himmelblau himmelblau-qr-greeter';
  }
  linksContainer.appendChild(installCmd);

  const opt = document.createElement('p');
  opt.textContent =
    'Optional packages: himmelblau-sshd-config (for SSH integration) and himmelblau-sso (for browser single sign-on).';
  linksContainer.appendChild(opt);

  addCopyButtons();
}
