"""Nightly DDI selection, trust boundaries, and host activation contracts.

Network and host commands are simulated; filesystem changes stay in tempdirs.
"""
import contextlib
import copy
import hashlib
import io
import os
import pathlib
import shutil
import subprocess
import tempfile
import types
import unittest
from unittest import mock

from test_install_endpoint import installer, load_worker_module


VERSION = "2026-11-19.060403367496-0b6793501f96"
OLDER = "2026-11-18.060403367496-0b6793501f96"


def result(stdout="", returncode=0, stderr=""):
    return types.SimpleNamespace(stdout=stdout, returncode=returncode, stderr=stderr)


def image_spec(target="debian13", arch="x86-64", version=VERSION):
    return {"architecture": arch, "version": version,
            "portable": {"filename": "himmelblaud_" + version + "-" + arch + ".raw", "sha256": "a" * 64},
            "sysext": {"filename": "himmelblau_" + version + "-" + target + "-" + arch + ".sysext.raw", "sha256": "b" * 64}}


def ddi_plan(target="debian13", manager="apt"):
    selection = {"install_method": "ddi", "ddi": image_spec(target), "reason": None}
    with mock.patch.object(installer, "installation_selection", return_value=selection), \
            mock.patch.object(installer, "detected_package_selection", return_value=(["himmelblau"], [])):
        return installer.build_install_plan("nightly", target, {"mode": "entra", "domain": "example.org"},
                                            True, manager=manager)


class DdiEligibilityTests(unittest.TestCase):
    @contextlib.contextmanager
    def capable_host(self, module, version="systemd 262 (262.2)", packages=False):
        def capture(argv, check=True):
            if argv == ["systemctl", "--version"]:
                return result(version)
            if "--property=Version" in argv:
                return result("262")
            if "systemd-detect-virt" in argv:
                return result(returncode=1)
            return result()
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(module, "ddi_capture", side_effect=capture))
            stack.enter_context(mock.patch.object(module.os.path, "isdir", return_value=True))
            stack.enter_context(mock.patch.object(module.os.path, "exists", return_value=False))
            stack.enter_context(mock.patch.object(module, "ddi_tool", side_effect=lambda x: "/usr/bin/" + x))
            stack.enter_context(mock.patch.object(module, "ddi_architecture", return_value="x86-64"))
            stack.enter_context(mock.patch.object(module, "ddi_packages_present", return_value=packages))
            stack.enter_context(mock.patch.object(module, "ddi_auth_features", return_value=[]))
            yield

    def test_non_nightly_never_probes_systemd_or_network(self):
        for module in (installer, load_worker_module()):
            for channel in ("stable", "subscription"):
                with self.subTest(channel=channel), mock.patch.object(module, "ddi_capture") as capture, \
                        mock.patch.object(module.urllib.request, "urlopen") as fetch:
                    self.assertIn("only", module.ddi_local_reason(channel, "debian13"))
                    capture.assert_not_called()
                    fetch.assert_not_called()

    def test_old_missing_failed_and_malformed_versions_skip_all_discovery(self):
        for module in (installer, load_worker_module()):
            for proc in (result("systemd 261"), result("systemd 26"), result("unknown"), result("systemd 262", 1)):
                with self.subTest(proc=proc), mock.patch.object(module, "ddi_capture", return_value=proc) as capture, \
                        mock.patch.object(module.urllib.request, "urlopen") as fetch:
                    self.assertIn("262", module.ddi_local_reason("nightly", "debian13"))
                    self.assertEqual(capture.call_count, 1)
                    fetch.assert_not_called()
            with mock.patch.object(module, "ddi_capture", side_effect=module.DdiUnavailable("missing systemctl")):
                self.assertIn("missing", module.ddi_local_reason("nightly", "debian13"))

    def test_262_and_future_version_formats_are_eligible(self):
        for module in (installer, load_worker_module()):
            for version in ("systemd 262 (262.2)", "systemd 262~rc1", "systemd 263 (263-1.fc46)"):
                with self.subTest(version=version), self.capable_host(module, version):
                    self.assertIsNone(module.ddi_local_reason("nightly", "debian13"))

    def test_new_client_with_old_running_manager_is_ineligible(self):
        with self.capable_host(installer), mock.patch.object(installer, "ddi_capture", side_effect=[result("systemd 262"), result("261")]), \
                mock.patch.object(installer.urllib.request, "urlopen") as fetch:
            self.assertIn("running systemd manager", installer.ddi_local_reason("nightly", "debian13"))
            fetch.assert_not_called()

    def test_existing_packages_prevent_automatic_conversion(self):
        with self.capable_host(installer, packages=True):
            self.assertIn("Existing Himmelblau packages", installer.ddi_local_reason("nightly", "debian13"))

    def test_missing_tools_and_custom_auth_configuration_fall_back(self):
        with self.capable_host(installer), mock.patch.object(installer, "ddi_tool", return_value=None):
            self.assertIn("Missing DDI tools", installer.ddi_local_reason("nightly", "debian13"))
        with self.capable_host(installer), mock.patch.object(installer, "ddi_auth_features", side_effect=installer.DdiUnavailable("custom PAM")):
            self.assertEqual(installer.ddi_local_reason("nightly", "debian13"), "custom PAM")

    def test_architecture_mapping(self):
        for machine, expected in (("x86_64", "x86-64"), ("aarch64", "arm64"), ("armv7l", None)):
            with self.subTest(machine=machine), mock.patch.object(installer.os, "uname", return_value=types.SimpleNamespace(machine=machine)):
                self.assertEqual(installer.ddi_architecture(), expected)

    def test_review_and_install_share_one_manifest_resolution(self):
        with mock.patch.dict(installer.DDI_SELECTION_CACHE, {}, clear=True), \
                mock.patch.object(installer.os.path, "exists", return_value=False), \
                mock.patch.object(installer, "ddi_local_reason", return_value=None), \
                mock.patch.object(installer, "ddi_resolve", return_value=image_spec()) as resolve:
            lines = installer.summary_lines("debian13", "apt", "nightly", {"mode": "entra", "domain": "example.org"}, False)
            plan = installer.build_package_only_plan("nightly", "debian13")
            self.assertIn("Image version: " + VERSION, lines)
            self.assertEqual(plan["ddi"]["version"], VERSION)
            resolve.assert_called_once()

    def test_existing_ddi_cannot_be_replaced_with_packages(self):
        with mock.patch.dict(installer.DDI_SELECTION_CACHE, {}, clear=True), \
                mock.patch.object(installer.os.path, "exists", return_value=True):
            with self.assertRaisesRegex(installer.InstallError, "requires nightly"):
                installer.installation_selection("stable", "debian13")
            with mock.patch.object(installer, "ddi_local_reason", return_value="missing tool"):
                with self.assertRaisesRegex(installer.InstallError, "cannot fall back"):
                    installer.installation_selection("nightly", "debian13")


class DdiTrustTests(unittest.TestCase):
    def test_signed_manifests_select_newest_common_version(self):
        def manifest(target, arch, kind, directory, gpg):
            spec = image_spec(target, arch)
            old = image_spec(target, arch, OLDER)
            return {VERSION: spec[kind], OLDER: old[kind]} if kind == "portable" else {OLDER: old[kind]}
        with mock.patch.object(installer, "ddi_architecture", return_value="arm64"), \
                mock.patch.object(installer, "ddi_keyring", return_value=([], "key")), \
                mock.patch.object(installer, "ddi_manifest", side_effect=manifest):
            selected = installer.ddi_resolve("debian13")
        self.assertEqual(selected, image_spec(arch="arm64", version=OLDER))

    def test_unmatched_versions_are_unavailable(self):
        with mock.patch.object(installer, "ddi_architecture", return_value="arm64"), \
                mock.patch.object(installer, "ddi_keyring", return_value=([], "key")), \
                mock.patch.object(installer, "ddi_manifest", side_effect=({VERSION: {}}, {OLDER: {}})):
            with self.assertRaisesRegex(installer.DdiUnavailable, "No matched"):
                installer.ddi_resolve("debian13")

    def test_manifest_rejects_paths_wrong_architectures_and_duplicate_versions(self):
        good = "a" * 64 + " *" + image_spec()["portable"]["filename"] + "\n"
        for content in (good.replace("himmelblaud_", "../himmelblaud_"), good.replace("x86-64", "arm64"), good + good):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory, \
                    mock.patch.object(installer, "ddi_fetch", side_effect=[content.encode(), b"signature"]), \
                    mock.patch.object(installer, "ddi_capture", return_value=result()):
                with self.assertRaisesRegex(installer.InstallError, "manifest entry"):
                    installer.ddi_manifest("debian13", "x86-64", "portable", directory, ["gpg"])

    def test_bad_manifest_signature_stops_before_parsing(self):
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(installer, "ddi_fetch", return_value=b"untrusted data"), \
                mock.patch.object(installer, "ddi_capture", side_effect=installer.InstallError("bad signature")):
            with self.assertRaisesRegex(installer.InstallError, "bad signature"):
                installer.ddi_manifest("debian13", "x86-64", "portable", directory, ["gpg"])

    def test_key_fingerprint_mismatch_never_imports_key(self):
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(installer, "ddi_fetch", return_value=b"wrong key"), \
                mock.patch.object(installer, "ddi_capture", return_value=result("pub:::::::::\nfpr:::::::::BAD:\n")) as capture:
            with self.assertRaisesRegex(installer.InstallError, "fingerprint mismatch"):
                installer.ddi_keyring(directory)
            self.assertEqual(capture.call_count, 1)

    def test_download_streams_and_rejects_corruption(self):
        worker = load_worker_module()
        data = b"signed disk image" * 100000
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(worker.urllib.request, "urlopen", side_effect=lambda *a, **k: io.BytesIO(data)):
            path = pathlib.Path(directory) / "image.raw"
            worker.ddi_download("https://example.org/image", str(path), hashlib.sha256(data).hexdigest())
            self.assertEqual(path.read_bytes(), data)
            with self.assertRaisesRegex(worker.WorkerError, "checksum mismatch"):
                worker.ddi_download("https://example.org/image", str(path) + "2", "0" * 64)

    def test_atomic_publication_leaves_only_complete_readonly_image(self):
        worker = load_worker_module()
        with tempfile.TemporaryDirectory() as directory:
            source = pathlib.Path(directory) / "source"
            source.write_bytes(b"complete image")
            target = pathlib.Path(directory) / "images"
            worker.ddi_publish(str(source), str(target), "image.raw")
            self.assertEqual(list(target.iterdir()), [target / "image.raw"])
            self.assertEqual((target / "image.raw").read_bytes(), b"complete image")
            self.assertEqual((target / "image.raw").stat().st_mode & 0o777, 0o444)


    def test_failed_publication_preserves_previous_image_and_removes_partial_file(self):
        worker = load_worker_module()
        with tempfile.TemporaryDirectory() as directory:
            source = pathlib.Path(directory) / "source"
            source.write_bytes(b"new image")
            target = pathlib.Path(directory) / "images"
            target.mkdir()
            image = target / "image.raw"
            image.write_bytes(b"previous image")
            with mock.patch.object(worker.shutil, "copyfileobj", side_effect=OSError("disk full")):
                with self.assertRaisesRegex(OSError, "disk full"):
                    worker.ddi_publish(str(source), str(target), "image.raw")
            self.assertEqual(list(target.iterdir()), [image])
            self.assertEqual(image.read_bytes(), b"previous image")

    @unittest.skipUnless(shutil.which("gpg"), "GnuPG is required for the signature integration test")
    def test_real_signatures_are_verified_and_tampered_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            home = pathlib.Path(directory) / "signer"
            home.mkdir(mode=0o700)
            gpg = ["gpg", "--homedir", str(home), "--batch", "--pinentry-mode", "loopback", "--passphrase", ""]
            def command(*args):
                return subprocess.run(gpg + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout
            command("--quick-generate-key", "Installer test <installer@example.invalid>", "rsa2048", "sign", "1d")
            listing = command("--with-colons", "--list-keys").decode()
            fingerprint = next(line.split(":")[9] for line in listing.splitlines() if line.startswith("fpr:"))
            key = command("--armor", "--export", fingerprint)
            manifest = pathlib.Path(directory) / "SHA256SUMS"
            manifest.write_text("a" * 64 + " *himmelblaud_" + VERSION + "-x86-64.raw\n")
            command("--detach-sign", str(manifest))
            data, signature = manifest.read_bytes(), pathlib.Path(str(manifest) + ".sig").read_bytes()
            def fetch(url, *args):
                return key if url == installer.DDI_KEY_URL else signature if url.endswith(".gpg") else data
            with tempfile.TemporaryDirectory() as verifier, \
                    mock.patch.object(installer, "DDI_FINGERPRINT", fingerprint), \
                    mock.patch.object(installer, "ddi_fetch", side_effect=fetch):
                verifier_gpg, _ = installer.ddi_keyring(verifier)
                trusted = installer.ddi_manifest("debian13", "x86-64", "portable", verifier, verifier_gpg)
                self.assertEqual(trusted[VERSION]["sha256"], "a" * 64)
                data = data.replace(b"a" * 64, b"b" * 64)
                with self.assertRaisesRegex(installer.InstallError, "DDI command failed"):
                    installer.ddi_manifest("debian13", "x86-64", "portable", verifier, verifier_gpg)
            subprocess.run(["gpgconf", "--homedir", str(home), "--kill", "gpg-agent"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

class DdiPlanTests(unittest.TestCase):
    def test_both_validators_accept_nightly_and_reject_mixed_sources_and_mismatched_images(self):
        plan = ddi_plan()
        for validate in (installer.validate_install_plan, load_worker_module().validate_plan):
            validate(plan)
            bad_plans = []
            for field, value in (("channel", "subscription"), ("install_method", "packages"),
                                 ("steps", [{"kind": "install_ddi"}, {"kind": "enable_services"}])):
                bad = copy.deepcopy(plan)
                bad[field] = value
                bad_plans.append(bad)
            bad = copy.deepcopy(plan)
            bad["ddi"]["sysext"]["filename"] = "../../wrong.raw"
            bad_plans.append(bad)
            bad = copy.deepcopy(plan)
            bad["package_steps"].append({"kind": "install_ddi"})
            bad_plans.append(bad)
            for bad in bad_plans:
                with self.subTest(validate=validate, bad=bad), self.assertRaises(Exception):
                    validate(bad)

    def test_fallback_runs_original_package_plan_before_any_ddi_changes(self):
        worker = load_worker_module()
        plan = ddi_plan()
        with mock.patch.object(worker, "ddi_prepare", side_effect=worker.DdiUnavailable("no matching image")), \
                mock.patch.object(worker.os.path, "exists", return_value=False), \
                mock.patch.object(worker, "emit") as emit, mock.patch.object(worker, "execute_step") as step, \
                mock.patch.object(worker, "ddi_activate") as activate:
            worker.execute_ddi_plan(plan, "events")
        self.assertEqual([call.args[0] for call in step.call_args_list], plan["package_steps"])
        self.assertTrue(all(call.args[2]["install_method"] == "packages" for call in step.call_args_list))
        self.assertIn("no matching image", emit.call_args.args[1]["text"])
        activate.assert_not_called()

    def test_verification_and_activation_errors_never_install_packages(self):
        worker = load_worker_module()
        for phase in ("prepare", "activate"):
            with self.subTest(phase=phase), mock.patch.object(worker, "ddi_prepare", return_value="key") as prepare, \
                    mock.patch.object(worker, "ddi_activate") as activate, mock.patch.object(worker, "execute_step") as packages, mock.patch.object(worker, "emit"):
                (prepare if phase == "prepare" else activate).side_effect = worker.WorkerError("verification or activation failed")
                with self.assertRaisesRegex(worker.WorkerError, "failed"):
                    worker.execute_ddi_plan(ddi_plan(), "events")
                packages.assert_not_called()

    def test_existing_ddi_preflight_failure_never_installs_packages(self):
        worker = load_worker_module()
        with mock.patch.object(worker, "ddi_prepare", side_effect=worker.DdiUnavailable("missing tool")), \
                mock.patch.object(worker.os.path, "exists", return_value=True), \
                mock.patch.object(worker, "execute_step") as packages, mock.patch.object(worker, "emit"):
            with self.assertRaisesRegex(worker.WorkerError, "cannot fall back"):
                worker.execute_ddi_plan(ddi_plan(), "events")
            packages.assert_not_called()


class DdiHostSetupTests(unittest.TestCase):
    def test_nss_setup_preserves_local_entries_comments_and_is_idempotent(self):
        worker = load_worker_module()
        original = "passwd: files systemd # local auth\ngroup: files\nshadow: files\nhosts: files dns\n"
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "nsswitch.conf"
            path.write_text(original)
            worker.ddi_configure_nss(str(path))
            worker.ddi_configure_nss(str(path))
            self.assertEqual(path.read_text(), "passwd: files systemd himmelblau # local auth\ngroup: files himmelblau\nshadow: files himmelblau\nhosts: files dns\n")
            self.assertEqual(pathlib.Path(str(path) + ".himmelblau-before-ddi").read_text(), original)

    def test_verified_payload_metadata_and_host_libraries_are_checked_on_both_architectures(self):
        worker = load_worker_module()
        read_release = worker.ddi_os_release
        for arch in ("x86-64", "arm64"):
            with self.subTest(architecture=arch), tempfile.TemporaryDirectory() as directory:
                calls = []
                def capture(argv, check=True):
                    calls.append(argv)
                    if argv[:2] == ["systemd-dissect", "--copy-from"] and argv[3] == "/usr":
                        usr = pathlib.Path(argv[4])
                        files = {
                            "lib/extension-release.d/extension-release.himmelblau":
                                'ID=debian\nVERSION_ID="13"\nARCHITECTURE=' + arch + '\nSYSEXT_VERSION_ID=' + VERSION + '-debian13\n',
                            "bin/aad-tool": "binary", "lib/security/pam_himmelblau.so": "binary",
                            "lib/libnss_himmelblau.so.2": "binary", "share/pam-configs/himmelblau": "PAM profile",
                        }
                        for name, text in files.items():
                            path = usr / name
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.write_text(text)
                    if argv[-1] == "/usr/lib/os-release":
                        return result('IMAGE_VERSION=' + VERSION + '\nARCHITECTURE=' + arch + '\n')
                    return result()
                def release(path="/etc/os-release"):
                    return {"ID": "debian", "VERSION_ID": "13"} if path == "/etc/os-release" else read_release(path)
                with mock.patch.object(worker, "ddi_capture", side_effect=capture), \
                        mock.patch.object(worker, "ddi_os_release", side_effect=release):
                    worker.ddi_check_payload(directory, "debian13", image_spec(arch=arch))
                self.assertEqual(len([cmd for cmd in calls if cmd[0] == "ldd"]), 3)
                self.assertTrue(any("/etc/himmelblau/himmelblau.conf" in cmd for cmd in calls))

    def test_rerunning_an_older_plan_cannot_downgrade_existing_images(self):
        worker = load_worker_module()
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(worker, "ddi_local_reason", return_value=None), \
                mock.patch.object(worker.glob, "glob", return_value=["/installed/himmelblaud_" + VERSION + "-x86-64.raw"]), \
                mock.patch.object(worker, "ddi_fetch") as fetch:
            plan = ddi_plan()
            plan["ddi"] = image_spec(version=OLDER)
            with self.assertRaisesRegex(worker.DdiUnavailable, "refusing to downgrade"):
                worker.ddi_prepare(plan, directory)
            fetch.assert_not_called()

    def test_mint_does_not_inherit_ubuntu_sysext_compatibility(self):
        worker = load_worker_module()
        release = {"ID": "ubuntu", "VERSION_ID": "24.04", "ARCHITECTURE": "x86-64"}
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(worker, "ddi_capture", return_value=result()), \
                mock.patch.object(worker, "ddi_os_release", side_effect=[release, {"ID": "linuxmint", "VERSION_ID": "22"}]):
            with self.assertRaisesRegex(worker.DdiUnavailable, "distribution"):
                worker.ddi_check_payload(directory, "ubuntu24.04", image_spec("ubuntu24.04"))

    def test_release_mismatch_is_a_pre_activation_fallback(self):
        worker = load_worker_module()
        release = {"ID": "debian", "VERSION_ID": "13", "ARCHITECTURE": "x86-64"}
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(worker, "ddi_capture", return_value=result()), \
                mock.patch.object(worker, "ddi_os_release", side_effect=[release, {"ID": "debian", "VERSION_ID": "14"}]):
            with self.assertRaisesRegex(worker.DdiUnavailable, "release"):
                worker.ddi_check_payload(directory, "debian13", image_spec())

    def test_current_user_attachment_targets_real_user_bus_and_future_logins(self):
        worker = load_worker_module()
        commands, files = [], {}
        def run(argv, *args, **kwargs):
            commands.append(argv)
            if "list-units" in argv:
                return result("user@1000.service loaded active running User Manager\n")
            if "is-attached" in argv:
                return result("detached\n")
            return result()
        with mock.patch.object(worker.os, "makedirs"), mock.patch.object(worker, "run", side_effect=run), \
                mock.patch.object(worker, "install_text", side_effect=lambda path, text, *args: files.update({path: text})):
            worker.ddi_install_users("events")
        attachment = next(cmd for cmd in commands if cmd[0] == "busctl")
        self.assertIn("--machine=1000@.host", attachment)
        self.assertIn("AttachImage", attachment)
        self.assertIn("himmelblau-compliance-check", attachment)
        self.assertIn(["systemctl", "--global", "enable", "himmelblau-portable-setup.service"], commands)
        self.assertIn("WantedBy=default.target", files["/etc/systemd/user/himmelblau-portable-setup.service"])
        self.assertIn("portablectl --user", files[worker.DDI_ROOT + "/attach-user"])
        subprocess.run(["sh", "-n"], input=files[worker.DDI_ROOT + "/attach-user"], universal_newlines=True, check=True)

    def test_activation_writes_configuration_before_start_and_enables_updates(self):
        worker = load_worker_module()
        for target, manager in (("debian13", "apt"), ("fedora44", "rpm-ostree")):
            commands = []
            def run(argv, *args, **kwargs):
                commands.append(argv)
                return result("detached" if "is-attached" in argv else "")
            with self.subTest(manager=manager), contextlib.ExitStack() as stack:
                for name in ("ddi_publish", "ddi_configure_nss", "ddi_install_users", "emit"):
                    stack.enter_context(mock.patch.object(worker, name))
                stack.enter_context(mock.patch.object(worker, "ddi_tool", side_effect=lambda x: x))
                stack.enter_context(mock.patch.object(worker, "ddi_auth_features", return_value=[]))
                stack.enter_context(mock.patch.object(worker, "write_global_config", side_effect=lambda *a: commands.append(["config"])))
                stack.enter_context(mock.patch.object(worker, "run", side_effect=run))
                stack.enter_context(mock.patch.object(worker.glob, "glob", return_value=["/usr/share/pam-configs/himmelblau"]))
                stack.enter_context(mock.patch.object(worker.os.path, "exists", return_value=True))
                stack.enter_context(mock.patch.object(worker.shutil, "copyfile"))
                stack.enter_context(mock.patch("builtins.open", mock.mock_open(read_data="auth sufficient pam_himmelblau.so\n")))
                worker.ddi_activate(ddi_plan(target, manager), "/temp", "/temp/key", "events")
            attach_index = next(i for i, cmd in enumerate(commands) if cmd[:2] == ["portablectl", "attach"])
            self.assertLess(commands.index(["config"]), attach_index)
            self.assertIn(["systemctl", "enable", "--now", "himmelblaud-sysupdate-notify.socket"], commands)
            self.assertIn(["systemd-sysupdate", "enable-component", "himmelblau"], commands)
            self.assertIn(["systemctl", "enable", "--now", "himmelblau-sysupdate.timer"], commands)
            self.assertFalse(any(cmd[0] in ("apt-get", "dnf", "rpm-ostree") for cmd in commands))


if __name__ == "__main__":
    unittest.main()
