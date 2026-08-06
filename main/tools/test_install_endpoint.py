#!/usr/bin/env python3
import contextlib
import io
import json
import pathlib
import shutil
import tempfile
import types
import unittest
import urllib.parse
import urllib.error


ROOT = pathlib.Path(__file__).resolve().parents[1]
INSTALL_PATH = ROOT / "docs" / "install"
ROOT_INSTALL_PATH = ROOT.parent / "install"
INSTALL_JS_PATH = ROOT / "docs" / "js" / "install.js"


def load_installer_module():
    text = INSTALL_PATH.read_text(encoding="utf-8")
    marker = "<<'PYTHON_PAYLOAD'\n"
    start = text.index(marker) + len(marker)
    end = text.rindex("\nPYTHON_PAYLOAD")
    source = text[start:end]
    module = types.ModuleType("himmelblau_install")
    module.__dict__["__name__"] = "himmelblau_install"
    exec(compile(source, str(INSTALL_PATH), "exec"), module.__dict__)
    return module


installer = load_installer_module()


APT_CONFFILE_OPTIONS = [
    "-o",
    "Dpkg::Options::=--force-confdef",
    "-o",
    "Dpkg::Options::=--force-confold",
]


class InstallEndpointTests(unittest.TestCase):
    def test_endpoint_is_extensionless_shell_wrapper(self):
        self.assertEqual(INSTALL_PATH.name, "install")
        text = INSTALL_PATH.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("#!/bin/sh\n"))
        self.assertIn("command -v python3", text)

    def test_root_endpoint_matches_docs_source(self):
        self.assertEqual(ROOT_INSTALL_PATH.read_text(encoding="utf-8"), INSTALL_PATH.read_text(encoding="utf-8"))

    def test_installer_avoids_python37_only_subprocess_text_keyword(self):
        source = INSTALL_PATH.read_text(encoding="utf-8")
        self.assertNotIn("text=True", source)
        self.assertNotIn("text=True", installer.ROOT_WORKER_SOURCE)
        self.assertIn("universal_newlines=True", source)
        self.assertIn("universal_newlines=True", installer.ROOT_WORKER_SOURCE)

    def test_run_helper_uses_python36_compatible_subprocess_kwargs(self):
        calls = []
        old_run = installer.subprocess.run
        old_log = installer.log

        class FakeProc:
            stdout = "ok\n"
            returncode = 0

        try:
            installer.log = lambda message: None

            def fake_run(argv, *args, **kwargs):
                self.assertNotIn("text", kwargs)
                calls.append(kwargs)
                return FakeProc()

            installer.subprocess.run = fake_run
            ui = types.SimpleNamespace(info=lambda message: None)
            installer.run(["echo", "ok"], ui)
            self.assertTrue(calls[0]["universal_newlines"])
        finally:
            installer.subprocess.run = old_run
            installer.log = old_log

    def test_himmelblau_installed_uses_python36_compatible_subprocess_kwargs(self):
        calls = []
        old_run = installer.subprocess.run
        try:
            def fake_run(argv, *args, **kwargs):
                self.assertNotIn("text", kwargs)
                calls.append((argv, kwargs))
                return types.SimpleNamespace(stdout="install ok installed")

            installer.subprocess.run = fake_run
            self.assertTrue(installer.himmelblau_installed("ubuntu24.04"))
            self.assertTrue(calls[0][1]["universal_newlines"])
        finally:
            installer.subprocess.run = old_run

    def test_headless_events_are_persisted_to_log(self):
        messages = []
        old_log = installer.log
        try:
            installer.log = messages.append
            with contextlib.redirect_stdout(io.StringIO()):
                installer.print_headless_event({"type": "step", "index": 2, "total": 5, "kind": "apt_repo"})
                installer.print_headless_event({"type": "output", "text": "Repository added."})
                installer.print_headless_event({"type": "done"})
                installer.print_headless_event({"type": "info", "text": ""})
            self.assertEqual(messages, [
                "Step 2 of 5: apt_repo",
                "Repository added.",
                "Finishing...",
            ])
        finally:
            installer.log = old_log

    def test_curses_worker_events_are_persisted_to_log(self):
        messages = []
        old_log = installer.log
        try:
            installer.log = messages.append
            ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
            ui.progress_percent = 0
            ui.progress_text = ""
            ui.transcript = []
            ui.render = lambda: None

            ui.on_event({"type": "step", "index": 3, "total": 6, "kind": "install_packages"})
            ui.on_event({"type": "done"})
            ui.on_event({"type": "warning", "text": "systemctl was not found."})
            ui.on_event({"type": "output", "text": ""})

            self.assertEqual(ui.progress_percent, 100)
            self.assertEqual(ui.progress_text, "Finishing...")
            self.assertEqual(ui.transcript, ["systemctl was not found."])
            self.assertEqual(messages, [
                "Step 3 of 6: install_packages",
                "Finishing...",
                "systemctl was not found.",
            ])
        finally:
            installer.log = old_log

    def test_curses_details_rows_are_clipped_after_wrapping(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        transcript = [
            "Enabled     : Yes",
            "Running: zypper --non-interactive --no-refresh install -y --from himmelblau-stable himmelblau pam-himmelblau nss-himmelblau",
            "The newest package output should remain visible",
        ]

        visible = ui._visible_wrapped_lines(transcript, width=32, limit=4)

        self.assertLessEqual(len(visible), 4)
        self.assertEqual(visible, [
            "himmelblau pam-himmelblau nss-",
            "himmelblau",
            "The newest package output should",
            "remain visible",
        ])

    def test_curses_row_advances_after_wrapped_value(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        writes = []
        ui._attr = lambda name, extra=0: 0
        ui._write = lambda y, x, text, attr=0: writes.append((y, x, text))
        ui._draw_wrapped = lambda y, x, text, width, attr=0: y + 3

        next_y = ui._row(4, 2, 48, "Repository base", "https://packages.example/stable/latest")

        self.assertEqual(next_y, 7)
        self.assertEqual(writes, [(4, 2, "Repository base")])

    def test_curses_row_reserves_long_label_column(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        writes = []
        wrapped = []
        ui._attr = lambda name, extra=0: 0
        ui._write = lambda y, x, text, attr=0: writes.append((y, x, text))

        def fake_draw_wrapped(y, x, text, width, attr=0):
            wrapped.append((y, x, text, width))
            return y + 1

        ui._draw_wrapped = fake_draw_wrapped
        ui._row(1, 3, 62, "Console password-only", "Enabled")

        self.assertEqual(writes, [(1, 3, "Console password-only")])
        self.assertGreaterEqual(wrapped[0][1], 3 + len("Console password-only") + 1)
        self.assertEqual(wrapped[0][2], "Enabled")

    def test_curses_row_stacks_when_too_narrow_for_columns(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        writes = []
        wrapped = []
        ui._attr = lambda name, extra=0: 0
        ui._write = lambda y, x, text, attr=0: writes.append((y, x, text))

        def fake_draw_wrapped(y, x, text, width, attr=0):
            wrapped.append((y, x, text, width))
            return y + 2

        ui._draw_wrapped = fake_draw_wrapped
        next_y = ui._row(6, 4, 22, "Console password-only", "Enabled")

        self.assertEqual(next_y, 9)
        self.assertEqual(writes, [(6, 4, "Console password-only")])
        self.assertEqual(wrapped, [(7, 6, "Enabled", 20)])

    def test_extracts_current_repo_support_object(self):
        matrix = installer.extract_repo_support(INSTALL_JS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(matrix["stable"]["exclude"], ["fedora44"])
        self.assertEqual(matrix["nightly"]["exclude"], ["fedora42"])
        self.assertIn("sle16", matrix["subscription"]["include"])

    def test_channel_choices_are_recommendation_ordered(self):
        matrix = installer.extract_repo_support(INSTALL_JS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            [choice["value"] for choice in installer.channel_choices(matrix, "sle16")],
            ["stable", "nightly"],
        )
        self.assertEqual(
            [choice["value"] for choice in installer.channel_choices(matrix, "fedora42")],
            ["stable"],
        )
        self.assertEqual(
            [choice["value"] for choice in installer.channel_choices(matrix, "fedora44")],
            ["nightly"],
        )
        self.assertNotIn("subscription", [choice["value"] for choice in installer.channel_choices(matrix, "sle16")])

    def test_distro_mapping(self):
        cases = [
            ({"ID": "ubuntu", "VERSION_ID": "24.04"}, "ubuntu24.04"),
            ({"ID": "linuxmint", "VERSION_ID": "22"}, "ubuntu24.04"),
            ({"ID": "debian", "VERSION_ID": "13"}, "debian13"),
            ({"ID": "fedora", "VERSION_ID": "43"}, "fedora43"),
            ({"ID": "fedora", "VERSION_ID": "rawhide"}, "rawhide"),
            ({"ID": "fedora", "VERSION_ID": "45", "VERSION": "45 (Rawhide Prerelease)"}, "rawhide"),
            ({"ID": "fedora", "VERSION_ID": "45", "PRETTY_NAME": "Fedora Linux 45 (Rawhide Prerelease)"}, "rawhide"),
            ({"ID": "fedora", "VERSION_ID": "45", "REDHAT_BUGZILLA_PRODUCT_VERSION": "rawhide"}, "rawhide"),
            ({"ID": "fedora", "VERSION_ID": "45", "REDHAT_SUPPORT_PRODUCT_VERSION": "rawhide"}, "rawhide"),
            ({"ID": "fedora", "VERSION_ID": "45"}, "fedora45"),
            ({"ID": "rocky", "VERSION_ID": "9.5"}, "rocky9"),
            ({"ID": "almalinux", "VERSION_ID": "10"}, "rocky10"),
            ({"ID": "amzn", "VERSION_ID": "2023"}, "amzn2023"),
            ({"ID": "opensuse-tumbleweed", "VERSION_ID": "20260701"}, "tumbleweed"),
            ({"ID": "sles", "VERSION_ID": "15-SP7"}, "sle15sp7"),
            ({"ID": "nixos", "VERSION_ID": "25.05"}, "nixos"),
        ]
        for info, expected in cases:
            with self.subTest(info=info):
                self.assertEqual(installer.distro_target(info), expected)

    def test_required_manager_command_matches_invoked_tool(self):
        self.assertEqual(installer.package_manager("ubuntu24.04"), "apt")
        self.assertEqual(installer.required_manager_command("ubuntu24.04"), "apt-get")
        self.assertEqual(installer.required_manager_command("debian13"), "apt-get")
        self.assertEqual(installer.required_manager_command("fedora43"), "dnf")
        self.assertEqual(installer.required_manager_command("sle16"), "zypper")

    def test_apt_get_command_sets_noninteractive_debconf_frontend(self):
        old_geteuid = installer.os.geteuid
        try:
            installer.os.geteuid = lambda: 0
            self.assertEqual(
                installer.apt_get_command("install", "-y", "himmelblau"),
                ["env", "DEBIAN_FRONTEND=noninteractive", "apt-get"] + APT_CONFFILE_OPTIONS + ["install", "-y", "himmelblau"],
            )

            installer.os.geteuid = lambda: 1000
            self.assertEqual(
                installer.apt_get_command("update"),
                ["sudo", "env", "DEBIAN_FRONTEND=noninteractive", "apt-get", "update"],
            )
        finally:
            installer.os.geteuid = old_geteuid

    def test_apt_source_line_uses_detected_arch_and_dearmored_keyring(self):
        source = installer.apt_source_line("https://packages.example/deb/ubuntu24.04", "arm64")
        self.assertEqual(
            source,
            "deb [arch=arm64 signed-by=/etc/apt/keyrings/himmelblau.gpg] https://packages.example/deb/ubuntu24.04 ./\n",
        )
        self.assertNotIn("arch=amd64", source)
        self.assertNotIn("himmelblau.asc", source)

    def test_root_worker_apt_setup_uses_detected_arch_and_dearmored_keyring(self):
        source = installer.ROOT_WORKER_SOURCE
        self.assertIn('run(["dpkg", "--print-architecture"]', source)
        self.assertIn('APT_KEYRING_PATH = APT_KEYRING_DIR + "/himmelblau.gpg"', source)
        self.assertIn('subprocess.run(["gpg", "--dearmor"]', source)
        self.assertIn('APT_DEBCONF_ENV = "DEBIAN_FRONTEND=noninteractive"', source)
        self.assertIn('def apt_get_command(*args):', source)
        self.assertIn('Dpkg::Options::=--force-confdef', source)
        self.assertIn('Dpkg::Options::=--force-confold', source)
        self.assertNotIn('run(["apt-get"', source)
        self.assertNotIn("arch=amd64", source)
        self.assertNotIn("/etc/apt/keyrings/himmelblau.asc", source)

    def test_debian_package_install_preserves_existing_conffiles(self):
        calls = []
        old_run = installer.run
        old_repo = installer.apt_repo_setup
        old_geteuid = installer.os.geteuid
        try:
            installer.os.geteuid = lambda: 0
            installer.apt_repo_setup = lambda channel, target, ui: calls.append(["repo", channel, target])
            installer.run = lambda argv, ui, check=True, input_text=None: calls.append(argv) or types.SimpleNamespace(stdout="")
            installer.install_packages("stable", "debian13", object(), installer.COMMUNITY_PACKAGES, [])
            install_calls = [call for call in calls if isinstance(call, list) and call[:3] == ["env", "DEBIAN_FRONTEND=noninteractive", "apt-get"] and "install" in call]
            self.assertTrue(install_calls)
            self.assertIn("Dpkg::Options::=--force-confdef", install_calls[-1])
            self.assertIn("Dpkg::Options::=--force-confold", install_calls[-1])
            self.assertEqual(install_calls[-1][-3:], ["himmelblau", "pam-himmelblau", "nss-himmelblau"])
        finally:
            installer.run = old_run
            installer.apt_repo_setup = old_repo
            installer.os.geteuid = old_geteuid

    def test_zypper_community_install_uses_himmelblau_repo_without_refreshing_all_repos(self):
        calls = []
        old_run = installer.run
        old_geteuid = installer.os.geteuid
        try:
            installer.os.geteuid = lambda: 0
            installer.run = lambda argv, ui, check=True, input_text=None: calls.append(argv) or types.SimpleNamespace(stdout="")
            installer.install_packages("stable", "tumbleweed", object(), installer.COMMUNITY_PACKAGES, [])
            self.assertIn(
                [
                    "zypper",
                    "--non-interactive",
                    "--no-refresh",
                    "install",
                    "-y",
                    "--from",
                    "himmelblau-stable",
                    "himmelblau",
                    "pam-himmelblau",
                    "nss-himmelblau",
                ],
                calls,
            )
        finally:
            installer.run = old_run
            installer.os.geteuid = old_geteuid

    def test_zypper_subscription_install_keeps_default_repo_behavior(self):
        calls = []
        old_run = installer.run
        old_geteuid = installer.os.geteuid
        try:
            installer.os.geteuid = lambda: 0
            installer.run = lambda argv, ui, check=True, input_text=None: calls.append(argv) or types.SimpleNamespace(stdout="")
            installer.install_packages("subscription", "tumbleweed", object(), installer.SUSE_SUBSCRIPTION_PACKAGES, [])
            self.assertEqual(calls, [[
                "zypper",
                "--non-interactive",
                "install",
                "-y",
                "himmelblau",
                "pam-himmelblau",
                "libnss_himmelblau2",
            ]])
        finally:
            installer.run = old_run
            installer.os.geteuid = old_geteuid

    def test_root_worker_zypper_community_install_uses_himmelblau_repo_without_refreshing_all_repos(self):
        source = installer.ROOT_WORKER_SOURCE
        self.assertIn('["zypper", "--non-interactive", "--no-refresh", "install", "-y", "--from", "himmelblau-%s" % channel] + packages', source)
        self.assertIn('["zypper", "--non-interactive", "install", "-y"] + packages', source)

    def test_detected_package_selection_includes_contextual_packages(self):
        old_package_installed = installer.package_installed
        old_which = installer.shutil.which
        old_path_exists = installer.path_exists
        old_list_dir = installer.list_dir
        old_command_output = installer.command_output
        old_read_text_file = installer.read_text_file
        installed = {
            "openssh-server",
            "gdm3",
            "firefox",
        }
        try:
            installer.package_installed = lambda target, names: any(name in installed for name in names)
            installer.shutil.which = lambda command: None
            installer.path_exists = lambda path: path == "/sys/fs/selinux"
            installer.list_dir = lambda path: ["plasma.desktop"] if path == "/usr/share/xsessions" else []
            installer.command_output = lambda argv: types.SimpleNamespace(stdout="", returncode=1)
            installer.read_text_file = lambda path: "Y" if path == "/sys/module/apparmor/parameters/enabled" else ""
            packages, best_effort = installer.detected_package_selection("stable", "ubuntu24.04")
            self.assertEqual(
                packages,
                [
                    "himmelblau",
                    "pam-himmelblau",
                    "nss-himmelblau",
                    "himmelblau-sshd-config",
                    "himmelblau-qr-greeter",
                    "himmelblau-sso",
                    "himmelblau-sso-policies",
                    "o365",
                ],
            )
            self.assertEqual(best_effort, ["himmelblau-selinux", "himmelblau-apparmor"])
        finally:
            installer.package_installed = old_package_installed
            installer.shutil.which = old_which
            installer.path_exists = old_path_exists
            installer.list_dir = old_list_dir
            installer.command_output = old_command_output
            installer.read_text_file = old_read_text_file

    def test_edge_installs_sso_without_browser_policies(self):
        old_package_installed = installer.package_installed
        old_which = installer.shutil.which
        old_path_exists = installer.path_exists
        old_list_dir = installer.list_dir
        old_read_text_file = installer.read_text_file
        try:
            installer.package_installed = lambda target, names: "microsoft-edge-stable" in names
            installer.shutil.which = lambda command: None
            installer.path_exists = lambda path: False
            installer.list_dir = lambda path: []
            installer.read_text_file = lambda path: ""
            packages, best_effort = installer.detected_package_selection("stable", "ubuntu24.04")
            self.assertIn("himmelblau-sso", packages)
            self.assertNotIn("himmelblau-sso-policies", packages)
            self.assertEqual(best_effort, [])
        finally:
            installer.package_installed = old_package_installed
            installer.shutil.which = old_which
            installer.path_exists = old_path_exists
            installer.list_dir = old_list_dir
            installer.read_text_file = old_read_text_file

    def test_dnf_install_includes_required_and_best_effort_packages(self):
        calls = []
        warnings = []
        ui = types.SimpleNamespace(warn=warnings.append)
        old_run = installer.run
        try:
            def fake_run(argv, ui, check=True, input_text=None):
                calls.append((argv, check))
                return types.SimpleNamespace(stdout="", returncode=1 if not check else 0)

            installer.run = fake_run
            installer.install_packages(
                "stable",
                "fedora43",
                ui,
                ["himmelblau", "pam-himmelblau", "nss-himmelblau", "himmelblau-sso"],
                ["himmelblau-selinux", "himmelblau-apparmor"],
            )
            self.assertIn((["sudo", "dnf", "install", "-y", "himmelblau", "pam-himmelblau", "nss-himmelblau", "himmelblau-sso"], True), calls)
            self.assertIn((["sudo", "dnf", "install", "-y", "himmelblau-selinux"], False), calls)
            self.assertIn((["sudo", "dnf", "install", "-y", "himmelblau-apparmor"], False), calls)
            self.assertEqual(
                warnings,
                [
                    "Optional package himmelblau-selinux could not be installed; continuing.",
                    "Optional package himmelblau-apparmor could not be installed; continuing.",
                ],
            )
        finally:
            installer.run = old_run

    def test_worker_failure_status_reads_last_worker_error(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            path = handle.name
            handle.write(json.dumps({"type": "started"}) + "\n")
            handle.write(json.dumps({"type": "error", "text": "first failure"}) + "\n")
            handle.write(json.dumps({"type": "error", "text": "last failure"}) + "\n")
        try:
            self.assertEqual(installer.worker_failure_status(path), (True, "last failure"))
        finally:
            pathlib.Path(path).unlink(missing_ok=True)

    def test_noninteractive_elevation_reports_worker_error_after_worker_started(self):
        old_geteuid = installer.os.geteuid
        old_which = installer.shutil.which
        old_popen = installer.subprocess.Popen
        old_wait = installer.wait_with_events
        try:
            installer.os.geteuid = lambda: 1000
            installer.shutil.which = lambda command: "/usr/bin/sudo" if command == "sudo" else None
            installer.subprocess.Popen = lambda argv: object()

            def fake_wait(proc, event_log, on_event):
                with open(event_log, "w", encoding="utf-8") as handle:
                    handle.write(json.dumps({"type": "started"}) + "\n")
                    handle.write(json.dumps({"type": "error", "text": "zypper failed"}) + "\n")
                return 1

            installer.wait_with_events = fake_wait
            with self.assertRaises(installer.InstallError) as raised:
                installer.run_elevated_plan(installer.build_package_only_plan("stable", "ubuntu24.04"), non_interactive=True)
            self.assertEqual(str(raised.exception), "zypper failed")
            self.assertNotIsInstance(raised.exception, installer.ElevationError)
        finally:
            installer.os.geteuid = old_geteuid
            installer.shutil.which = old_which
            installer.subprocess.Popen = old_popen
            installer.wait_with_events = old_wait

    def test_noninteractive_elevation_reports_sudo_error_when_worker_never_started(self):
        old_geteuid = installer.os.geteuid
        old_which = installer.shutil.which
        old_popen = installer.subprocess.Popen
        old_wait = installer.wait_with_events
        try:
            installer.os.geteuid = lambda: 1000
            installer.shutil.which = lambda command: "/usr/bin/sudo" if command == "sudo" else None
            installer.subprocess.Popen = lambda argv: object()
            installer.wait_with_events = lambda proc, event_log, on_event: 1
            with self.assertRaises(installer.ElevationError) as raised:
                installer.run_elevated_plan(installer.build_package_only_plan("stable", "ubuntu24.04"), non_interactive=True)
            self.assertIn("requires root or passwordless sudo", str(raised.exception))
        finally:
            installer.os.geteuid = old_geteuid
            installer.shutil.which = old_which
            installer.subprocess.Popen = old_popen
            installer.wait_with_events = old_wait

    def test_domain_validation(self):
        self.assertEqual(installer.validate_domain("example.onmicrosoft.com"), (True, ""))
        ok, _ = installer.validate_domain("example")
        self.assertFalse(ok)
        ok, _ = installer.validate_domain("-bad.example.com")
        self.assertFalse(ok)

    def test_oidc_validation(self):
        self.assertEqual(installer.validate_oidc_issuer_url("https://keycloak.example.com/realms/himmelblau"), (True, ""))
        ok, _ = installer.validate_oidc_issuer_url("keycloak.example.com/realms/himmelblau")
        self.assertFalse(ok)
        ok, message = installer.validate_oidc_issuer_url("http://keycloak.example.com/realms/himmelblau")
        self.assertFalse(ok)
        self.assertIn("HTTPS issuer URL", message)
        ok, _ = installer.validate_oidc_issuer_url("https://keycloak.example.com/realms/himmelblau?x=1")
        self.assertFalse(ok)
        self.assertEqual(installer.validate_app_id("himmelblau-login"), (True, ""))
        ok, _ = installer.validate_app_id("")
        self.assertFalse(ok)
        ok, _ = installer.validate_app_id("bad client")
        self.assertFalse(ok)

    def test_username_validation_extracts_lookup_domain(self):
        self.assertEqual(installer.lookup_domain("username", "alice@example.com"), ("example.com", ""))
        domain, message = installer.lookup_domain("username", "alice")
        self.assertIsNone(domain)
        self.assertIn("UPN", message)

    def test_entra_discovery_uses_static_odc_endpoint(self):
        calls = []
        old_open_json = installer._open_json
        try:
            def fake_open_json(url, *args, **kwargs):
                calls.append(url)
                return {"tenantId": "tenant-123", "authority_host": "login.microsoftonline.com"}

            installer._open_json = fake_open_json
            candidate = installer.discover_entra_candidate("example.com")
            self.assertEqual(candidate["config"], {"mode": "entra", "domain": "example.com"})
            self.assertEqual(candidate["source"], "Entra ID")
            parsed = urllib.parse.urlparse(calls[0])
            self.assertEqual(parsed.scheme + "://" + parsed.netloc + parsed.path, installer.ENTRA_ODC_URL)
            self.assertEqual(urllib.parse.parse_qs(parsed.query), {"domain": ["example.com"]})
        finally:
            installer._open_json = old_open_json

    def test_webfinger_checks_actual_domain_before_provider_variants(self):
        calls = []
        old_open_json = installer._open_json
        try:
            def fake_open_json(url, *args, **kwargs):
                calls.append(url)
                raise urllib.error.URLError("missing")

            installer._open_json = fake_open_json
            candidates, messages = installer.discover_oidc_candidates("username", "alice@example.com", "example.com")
            self.assertEqual(candidates, [])
            self.assertEqual(messages, [])
            first = urllib.parse.urlparse(calls[0])
            self.assertEqual(first.scheme + "://" + first.netloc + first.path, "https://example.com/.well-known/webfinger")
            self.assertEqual(urllib.parse.parse_qs(first.query)["resource"], ["acct:alice@example.com"])
        finally:
            installer._open_json = old_open_json

    def test_domain_webfinger_does_not_invent_account_resource(self):
        calls = []
        old_open_json = installer._open_json
        try:
            def fake_open_json(url, *args, **kwargs):
                calls.append(url)
                raise urllib.error.URLError("missing")

            installer._open_json = fake_open_json
            candidates, messages = installer.discover_oidc_candidates("domain", "example.com", "example.com")
            self.assertEqual(candidates, [])
            resources = []
            for url in calls:
                resources.extend(urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get("resource", []))
            self.assertEqual(resources, ["https://example.com/", "https://example.com/"])
            self.assertNotIn("acct:himmelblau@example.com", resources)
            self.assertNotIn("okta:acct:himmelblau@example.com", resources)
        finally:
            installer._open_json = old_open_json

    def test_discovery_candidate_order_includes_existing_entra_oidc_manual(self):
        old_open_json = installer._open_json
        try:
            def fake_open_json(url, *args, **kwargs):
                if url.startswith(installer.ENTRA_ODC_URL):
                    return {"tenantId": "tenant-123", "authority_host": "login.microsoftonline.com"}
                parsed = urllib.parse.urlparse(url)
                if parsed.path == "/.well-known/webfinger":
                    return {"links": [{"rel": installer.OIDC_WEBFINGER_REL, "href": "https://issuer.example.com"}]}
                raise urllib.error.URLError("missing")

            installer._open_json = fake_open_json
            existing = {"mode": "entra", "domain": "old.example.com"}
            candidates, messages, domain = installer.discover_idp_candidates("domain", "example.com", existing)
            self.assertEqual(domain, "example.com")
            self.assertEqual([candidate["key"].split(":")[0] for candidate in candidates], ["existing", "discovered", "discovered", "manual"])
            self.assertEqual(candidates[1]["config"], {"mode": "entra", "domain": "example.com"})
            self.assertEqual(candidates[2]["config"]["oidc_issuer_url"], "https://issuer.example.com")
            self.assertTrue(candidates[2]["requires_app_id"])
        finally:
            installer._open_json = old_open_json

    def test_oidc_discovery_deduplicates_issuers(self):
        old_open_json = installer._open_json
        try:
            def fake_open_json(url, *args, **kwargs):
                return {"links": [{"rel": installer.OIDC_WEBFINGER_REL_HTTPS, "href": "https://issuer.example.com"}]}

            installer._open_json = fake_open_json
            candidates, _ = installer.discover_oidc_candidates("domain", "example.com", "example.com")
            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0]["config"]["oidc_issuer_url"], "https://issuer.example.com")
        finally:
            installer._open_json = old_open_json

    def test_existing_idp_config_detects_entra_domain(self):
        with self.subTest("domain"):
            path = pathlib.Path(self.id()).with_suffix(".conf")
            try:
                path.write_text("[global]\ndomain = example.onmicrosoft.com\n", encoding="utf-8")
                self.assertEqual(
                    installer.existing_idp_config(path),
                    {"mode": "entra", "domain": "example.onmicrosoft.com"},
                )
            finally:
                path.unlink(missing_ok=True)

    def test_existing_idp_config_detects_complete_oidc(self):
        path = pathlib.Path(self.id()).with_suffix(".conf")
        try:
            path.write_text(
                "[global]\noidc_issuer_url = https://keycloak.example.com/realms/himmelblau\napp_id = himmelblau-login\n",
                encoding="utf-8",
            )
            self.assertEqual(
                installer.existing_idp_config(path),
                {
                    "mode": "oidc",
                    "oidc_issuer_url": "https://keycloak.example.com/realms/himmelblau",
                    "app_id": "himmelblau-login",
                },
            )
        finally:
            path.unlink(missing_ok=True)

    def test_existing_idp_config_ignores_partial_oidc(self):
        path = pathlib.Path(self.id()).with_suffix(".conf")
        try:
            path.write_text("[global]\noidc_issuer_url = https://keycloak.example.com/realms/himmelblau\n", encoding="utf-8")
            self.assertIsNone(installer.existing_idp_config(path))
        finally:
            path.unlink(missing_ok=True)

    def test_existing_options_config_defaults_to_documented_values(self):
        path = pathlib.Path(self.id()).with_suffix(".conf")
        try:
            path.write_text("[global]\ndomain = example.onmicrosoft.com\n", encoding="utf-8")
            self.assertEqual(
                installer.existing_options_config(path),
                {
                    "pam_allow_groups": "",
                    "enable_hello": True,
                    "allow_console_password_only": True,
                    "apply_policy": True,
                },
            )
        finally:
            path.unlink(missing_ok=True)

    def test_existing_options_config_loads_existing_values(self):
        path = pathlib.Path(self.id()).with_suffix(".conf")
        try:
            path.write_text(
                "[global]\n"
                "pam_allow_groups = admins@example.com, f3c9a7e4-7d5a-47e8-832f-3d2d92abcd12\n"
                "enable_hello = false\n"
                "allow_console_password_only = false\n"
                "apply_policy = false\n",
                encoding="utf-8",
            )
            self.assertEqual(
                installer.existing_options_config(path),
                {
                    "pam_allow_groups": "admins@example.com, f3c9a7e4-7d5a-47e8-832f-3d2d92abcd12",
                    "enable_hello": False,
                    "allow_console_password_only": False,
                    "apply_policy": False,
                },
            )
        finally:
            path.unlink(missing_ok=True)

    def test_render_entra_config_preserves_existing_content(self):
        existing = "# keep me\n[global]\n# keep this too\napply_policy = true\n\n[other]\nvalue = 1\n"
        rendered = installer.render_idp_config(existing, {"mode": "entra", "domain": "example.onmicrosoft.com"})
        self.assertIn("# keep me\n", rendered)
        self.assertIn("# keep this too\n", rendered)
        self.assertIn("apply_policy = true\n", rendered)
        self.assertIn("[other]\nvalue = 1\n", rendered)
        self.assertIn("[global]\ndomain = example.onmicrosoft.com\n# keep this too", rendered)

    def test_render_entra_config_replaces_existing_domain_only(self):
        existing = "[global]\n  domain = old.example.com\napply_policy = true\n"
        rendered = installer.render_idp_config(existing, {"mode": "entra", "domain": "new.example.com"})
        self.assertIn("  domain = new.example.com\n", rendered)
        self.assertIn("apply_policy = true\n", rendered)
        self.assertNotIn("old.example.com", rendered)

    def test_render_oidc_config(self):
        rendered = installer.render_idp_config(
            "",
            {
                "mode": "oidc",
                "oidc_issuer_url": "https://keycloak.example.com/realms/himmelblau",
                "app_id": "himmelblau-login",
            },
        )
        self.assertEqual(
            rendered,
            "[global]\noidc_issuer_url = https://keycloak.example.com/realms/himmelblau\napp_id = himmelblau-login\n",
        )

    def test_render_oidc_config_preserves_existing_content(self):
        existing = "# keep me\n[global]\napp_id = old-client\napply_policy = true\n\n[other]\nvalue = 1\n"
        rendered = installer.render_idp_config(
            existing,
            {
                "mode": "oidc",
                "oidc_issuer_url": "https://keycloak.example.com/realms/himmelblau",
                "app_id": "himmelblau-login",
            },
        )
        self.assertIn("# keep me\n", rendered)
        self.assertIn("apply_policy = true\n", rendered)
        self.assertIn("[other]\nvalue = 1\n", rendered)
        self.assertIn("oidc_issuer_url = https://keycloak.example.com/realms/himmelblau\napp_id = himmelblau-login\n", rendered)
        self.assertNotIn("old-client", rendered)

    def test_render_global_config_writes_non_default_options_only(self):
        rendered = installer.render_global_config(
            "",
            {"mode": "entra", "domain": "example.onmicrosoft.com"},
            True,
            {
                "pam_allow_groups": "f3c9a7e4-7d5a-47e8-832f-3d2d92abcd12, admin@example.com",
                "enable_hello": False,
                "allow_console_password_only": True,
                "apply_policy": False,
            },
        )
        self.assertIn("domain = example.onmicrosoft.com\n", rendered)
        self.assertIn("pam_allow_groups = f3c9a7e4-7d5a-47e8-832f-3d2d92abcd12, admin@example.com\n", rendered)
        self.assertIn("enable_hello = false\n", rendered)
        self.assertIn("apply_policy = false\n", rendered)
        self.assertNotIn("allow_console_password_only", rendered)

    def test_render_global_config_removes_default_options_and_blank_groups(self):
        existing = (
            "# keep me\n[global]\n"
            "domain = old.example.com\n"
            "pam_allow_groups = admins@example.com\n"
            "enable_hello = false\n"
            "allow_console_password_only = false\n"
            "apply_policy = false\n"
            "debug = true\n\n[other]\nvalue = 1\n"
        )
        rendered = installer.render_global_config(
            existing,
            {"mode": "entra", "domain": "new.example.com"},
            True,
            {
                "pam_allow_groups": "",
                "enable_hello": True,
                "allow_console_password_only": True,
                "apply_policy": True,
            },
        )
        self.assertIn("# keep me\n", rendered)
        self.assertIn("domain = new.example.com\n", rendered)
        self.assertIn("debug = true\n", rendered)
        self.assertIn("[other]\nvalue = 1\n", rendered)
        self.assertNotIn("pam_allow_groups", rendered)
        self.assertNotIn("enable_hello", rendered)
        self.assertNotIn("allow_console_password_only", rendered)
        self.assertNotIn("apply_policy", rendered)

    def test_render_global_config_preserves_apply_policy_for_oidc(self):
        existing = "[global]\noidc_issuer_url = https://old.example.com\napp_id = old\napply_policy = false\n"
        rendered = installer.render_global_config(
            existing,
            {
                "mode": "oidc",
                "oidc_issuer_url": "https://keycloak.example.com/realms/himmelblau",
                "app_id": "himmelblau-login",
            },
            True,
            {
                "pam_allow_groups": "",
                "enable_hello": True,
                "allow_console_password_only": True,
                "apply_policy": True,
            },
        )
        self.assertIn("oidc_issuer_url = https://keycloak.example.com/realms/himmelblau\n", rendered)
        self.assertIn("app_id = himmelblau-login\n", rendered)
        self.assertIn("apply_policy = false\n", rendered)

    def test_validate_pam_allow_groups_accepts_upns_and_guids(self):
        ok, message = installer.validate_pam_allow_groups(
            "f3c9a7e4-7d5a-47e8-832f-3d2d92abcd12, admin@himmelblau-idm.org"
        )
        self.assertTrue(ok, message)
        ok, _ = installer.validate_pam_allow_groups("Admins")
        self.assertFalse(ok)
        ok, _ = installer.validate_pam_allow_groups("admin@example.com,,ops@example.com")
        self.assertFalse(ok)

    def test_build_install_plan_uses_known_step_kinds(self):
        old_detected = installer.detected_package_selection
        try:
            installer.detected_package_selection = lambda channel, target: (
                ["himmelblau", "pam-himmelblau", "nss-himmelblau", "himmelblau-sso"],
                ["himmelblau-selinux"],
            )
            plan = installer.build_install_plan(
                "stable",
                "ubuntu24.04",
                {"mode": "entra", "domain": "example.onmicrosoft.com"},
                True,
                {
                    "pam_allow_groups": "",
                    "enable_hello": True,
                    "allow_console_password_only": True,
                    "apply_policy": True,
                },
            )
            self.assertEqual(plan["version"], installer.PLAN_VERSION)
            self.assertEqual(
                [step["kind"] for step in plan["steps"]],
                ["apt_prereqs", "apt_repo", "install_packages", "write_global_config", "note", "enable_services", "maybe_status"],
            )
            self.assertEqual(plan["steps"][2]["packages"], ["himmelblau", "pam-himmelblau", "nss-himmelblau", "himmelblau-sso"])
            self.assertEqual(plan["steps"][2]["best_effort_packages"], ["himmelblau-selinux"])
            self.assertEqual(plan["steps"][3]["config"]["write_idp"], True)
            self.assertTrue(installer.validate_install_plan(plan))
        finally:
            installer.detected_package_selection = old_detected

    def test_install_plan_rejects_unknown_step_kind(self):
        old_detected = installer.detected_package_selection
        installer.detected_package_selection = lambda channel, target: (["himmelblau", "pam-himmelblau", "nss-himmelblau"], [])
        plan = installer.build_install_plan(
            "stable",
            "ubuntu24.04",
            {"mode": "entra", "domain": "example.onmicrosoft.com"},
            False,
        )
        try:
            plan["steps"].append({"kind": "shell", "command": "whoami"})
            with self.assertRaises(installer.InstallError):
                installer.validate_install_plan(plan)
        finally:
            installer.detected_package_selection = old_detected

    def test_install_plan_rejects_invalid_package_name(self):
        old_detected = installer.detected_package_selection
        try:
            installer.detected_package_selection = lambda channel, target: (["himmelblau", "bad package"], [])
            plan = installer.build_package_only_plan("stable", "ubuntu24.04")
            with self.assertRaises(installer.InstallError):
                installer.validate_install_plan(plan)
        finally:
            installer.detected_package_selection = old_detected

    def test_package_only_plan_omits_configuration_steps(self):
        old_detected = installer.detected_package_selection
        try:
            installer.detected_package_selection = lambda channel, target: (["himmelblau", "pam-himmelblau", "nss-himmelblau"], [])
            plan = installer.build_package_only_plan("stable", "ubuntu24.04")
            kinds = [step["kind"] for step in plan["steps"]]
            self.assertNotIn("write_idp_config", kinds)
            self.assertNotIn("write_global_config", kinds)
            self.assertNotIn("configure_distro_provided", kinds)
            self.assertEqual(kinds, ["apt_prereqs", "apt_repo", "install_packages", "note", "enable_services", "maybe_status"])
        finally:
            installer.detected_package_selection = old_detected

    def test_rawhide_plan_uses_rawhide_dnf_repo_target(self):
        plan = installer.build_package_only_plan("nightly", "rawhide")
        self.assertEqual(plan["target"], "rawhide")
        self.assertEqual(plan["manager"], "dnf")
        self.assertIn({"kind": "dnf_repo", "channel": "nightly", "target": "rawhide"}, plan["steps"])

    def test_default_community_channel_prefers_stable(self):
        matrix = installer.extract_repo_support(INSTALL_JS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(installer.default_community_channel(matrix, "fedora42"), ("stable", None))

    def test_default_community_channel_falls_back_to_nightly(self):
        matrix = installer.extract_repo_support(INSTALL_JS_PATH.read_text(encoding="utf-8"))
        channel, message = installer.default_community_channel(matrix, "fedora44")
        self.assertEqual(channel, "nightly")
        self.assertIn("Community Stable packages are not available", message)

    def test_default_community_channel_fails_without_community_support(self):
        matrix = {
            "stable": {"include": [], "exclude": ["fedora44"]},
            "nightly": {"include": [], "exclude": ["fedora44"]},
            "subscription": {"include": ["fedora44"], "exclude": []},
        }
        with self.assertRaises(installer.InstallError):
            installer.default_community_channel(matrix, "fedora44")

    def test_cli_choose_defaults_to_first_choice(self):
        ui = installer.CliUi.__new__(installer.CliUi)

        class FakeTty:
            def __init__(self):
                self.output = []

            def readline(self):
                return "\n"

            def write(self, text):
                self.output.append(text)

            def flush(self):
                pass

        ui.tty = FakeTty()
        self.assertEqual(
            ui.choose("Choose installation source", [
                {"label": "Community Stable repository", "value": "stable"},
                {"label": "Community Nightly repository", "value": "nightly"},
            ]),
            "stable",
        )

    def test_has_interactive_terminal_uses_stdin_tty(self):
        old_open = installer.os.open
        old_isatty = installer.os.isatty
        old_close = installer.os.close
        opened = []
        closed = []

        try:
            def fake_isatty(fd):
                return fd in (0, 100)

            def fake_open(path, flags):
                opened.append(path)
                if path == "/dev/tty":
                    raise OSError("no controlling tty")
                if path == "/proc/self/fd/0":
                    return 100
                raise OSError("unexpected path")

            installer.os.isatty = fake_isatty
            installer.os.open = fake_open
            installer.os.close = lambda fd: closed.append(fd)
            self.assertTrue(installer.has_interactive_terminal())
            self.assertEqual(opened, ["/dev/tty", "/proc/self/fd/0"])
            self.assertEqual(closed, [100])
        finally:
            installer.os.open = old_open
            installer.os.isatty = old_isatty
            installer.os.close = old_close

    def test_has_interactive_terminal_uses_dev_tty(self):
        old_open = installer.os.open
        old_isatty = installer.os.isatty
        old_close = installer.os.close
        closed = []

        try:
            installer.os.isatty = lambda fd: fd == 100

            def fake_open(path, flags):
                self.assertEqual(path, "/dev/tty")
                return 100

            installer.os.open = fake_open
            installer.os.close = lambda fd: closed.append(fd)
            self.assertTrue(installer.has_interactive_terminal())
            self.assertEqual(closed, [100])
        finally:
            installer.os.open = old_open
            installer.os.isatty = old_isatty
            installer.os.close = old_close

    def test_has_interactive_terminal_uses_stdout_tty_without_dev_tty(self):
        old_open = installer.os.open
        old_isatty = installer.os.isatty
        old_close = installer.os.close
        opened = []
        closed = []

        try:
            def fake_isatty(fd):
                return fd in (1, 100)

            def fake_open(path, flags):
                opened.append(path)
                if path == "/dev/tty":
                    raise OSError("no controlling tty")
                if path == "/proc/self/fd/1":
                    return 100
                raise OSError("unexpected path")

            installer.os.isatty = fake_isatty
            installer.os.open = fake_open
            installer.os.close = lambda fd: closed.append(fd)
            self.assertTrue(installer.has_interactive_terminal())
            self.assertEqual(opened, ["/dev/tty", "/proc/self/fd/1"])
            self.assertEqual(closed, [100])
        finally:
            installer.os.open = old_open
            installer.os.isatty = old_isatty
            installer.os.close = old_close

    def test_has_interactive_terminal_false_without_tty(self):
        old_open = installer.os.open
        old_isatty = installer.os.isatty

        try:
            installer.os.isatty = lambda fd: False
            installer.os.open = lambda path, flags: (_ for _ in ()).throw(OSError("no tty"))
            self.assertFalse(installer.has_interactive_terminal())
        finally:
            installer.os.open = old_open
            installer.os.isatty = old_isatty

    def test_main_uses_curses_when_tty_available(self):
        calls = []
        old_has_interactive_terminal = installer.has_interactive_terminal
        old_run_curses_terminal_child = installer.run_curses_terminal_child
        old_run_headless_install = installer.run_headless_install
        try:
            installer.has_interactive_terminal = lambda: True
            installer.run_curses_terminal_child = lambda: calls.append("curses") or 0
            installer.run_headless_install = lambda: calls.append("headless")
            installer.main()
            self.assertEqual(calls, ["curses"])
        finally:
            installer.has_interactive_terminal = old_has_interactive_terminal
            installer.run_curses_terminal_child = old_run_curses_terminal_child
            installer.run_headless_install = old_run_headless_install

    def test_main_uses_headless_without_tty(self):
        calls = []
        old_has_interactive_terminal = installer.has_interactive_terminal
        old_run_curses_terminal_child = installer.run_curses_terminal_child
        old_run_headless_install = installer.run_headless_install
        try:
            installer.has_interactive_terminal = lambda: False
            installer.run_curses_terminal_child = lambda: calls.append("curses") or 0
            installer.run_headless_install = lambda: calls.append("headless")
            installer.main()
            self.assertEqual(calls, ["headless"])
        finally:
            installer.has_interactive_terminal = old_has_interactive_terminal
            installer.run_curses_terminal_child = old_run_curses_terminal_child
            installer.run_headless_install = old_run_headless_install

    def test_main_does_not_use_headless_when_interactive_curses_fails(self):
        calls = []
        old_has_interactive_terminal = installer.has_interactive_terminal
        old_run_curses_terminal_child = installer.run_curses_terminal_child
        old_run_headless_install = installer.run_headless_install
        try:
            installer.has_interactive_terminal = lambda: True
            installer.run_curses_terminal_child = lambda: calls.append("curses") or installer.CURSES_STARTUP_EXIT
            installer.run_headless_install = lambda: calls.append("headless")
            with self.assertRaises(installer.InstallError):
                installer.main()
            self.assertEqual(calls, ["curses"])
        finally:
            installer.has_interactive_terminal = old_has_interactive_terminal
            installer.run_curses_terminal_child = old_run_curses_terminal_child
            installer.run_headless_install = old_run_headless_install

    def test_acquire_terminal_fd_falls_back_to_stdout_tty(self):
        old_open = installer.os.open
        old_isatty = installer.os.isatty
        old_close = installer.os.close
        opened = []
        closed = []
        try:
            def fake_isatty(fd):
                return fd in (1, 100)

            def fake_open(path, flags):
                opened.append(path)
                if path == "/dev/tty":
                    raise OSError("no controlling tty")
                if path == "/proc/self/fd/1":
                    return 100
                raise OSError("unexpected path")

            installer.os.isatty = fake_isatty
            installer.os.open = fake_open
            installer.os.close = lambda fd: closed.append(fd)
            self.assertEqual(installer.acquire_terminal_fd(), 100)
            self.assertEqual(opened, ["/dev/tty", "/proc/self/fd/1"])
            self.assertEqual(closed, [])
        finally:
            installer.os.open = old_open
            installer.os.isatty = old_isatty
            installer.os.close = old_close

    def test_acquire_terminal_fd_fails_without_any_terminal(self):
        old_open = installer.os.open
        old_isatty = installer.os.isatty
        try:
            installer.os.isatty = lambda fd: False
            installer.os.open = lambda path, flags: (_ for _ in ()).throw(OSError("no tty"))
            with self.assertRaises(installer.InstallError):
                installer.acquire_terminal_fd()
        finally:
            installer.os.open = old_open
            installer.os.isatty = old_isatty

    def test_attach_terminal_stdio_duplicates_fd_to_standard_streams(self):
        calls = []
        old_dup2 = installer.os.dup2
        try:
            installer.os.dup2 = lambda source, target: calls.append((source, target))
            installer.attach_terminal_stdio(42)
            self.assertEqual(calls, [(42, 0), (42, 1), (42, 2)])
        finally:
            installer.os.dup2 = old_dup2

    def test_non_interactive_elevation_uses_sudo_n(self):
        plan = installer.build_package_only_plan("stable", "ubuntu24.04")
        calls = []
        events = []

        class FakeProc:
            def poll(self):
                return 0

            @property
            def returncode(self):
                return 0

        old_geteuid = installer.os.geteuid
        old_which = installer.shutil.which
        old_popen = installer.subprocess.Popen
        old_wait = installer.wait_with_events
        try:
            installer.os.geteuid = lambda: 1000
            installer.shutil.which = lambda command: "/usr/bin/sudo" if command == "sudo" else None

            def fake_popen(argv):
                calls.append(argv)
                return FakeProc()

            installer.subprocess.Popen = fake_popen
            installer.wait_with_events = lambda proc, event_log, on_event: 0
            installer.run_elevated_plan(plan, on_event=events.append, prefer_gui=False, non_interactive=True)
            self.assertEqual(calls[0][:2], ["sudo", "-n"])
        finally:
            installer.os.geteuid = old_geteuid
            installer.shutil.which = old_which
            installer.subprocess.Popen = old_popen
            installer.wait_with_events = old_wait

    def test_curses_install_validates_sudo_before_worker(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.curses = types.SimpleNamespace(
            def_prog_mode=lambda: None,
            endwin=lambda: None,
            reset_prog_mode=lambda: None,
            curs_set=lambda value: None,
        )
        ui.channel = "stable"
        ui.target = "ubuntu24.04"
        ui.existing_config = None
        ui.mode = "entra"
        ui.domain = "example.onmicrosoft.com"
        ui.pam_allow_groups = ""
        ui.enable_hello = True
        ui.allow_console_password_only = True
        ui.apply_policy = True
        ui.render = lambda: None
        ui.on_event = lambda event: None

        calls = []

        class FakeProc:
            returncode = 0

        old_geteuid = installer.os.geteuid
        old_which = installer.shutil.which
        old_run = installer.subprocess.run
        old_run_elevated_plan = installer.run_elevated_plan
        try:
            installer.os.geteuid = lambda: 1000
            installer.shutil.which = lambda command: "/usr/bin/sudo" if command == "sudo" else None

            def fake_run(argv, stdin=None, stdout=None, stderr=None, check=False):
                calls.append(("sudo", argv))
                return FakeProc()

            def fake_run_elevated_plan(plan, on_event=None, prefer_gui=True, non_interactive=False):
                calls.append(("worker", prefer_gui, non_interactive))

            installer.subprocess.run = fake_run
            installer.run_elevated_plan = fake_run_elevated_plan
            ui.start_install()
            self.assertEqual(calls[0], ("sudo", ["sudo", "-S", "-v"]))
            self.assertEqual(calls[1], ("worker", False, True))
            self.assertTrue(ui.install_ok)
        finally:
            installer.os.geteuid = old_geteuid
            installer.shutil.which = old_which
            installer.subprocess.run = old_run
            installer.run_elevated_plan = old_run_elevated_plan

    def test_curses_navigation_includes_options_page(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.page = "identity"
        ui.existing_config = None
        ui.mode = "entra"
        ui.domain = "example.onmicrosoft.com"
        ui.message = ""
        ui.pam_allow_groups = ""
        ui.enable_hello = True
        ui.allow_console_password_only = True
        ui.apply_policy = True
        self.assertTrue(ui.next_page())
        self.assertEqual(ui.page, "options")
        self.assertTrue(ui.next_page())
        self.assertEqual(ui.page, "review")
        self.assertTrue(ui.back_page())
        self.assertEqual(ui.page, "options")
        self.assertTrue(ui.back_page())
        self.assertEqual(ui.page, "identity")

    def test_curses_identity_next_runs_discovery_before_options(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.page = "identity"
        ui.identity_stage = "input"
        ui.input_mode = "domain"
        ui.domain = "example.com"
        ui.username = ""
        ui.existing_config = None
        ui.discovery_candidates = []
        ui.discovery_messages = []
        ui.selected_candidate_key = None
        ui.manual_mode = "entra"
        ui.message = ""

        old_discover = installer.discover_idp_candidates
        try:
            def fake_discover(input_mode, identifier, existing_config=None):
                self.assertEqual((input_mode, identifier, existing_config), ("domain", "example.com", None))
                return [
                    {
                        "key": "manual",
                        "label": "Configure identity provider manually",
                        "config": None,
                        "write_idp": True,
                        "requires_app_id": False,
                    }
                ], ["No OIDC issuer was discovered with WebFinger."], "example.com"

            installer.discover_idp_candidates = fake_discover
            self.assertTrue(ui.next_page())
            self.assertEqual(ui.page, "identity")
            self.assertEqual(ui.identity_stage, "results")
            self.assertEqual(ui.selected_candidate_key, "manual")
            self.assertTrue(ui.next_page())
            self.assertEqual(ui.page, "options")
        finally:
            installer.discover_idp_candidates = old_discover

    def test_curses_identity_skip_empty_domain_opens_manual_without_discovery(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.page = "identity"
        ui.identity_stage = "input"
        ui.input_mode = "domain"
        ui.domain = "   "
        ui.username = ""
        ui.existing_config = None
        ui.discovery_candidates = []
        ui.discovery_messages = ["old message"]
        ui.selected_candidate_key = None
        ui.message = "old error"

        old_discover = installer.discover_idp_candidates
        try:
            def fake_discover(*args, **kwargs):
                raise AssertionError("discovery should not run when skipping")

            installer.discover_idp_candidates = fake_discover
            self.assertTrue(ui.skip_identity_discovery())
            self.assertEqual(ui.page, "identity")
            self.assertEqual(ui.identity_stage, "results")
            self.assertEqual(ui.discovery_messages, [])
            self.assertEqual(ui.selected_candidate_key, "manual")
            self.assertEqual(ui.discovery_candidates, [installer.manual_idp_candidate()])
            self.assertEqual(ui.message, "")
        finally:
            installer.discover_idp_candidates = old_discover

    def test_curses_identity_skip_empty_username_opens_manual_without_discovery(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.page = "identity"
        ui.identity_stage = "input"
        ui.input_mode = "username"
        ui.domain = ""
        ui.username = ""
        ui.discovery_candidates = []
        ui.discovery_messages = []
        ui.selected_candidate_key = None
        ui.message = ""

        old_discover = installer.discover_idp_candidates
        try:
            def fake_discover(*args, **kwargs):
                raise AssertionError("discovery should not run when skipping")

            installer.discover_idp_candidates = fake_discover
            self.assertTrue(ui.skip_identity_discovery())
            self.assertEqual(ui.identity_stage, "results")
            self.assertEqual(ui.selected_candidate_key, "manual")
            self.assertEqual(ui.discovery_candidates, [installer.manual_idp_candidate()])
        finally:
            installer.discover_idp_candidates = old_discover

    def test_curses_identity_footer_primary_switches_between_skip_and_next(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.identity_stage = "input"
        ui.input_mode = "domain"
        ui.domain = ""
        ui.username = ""
        ui.message = ""
        ui.glyphs = {"back": "<", "cancel": "x", "next": ">"}
        ui._attr = lambda name, extra=0: 0
        ui._begin_frame = lambda title, subtitle: {
            "content_y": 0,
            "content_x": 0,
            "content_h": 20,
            "content_w": 80,
            "footer_y": 19,
            "win_x": 0,
            "win_w": 80,
        }
        ui._draw_box = lambda *args, **kwargs: None
        ui._radio = lambda y, x, width, key, label, selected, action: y + 1
        ui._input = lambda y, x, width, field, label: y + 1
        ui._draw_wrapped = lambda y, x, text, width, attr=0: y + 1
        footers = []
        ui._footer_buttons = lambda layout, buttons: footers.append(buttons)

        ui.render_identity()
        self.assertEqual(footers[-1][-1]["key_label"], "Skip")
        self.assertEqual(footers[-1][-1]["action"], ui.skip_identity_discovery)

        ui.domain = "example.com"
        ui.render_identity()
        self.assertEqual(footers[-1][-1]["key_label"], "Next")
        self.assertEqual(footers[-1][-1]["action"], ui.next_page)

    def test_curses_options_page_hides_apply_policy_for_oidc(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.existing_config = None
        ui.mode = "oidc"
        ui.issuer = "https://keycloak.example.com/realms/himmelblau"
        ui.appid = "himmelblau-login"
        ui.pam_allow_groups = ""
        ui.enable_hello = True
        ui.allow_console_password_only = True
        ui.apply_policy = True
        ui.message = ""
        ui.glyphs = {"back": "<", "cancel": "x", "next": ">", "check_on": "[x]", "check_off": "[ ]"}
        ui._attr = lambda name, extra=0: 0
        ui._begin_frame = lambda title, subtitle: {
            "content_y": 0,
            "content_x": 0,
            "content_h": 20,
            "content_w": 80,
            "footer_y": 19,
        }
        ui._draw_box = lambda *args, **kwargs: None
        ui._write = lambda *args, **kwargs: None
        ui._draw_wrapped = lambda y, x, text, width, attr=0: y + 1
        ui._input = lambda y, x, width, field, label: y + 1
        ui._footer_buttons = lambda *args, **kwargs: None
        labels = []

        def fake_checkbox(y, x, width, key, label, checked, action):
            labels.append(label)
            return y + 1

        ui._checkbox = fake_checkbox
        ui.render_options()
        self.assertIn("Enable Linux Hello PIN authentication", labels)
        self.assertIn("Allow password-only local console logins", labels)
        self.assertNotIn("Apply Intune device compliance policies", labels)

    def test_curses_theme_falls_back_without_color_support(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.curses = types.SimpleNamespace(A_BOLD=1, A_REVERSE=2, has_colors=lambda: False)
        ui._configure_colors()
        self.assertIn("button_focus", ui.colors)
        self.assertEqual(ui.colors["button_focus"], 2)

    def test_curses_rgb_to_curses_scale(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        self.assertEqual(ui._rgb_to_curses(0xFA, 0xFA, 0xFB), (980, 980, 984))
        self.assertEqual(ui._rgb_to_curses(0xDE, 0xDA, 0xD7), (871, 855, 843))

    def test_curses_theme_defines_custom_gtk_like_colors(self):
        calls = []

        class FakeCurses:
            A_BOLD = 1
            A_REVERSE = 2
            COLOR_BLACK = 0
            COLOR_RED = 1
            COLOR_YELLOW = 3
            COLOR_BLUE = 4
            COLOR_WHITE = 7
            COLORS = 256

            def has_colors(self):
                return True

            def start_color(self):
                pass

            def use_default_colors(self):
                pass

            def can_change_color(self):
                return True

            def init_color(self, number, red, green, blue):
                calls.append(("color", number, red, green, blue))

            def init_pair(self, number, fg, bg):
                calls.append(("pair", number, fg, bg))

            def color_pair(self, number):
                return number * 100

        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.curses = FakeCurses()
        ui._configure_colors()
        self.assertIn(("color", 240, 980, 980, 984), calls)
        self.assertIn(("color", 241, 871, 855, 843), calls)
        self.assertIn(("color", 242, 941, 941, 941), calls)
        self.assertEqual(ui.colors["window"], 100)
        self.assertEqual(ui.colors["title"], 301)

    def test_curses_theme_falls_back_when_custom_colors_unavailable(self):
        class FakeCurses:
            A_BOLD = 1
            A_REVERSE = 2
            COLOR_BLACK = 0
            COLOR_RED = 1
            COLOR_YELLOW = 3
            COLOR_BLUE = 4
            COLOR_WHITE = 7
            COLORS = 16

            def has_colors(self):
                return True

            def start_color(self):
                pass

            def use_default_colors(self):
                pass

            def can_change_color(self):
                return False

            def init_pair(self, number, fg, bg):
                pass

            def color_pair(self, number):
                return number

        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.curses = FakeCurses()
        palette = ui._theme_palette()
        self.assertEqual(palette["window_bg"], FakeCurses.COLOR_WHITE)
        self.assertEqual(palette["title_bg"], FakeCurses.COLOR_WHITE)

    def test_curses_glyphs_use_unicode_when_supported(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui._supports_unicode = lambda: True
        self.assertEqual(ui._glyphs()["tl"], "╭")
        self.assertEqual(ui._glyphs()["bar_full"], "█")

    def test_curses_glyphs_fall_back_to_ascii(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui._supports_unicode = lambda: False
        self.assertEqual(ui._glyphs()["tl"], "+")
        self.assertEqual(ui._glyphs()["bar_full"], "#")

    def test_curses_focus_key_is_visible_during_rebuild(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.focusables = []
        ui.focus_index = 0
        ui.focus_key = "button:next"
        self.assertTrue(ui._is_focused("button:next"))

    def test_curses_focus_skips_disabled_controls(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.focusables = [
            {"key": "back", "enabled": True},
            {"key": "cancel", "enabled": False},
            {"key": "next", "enabled": True},
        ]
        ui.focus_index = 0
        ui.focus_key = "back"
        ui._move_focus(1)
        self.assertEqual(ui.focus_key, "next")

    def test_curses_button_activation_uses_focused_action(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        calls = []
        ui.focusables = [{"key": "button:next", "kind": "button", "enabled": True, "action": lambda: calls.append("next") or False}]
        ui.focus_index = 0
        self.assertFalse(ui._activate_focused())
        self.assertEqual(calls, ["next"])

    def test_curses_button_renders_focus_markers(self):
        class FakeScreen:
            def __init__(self):
                self.writes = []

            def getmaxyx(self):
                return (24, 80)

            def addnstr(self, y, x, text, limit, attr):
                self.writes.append(text[:limit])

        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.stdscr = FakeScreen()
        ui.curses = types.SimpleNamespace(error=Exception, A_BOLD=1, A_REVERSE=2)
        ui.colors = {"button_focus": 20, "button": 10, "primary": 11, "primary_focus": 21, "disabled": 0}
        ui.glyphs = {"focus_l": "▶", "focus_r": "◀"}
        ui.focusables = []
        ui.mouse_targets = []
        ui.focus_index = 0
        ui.focus_key = "button:next"
        ui._button(1, 1, "Next", lambda: None)
        self.assertIn("▶", ui.stdscr.writes[0])
        self.assertIn("◀", ui.stdscr.writes[0])

    def test_curses_frame_keeps_surrounding_background_default(self):
        class FakeScreen:
            def __init__(self):
                self.backgrounds = []

            def getmaxyx(self):
                return (24, 80)

            def bkgd(self, char, attr):
                self.backgrounds.append((char, attr))

            def erase(self):
                pass

            def addnstr(self, y, x, text, limit, attr):
                pass

        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.stdscr = FakeScreen()
        ui.curses = types.SimpleNamespace(error=Exception, A_BOLD=1)
        ui.colors = {"window": 10, "panel": 11, "title": 12, "accent": 13, "muted": 14, "selected": 15}
        ui.glyphs = {"tl": "╭", "tr": "╮", "bl": "╰", "br": "╯", "h": "─", "v": "│", "current": "▶", "done": "●", "pending": "○"}
        ui.page = "preflight"
        ui.focusables = []
        ui.mouse_targets = []
        ui._begin_frame("Preflight", "Subtitle")
        self.assertEqual(ui.stdscr.backgrounds[0], (" ", 0))

    def test_curses_progress_bar_uses_block_glyphs(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.glyphs = {"bar_full": "█", "bar_empty": "░"}
        filled = int(10 * 50 / 100.0)
        bar = ui.glyphs["bar_full"] * filled + ui.glyphs["bar_empty"] * (10 - filled)
        self.assertEqual(bar, "█████░░░░░")

    def test_curses_mouse_click_activates_target(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        calls = []
        ui.curses = types.SimpleNamespace(
            BUTTON1_CLICKED=1,
            BUTTON1_RELEASED=2,
            getmouse=lambda: (0, 12, 5, 0, 1),
        )
        target = {"key": "button:next", "kind": "button", "bounds": (5, 10, 1, 10), "enabled": True, "action": lambda: calls.append("next") or True}
        ui.focusables = [target]
        ui.mouse_targets = [target]
        ui.focus_index = 0
        ui.focus_key = None
        self.assertTrue(ui._handle_mouse())
        self.assertEqual(calls, ["next"])
        self.assertEqual(ui.focus_key, "button:next")

    def test_curses_text_input_editing_supports_cursor_keys(self):
        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.curses = types.SimpleNamespace(KEY_BACKSPACE=263, KEY_DC=330, KEY_LEFT=260, KEY_RIGHT=261, KEY_HOME=262, KEY_END=360)
        ui.domain = "abc"
        ui.issuer = ""
        ui.appid = ""
        ui.input_cursor = {"domain": 1, "issuer": 0, "appid": 0}
        ui._edit_field("domain", ord("Z"))
        self.assertEqual(ui.domain, "aZbc")
        self.assertEqual(ui.input_cursor["domain"], 2)
        ui._edit_field("domain", ui.curses.KEY_LEFT)
        ui._edit_field("domain", ui.curses.KEY_BACKSPACE)
        self.assertEqual(ui.domain, "Zbc")
        ui._edit_field("domain", ui.curses.KEY_END)
        ui._edit_field("domain", ui.curses.KEY_DC)
        self.assertEqual(ui.domain, "Zbc")

    def test_curses_input_defers_cursor_move_until_render_end(self):
        class FakeScreen:
            def __init__(self):
                self.moves = []

            def getmaxyx(self):
                return (24, 80)

            def addnstr(self, y, x, text, limit, attr):
                pass

            def move(self, y, x):
                self.moves.append((y, x))

        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.stdscr = FakeScreen()
        ui.curses = types.SimpleNamespace(error=Exception, A_BOLD=1, A_REVERSE=2)
        ui.colors = {"muted": 0, "input_focus": 10, "input": 9, "button_focus": 11}
        ui.glyphs = {"focus_l": "▶", "focus_r": "◀"}
        ui.focusables = []
        ui.mouse_targets = []
        ui.focus_index = 0
        ui.focus_key = "field:domain"
        ui.domain = "example.com"
        ui.input_cursor = {"domain": 3}
        ui.cursor_position = None
        ui._input(5, 2, 50, "domain", "Domain")
        self.assertEqual(ui.cursor_position, (5, 21))
        self.assertEqual(ui.stdscr.moves, [])

    def test_curses_inactive_input_renders_visible_edges_and_hitbox(self):
        class FakeScreen:
            def __init__(self):
                self.writes = []

            def getmaxyx(self):
                return (24, 80)

            def addnstr(self, y, x, text, limit, attr):
                self.writes.append((y, x, text[:limit], attr))

        ui = installer.WizardCursesUi.__new__(installer.WizardCursesUi)
        ui.stdscr = FakeScreen()
        ui.curses = types.SimpleNamespace(error=Exception, A_BOLD=1, A_REVERSE=2)
        ui.colors = {"muted": 0, "input_focus": 10, "input": 9, "button_focus": 11}
        ui.glyphs = {"focus_l": "▶", "focus_r": "◀", "input_l": "▏", "input_r": "▕"}
        ui.focusables = []
        ui.mouse_targets = []
        ui.focus_index = 0
        ui.focus_key = "button:next"
        ui.domain = ""
        ui.input_cursor = {"domain": 0}
        ui.cursor_position = None
        ui._input(5, 2, 50, "domain", "Domain")
        self.assertIn((5, 17, "▏", 9), ui.stdscr.writes)
        self.assertTrue(any(write[2] == "▕" for write in ui.stdscr.writes))
        self.assertEqual(ui.mouse_targets[0]["bounds"], (5, 17, 1, 35))
        self.assertIsNone(ui.cursor_position)

    def test_terminal_launcher_prefers_xdg_terminal_exec(self):
        available = {"xdg-terminal-exec", "x-terminal-emulator", "gnome-terminal"}

        def fake_which(command):
            return "/usr/bin/" + command if command in available else None

        self.assertEqual(
            installer.terminal_launcher_command(["sudo", "python3", "worker.py"], which=fake_which),
            ["xdg-terminal-exec", "sudo", "python3", "worker.py"],
        )

    def test_terminal_launcher_falls_back_to_known_terminal(self):
        available = {"konsole"}

        def fake_which(command):
            return "/usr/bin/" + command if command in available else None

        self.assertEqual(
            installer.terminal_launcher_command(["sudo", "python3", "worker.py"], which=fake_which),
            ["konsole", "-e", "sudo", "python3", "worker.py"],
        )

    def test_work_dir_prefers_current_directory(self):
        original = pathlib.Path.cwd()
        temp_dir = pathlib.Path(tempfile.mkdtemp())
        try:
            import os

            os.chdir(temp_dir)
            work_dir = pathlib.Path(installer.make_work_dir())
            try:
                self.assertEqual(work_dir.parent, temp_dir)
                self.assertTrue(work_dir.name.startswith(".himmelblau-installer-"))
            finally:
                shutil.rmtree(work_dir, ignore_errors=True)
        finally:
            os.chdir(original)
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
