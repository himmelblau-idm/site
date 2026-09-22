"""Subscription source contracts, with synthetic credentials and no system changes."""
import contextlib
import io
import json
import pathlib
import tempfile
import types
import unittest
import urllib.error
from unittest import mock

from test_install_endpoint import installer

TOKEN = "synthetic-subscriber-credential"
ROOT = "https://repo.himmelblau-idm.org/" + TOKEN + "/himmelblau/v_4"


def worker_module():
    module = types.ModuleType("stable_worker")
    exec(compile(installer.ROOT_WORKER_SOURCE, "root-worker", "exec"), module.__dict__)
    return module


class StableRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.worker = worker_module()
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)

    def patch(self, obj, name, value):
        return self.stack.enter_context(mock.patch.object(obj, name, value))

    def plan(self, target="ubuntu24.04"):
        with mock.patch.object(installer, "detected_package_selection", return_value=(["himmelblau"], [])):
            return installer.build_package_only_plan("stable", target, TOKEN)

    def test_tokens_are_normalized_and_generate_stream_roots(self):
        for module in (installer, self.worker):
            self.assertEqual(module.normalize_entitlement_token("  " + TOKEN + "\n"), TOKEN)
            self.assertEqual(module.stable_root(TOKEN, "4"), ROOT)
            self.assertEqual(module.stable_root(TOKEN, "3"), ROOT.replace("v_4", "v_3"))

    def test_rejects_urls_and_malformed_tokens(self):
        invalid = [ROOT, "short", "public", "basic", TOKEN + " second", TOKEN + "/path", TOKEN + "\nmalformed", None]
        for module in (installer, self.worker):
            for token in invalid:
                with self.subTest(token=module.redact(token)), self.assertRaises(ValueError):
                    module.normalize_entitlement_token(token)

    def test_native_indexes_match_publication_destinations(self):
        for module in (installer, self.worker):
            root = module.stable_root(TOKEN, "4")
            distro, version = module.stable_destination("ubuntu24.04")
            config, index = module.native_stable_config(root, distro, version, "arm64", "apt")
            self.assertIn("/deb/ubuntu noble main", config)
            self.assertIn("arch=arm64 signed-by=", config)
            self.assertTrue(index.endswith("/dists/noble/main/binary-arm64/Packages.gz"))
            distro, version = module.stable_destination("rocky9")
            config, index = module.native_stable_config(root, distro, version, "aarch64", "dnf")
            self.assertIn("/rpm/el/9/aarch64", config)
            self.assertIn("/rpm/el/9/noarch", config)
            self.assertIn("gpgcheck=1", config)
            self.assertIn("priority=1", config)
            self.assertIn("gpgkey=file://", config)
            self.assertTrue(index.endswith("/aarch64/repodata/repomd.xml"))
            self.assertEqual(module.stable_destination("sle15sp6"), ("opensuse", "15.6"))
            self.assertEqual(module.stable_destination("sle15sp7"), ("sles", "15"))
            self.assertEqual(module.stable_destination("sle16"), ("sles", "16"))
            self.assertEqual(module.stable_destination("rawhide"), ("fedora", "46"))
            with self.assertRaises(ValueError):
                module.native_stable_config(ROOT, "el", "8", "aarch64", "dnf")
            with self.assertRaises(ValueError):
                module.native_stable_config(ROOT, "ubuntu", "noble", "i386", "apt")
            with self.assertRaises(ValueError):
                module.stable_destination("nixos")

    def test_documented_targets_use_native_stable_destinations(self):
        expected = {
            "ubuntu22.04": ("ubuntu", "jammy"),
            "ubuntu24.04": ("ubuntu", "noble"),
            "ubuntu25.10": ("ubuntu", "questing"),
            "ubuntu26.04": ("ubuntu", "resolute"),
            "debian12": ("debian", "bookworm"),
            "debian13": ("debian", "trixie"),
            "rocky8": ("el", "8"),
            "rocky9": ("el", "9"),
            "rocky10": ("el", "10"),
            "fedora43": ("fedora", "43"),
            "fedora44": ("fedora", "44"),
            "rawhide": ("fedora", "46"),
            "amzn2023": ("amzn", "2023"),
            "tumbleweed": ("opensuse", "tumbleweed"),
            "sle15sp6": ("opensuse", "15.6"),
            "sle15sp7": ("sles", "15"),
            "sle16": ("sles", "16"),
        }
        for module in (installer, self.worker):
            with self.subTest(module=module.__name__):
                self.assertEqual({target: module.stable_destination(target) for target in expected}, expected)

    def test_leap_16_uses_sle_16_stable_repository(self):
        self.assertEqual(installer.distro_target({"ID": "opensuse-leap", "VERSION_ID": "16.0"}), "sle16")
        for module in (installer, self.worker):
            distro, version = module.stable_destination("sle16")
            config, metadata = module.native_stable_config(ROOT, distro, version, "x86_64", "zypper")
            self.assertIn(ROOT + "/rpm/sles/16/x86_64", config)
            self.assertIn(ROOT + "/rpm/sles/16/noarch", config)
            self.assertEqual(metadata, ROOT + "/rpm/sles/16/x86_64/repodata/repomd.xml")

    def test_both_plan_validators_require_consistent_authenticated_source(self):
        plan = self.plan()
        self.assertTrue(installer.validate_install_plan(plan))
        self.worker.validate_plan(plan)
        for mutate in (lambda p: p.update(entitlement_token=None),
                       lambda p: p["steps"][1].update(channel="nightly"),
                       lambda p: p["steps"][0].update(target="rocky9"),
                       lambda p: p["steps"].pop(0)):
            plan = self.plan()
            mutate(plan)
            with self.assertRaises(installer.InstallError):
                installer.validate_install_plan(plan)
            with self.assertRaises(self.worker.WorkerError):
                self.worker.validate_plan(plan)

    def test_network_errors_are_actionable_without_credentials(self):
        for code, text in ((401, "access was denied"), (403, "access was denied"), (404, "does not contain packages")):
            error = urllib.error.HTTPError(ROOT, code, TOKEN, {}, None)
            for module in (installer, self.worker):
                with mock.patch.object(module.urllib.request, "urlopen", side_effect=error):
                    with self.assertRaisesRegex(ValueError, text) as raised:
                        module.fetch_stable_data(ROOT)
                self.assertNotIn(TOKEN, str(raised.exception))

    def test_repository_discovery_requires_one_accessible_stream(self):
        for module in (installer, self.worker):
            def only_four(url, unavailable_ok=False):
                return b"metadata" if "/v_4/" in url else None
            with mock.patch.object(module, "fetch_stable_data", side_effect=only_four):
                stream, root, distro, version, config = module.resolve_stable_repository(TOKEN, "ubuntu24.04", "amd64", "apt")
            self.assertEqual((stream, root, distro, version), ("4", ROOT, "ubuntu", "noble"))
            self.assertIn(ROOT, config)
            def only_three(url, unavailable_ok=False):
                return b"metadata" if "/v_3/" in url else None
            with mock.patch.object(module, "fetch_stable_data", side_effect=only_three):
                stream, root, _, _, _ = module.resolve_stable_repository(TOKEN, "rocky9", "x86_64", "dnf")
            self.assertEqual(stream, "3")
            self.assertTrue(root.endswith("/v_3"))
            with mock.patch.object(module, "fetch_stable_data", return_value=None):
                with self.assertRaisesRegex(ValueError, "does not provide"):
                    module.resolve_stable_repository(TOKEN, "ubuntu24.04", "amd64", "apt")
            with mock.patch.object(module, "fetch_stable_data", return_value=b"metadata"):
                with self.assertRaisesRegex(ValueError, "multiple stable streams"):
                    module.resolve_stable_repository(TOKEN, "ubuntu24.04", "amd64", "apt")

    def configure_fake_system(self, manager, folder):
        w = self.worker
        self.patch(w, "STABLE_APT_SOURCE_PATH", str(folder / "himmelblau.list"))
        self.patch(w, "STABLE_APT_PREFERENCES_PATH", str(folder / "preferences"))
        self.patch(w, "STABLE_APT_DEB822_PATH", str(folder / "himmelblau.sources"))
        self.patch(w, "APT_KEYRING_PATH", str(folder / "key.gpg"))
        self.patch(w, "STABLE_RPM_DIRS", {"dnf": str(folder), "zypper": str(folder)})
        self.patch(w, "STABLE_RPM_KEYS", {"dnf": str(folder / "key.asc"), "zypper": str(folder / "key.asc")})
        self.patch(w, "check_stable_major", lambda *args: None)
        self.patch(w, "dearmor_apt_key", lambda data: b"new-dearmored-key")
        def fetch(url, unavailable_ok=False):
            if url.endswith("gpg.key"):
                return b"new-key"
            return b"index" if "/v_4/" in url else None
        self.patch(w, "fetch_stable_data", fetch)
        def save(path, data, mode, event_log):
            pathlib.Path(path).write_bytes(data if isinstance(data, bytes) else data.encode())
            pathlib.Path(path).chmod(int(mode, 8))
        self.patch(w, "install_bytes", save)
        self.patch(w, "install_text", save)
        def run(argv, event_log, check=True):
            return types.SimpleNamespace(stdout="amd64" if argv[0] == "dpkg" else "x86_64", returncode=0)
        self.patch(w, "run", run)
        return folder / ("himmelblau.list" if manager == "apt" else "himmelblau-stable.repo"), folder / ("key.gpg" if manager == "apt" else "key.asc")

    def test_repository_setup_uses_native_managers_and_private_configuration(self):
        for manager, target in (("apt", "ubuntu24.04"), ("dnf", "rocky9"), ("zypper", "sle16")):
            with self.subTest(manager=manager), tempfile.TemporaryDirectory() as tmp:
                folder = pathlib.Path(tmp)
                source, key = self.configure_fake_system(manager, folder)
                source.write_text("baseurl=https://packages.himmelblau-idm.org/stable/latest")
                key.write_bytes(b"old-key")
                self.worker.setup_stable_repository(self.plan(target=target), str(folder / "events"))
                self.assertIn(ROOT, source.read_text())
                self.assertEqual(source.stat().st_mode & 0o777, 0o600)
                self.assertNotEqual(key.read_bytes(), b"old-key")
                self.assertNotIn("stable/latest", source.read_text())
                if manager == "apt":
                    self.assertIn("Pin: origin repo.himmelblau-idm.org", (folder / "preferences").read_text())

    def test_failed_refresh_restores_previous_repository_and_signing_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp)
            source, key = self.configure_fake_system("apt", folder)
            previous = "deb " + ROOT.replace("v_4", "v_3") + "/deb/ubuntu noble main"
            source.write_text(previous)
            source.chmod(0o644)
            key.write_bytes(b"previous-key")
            preferences = folder / "preferences"
            preferences.write_text("Previous pinning rules\n")
            def fail_refresh(argv, event_log, check=True):
                if argv[-1] == "update":
                    raise self.worker.WorkerError("refresh failed")
                return types.SimpleNamespace(stdout="amd64", returncode=0)
            self.patch(self.worker, "run", fail_refresh)
            with self.assertRaisesRegex(self.worker.WorkerError, "refresh failed"):
                self.worker.setup_stable_repository(self.plan(), str(folder / "events"))
            self.assertEqual(source.read_text(), previous)
            self.assertEqual(key.read_bytes(), b"previous-key")
            self.assertEqual(preferences.read_text(), "Previous pinning rules\n")
            self.assertEqual(source.stat().st_mode & 0o777, 0o644)

    def test_denied_access_and_unrelated_filename_leave_existing_files_intact(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp)
            source, key = self.configure_fake_system("apt", folder)
            source.write_text("deb https://example.org/ unrelated main")
            key.write_bytes(b"unrelated-key")
            with self.assertRaisesRegex(self.worker.WorkerError, "another source"):
                self.worker.setup_stable_repository(self.plan(), str(folder / "events"))
            self.patch(self.worker, "fetch_stable_data", mock.Mock(side_effect=ValueError("access was denied")))
            with self.assertRaisesRegex(self.worker.WorkerError, "access was denied"):
                self.worker.setup_stable_repository(self.plan(), str(folder / "events"))
            self.assertEqual(source.read_text(), "deb https://example.org/ unrelated main")
            self.assertEqual(key.read_bytes(), b"unrelated-key")

    def test_worker_logs_and_exceptions_redact_urls_and_bare_tokens(self):
        self.worker.normalize_entitlement_token(TOKEN)
        with tempfile.TemporaryDirectory() as tmp:
            events = str(pathlib.Path(tmp) / "events")
            proc = types.SimpleNamespace(stdout=ROOT + "\ncredential=" + TOKEN, returncode=1)
            with mock.patch.object(self.worker.subprocess, "run", return_value=proc):
                with self.assertRaises(self.worker.WorkerError) as raised:
                    self.worker.run(["example", ROOT], events)
            text = pathlib.Path(events).read_text()
            self.assertNotIn(TOKEN, text)
            self.assertNotIn(TOKEN, str(raised.exception))
            self.assertIn("REDACTED", text)
            for line in text.splitlines():
                json.loads(line)

    def test_parent_logs_redact_captured_output(self):
        installer.normalize_entitlement_token(TOKEN)
        with tempfile.TemporaryDirectory() as tmp:
            log_path = str(pathlib.Path(tmp) / "install.log")
            proc = types.SimpleNamespace(stdout=ROOT + " " + TOKEN, returncode=1)
            messages = []
            with mock.patch.object(installer, "LOG_PATH", log_path), mock.patch.object(installer.subprocess, "run", return_value=proc):
                with self.assertRaises(installer.InstallError) as raised:
                    installer.run(["example", ROOT], types.SimpleNamespace(info=messages.append))
            self.assertNotIn(TOKEN, pathlib.Path(log_path).read_text())
            self.assertNotIn(TOKEN, str(raised.exception))
            self.assertNotIn(TOKEN, " ".join(messages))

    def test_installed_major_cannot_be_downgraded(self):
        proc = types.SimpleNamespace(stdout="4.1.0", returncode=0)
        with mock.patch.object(self.worker.subprocess, "run", return_value=proc):
            with self.assertRaisesRegex(self.worker.WorkerError, "downgrade"):
                self.worker.check_stable_major("3", "apt")
            self.worker.check_stable_major("4", "apt")

    def test_existing_access_is_preserved_and_ambiguous_sources_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "source"
            path.write_text("deb " + ROOT + "/deb/ubuntu noble main")
            self.assertEqual(installer.existing_stable_access([str(path)]), ("4", TOKEN))
            path.write_text(ROOT + "\n" + ROOT.replace("v_4", "v_3"))
            with self.assertRaisesRegex(installer.InstallError, "Multiple"):
                installer.existing_stable_access([str(path)])

    def test_noninteractive_setup_requires_explicit_source_and_stable_credential(self):
        self.patch(installer, "read_os_release", lambda: {"ID": "ubuntu", "VERSION_ID": "24.04"})
        self.patch(installer, "existing_stable_access", lambda: None)
        self.patch(installer, "load_repo_support", lambda ui: installer.FALLBACK_REPO_SUPPORT)
        self.patch(installer, "run_elevated_plan", mock.Mock())
        with self.assertRaisesRegex(installer.InstallError, "Choose --channel"):
            installer.run_headless_install(installer.parse_install_options([]))
        with self.assertRaisesRegex(installer.InstallError, "requires --entitlement-token-file"):
            installer.run_headless_install(installer.parse_install_options(["--channel", "stable"]))
        installer.run_elevated_plan.assert_not_called()

    def test_noninteractive_repair_reuses_existing_token(self):
        self.patch(installer, "read_os_release", lambda: {"ID": "ubuntu", "VERSION_ID": "24.04"})
        self.patch(installer, "existing_stable_access", lambda: ("3", TOKEN))
        self.patch(installer, "load_repo_support", lambda ui: installer.FALLBACK_REPO_SUPPORT)
        self.patch(installer, "detected_package_selection", lambda *args: (["himmelblau"], []))
        worker = self.patch(installer, "run_elevated_plan", mock.Mock())
        installer.run_headless_install(installer.parse_install_options([]))
        plan = worker.call_args[0][0]
        self.assertEqual(plan["entitlement_token"], TOKEN)
        self.assertNotIn("stable_stream", plan)

    def test_noninteractive_new_subscription_accepts_private_token_file(self):
        self.patch(installer, "read_os_release", lambda: {"ID": "ubuntu", "VERSION_ID": "24.04"})
        self.patch(installer, "existing_stable_access", lambda: None)
        self.patch(installer, "load_repo_support", lambda ui: installer.FALLBACK_REPO_SUPPORT)
        self.patch(installer, "detected_package_selection", lambda *args: (["himmelblau"], []))
        run_worker = self.patch(installer, "run_elevated_plan", mock.Mock())
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "subscription"
            path.write_text(TOKEN + "\n")
            path.chmod(0o600)
            options = installer.parse_install_options(["--channel", "stable", "--entitlement-token-file", str(path)])
            installer.run_headless_install(options)
            plan = run_worker.call_args[0][0]
            installer.validate_install_plan(plan)
            self.assertEqual(plan["entitlement_token"], TOKEN)

    def test_old_url_and_stream_flags_are_no_longer_accepted(self):
        for argv in (["--channel", "stable", "--repo-url-file", "/tmp/url"],
                     ["--channel", "stable", "--stable-stream", "4"]):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                installer.parse_install_options(argv)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            installer.parse_install_options(["--channel", "nightly", "--entitlement-token-file", "/tmp/token"])

    def test_wizard_accepts_token_without_stream_selection(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.page = "stable"
        ui.target = "ubuntu24.04"
        ui.entitlement_token = TOKEN
        ui.message = ""
        ui.next_page()
        self.assertEqual(ui.page, "identity")

    def test_nightly_switch_disables_paid_source_and_restores_it_on_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp)
            source, key = self.configure_fake_system("apt", folder)
            previous = "deb " + ROOT + "/deb/ubuntu noble main"
            source.write_text(previous)
            key.write_bytes(b"paid-key")
            def fail_setup(channel, target, events):
                source.write_text("new nightly configuration")
                key.write_bytes(b"nightly-key")
                raise self.worker.WorkerError("network failed")
            self.patch(self.worker, "apt_repo_setup", fail_setup)
            with self.assertRaisesRegex(self.worker.WorkerError, "network failed"):
                self.worker.setup_nightly_repository({"channel": "nightly", "target": "ubuntu24.04"}, str(folder / "events"))
            self.assertEqual(source.read_text(), previous)
            self.assertEqual(key.read_bytes(), b"paid-key")

    def test_vendor_switch_disables_project_repos_without_modifying_other_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp)
            source, key = self.configure_fake_system("zypper", folder)
            source.write_text("baseurl=" + ROOT + "/rpm/opensuse/16.0/x86_64")
            other = folder / "unrelated.repo"
            other.write_text("baseurl=https://example.org/")
            self.worker.setup_vendor_repositories("sle16")
            self.assertFalse(source.exists())
            backup = pathlib.Path(str(source) + ".himmelblau-disabled")
            self.assertEqual(backup.stat().st_mode & 0o777, 0o600)
            self.assertIn(ROOT, backup.read_text())
            self.assertEqual(other.read_text(), "baseurl=https://example.org/")

    def test_wizard_masks_entitlement_token(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.entitlement_token = TOKEN
        ui.input_cursor = {"entitlement_token": len(TOKEN)}
        ui.focus_key = None
        ui._is_focused = lambda key: False
        ui._attr = lambda name: 0
        ui._add_target = lambda *args: None
        ui.glyphs = {"input_l": "[", "input_r": "]"}
        text = []
        ui._write = lambda y, x, value, attr: text.append(value)
        ui._input(0, 0, 80, "entitlement_token", "Entitlement token")
        self.assertNotIn(TOKEN, " ".join(text))
        self.assertTrue(any("*" in value for value in text))


if __name__ == "__main__":
    unittest.main()
