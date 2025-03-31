document.getElementById('linux-distro').addEventListener('change', function () {
	provideLinks(); // Call the function directly when the selection changes
});

async function fetchLatestVersion(apiUrl) {
	try {
		const response = await fetch(apiUrl);
		if (!response.ok) {
			throw new Error('Failed to fetch the latest release info');
		}
		const data = await response.json();
		return data.tag_name; // Assuming the tag name is the version number
	} catch (error) {
		console.error('Error fetching release data:', error);
		return null; // Handle the error appropriately in your production environment
	}
}

async function provideLinks() {
	const version = await fetchLatestVersion(
		'https://api.github.com/repos/himmelblau-idm/himmelblau/releases/latest',
	); // Get the latest version number
	if (!version) {
		document.getElementById('download-links').innerHTML =
			'Failed to retrieve the latest version.';
		return;
	}
	const cirrus_scope_version = await fetchLatestVersion(
		'https://api.github.com/repos/himmelblau-idm/cirrus-scope/releases/latest',
	);
	if (!cirrus_scope_version) {
		document.getElementById('download-links').innerHTML =
			'Failed to retrieve the latest cirrus-scope version.';
		return;
	}

	const distro = document.getElementById('linux-distro').value;
	const linksContainer = document.getElementById('download-links');
	linksContainer.innerHTML = ''; // Clear previous links

	if (!distro) {
		linksContainer.innerHTML = 'Please select a valid distribution.';
		return;
	}

	const configSection = document.getElementById('configuration');
	if (!distro) {
		configSection.style.display = 'none';
		linksContainer.innerHTML = 'Please select a valid distribution.';
		return;
	}

	configSection.style.display = 'block';

	const baseUrl =
		'https://github.com/himmelblau-idm/himmelblau/releases/latest/download/';
	const packages = [
		'himmelblau',
		'himmelblau-sshd-config',
		'himmelblau-sso',
		'nss-himmelblau',
		'pam-himmelblau',
		'himmelblau-qr-greeter',
	];
	const cirrus_scope_base_url =
		'https://github.com/himmelblau-idm/cirrus-scope/releases/latest/download/';

	const list = document.createElement('ul');
	list.classList.add('download-list');
	packages.forEach((pkg) => {
		const filename =
			distro === 'debian12' || distro.startsWith('ubuntu')
				? `${pkg}_${version}-${distro}_amd64.deb`
				: `${pkg}-${version}-1.x86_64-${distro}.rpm`;
		const link = document.createElement('a');
		link.href = baseUrl + filename;
		link.textContent = filename;
		link.target = '_blank';

		const listItem = document.createElement('li');
		listItem.appendChild(link);
		list.appendChild(listItem);
	});
	const cirrus_scope_filename =
		distro === 'debian12' || distro.startsWith('ubuntu')
			? `cirrus-scope_${cirrus_scope_version}-${distro}_amd64.deb`
			: `cirrus-scope-${cirrus_scope_version}-1.x86_64-${distro}.rpm`;
	const link = document.createElement('a');
	link.href = cirrus_scope_base_url + cirrus_scope_filename;
	link.textContent = cirrus_scope_filename;
	link.target = '_blank';

	const listItem = document.createElement('li');
	listItem.appendChild(link);
	list.appendChild(listItem);

	linksContainer.appendChild(list);

	const title = document.createElement('h2');
	title.textContent = 'Installing Himmelblau';
	linksContainer.appendChild(title);

	const item1 = document.createElement('p');
	item1.textContent =
		'Ensure the system is updated and you have administrative access:';
	linksContainer.appendChild(item1);

	if (distro.startsWith('sle') || distro === 'tumbleweed') {
		const cmd1 = document.createElement('pre');
		cmd1.textContent = 'sudo zypper update';
		linksContainer.appendChild(cmd1);
	} else if (distro.startsWith('ubuntu') || distro.startsWith('debian')) {
		const cmd1 = document.createElement('pre');
		cmd1.textContent = 'sudo apt update && sudo apt upgrade';
		linksContainer.appendChild(cmd1);
	} else if (
		distro.startsWith('rocky') ||
		distro === 'rawhide' ||
		distro.startsWith('fedora')
	) {
		const cmd1 = document.createElement('pre');
		cmd1.textContent = 'sudo dnf update';
		linksContainer.appendChild(cmd1);
	}

	const item2 = document.createElement('p');
	item2.textContent =
		'Download the packages from the links above, import the package signing key, and install the packages:';
	linksContainer.appendChild(item2);

	if (distro.startsWith('sle') || distro === 'tumbleweed') {
		// GPG key import command for Zypper
		const keyCmd = document.createElement('pre');
		keyCmd.textContent =
			'sudo rpm --import https://himmelblau-idm.org/himmelblau.asc';
		linksContainer.appendChild(keyCmd);

		const cmd1 = document.createElement('pre');
		cmd1.textContent = 'sudo zypper install ';
		packages.forEach((pkg) => {
			const filename = `${pkg}-${version}-1.x86_64-${distro}.rpm`;
			cmd1.textContent += './' + filename + ' ';
		});
		linksContainer.appendChild(cmd1);
	} else if (distro.startsWith('ubuntu') || distro.startsWith('debian')) {
		// DEB packages don't have signing available yet
		// GPG key install for APT
		//const keyCmd = document.createElement('pre');
		//keyCmd.textContent =
		//	'curl -fsSL https://himmelblau-idm.org/himmelblau.asc | gpg --dearmor | sudo tee /usr/share/keyrings/himmelblau.gpg > /dev/null';
		//linksContainer.appendChild(keyCmd);

		const cmd1 = document.createElement('pre');
		cmd1.textContent = 'sudo apt install -y ';
		packages.forEach((pkg) => {
			const filename = `${pkg}_${version}-${distro}_amd64.deb`;
			cmd1.textContent += './' + filename + ' ';
		});
		linksContainer.appendChild(cmd1);
	} else if (
		distro.startsWith('rocky') ||
		distro === 'rawhide' ||
		distro.startsWith('fedora')
	) {
		// GPG key import command for DNF/YUM-based systems
		const keyCmd = document.createElement('pre');
		keyCmd.textContent =
			'sudo rpm --import https://himmelblau-idm.org/himmelblau.asc';
		linksContainer.appendChild(keyCmd);

		const cmd1 = document.createElement('pre');
		cmd1.textContent = 'sudo dnf install ';
		packages.forEach((pkg) => {
			const filename = `${pkg}-${version}-1.x86_64-${distro}.rpm`;
			cmd1.textContent += './' + filename + ' ';
		});
		linksContainer.appendChild(cmd1);
	}

	const opt_title = document.createElement('h3');
	opt_title.textContent = 'Optional Packages';
	linksContainer.appendChild(opt_title);

	const sshd_pkg = 'himmelblau-sshd-config';
	const sshd_filename =
		distro === 'debian12' || distro.startsWith('ubuntu')
			? `${sshd_pkg}_${version}-${distro}_amd64.deb`
			: `${sshd_pkg}-${version}-1.x86_64-${distro}.rpm`;
	const sso_pkg = 'himmelblau-sso';
	const sso_filename =
		distro === 'debian12' || distro.startsWith('ubuntu')
			? `${sso_pkg}_${version}-${distro}_amd64.deb`
			: `${sso_pkg}-${version}-1.x86_64-${distro}.rpm`;
	const item3 = document.createElement('p');
	item3.textContent = `You need only install the package ${sshd_filename} if the host will require ssh access, and need only install the ${sso_filename} package if you require Firefox and Chrome Single-Sign-On.`;
	linksContainer.appendChild(item3);

	if (distro.startsWith('ubuntu') || distro.startsWith('debian')) {
		const krb5_title = document.createElement('h3');
		krb5_title.textContent = 'krb5.conf Configuration';
		linksContainer.appendChild(krb5_title);

		const item = document.createElement('p');
		item.textContent =
			"If you're prompted to configure your krb5.conf with a realm during installation, set this to your on-prem synced local Active Directory realm. If you do not have an on-prem synced Active Directory, you may leave this realm field empty. After installation, you must ensure that your krb5.conf contains an `includedir  /etc/krb5.conf.d` entry. Himmelblau will automatically configure your cloud realm in the /etc/krb5.conf.d directory.";
		linksContainer.appendChild(item);
	}

	const debug_title = document.createElement('h3');
	debug_title.textContent = 'Debugging Himmelblau';
	linksContainer.appendChild(debug_title);

	const item4 = document.createElement('p');
	item4.textContent = `The purpose of the package ${cirrus_scope_filename} is for debugging authentication scenarios in Entra Id via libhimmelblau. A developer may request that you install this package for collecting network packet captures. See the cirrus-scope man page for instructions.`;
	linksContainer.appendChild(item4);
}
