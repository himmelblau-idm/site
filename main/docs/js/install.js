/***** STATIC REPO SUPPORT MATRIX ******************************************
 * Leave "include" empty to mean "all distros in your selector are supported"
 * and just list exceptions in "exclude". If you prefer strict allow-lists,
 * put distros in "include" and set "exclude" to [].
 **************************************************************************/
const REPO_SUPPORT = {
	stable: {
		include: [],
		exclude: [],
	},
	nightly: {
		include: [],
		exclude: [],
	},
};

function isDeb(d) {
	return d.startsWith('ubuntu') || d.startsWith('debian');
}
function isNix(d) {
	return d === 'nixos';
}
function isFedora(d) {
  return d === 'fedora42' || d === 'fedora43' || d === 'rawhide';
}

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
		button.innerHTML =
			'<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path d="M10 1.5A1.5 1.5 0 0 1 11.5 3v9A1.5 1.5 0 0 1 10 13.5H4A1.5 1.5 0 0 1 2.5 12V3A1.5 1.5 0 0 1 4 1.5h6zm0 1H4a.5.5 0 0 0-.5.5v9c0 .28.22.5.5.5h6a.5.5 0 0 0 .5-.5V3a.5.5 0 0 1 .5-.5zM13.5 4a.5.5 0 0 1 .5.5v8A1.5 1.5 0 0 1 12.5 14h-6a.5.5 0 0 1 0-1h6a.5.5 0 0 0 .5-.5v-8a.5.5 0 0 1 .5-.5z"/></svg>';
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
	const requestedChannel =
		channelEl && channelEl.value ? channelEl.value : 'stable';

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
	} else if (isNix(distro)) {
		updateCmd = 'sudo nixos-rebuild switch --upgrade';
	} else if (distro.startsWith('sle') || distro === 'tumbleweed') {
		updateCmd = 'sudo zypper update';
	} else if (isFedora(distro)) {
		// DNF5 everywhere for our Fedora targets
		updateCmd = 'sudo dnf upgrade --refresh';
	} else {
		updateCmd = 'sudo dnf update';
	}
	linksContainer.appendChild(
		Object.assign(document.createElement('pre'), {
			textContent: updateCmd,
		}),
	);

	if (isNix(distro)) {
		if (channel === 'stable') {
			// 2) Add the Himmelblau binary cache
			const repoSection = document.createElement('h3');
			repoSection.textContent = '2. Add the Himmelblau binary cache';
			linksContainer.appendChild(repoSection);
			// Use Cachix for binary substitutes
			[
				// Configure Himmelblau cache system-wide (adds substituter & key)
				'sudo nix run nixpkgs#cachix -- use himmelblau',
			].forEach((cmd) =>
				linksContainer.appendChild(
					Object.assign(document.createElement('pre'), {
						textContent: cmd,
					}),
				),
			);

			// Show “install” commands now (NixOS doesn’t use your RPM/DEB repos)
			const installSection = document.createElement('h3');
			installSection.textContent = '3. Install Himmelblau';
			linksContainer.appendChild(installSection);
		} else {
			// Nightly: no cache; building locally is expected
			const tip = document.createElement('p');
			tip.textContent =
				'Tip: builds may take a while the first time since there is no binary cache for nightly.';
			linksContainer.appendChild(tip);

			// Show “install” commands now (NixOS doesn’t use your RPM/DEB repos)
			const installSection = document.createElement('h3');
			installSection.textContent = '2. Install Himmelblau';
			linksContainer.appendChild(installSection);
		}

		// Quick user-profile install (works for both stable & nightly)
		[
			'nix profile install github:himmelblau-idm/himmelblau#himmelblau',
			// Optional desktop/meta package if your flake exposes it
			'nix profile install github:himmelblau-idm/himmelblau#himmelblau-desktop',
		].forEach((cmd) =>
			linksContainer.appendChild(
				Object.assign(document.createElement('pre'), {
					textContent: cmd,
				}),
			),
		);

		// Optional: a system configuration hint for NixOS flake users
		const sysCfg = document.createElement('details');
		const sum = document.createElement('summary');
		sum.textContent = 'NixOS system configuration (flake) example';
		sysCfg.appendChild(sum);
		sysCfg.appendChild(
			Object.assign(document.createElement('pre'), {
				textContent: `# flake.nix (snippet)
{
  description = "My NixOS with Himmelblau";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    himmelblau.url = "github:himmelblau-idm/himmelblau";
  };

  outputs = { self, nixpkgs, himmelblau, ... }:
  let
    system = "x86_64-linux";
  in {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      inherit system;
      modules = [
        # Import the upstream Himmelblau NixOS module
        himmelblau.nixosModules.himmelblau

        # Host configuration
        ({ pkgs, ... }: {
          services.himmelblau = {
            enable = true;

            # Minimal required settings (adjust for your tenant)
            settings = {
              domains = [ "example.com" ];
              pam_allow_groups = [ "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX" ];
            };

            # Optional toggles
            mfaSshWorkaroundFlag = false;
            debugFlag = false;

            # PAM services to wire (sshd added automatically if enabled)
            pamServices = [ "login" "passwd" ];
          };

          # Optional: make CLI available system-wide
          environment.systemPackages = [
            himmelblau.packages.${'${pkgs.system}'}.himmelblau
            # himmelblau.packages.${'${pkgs.system}'} .himmelblau-desktop
          ];

          # Optional: enable SSH so PAM entries for sshd are added
          services.sshd.enable = true;
        })
      ];
    };
  };
}`,
			}),
		);
		linksContainer.appendChild(sysCfg);

		addCopyButtons();
		return; // skip the DEB/RPM paths
	}

	// 2) Add repo + key
	const repoSection = document.createElement('h3');
	repoSection.textContent =
		'2. Add the Himmelblau repository and import the signing key';
	linksContainer.appendChild(repoSection);

	if (isDeb(distro)) {
		[
			`sudo apt install curl && curl -fsSL ${gpgKeyUrl} | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/himmelblau.gpg`,
			`sudo add-apt-repository "deb [arch=amd64] ${baseUrl}/deb/${distro}/ ./"`,
		].forEach((cmd) =>
			linksContainer.appendChild(
				Object.assign(document.createElement('pre'), {
					textContent: cmd,
				}),
			),
		);
	} else if (distro.startsWith('sle') || distro === 'tumbleweed') {
		[
			`sudo rpm --import ${gpgKeyUrl}`,
			`sudo zypper addrepo ${baseUrl}/rpm/${distro} himmelblau-${channel}`,
			'sudo zypper refresh',
		].forEach((cmd) =>
			linksContainer.appendChild(
				Object.assign(document.createElement('pre'), {
					textContent: cmd,
				}),
			),
		);
	} else if (isFedora(distro)) {
		const repoFileUrl = `${baseUrl}/rpm/${distro}/himmelblau.repo`;
		[
			`sudo rpm --import ${gpgKeyUrl}`,
			`sudo dnf config-manager addrepo --from-repofile=${repoFileUrl}`,
			'sudo dnf makecache',
		].forEach((cmd) =>
			linksContainer.appendChild(
				Object.assign(document.createElement('pre'), { textContent: cmd }),
			),
		);
	} else {
		[
			`sudo rpm --import ${gpgKeyUrl}`,
			`sudo dnf config-manager --add-repo=${baseUrl}/rpm/${distro}`,
			'sudo dnf makecache',
		].forEach((cmd) =>
			linksContainer.appendChild(
				Object.assign(document.createElement('pre'), {
					textContent: cmd,
				}),
			),
		);
	}

	// 3) Install
	const installSection = document.createElement('h3');
	installSection.textContent = '3. Install Himmelblau';
	linksContainer.appendChild(installSection);

	const installPre = document.createElement('pre');
	installPre.textContent = isDeb(distro)
		? 'sudo apt install -y himmelblau pam-himmelblau nss-himmelblau'
		: distro.startsWith('sle') || distro === 'tumbleweed'
			? 'sudo zypper in -y himmelblau pam-himmelblau nss-himmelblau'
			: 'sudo dnf install -y himmelblau pam-himmelblau nss-himmelblau';
	linksContainer.appendChild(installPre);

	const opt = document.createElement('p');
	opt.textContent = 'Optional packages: himmelblau-sshd-config (for SSH integration), himmelblau-qr-greeter (for DAG QR integration in GDM), himmelblau-sso (for browser single sign-on), o365 (Office 365 web apps), and himmelblau-selinux (SELinux module).';
	linksContainer.appendChild(opt);

	addCopyButtons();
}

// Listeners
document
	.getElementById('linux-distro')
	.addEventListener('change', provideRepoInstructions);
const channelEl = document.getElementById('channel');
if (channelEl) channelEl.addEventListener('change', provideRepoInstructions);
document.addEventListener('DOMContentLoaded', () => {
	if (document.getElementById('linux-distro')) provideRepoInstructions();
});
