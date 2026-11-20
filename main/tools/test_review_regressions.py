"""Regression coverage for PR 12 review findings; no host mutations or network."""
import http.client
import pathlib
import tempfile
import unittest
from unittest import mock
from test_install_endpoint import installer, load_worker_module
from test_install_ddi import result


class ReviewRegressionTests(unittest.TestCase):
    def test_native_dpkg_states_independent_of_selection(self):
        for module in (installer, load_worker_module()):
            for state in ('installed', 'unpacked', 'half-installed', 'half-configured', 'triggers-awaited', 'triggers-pending', 'config-files', 'not-installed'):
                with self.subTest(state=state), mock.patch.object(module, 'ddi_capture', return_value=result(state)) as capture:
                    self.assertEqual(module.ddi_packages_present('debian13'), state not in ('config-files', 'not-installed'))
                    self.assertIn('-f=${db:Status-Status}', capture.call_args[0][0])

    def test_cached_packages_rejected_when_ddi_appears(self):
        with mock.patch.dict(installer.DDI_SELECTION_CACHE, {('nightly', 'debian13'): {'install_method': 'packages'}}, clear=True), mock.patch.object(installer.os.path, 'exists', return_value=True):
            with self.assertRaisesRegex(installer.InstallError, 'cannot fall back'):
                installer.installation_selection('nightly', 'debian13')

    def test_worker_rejects_packages_before_repository_setup(self):
        w = load_worker_module()
        with mock.patch.object(w.os.path, 'exists', return_value=True), mock.patch.object(w, 'setup_nightly_repository') as setup:
            with self.assertRaisesRegex(w.WorkerError, 'cannot fall back'):
                w.execute_step({'kind': 'dnf_repo'}, 'events', {'channel': 'nightly', 'install_method': 'packages'})
            setup.assert_not_called()

    def test_truncated_download_allows_fallback(self):
        w = load_worker_module()
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(w.urllib.request, 'urlopen') as urlopen:
            urlopen.return_value.__enter__.return_value.read.side_effect = http.client.IncompleteRead(b'partial', 100)
            with self.assertRaises(w.DdiUnavailable):
                w.ddi_download('https://example.org/image', folder + '/image', 'a' * 64)

    def test_nss_rules_and_atomic_write_failure(self):
        w = load_worker_module()
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder, 'nsswitch.conf')
            for rule in ('files [NOTFOUND=return]', 'files [!SUCCESS=return]'):
                original = 'passwd: ' + rule + '\n'
                path.write_text(original)
                with self.assertRaisesRegex(w.WorkerError, 'NSS rule'):
                    w.ddi_configure_nss(str(path), check_only=True)
                self.assertEqual(path.read_text(), original)
            path.write_text('passwd: files\n')
            with mock.patch.object(w.os, 'replace', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    w.ddi_configure_nss(str(path))
            self.assertEqual(path.read_text(), 'passwd: files\n')

    def test_pending_ostree_deployment_requires_reboot(self):
        w = load_worker_module()
        with mock.patch.object(w, 'ddi_capture', return_value=result('{"deployments":[{"booted":false},{"booted":true}]}')):
            with self.assertRaisesRegex(w.WorkerError, 'Reboot'):
                w.check_ostree_pending()
