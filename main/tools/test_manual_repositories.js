#!/usr/bin/env node
// Render the real downloads script with a minimal DOM; never execute its commands.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { spawnSync } = require('node:child_process');

const source = fs.readFileSync(path.join(__dirname, '../docs/js/install.js'), 'utf8');
const nightly = 'https://repo.himmelblau-idm.org/public/himmelblau/nightly';
const stable = 'https://repo.himmelblau-idm.org/ENTITLEMENT_TOKEN/himmelblau/v_4';

function element(tagName) {
  return {
    children: [], textContent: '', innerHTML: '', tagName,
    appendChild(child) { this.children.push(child); },
    addEventListener() {},
  };
}

async function render(channel, distro) {
  const container = element();
  const elements = {
    channel: Object.assign(element(), { value: channel }),
    'linux-distro': Object.assign(element(), {
      value: distro, selectedIndex: 0, options: [{ text: distro }],
    }),
    'download-links': container,
  };
  const context = vm.createContext({
    document: {
      getElementById: id => elements[id],
      createElement: element,
      querySelectorAll: () => [],
      addEventListener() {},
    },
  });
  vm.runInContext(source, context);
  await vm.runInContext('provideRepoInstructions()', context);
  for (const child of container.children.filter(child => child.tagName === 'pre')) {
    const syntax = spawnSync('sh', ['-n'], { input: child.textContent, encoding: 'utf8' });
    assert.equal(syntax.status, 0, `${channel} ${distro}: ${syntax.stderr}`);
  }
  return container.children.map(child => child.textContent).join('\n');
}

(async () => {
  const targets = [
    ['ubuntu22.04', 'deb/ubuntu jammy main'],
    ['ubuntu24.04', 'deb/ubuntu noble main'],
    ['ubuntu25.10', 'deb/ubuntu questing main'],
    ['ubuntu26.04', 'deb/ubuntu resolute main'],
    ['debian12', 'deb/debian bookworm main'],
    ['debian13', 'deb/debian trixie main'],
    ['rocky8', 'rpm/el/8'], ['rocky9', 'rpm/el/9'], ['rocky10', 'rpm/el/10'],
    ['fedora42', 'rpm/fedora/42'], ['fedora43', 'rpm/fedora/43'], ['fedora44', 'rpm/fedora/44'], ['fedora45', 'rpm/fedora/45'],
    ['rawhide', 'rpm/fedora/46'], ['amzn2023', 'rpm/amzn/2023'],
    ['sle15sp6', 'rpm/opensuse/15.6'], ['sle15sp7', 'rpm/sles/15'],
    ['sle16', 'rpm/sles/16'], ['tumbleweed', 'rpm/opensuse/tumbleweed'],
    ['silverblue43', 'rpm/fedora/43'], ['silverblue44', 'rpm/fedora/44'], ['silverblue45', 'rpm/fedora/45'],
  ];
  for (const channel of ['nightly', 'stable']) {
    const root = channel === 'nightly' ? nightly : stable;
    for (const [distro, destination] of targets) {
      const text = await render(channel, distro);
      assert.ok(text.includes(`${root}/${destination}`), `${channel} ${distro}: native destination`);
      assert.ok(text.includes(`${root}/gpg.key`), `${channel} ${distro}: channel key`);
      assert.ok(![...text.matchAll(/https?:\/\/[^\s'"<>`]+/g)].some(match => new URL(match[0]).hostname === 'packages.himmelblau-idm.org'), `${channel} ${distro}: no old server`);
      assert.ok(!text.includes('${'), `${channel} ${distro}: interpolated commands`);
      if (destination.startsWith('rpm/')) {
        assert.ok(text.includes(`${root}/${destination}/noarch`));
        assert.ok(text.includes(`himmelblau-${channel}`));
        assert.ok(text.includes(distro.startsWith('sle') || distro === 'tumbleweed' ? '--gpgcheck' : 'gpgcheck=1'));
      } else {
        assert.ok(text.includes('arch=$(dpkg --print-architecture)'));
        assert.ok(text.includes('signed-by=/etc/apt/keyrings/himmelblau.gpg'));
      }
      if (channel === 'nightly') {
        assert.ok(!text.includes('ENTITLEMENT_TOKEN'));
        assert.ok(text.includes('requires no entitlement token'));
        assert.ok(text.includes('chmod 0644'));
      } else {
        assert.ok(text.includes('chmod 0600'));
      }
      if (distro.startsWith('silverblue')) {
        assert.ok(text.includes(`file:///etc/pki/rpm-gpg/himmelblau-${channel}.asc`));
        assert.ok(text.includes('sudo rpm-ostree install'));
        assert.ok(!text.includes('sudo dnf'));
        assert.ok(!text.includes('rpm --import'));
      }
    }
  }
  const output = await render('nightly', 'silverblue44');
  assert.ok(output.includes('baseurl=' + nightly + '/rpm/fedora/44/$basearch'));
  console.log(`Manual repository instructions passed for ${targets.length * 2} channel/distribution combinations.`);
})().catch(error => { console.error(error); process.exitCode = 1; });
