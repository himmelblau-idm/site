"""Follow-up regressions use temporary sources and simulated host commands."""
import os
import pathlib
import subprocess
import tempfile
import unittest
from unittest import mock
from test_install_endpoint import load_worker_module
import test_nightly_repositories as nightly_tests
from test_nightly_repositories import NIGHTLY, PAID


class FollowupReviewTests(unittest.TestCase):
    def test_login_helper_accepts_detached_exit_one_only(self):
        w = load_worker_module()
        with tempfile.TemporaryDirectory() as folder:
            for command, body in {
                'portablectl': 'case "$*" in *is-attached*) echo "$STATE"; exit 1;; esac\necho attached >> "$LOG"\n',
                'systemctl': 'exit 0\n',
            }.items():
                path = pathlib.Path(folder, command)
                path.write_text('#!/bin/sh\n' + body)
                path.chmod(0o755)
            env = dict(os.environ, PATH=folder + ':' + os.environ['PATH'], LOG=folder + '/log', STATE='detached')
            subprocess.run(['/bin/sh'], input=w.DDI_USER_HELPER, text=True, env=env, check=True)
            self.assertIn('attached', pathlib.Path(env['LOG']).read_text())
            env['STATE'] = 'invalid'
            self.assertNotEqual(subprocess.run(['/bin/sh'], input=w.DDI_USER_HELPER, text=True, env=env).returncode, 0)

    def switch(self, w, folder, manager, channel):
        target = 'ubuntu24.04' if manager == 'apt' else 'sle16'
        if channel == 'nightly':
            w.setup_nightly_repository({'channel': channel, 'target': target}, str(folder / 'events'), manager)
        elif channel == 'vendor':
            w.setup_vendor_repositories(target, manager)
        else:
            distro, version = w.stable_destination(target)
            config, _ = w.native_stable_config(PAID, distro, version, 'amd64' if manager == 'apt' else 'x86_64', manager)
            with mock.patch.object(w, 'resolve_stable_repository', return_value=('4', PAID, distro, version, config)), mock.patch.object(w, 'check_stable_major'):
                w.setup_stable_repository({'target': target, 'manager': manager, 'entitlement_token': 'synthetic'}, str(folder / 'events'))

    def legacy_files(self, folder, manager):
        if manager == 'apt':
            entries = {
                'packages_himmelblau_idm_org-nightly.list': 'deb https://packages.himmelblau-idm.org/nightly/latest/deb/ubuntu24.04 ./\n',
                'shared.list': '# local repositories\ndeb https://unrelated.example/deb noble main\ndeb ' + PAID + '/deb/ubuntu noble main\n',
                'shared.sources': 'Types: deb\nURIs: ' + NIGHTLY + '/deb/ubuntu https://unrelated.example/deb\nSuites: noble\nComponents: main\n\nTypes: deb\nURIs: https://other.example/deb\nSuites: noble\nComponents: main\n',
            }
        else:
            entries = {
                'himmelblau-nightly-noarch.repo': '[himmelblau-nightly-noarch]\nbaseurl=' + NIGHTLY + '/rpm/sles/16/noarch\nenabled=1\n',
                'shared.repo': '[local]\nbaseurl=https://unrelated.example/rpm\nenabled=1\n\n[old-himmelblau]\nbaseurl=' + PAID + '/rpm/sles/16/x86_64\nenabled=1\n',
            }
        for name, text in entries.items():
            path = folder / name
            path.write_text(text)
            path.chmod(0o644)
        return entries

    def test_all_switches_discover_legacy_files_and_preserve_unrelated_entries(self):
        fixture = nightly_tests.NightlyRepositoryTests()
        for manager in ('apt', 'zypper'):
            for channel in ('nightly', 'stable', 'vendor'):
                with self.subTest(manager=manager, channel=channel), fixture.system(manager) as (w, folder, source, key, commands):
                    entries = self.legacy_files(folder, manager)
                    self.switch(w, folder, manager, channel)
                    for name in entries:
                        path = folder / name
                        if path.exists():
                            self.assertFalse(w.repository_remainder(str(path), path.read_text())[0])
                            self.assertEqual(path.stat().st_mode & 0o777, 0o644)
                    shared = folder / ('shared.list' if manager == 'apt' else 'shared.repo')
                    self.assertIn('https://unrelated.example', shared.read_text())
                    if manager == 'apt':
                        deb822 = (folder / 'shared.sources').read_text()
                        self.assertIn('URIs: https://unrelated.example/deb', deb822)
                        self.assertIn('https://other.example/deb', deb822)

    def test_all_switches_restore_discovered_files_on_failure(self):
        fixture = nightly_tests.NightlyRepositoryTests()
        for manager in ('apt', 'zypper'):
            for channel in ('nightly', 'stable', 'vendor'):
                with self.subTest(manager=manager, channel=channel), fixture.system(manager) as (w, folder, source, key, commands):
                    entries = self.legacy_files(folder, manager)
                    original = w.retain_repository_entries
                    count = [0]
                    def fail_after_partial_migration(*args):
                        original(*args)
                        count[0] += 1
                        if count[0] == 2:
                            raise OSError('simulated disk failure')
                    with mock.patch.object(w, 'retain_repository_entries', side_effect=fail_after_partial_migration):
                        with self.assertRaisesRegex(OSError, 'simulated disk failure'):
                            self.switch(w, folder, manager, channel)
                    for name, text in entries.items():
                        path = folder / name
                        self.assertEqual(path.read_text(), text)
                        self.assertEqual(path.stat().st_mode & 0o777, 0o644)

    def test_refresh_failure_restores_discovered_sources(self):
        fixture = nightly_tests.NightlyRepositoryTests()
        for manager in ('apt', 'zypper'):
            for channel in ('nightly', 'stable'):
                with self.subTest(manager=manager, channel=channel), fixture.system(manager) as (w, folder, source, key, commands):
                    entries = self.legacy_files(folder, manager)
                    original = w.run
                    def fail_refresh(argv, *args, **kwargs):
                        if 'update' in argv or 'refresh' in argv:
                            raise w.WorkerError('refresh failed')
                        return original(argv, *args, **kwargs)
                    with mock.patch.object(w, 'run', side_effect=fail_refresh):
                        with self.assertRaisesRegex(w.WorkerError, 'refresh failed'):
                            self.switch(w, folder, manager, channel)
                    for name, text in entries.items():
                        self.assertEqual((folder / name).read_text(), text)
                    self.assertFalse(source.exists())
