#!/usr/bin/env python3
"""Run the Himmelblau installer manually across supported container targets."""

from __future__ import annotations

import argparse
import dataclasses
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import sys
from typing import Iterable, Sequence


ROOT = pathlib.Path(__file__).resolve().parents[2]
INSTALL_PATH = ROOT / "install"
CONFIG_TEXT = "[global]\ndomain = himmelblau-idm.org\n"


@dataclasses.dataclass(frozen=True)
class Target:
    name: str
    label: str
    image: str
    manager: str
    rolling: bool = False


TARGETS: tuple[Target, ...] = (
    Target("sle15sp6", "SUSE Linux Enterprise 15 SP6 / openSUSE Leap 15.6", "opensuse/leap:15.6", "zypper"),
    Target("sle15sp7", "SUSE Linux Enterprise 15 SP7", "registry.suse.com/bci/bci-base:15.7", "zypper"),
    Target("sle16", "SUSE Linux Enterprise 16 / openSUSE Leap 16", "opensuse/leap:16.0", "zypper"),
    Target("tumbleweed", "openSUSE Tumbleweed", "opensuse/tumbleweed:latest", "zypper", rolling=True),
    Target("rocky8", "RHEL/Rocky/Alma/Oracle Linux 8", "rockylinux:8", "dnf"),
    Target("rocky9", "RHEL/Rocky/Alma/Oracle Linux 9", "rockylinux:9", "dnf"),
    Target("rocky10", "RHEL/Rocky/Alma/Oracle Linux 10", "rockylinux:10", "dnf"),
    Target("fedora42", "Fedora 42", "fedora:42", "dnf"),
    Target("fedora43", "Fedora 43", "fedora:43", "dnf"),
    Target("fedora44", "Fedora 44", "fedora:44", "dnf"),
    Target("rawhide", "Fedora Rawhide", "fedora:rawhide", "dnf"),
    Target("amzn2023", "Amazon Linux 2023", "amazonlinux:2023", "dnf"),
    Target("debian12", "Debian 12", "debian:12", "apt"),
    Target("debian13", "Debian 13", "debian:13", "apt"),
    Target("ubuntu22.04", "Ubuntu 22.04 / Linux Mint 21.3", "ubuntu:22.04", "apt"),
    Target("ubuntu24.04", "Ubuntu 24.04 / Linux Mint 22", "ubuntu:24.04", "apt"),
    Target("ubuntu25.10", "Ubuntu 25.10", "ubuntu:25.10", "apt"),
    Target("ubuntu26.04", "Ubuntu 26.04 / Linux Mint 23", "ubuntu:26.04", "apt"),
)


class CommandRunner:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def run(self, argv: Sequence[str], check: bool = True) -> subprocess.CompletedProcess[str]:
        print("$ " + shell_join(argv), flush=True)
        if self.dry_run:
            return subprocess.CompletedProcess(list(argv), 0, "", "")
        proc = subprocess.run(list(argv), text=True, check=False)
        if check and proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, list(argv))
        return proc


class SetupError(Exception):
    pass


def shell_join(argv: Sequence[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in argv)


def target_map(targets: Iterable[Target] = TARGETS) -> dict[str, Target]:
    return {target.name: target for target in targets}


def parse_image_override(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("image overrides must use TARGET=IMAGE")
    target, image = value.split("=", 1)
    target = target.strip()
    image = image.strip()
    if not target or not image:
        raise argparse.ArgumentTypeError("image overrides must use TARGET=IMAGE")
    return target, image


def apply_image_overrides(targets: Sequence[Target], overrides: Sequence[tuple[str, str]]) -> tuple[Target, ...]:
    known = target_map(targets)
    unknown = sorted({target for target, _ in overrides if target not in known})
    if unknown:
        raise ValueError("Unknown target in --image override: " + ", ".join(unknown))
    images = dict(overrides)
    return tuple(dataclasses.replace(target, image=images[target.name]) if target.name in images else target for target in targets)


def select_targets(targets: Sequence[Target], requested: str | None) -> tuple[Target, ...]:
    if requested is None:
        return tuple(targets)
    known = target_map(targets)
    if requested not in known:
        raise ValueError(f"Unknown target: {requested}")
    return (known[requested],)


def list_targets(targets: Sequence[Target]) -> None:
    width = max(len(target.name) for target in targets)
    for target in targets:
        print(f"{target.name:<{width}}  {target.image:<38}  {target.label}")


def container_name(target: Target) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", target.name)
    return f"himmelblau-install-{safe}-{os.getpid()}"


def podman_run_prefix(name: str, pull_policy: str) -> list[str]:
    return ["podman", "run", "--pull=" + pull_policy, "--detach", "--name", name]


def start_container(target: Target, name: str, runner: CommandRunner, no_systemd: bool, pull_policy: str) -> None:
    if not no_systemd:
        proc = runner.run(podman_run_prefix(name, pull_policy) + [
            "--systemd=always",
            "--privileged",
            "--tmpfs",
            "/run",
            "--tmpfs",
            "/run/lock",
            "--tmpfs",
            "/tmp",
            target.image,
            "/sbin/init",
        ], check=False)
        if proc.returncode == 0 and runner.run(["podman", "exec", name, "true"], check=False).returncode == 0:
            return
        print("systemd container startup failed; retrying without systemd.", flush=True)
        runner.run(["podman", "rm", "-f", name], check=False)

    runner.run(podman_run_prefix(name, pull_policy) + [target.image, "sleep", "infinity"])


def prereq_command(target: Target | str) -> str:
    manager = target.manager if isinstance(target, Target) else target
    rolling = isinstance(target, Target) and target.rolling
    if manager == "apt":
        return (
            "apt-get update && "
            "DEBIAN_FRONTEND=noninteractive apt-get install -y "
            "python3 ca-certificates curl gnupg sudo && "
            "(python3 -c 'import curses' || "
            "DEBIAN_FRONTEND=noninteractive apt-get install -y python3-curses || "
            "DEBIAN_FRONTEND=noninteractive apt-get install -y python3-full || "
            "DEBIAN_FRONTEND=noninteractive apt-get install -y python3.13-full || "
            "DEBIAN_FRONTEND=noninteractive apt-get install -y python3.12-full || "
            "DEBIAN_FRONTEND=noninteractive apt-get install -y python3.10-full) && "
            "python3 -c 'import curses'"
        )
    if manager == "zypper":
        if rolling:
            return (
                "zypper --non-interactive refresh && "
                "zypper --non-interactive dup -y --no-recommends && "
                "zypper --non-interactive install -y --no-recommends python3 ca-certificates curl gpg2 sudo && "
                "(zypper --non-interactive install -y --no-recommends python3-curses || "
                "zypper --non-interactive install -y --no-recommends python36-curses || "
                "zypper --non-interactive install -y --no-recommends 'python3*-curses')"
            )
        return (
            "zypper --non-interactive refresh || true; "
            "zypper --non-interactive install -y python3 ca-certificates curl gpg2 sudo || "
            "zypper --non-interactive install -y python3 ca-certificates curl gpg sudo; "
            "zypper --non-interactive install -y python3-curses || "
            "zypper --non-interactive install -y python36-curses || "
            "zypper --non-interactive install -y 'python3*-curses'"
        )
    return (
        "(dnf install -y python3 ca-certificates gnupg2 sudo || "
        "dnf install -y python3 ca-certificates gnupg sudo) && "
        "(python3 -c 'import curses' || "
        "dnf install -y python3-curses || "
        "dnf install -y python3-libs || "
        "dnf install -y python3.13-libs || "
        "dnf install -y python3.12-libs || "
        "dnf install -y python3.11-libs || "
        "dnf install -y python3.9-libs) && "
        "python3 -c 'import curses'"
    )


def write_config_command() -> str:
    quoted_lines = " ".join(shlex.quote(line) for line in CONFIG_TEXT.rstrip("\n").splitlines())
    return (
        "mkdir -p /etc/himmelblau && "
        f"printf '%s\\n' {quoted_lines} > /etc/himmelblau/himmelblau.conf && "
        "chmod 0644 /etc/himmelblau/himmelblau.conf && "
        "chmod +x /tmp/himmelblau-install"
    )


def setup_container(target: Target, name: str, runner: CommandRunner) -> None:
    try:
        runner.run(["podman", "cp", str(INSTALL_PATH), f"{name}:/tmp/himmelblau-install"])
        runner.run(["podman", "exec", name, "/bin/sh", "-lc", prereq_command(target)])
        runner.run(["podman", "exec", name, "/bin/sh", "-lc", write_config_command()])
    except subprocess.CalledProcessError as err:
        raise SetupError(
            "Container setup failed for %s while running: %s\n"
            "Rerun with --keep to inspect the failed container." % (target.name, shell_join(err.cmd))
        ) from err


def terminal_env() -> str:
    term = os.environ.get("TERM", "")
    return term if term and term != "dumb" else "xterm-256color"


def run_installer(name: str, runner: CommandRunner) -> None:
    runner.run(["podman", "exec", "-it", "--env", f"TERM={terminal_env()}", name, "/bin/sh", "-lc", "/tmp/himmelblau-install"], check=False)


def open_shell(name: str, runner: CommandRunner) -> None:
    runner.run(["podman", "exec", "-it", "--env", f"TERM={terminal_env()}", name, "/bin/sh"], check=False)


def prompt_after_run(name: str, runner: CommandRunner, keep: bool) -> bool:
    while True:
        try:
            answer = input("Next: [Enter] remove+continue, s=shell, k=keep+continue, q=quit: ").strip().lower()
        except EOFError:
            answer = ""
        if answer == "s":
            open_shell(name, runner)
            continue
        if answer == "k":
            print(f"Keeping container: {name}")
            return True
        if answer == "q":
            if keep:
                print(f"Keeping container: {name}")
            else:
                runner.run(["podman", "rm", "-f", name], check=False)
            return False
        if keep:
            print(f"Keeping container: {name}")
        else:
            runner.run(["podman", "rm", "-f", name], check=False)
        return True


def run_target(target: Target, runner: CommandRunner, keep: bool, no_systemd: bool, pull_policy: str) -> bool:
    name = container_name(target)
    print("")
    print(f"==> {target.name}: {target.label}")
    print(f"    Image: {target.image}")
    try:
        start_container(target, name, runner, no_systemd, pull_policy)
        setup_container(target, name, runner)
        print(f"Config preloaded in {name}: /etc/himmelblau/himmelblau.conf")
        run_installer(name, runner)
        if runner.dry_run:
            if not keep:
                runner.run(["podman", "rm", "-f", name], check=False)
            return True
        return prompt_after_run(name, runner, keep)
    except Exception:
        if not keep:
            runner.run(["podman", "rm", "-f", name], check=False)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Interactively run the local Himmelblau installer in Podman containers for each supported target.",
    )
    parser.add_argument("--list", action="store_true", help="list targets and images, then exit")
    parser.add_argument("--target", metavar="TARGET", help="run only one installer target")
    parser.add_argument("--dry-run", action="store_true", help="print commands without running Podman")
    parser.add_argument("--keep", action="store_true", help="keep containers after each run")
    parser.add_argument("--no-systemd", action="store_true", help="start containers with sleep infinity instead of trying /sbin/init")
    parser.add_argument(
        "--pull-policy",
        choices=("always", "missing", "never"),
        default="always",
        help="Podman image pull policy for container starts; default: always",
    )
    parser.add_argument(
        "--image",
        action="append",
        default=[],
        type=parse_image_override,
        metavar="TARGET=IMAGE",
        help="override the container image for a target; may be passed more than once",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        targets = apply_image_overrides(TARGETS, args.image)
        selected = select_targets(targets, args.target)
    except ValueError as err:
        print("error: " + str(err), file=sys.stderr)
        return 2

    if args.list:
        list_targets(selected if args.target else targets)
        return 0

    if not INSTALL_PATH.exists():
        print(f"error: installer not found: {INSTALL_PATH}", file=sys.stderr)
        return 1
    if not args.dry_run and not shutil.which("podman"):
        print("error: podman was not found in PATH", file=sys.stderr)
        return 1

    runner = CommandRunner(dry_run=args.dry_run)
    try:
        for target in selected:
            if not run_target(target, runner, args.keep, args.no_systemd, args.pull_policy):
                break
    except SetupError as err:
        print("error: " + str(err), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
