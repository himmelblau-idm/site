"""Public Nightly repository configuration and source migration contracts."""
import contextlib
import io
import pathlib
import tempfile
import types
import unittest
import urllib.error
from unittest import mock

from test_install_endpoint import installer, load_worker_module


NIGHTLY = "https://repo.himmelblau-idm.org/public/himmelblau/nightly"
PAID = "https://repo.himmelblau-idm.org/synthetic-paid-token/himmelblau/v_4"


class NightlyRepositoryTests(unittest.TestCase):
    @contextlib.contextmanager
    def system(self, manager="apt", architecture=None, module=None):
        """Keep real repository writes in a temporary directory; fake network and commands."""
        w = module or load_worker_module()
        commands = []
        with tempfile.TemporaryDirectory() as tmp, contextlib.ExitStack() as stack:
            folder = pathlib.Path(tmp)
            source = folder / ("himmelblau.list" if manager == "apt" else "himmelblau-nightly.repo")
            key = folder / "nightly.key"
            values = {
                "STABLE_APT_SOURCE_PATH": str(folder / "himmelblau.list"),
                "STABLE_APT_DEB822_PATH": str(folder / "himmelblau.sources"),
                "STABLE_APT_PREFERENCES_PATH": str(folder / "preferences"),
                "APT_KEYRING_PATH": str(key),
                "APT_KEYRING_DIR": str(folder),
                "STABLE_RPM_DIRS": dict.fromkeys(("dnf", "zypper", "rpm-ostree"), str(folder)),
                "NIGHTLY_RPM_KEYS": dict.fromkeys(("dnf", "zypper", "rpm-ostree"), str(key)),
                "STABLE_RPM_KEYS": dict.fromkeys(("dnf", "zypper", "rpm-ostree"), str(folder / "stable.key")),
            }
            def run(argv, context, check=True):
                commands.append(argv)
                return types.SimpleNamespace(stdout=architecture or ("amd64" if argv[0] == "dpkg" else "x86_64"), returncode=0)
            def save(path, data, mode, context):
                pathlib.Path(path).write_bytes(data if isinstance(data, bytes) else data.encode())
                pathlib.Path(path).chmod(int(mode, 8))
            values.update(run=run, install_bytes=save, install_text=save, dearmor_apt_key=lambda data: b"dearmored-key")
            for name, value in values.items():
                stack.enter_context(mock.patch.object(w, name, value))
            stack.enter_context(mock.patch.object(w.urllib.request, "urlopen", side_effect=lambda *args, **kwargs: io.BytesIO(b"repository-data")))
            yield w, folder, source, key, commands

    def setup(self, w, target, folder, manager="apt"):
        w.setup_nightly_repository({"channel": "nightly", "target": target}, str(folder / "events"), manager)

    def test_nightly_rpm_uses_architecture_noarch_and_local_key(self):
        for module in (installer, load_worker_module()):
            for target, manager, destination in (("rocky9", "dnf", "el/9"), ("sle16", "zypper", "sles/16"), ("fedora44", "rpm-ostree", "fedora/44")):
                for architecture in ("x86_64", "aarch64"):
                    with self.subTest(module=module.__name__, target=target, architecture=architecture):
                        config, metadata = module.native_nightly_config(target, architecture, manager)
                        self.assertIn("baseurl=" + NIGHTLY + "/rpm/" + destination + "/" + architecture + "\n", config)
                        self.assertIn("baseurl=" + NIGHTLY + "/rpm/" + destination + "/noarch\n", config)
                        self.assertEqual(config.count("gpgcheck=1"), 2)
                        self.assertEqual(config.count("gpgkey=file://"), 2)
                        self.assertEqual(metadata, NIGHTLY + "/rpm/" + destination + "/" + architecture + "/repodata/repomd.xml")

    def test_unsupported_architecture_fails_before_changing_files(self):
        with self.system("dnf", "aarch64") as (w, folder, source, key, commands):
            source.write_text("baseurl=" + NIGHTLY + "/rpm/el/8/x86_64")
            with self.assertRaisesRegex(w.WorkerError, "Enterprise Linux 8"):
                self.setup(w, "rocky8", folder, "dnf")
            self.assertIn("/x86_64", source.read_text())
            self.assertFalse(key.exists())
            self.assertFalse(list(folder.glob("*.himmelblau-disabled")))

    def test_legacy_apt_nightly_is_replaced_with_codename_source(self):
        with self.system(architecture="arm64") as (w, folder, source, key, commands):
            source.write_text("deb https://packages.himmelblau-idm.org/nightly/latest/deb/ubuntu24.04-arm64 ./\n")
            self.setup(w, "ubuntu24.04", folder)
            self.assertEqual(source.read_text(), "deb [arch=arm64 signed-by=%s] %s/deb/ubuntu noble main\n" % (key, NIGHTLY))
            self.assertEqual(key.read_bytes(), b"dearmored-key")
            self.assertEqual(source.stat().st_mode & 0o777, 0o644)
            self.assertFalse(list(folder.glob("*.himmelblau-disabled")))

    def test_rerunning_nightly_replaces_public_source(self):
        with self.system() as (w, folder, source, key, commands):
            source.write_text("deb " + NIGHTLY + "/deb/ubuntu noble main\n")
            self.setup(w, "ubuntu24.04", folder)
            self.assertIn(NIGHTLY, source.read_text())
            self.assertFalse(list(folder.glob("*.himmelblau-disabled")))

    def test_paid_source_is_disabled_and_preferences_are_preserved(self):
        with self.system() as (w, folder, source, key, commands):
            previous = "deb " + PAID + "/deb/ubuntu noble main\n"
            source.write_text(previous)
            preferences = folder / "preferences"
            preferences.write_text("Pin: origin repo.himmelblau-idm.org\nPin-Priority: 990\n")
            self.setup(w, "ubuntu24.04", folder)
            backup = pathlib.Path(str(source) + ".himmelblau-disabled")
            self.assertEqual(backup.read_text(), previous)
            self.assertEqual(backup.stat().st_mode & 0o777, 0o600)
            self.assertIn(NIGHTLY, source.read_text())
            self.assertIn("Pin-Priority: 990", preferences.read_text())

    def test_refresh_failure_restores_source_key_and_permissions(self):
        for manager, target in (("apt", "ubuntu24.04"), ("dnf", "fedora44"), ("zypper", "sle16")):
            with self.subTest(manager=manager), self.system(manager) as (w, folder, source, key, commands):
                previous = "repository=" + NIGHTLY + "/previous\n"
                source.write_text(previous)
                source.chmod(0o600)
                key.write_bytes(b"previous-key")
                preferences = folder / "preferences"
                preferences.write_text("previous preferences")
                normal_run = w.run
                def run(argv, context, check=True):
                    if "update" in argv or "makecache" in argv or "refresh" in argv:
                        raise w.WorkerError("refresh failed")
                    return normal_run(argv, context, check)
                with mock.patch.object(w, "run", run), self.assertRaisesRegex(w.WorkerError, "refresh failed"):
                    self.setup(w, target, folder, manager)
                self.assertEqual(source.read_text(), previous)
                self.assertEqual(source.stat().st_mode & 0o777, 0o600)
                self.assertEqual(key.read_bytes(), b"previous-key")
                self.assertEqual(preferences.read_text(), "previous preferences")
                self.assertFalse(list(folder.glob("*.himmelblau-disabled")))

    def test_backup_failure_does_not_delete_unmoved_source(self):
        with self.system("dnf") as (w, folder, source, key, commands):
            source.write_text("baseurl=" + NIGHTLY + "/rpm/fedora/44/x86_64")
            stable = folder / "himmelblau-stable.repo"
            stable.write_text("baseurl=" + PAID + "/rpm/fedora/44/x86_64")
            key.write_bytes(b"previous-key")
            rename = w.os.rename
            def fail_second_backup(src, dst):
                if src == str(source):
                    raise OSError("backup failed")
                rename(src, dst)
            with mock.patch.object(w.os, "rename", fail_second_backup), self.assertRaisesRegex(OSError, "backup failed"):
                self.setup(w, "fedora44", folder, "dnf")
            self.assertIn(NIGHTLY, source.read_text())
            self.assertIn(PAID, stable.read_text())
            self.assertEqual(key.read_bytes(), b"previous-key")
            self.assertFalse(list(folder.glob("*.himmelblau-disabled")))

    def test_metadata_or_key_failure_preserves_existing_source(self):
        for failing_suffix in ("Packages.gz", "gpg.key"):
            with self.subTest(failing_suffix=failing_suffix), self.system() as (w, folder, source, key, commands):
                previous = "deb " + PAID + "/deb/ubuntu noble main\n"
                source.write_text(previous)
                key.write_bytes(b"paid-key")
                def fetch(url, **kwargs):
                    if url.endswith(failing_suffix):
                        raise urllib.error.HTTPError(url, 404, "missing", {}, None)
                    return io.BytesIO(b"data")
                with mock.patch.object(w.urllib.request, "urlopen", fetch), self.assertRaisesRegex(w.WorkerError, "Nightly packages are unavailable"):
                    self.setup(w, "ubuntu24.04", folder)
                self.assertEqual(source.read_text(), previous)
                self.assertEqual(key.read_bytes(), b"paid-key")
                self.assertFalse(list(folder.glob("*.himmelblau-disabled")))

    def test_missing_noarch_metadata_does_not_replace_source(self):
        with self.system("dnf") as (w, folder, source, key, commands):
            source.write_text("baseurl=" + NIGHTLY + "/previous")
            def fetch(url, **kwargs):
                if "/noarch/" in url:
                    raise urllib.error.HTTPError(url, 404, "missing", {}, None)
                return io.BytesIO(b"data")
            with mock.patch.object(w.urllib.request, "urlopen", fetch), self.assertRaisesRegex(w.WorkerError, "Nightly packages are unavailable"):
                self.setup(w, "fedora44", folder, "dnf")
            self.assertTrue(source.read_text().endswith("/previous"))
            self.assertFalse(key.exists())

    def test_new_install_failure_removes_partial_source_and_key(self):
        with self.system() as (w, folder, source, key, commands):
            normal_run = w.run
            def run(argv, context, check=True):
                if "update" in argv:
                    raise w.WorkerError("refresh failed")
                return normal_run(argv, context, check)
            with mock.patch.object(w, "run", run), self.assertRaisesRegex(w.WorkerError, "refresh failed"):
                self.setup(w, "ubuntu24.04", folder)
            self.assertFalse(source.exists())
            self.assertFalse(key.exists())

    def test_backup_collision_keeps_existing_files(self):
        with self.system() as (w, folder, source, key, commands):
            source.write_text("deb " + NIGHTLY + "/deb/ubuntu noble main")
            backup = pathlib.Path(str(source) + ".himmelblau-disabled")
            backup.write_text("previous backup")
            with self.assertRaisesRegex(w.WorkerError, "backup already exists"):
                self.setup(w, "ubuntu24.04", folder)
            self.assertIn(NIGHTLY, source.read_text())
            self.assertEqual(backup.read_text(), "previous backup")
            self.assertFalse(key.exists())

    def test_public_source_can_be_switched_to_stable(self):
        with self.system() as (w, folder, source, key, commands):
            previous = "deb " + NIGHTLY + "/deb/ubuntu noble main"
            source.write_text(previous)
            with mock.patch.object(w, "fetch_stable_data", side_effect=lambda url, unavailable_ok=False: b"data" if "/v_4/" in url else None), mock.patch.object(w, "check_stable_major"):
                w.setup_stable_repository({"channel": "stable", "target": "ubuntu24.04", "manager": "apt", "entitlement_token": "synthetic-paid-token"}, str(folder / "events"))
            self.assertIn(PAID, source.read_text())
            self.assertFalse(pathlib.Path(str(source) + ".himmelblau-disabled").exists())
            self.assertEqual(source.stat().st_mode & 0o777, 0o600)

    def test_vendor_switch_disables_public_nightly(self):
        with self.system("dnf") as (w, folder, source, key, commands):
            source.write_text("baseurl=" + NIGHTLY + "/rpm/fedora/44/x86_64")
            unrelated = folder / "fedora.repo"
            unrelated.write_text("baseurl=https://example.org/fedora")
            w.setup_vendor_repositories("fedora44", "dnf")
            self.assertFalse(source.exists())
            backup = pathlib.Path(str(source) + ".himmelblau-disabled")
            self.assertIn(NIGHTLY, backup.read_text())
            self.assertEqual(backup.stat().st_mode & 0o777, 0o600)
            self.assertEqual(unrelated.read_text(), "baseurl=https://example.org/fedora")

    def test_native_manager_helpers_write_arm64_repos(self):
        for module in (installer, load_worker_module()):
            for manager, target in (("dnf", "fedora44"), ("zypper", "sle16"), ("rpm-ostree", "fedora44")):
                with self.subTest(module=module.__name__, manager=manager), self.system(manager, "aarch64", module) as (w, folder, source, key, commands):
                    with mock.patch.object(w, "sudo_prefix", return_value=[], create=True):
                        w.nightly_rpm_repo_setup(target, manager, str(folder / "events"))
                    config = source.read_text()
                    self.assertIn("/aarch64\n", config)
                    self.assertIn("/noarch\n", config)
                    self.assertIn("gpgkey=file://" + str(key), config)
                    self.assertEqual(key.read_bytes(), b"repository-data")
                    if manager == "rpm-ostree":
                        self.assertFalse(any(argv[0] == "dnf" or argv[:2] == ["rpm", "--import"] for argv in commands))

    def test_public_urls_are_visible_but_entitlement_urls_are_redacted(self):
        for module in (installer, load_worker_module()):
            self.assertEqual(module.redact(NIGHTLY), NIGHTLY)
            self.assertNotIn("synthetic-paid-token", module.redact(PAID))

    def test_public_errors_never_request_entitlement_tokens(self):
        for module in (installer, load_worker_module()):
            for code in (401, 403, 404, 429, 500):
                error = urllib.error.HTTPError(NIGHTLY, code, "failure", {}, None)
                with self.subTest(module=module.__name__, code=code), mock.patch.object(module.urllib.request, "urlopen", side_effect=error):
                    with self.assertRaises(ValueError) as raised:
                        module.fetch_nightly_data(NIGHTLY + "/gpg.key")
                    self.assertNotIn("token", str(raised.exception))
                    self.assertIn("Nightly", str(raised.exception))

    def test_empty_or_unreachable_public_repository_fails_clearly(self):
        for module in (installer, load_worker_module()):
            with self.subTest(module=module.__name__, failure="empty"), mock.patch.object(module.urllib.request, "urlopen", return_value=io.BytesIO(b"")):
                with self.assertRaisesRegex(ValueError, "empty data"):
                    module.fetch_nightly_data(NIGHTLY + "/gpg.key")
            with self.subTest(module=module.__name__, failure="network"), mock.patch.object(module.urllib.request, "urlopen", side_effect=urllib.error.URLError("offline")):
                with self.assertRaisesRegex(ValueError, "Check your connection"):
                    module.fetch_nightly_data(NIGHTLY + "/gpg.key")

    def test_headless_nightly_needs_no_token(self):
        with mock.patch.object(installer, "read_os_release", return_value={"ID": "ubuntu", "VERSION_ID": "24.04"}), \
                mock.patch.object(installer, "existing_stable_access", return_value=None), \
                mock.patch.object(installer, "load_repo_support", return_value=installer.FALLBACK_REPO_SUPPORT), \
                mock.patch.object(installer, "detected_package_selection", return_value=(["himmelblau"], [])), \
                mock.patch.object(installer, "run_elevated_plan") as execute:
            installer.run_headless_install(installer.parse_install_options(["--channel", "nightly"]))
            plan = execute.call_args[0][0]
        self.assertEqual(plan["channel"], "nightly")
        self.assertIsNone(plan["entitlement_token"])
        self.assertTrue(installer.validate_install_plan(plan))
        load_worker_module().validate_plan(plan)


if __name__ == "__main__":
    unittest.main()
