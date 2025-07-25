async function renderSupportedDistros() {
    const tableContainer = document.getElementById('supported-distros');

    const aliases = new Map([
        ['rocky9', [['Rocky Linux', '9'], ['RHEL', '9'], ['Oracle Linux', '9']]],
        ['rocky8', [['Rocky Linux', '8'], ['RHEL', '8'], ['Oracle Linux', '8']]],
		['rocky10', [['Rocky Linux', '10'], ['RHEL', '10'], ['Oracle Linux', '10']]],
        ['leap15.6', [['openSUSE Leap', '15.6'], ['SUSE Linux Enterprise', '15 SP6']]],
        ['tumbleweed', [['openSUSE', 'Tumbleweed']]],
        ['rawhide', [['Fedora', 'Rawhide']]],
        ['fedora41', [['Fedora', '41']]],
        ['debian12', [['Debian', '12']]],
        ['ubuntu22.04', [['Ubuntu', '22.04'], ['Linux Mint', '21.3']]],
        ['ubuntu24.04', [['Ubuntu', '24.04'], ['Linux Mint', '22']]],
        ['sle15sp6', [['SUSE Linux Enterprise', '15 SP6'], ['openSUSE', '15.6']]],
        ['sle16', [['SUSE Linux Enterprise', '16'], ['openSUSE', '16']]],
    ]);

    const seen = new Set();
    const distros = [];

    try {
        const response = await fetch(
            'https://api.github.com/repos/himmelblau-idm/himmelblau/releases/latest',
        );
        const release = await response.json();
        const assets = release.assets.map((a) => a.name.toLowerCase());

        for (const name of assets) {
            let id = null;

            // .deb files: look for {distro}_amd64.deb
            //const debMatch = name.match(/(ubuntu\d|debian\d+)_amd64\.deb$/);
			const debMatch = name.match(/himmelblau_\d+\.\d+\.\d+-([a-z0-9.]+)_amd64\.deb$/);
			if (debMatch) {
                id = debMatch[1]; // KEEP DOT
            }

            // .rpm files: look for -{distro}.rpm
            const rpmMatch = name.match(/-(fedora\d+|rawhide|rocky\d+|leap\d|tumbleweed|sle\d+sp\d+|sle\d{2})\.rpm$/);
            if (rpmMatch) {
                id = rpmMatch[1];
            }

            if (id && aliases.has(id)) {
                for (const [distro, version] of aliases.get(id)) {
                    const key = `${distro}|${version}`;
                    if (!seen.has(key)) {
                        seen.add(key);
                        distros.push([distro, version]);
                    }
                }
            }
        }

        distros.sort((a, b) =>
            a[0] === b[0] ? a[1].localeCompare(b[1]) : a[0].localeCompare(b[0]),
        );

        let html = `
            <p>The following distributions are currently packaged by the Himmelblau project:</p>
            <table>
                <thead><tr><th>Distribution</th><th>Version</th></tr></thead>
                <tbody>
        `;
        for (const [distro, version] of distros) {
            html += `<tr><td>${distro}</td><td>${version}</td></tr>`;
        }
		html += `<tr><td>NixOS</td><td></td></tr>`;
        html += '</tbody></table>';
        tableContainer.innerHTML = html;
    } catch (err) {
        console.error('Failed to fetch supported distros:', err);
        tableContainer.textContent = 'Failed to load supported distributions.';
    }
}

document.addEventListener('DOMContentLoaded', renderSupportedDistros);
