"""Regressions for repository parsing, access modes and DDI preflight."""
import json
import pathlib
import tempfile
import unittest
from unittest import mock
import test_nightly_repositories as nightly
import test_followup_reviews as followup
from test_install_endpoint import installer, load_worker_module
from test_install_ddi import result


class AdditionalReviewTests(unittest.TestCase):
    def test_retained_private_entries_keep_permissions(self):
        for manager in ('apt', 'zypper'):
            with self.subTest(manager=manager), nightly.NightlyRepositoryTests().system(manager) as (w, folder, source, key, commands):
                private = ('deb https://private.example/deb noble main\n' if manager == 'apt' else '[private]\nbaseurl=https://private.example/rpm\nenabled=1\n')
                public = ('deb ' + nightly.NIGHTLY + '/deb/ubuntu noble main\n' if manager == 'apt' else '[himmelblau-nightly]\nbaseurl=' + nightly.NIGHTLY + '/rpm/sles/16/x86_64\n')
                source.write_text(private + public)
                source.chmod(0o600)
                followup.FollowupReviewTests().switch(w, folder, manager, 'nightly')
                self.assertIn(private, source.read_text())
                self.assertIn(nightly.NIGHTLY, source.read_text())
                self.assertEqual(source.stat().st_mode & 0o777, 0o600)

    def test_list_comments_and_options_do_not_identify_source(self):
        w = load_worker_module()
        for entry in ('deb https://local.example/deb noble main # ' + nightly.NIGHTLY + '/deb/ubuntu\n',
                      'deb-src [signed-by=/keys/himmelblau.gpg] https://local.example/deb noble main # https://packages.himmelblau-idm.org/\n'):
            self.assertEqual(w.repository_remainder('shared.list', entry), (False, entry))
        self.assertEqual(w.repository_remainder('shared.list', 'deb [arch=amd64] ' + nightly.NIGHTLY + '/deb/ubuntu noble main # local comment\n'), (True, ''))

    def test_deb822_uris_continue_across_comments(self):
        w = load_worker_module()
        for first, second in (('https://local.example/deb', nightly.NIGHTLY + '/deb/ubuntu'),
                              (nightly.NIGHTLY + '/deb/ubuntu', 'https://local.example/deb')):
            text = 'Types: deb\nURIs: ' + first + '\n# mirror explanation\n  ' + second + '\nSuites: noble\nComponents: main\n'
            matched, remainder = w.repository_remainder('shared.sources', text)
            self.assertTrue(matched)
            self.assertNotIn(nightly.NIGHTLY, remainder)
            self.assertIn('URIs: https://local.example/deb\n', remainder)
            self.assertIn('# mirror explanation\n', remainder)
            self.assertIn('Suites: noble\n', remainder)
        text = 'Types: deb\nURIs: https://local.example/deb\n# ' + nightly.NIGHTLY + '/deb/ubuntu\nSuites: noble\n'
        self.assertEqual(w.repository_remainder('shared.sources', text), (False, text))

    def test_stable_switch_preserves_paid_backup_and_restores_public_source(self):
        for fail in (False, True):
            with self.subTest(fail=fail), nightly.NightlyRepositoryTests().system() as (w, folder, source, key, commands):
                backup = pathlib.Path(str(source) + '.himmelblau-disabled')
                backup.write_text('deb ' + nightly.PAID + '/deb/ubuntu noble main\n')
                paid = backup.read_text()
                current = 'deb ' + nightly.NIGHTLY + '/deb/ubuntu noble main\n'
                source.write_text(current)
                original = w.run
                def run(argv, *args, **kwargs):
                    if fail and 'update' in argv:
                        raise w.WorkerError('refresh failed')
                    return original(argv, *args, **kwargs)
                with mock.patch.object(w, 'run', side_effect=run):
                    if fail:
                        with self.assertRaisesRegex(w.WorkerError, 'refresh failed'):
                            followup.FollowupReviewTests().switch(w, folder, 'apt', 'stable')
                        self.assertEqual(source.read_text(), current)
                    else:
                        followup.FollowupReviewTests().switch(w, folder, 'apt', 'stable')
                        self.assertIn(nightly.PAID, source.read_text())
                self.assertEqual(backup.read_text(), paid)
                self.assertFalse(pathlib.Path(str(source) + '.himmelblau-rollback').exists())

    def test_pending_native_deployment_blocks_publication(self):
        w = load_worker_module()
        status = {'deployments': [{'booted': False, 'requested-packages': ['himmelblau', 'nss-himmelblau']}, {'booted': True}]}
        with mock.patch.object(w.os.path, 'exists', return_value=True), mock.patch.object(w, 'ddi_capture', return_value=result(json.dumps(status))), mock.patch.object(w, 'ddi_publish') as publish:
            with self.assertRaisesRegex(w.WorkerError, 'Reboot'):
                w.ddi_activate({'ddi': {}, 'target': 'fedora44'}, '/unused', '/unused/key', 'events')
            publish.assert_not_called()
        for module in (installer, w):
            with mock.patch.object(module.os.path, 'exists', return_value=True), mock.patch.object(module, 'ddi_capture', return_value=result('{"deployments":[{"booted":true}]}')):
                module.ddi_check_pending_deployment()
            with mock.patch.object(module.os.path, 'exists', return_value=False), mock.patch.object(module, 'ddi_capture') as capture:
                module.ddi_check_pending_deployment()
                capture.assert_not_called()

    def test_symlinked_nss_replaces_target_and_keeps_link(self):
        w = load_worker_module()
        with tempfile.TemporaryDirectory() as directory:
            folder = pathlib.Path(directory)
            target = folder / 'managed' / 'nsswitch.conf'
            target.parent.mkdir()
            original = 'passwd: files\ngroup: files\n'
            target.write_text(original)
            target.chmod(0o640)
            link = folder / 'nsswitch.conf'
            link.symlink_to('managed/nsswitch.conf')
            w.ddi_configure_nss(str(link), check_only=True)
            self.assertEqual(target.read_text(), original)
            w.ddi_configure_nss(str(link))
            self.assertTrue(link.is_symlink())
            self.assertIn('passwd: files himmelblau\n', target.read_text())
            self.assertEqual(target.stat().st_mode & 0o777, 0o640)
            self.assertEqual(pathlib.Path(str(target) + '.himmelblau-before-ddi').read_text(), original)
