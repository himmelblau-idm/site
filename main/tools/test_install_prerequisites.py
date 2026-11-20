"""Package scriptlet dependencies must exist before the package transaction."""
import contextlib
import unittest
from unittest import mock

from test_install_endpoint import APT_CONFFILE_OPTIONS, installer, load_worker_module


MANAGERS = (
    ("debian13", "apt", "apt_repo_setup", ["env", "DEBIAN_FRONTEND=noninteractive", "apt-get"] + APT_CONFFILE_OPTIONS + ["install", "-y", "gawk"]),
    ("ubuntu24.04", "apt", "apt_repo_setup", ["env", "DEBIAN_FRONTEND=noninteractive", "apt-get"] + APT_CONFFILE_OPTIONS + ["install", "-y", "gawk"]),
    ("tumbleweed", "zypper", "zypper_repo_setup", ["zypper", "--non-interactive", "install", "-y", "gawk"]),
    ("sle16", "zypper", "zypper_repo_setup", ["zypper", "--non-interactive", "install", "-y", "gawk"]),
    ("fedora44", "dnf", "dnf_repo_setup", ["dnf", "install", "-y", "gawk"]),
    ("rocky9", "dnf", "dnf_repo_setup", ["dnf", "install", "-y", "gawk"]),
    ("amzn2023", "dnf", "dnf_repo_setup", ["dnf", "install", "-y", "gawk"]),
    ("fedora44", "rpm-ostree", "ostree_repo_setup", ["rpm-ostree", "install", "-y", "--apply-live", "gawk"]),
)


class InstallPrerequisiteTests(unittest.TestCase):
    def test_missing_awk_is_installed_before_himmelblau_packages(self):
        for module in (installer, load_worker_module()):
            for target, manager, repo_setup, expected in MANAGERS:
                for channel in ("nightly", "stable", "subscription"):
                    with self.subTest(module=module.__name__, target=target, manager=manager, channel=channel), contextlib.ExitStack() as stack:
                        commands = []
                        stack.enter_context(mock.patch.object(module.shutil, "which", return_value=None))
                        stack.enter_context(mock.patch.object(module, "run", side_effect=lambda argv, *args, **kwargs: commands.append(argv)))
                        stack.enter_context(mock.patch.object(module, repo_setup))
                        stack.enter_context(mock.patch.object(module, "sudo_prefix", return_value=[], create=True))
                        module.install_packages(channel, target, object(), ["himmelblau", "nss-himmelblau"], [], manager=manager)
                        self.assertEqual(commands[0], expected)
                        self.assertIn("nss-himmelblau", commands[1])
                        self.assertNotIn("--from", commands[0])
                        self.assertEqual(len(commands), 2)

    def test_existing_awk_skips_prerequisite_installation_for_every_manager(self):
        for module in (installer, load_worker_module()):
            for manager in ("apt", "zypper", "dnf", "rpm-ostree"):
                with self.subTest(module=module.__name__, manager=manager), mock.patch.object(module.shutil, "which", return_value="/usr/bin/awk"), mock.patch.object(module, "run") as run:
                    module.ensure_package_prerequisites(manager, object())
                    run.assert_not_called()

    def test_prerequisite_failure_stops_before_himmelblau_transaction(self):
        worker = load_worker_module()
        for target, manager, repo_setup, expected in MANAGERS:
            with self.subTest(target=target, manager=manager), mock.patch.object(worker.shutil, "which", return_value=None), mock.patch.object(worker, "run", side_effect=worker.WorkerError("gawk install failed")) as run:
                with self.assertRaisesRegex(worker.WorkerError, "gawk install failed"):
                    worker.install_packages("nightly", target, object(), ["nss-himmelblau"], [], manager=manager)
                self.assertEqual(run.call_count, 1)
                self.assertEqual(run.call_args[0][0], expected)

    def test_self_built_install_also_installs_prerequisite_first(self):
        worker = load_worker_module()
        for target, manager, repo_setup, expected in MANAGERS[:-1]:
            with self.subTest(target=target), mock.patch.object(worker.os.path, "isfile", return_value=True), mock.patch.object(worker.shutil, "which", return_value=None), mock.patch.object(worker, "run") as run:
                worker.execute_step({"kind": "install_self_built"}, "events", {
                    "target": target, "manager": manager, "source_dir": "/tmp/source",
                })
                self.assertEqual(run.call_args_list, [
                    mock.call(expected, "events"),
                    mock.call(["make", "-C", "/tmp/source", "install"], "events"),
                ])

    def test_no_prerequisite_transaction_when_no_packages_are_requested(self):
        worker = load_worker_module()
        with mock.patch.object(worker.shutil, "which", return_value=None), mock.patch.object(worker, "run") as run:
            worker.install_packages("nightly", "tumbleweed", object(), [], [])
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
