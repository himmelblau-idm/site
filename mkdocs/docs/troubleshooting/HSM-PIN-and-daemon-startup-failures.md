# Troubleshooting Himmelblau daemon startup and HSM PIN credentials

If `himmelblaud.service` fails to start after an upgrade, diagnose the service and systemd credentials **before** clearing caches, removing TPM keys, or reinstalling packages. This guide covers failures such as:

```text
Failed to create HSM PIN into /run/credentials/himmelblaud.service/hsm-pin
err: Os { code: 13, kind: PermissionDenied, message: "Permission denied" }
```

This failure was reported on Ubuntu 24.04 with Himmelblau 4.0.6 running in a Hyper-V VM in [issue #1900](https://github.com/himmelblau-idm/himmelblau/issues/1900). The confirmed cause *in that case* was a local systemd override that disabled credential loading. Other failures with a similar message can have different causes.

!!! warning "Keep another way to administer the host"
    Keep a working local administrator login, console, or out-of-band recovery path available while investigating authentication failures. Do not delete encrypted PINs, cached databases, enrolled keys, or TPM state as an initial troubleshooting step. Such actions can invalidate enrollment and offline authentication state.

## 1. Capture the complete failure

Inspect both the PIN initialization service and the daemon, without truncating the error after the `|>` separator:

```sh
sudo systemctl status himmelblau-hsm-pin-init.service himmelblaud.service --no-pager -l
sudo journalctl -b -u himmelblau-hsm-pin-init.service -u himmelblaud.service --no-pager -o cat -n 200
systemctl cat himmelblau-hsm-pin-init.service himmelblaud.service
systemctl --version
```

Note the **first underlying error**, whether the PIN initializer ran or was skipped, and any drop-ins printed by `systemctl cat`. The displayed `/run/credentials/...` path is the per-service runtime credential directory managed by systemd, **not** a normal persistent location for an application to create a replacement secret.

Do not paste encrypted credential contents, decrypted PINs, tokens, or secrets into a public issue. Redact identifying information in unit overrides and journals.

## 2. Check whether a systemd override disabled credential loading

In the reported 4.0.6 failure, `systemctl cat himmelblaud.service` showed a local file:

```text
/etc/systemd/system/himmelblaud.service.d/override.conf
```

containing:

```ini
[Service]
LoadCredential=
LoadCredentialEncrypted=
```

**These are not harmless blank settings.** Empty systemd `LoadCredential=` and `LoadCredentialEncrypted=` assignments reset the service's credential lists. The packaged Himmelblau unit expects an encrypted HSM PIN credential to be loaded by systemd, and sets `HIMMELBLAU_HSM_PIN_PATH=%d/hsm-pin` to identify the runtime file. If a drop-in cancels loading while the environment variable remains, the daemon may attempt to create a PIN in systemd's protected credentials directory and fail with `PermissionDenied`.

Inspect all relevant unit and drop-in settings:

```sh
systemctl cat himmelblaud.service
systemctl show himmelblaud.service -p FragmentPath -p DropInPaths -p LoadCredential -p LoadCredentialEncrypted -p Environment
```

If the local override contains those **empty reset assignments**, back it up somewhere **outside** the systemd drop-in directory, then edit just the override to remove the offending lines. Preserve other local settings. Do not edit the packaged unit or remove the `HIMMELBLAU_HSM_PIN_PATH` environment variable.

```sh
sudo cp -a /etc/systemd/system/himmelblaud.service.d/override.conf /root/himmelblaud-override.conf.backup
sudoedit /etc/systemd/system/himmelblaud.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl reset-failed himmelblaud.service
sudo systemctl restart himmelblaud.service
sudo systemctl status himmelblaud.service --no-pager -l
sudo journalctl -b -u himmelblaud.service --no-pager -o cat -n 100
```

Only use this repair if your unit actually has the conflicting override; do not remove credential directives blindly. The reporter confirmed that removing these two reset lines restored Entra sign-in. This is a **configuration repair**, not evidence that every HSM PIN startup error is documentation-only.

## 3. Interpret the PIN initializer's result

You may see:

```text
himmelblau-hsm-pin-init.service ... skipped because of an unmet condition check
(ConditionPathExists=!/var/lib/private/himmelblaud/hsm-pin-nopcr.enc)
```

The initializer is configured to run only when its encrypted PIN file does **not** already exist. A skip with that condition is therefore not necessarily an error; it does not by itself prove the credential was loaded into the daemon.

The packaged unit can refer to `/var/lib/himmelblaud/hsm-pin-nopcr.enc` while systemd's private state storage appears on disk under `/var/lib/private/himmelblaud/`. Diagnose the *installed unit* and any overrides rather than assuming a missing or mismatched path from one log line.

For virtual machines, note whether a vTPM is present, and whether the VM has been cloned, restored, or had its vTPM replaced. Such changes can affect TPM-protected material, but should not be assumed to be the root cause without evidence.

If restoring the packaged credential loading does not resolve startup, preserve the full error and inspect the initializer logs and installed unit definitions again. An encrypted-credential decryption failure and a later key-loading failure require different investigation.

## 4. Important: `aad-tool cache-clear` requires a running daemon

**`aad-tool cache-clear` (including `--full`) only works when `himmelblaud` is running and its control socket is available.** The command requests the daemon to perform the operation; it is not an offline rescue command.

For example:

```text
sudo aad-tool cache-clear --full
Error -> Os { code: 2, kind: NotFound, message: "No such file or directory" }
Is himmelblaud running? Cache was NOT cleared.
```

When the daemon cannot start, this message is a **secondary symptom**, not evidence that cache corruption caused the startup failure. Diagnose and restore `himmelblaud.service` first. A successful `cache-clear --full` is also destructive: it unjoins the host and clears caches. Do not use it merely as a generic startup repair.

Similarly, an `apt purge` or package reinstall does not necessarily remove retained systemd overrides and persistent application state. Reinstalling is not a substitute for inspecting `systemctl cat`.

## 5. If login works but a user systemd manager fails

After restoring the daemon, you may separately encounter:

```text
systemd[PID]: Failed to allocate manager object: Permission denied
```

That message alone does **not** establish a Himmelblau cache problem or a collision between a local account and an Entra account. First gather the failing process metadata (substitute the observed PID from the current boot):

```sh
sudo journalctl -b _PID=<PID> --no-pager -o verbose
```

Inside the affected Entra login session, **without sudo**, run:

```sh
id
getent passwd "$(id -u)"
printf 'HOME=%s\nXDG_RUNTIME_DIR=%s\n' "$HOME" "$XDG_RUNTIME_DIR"
getent passwd '<local-login-name>' '<full-Entra-UPN>'
```

Then replace `<UID>` with the session's numeric UID:

```sh
sudo journalctl -b -u user@<UID>.service -u user-runtime-dir@<UID>.service --no-pager -n 100
```

Redact personal identifiers but preserve UID/GID values, path structure and whether the NSS identities differ. `home_attr` and `home_alias` concern home naming; they do not establish which identity systemd is using. Avoid changing UID mappings or recursively adjusting home directory permissions until the failing check is identified.

## 6. When reporting an unresolved startup failure

Include the Himmelblau version and Linux distribution, whether the failure followed an upgrade, the full journal error from step 1, and the **installed** unit and drop-ins from `systemctl cat`. Note whether the machine has a TPM/vTPM and whether it was cloned or restored. State which non-destructive recovery steps were attempted.

For the original resolved credential-loading problem and the separately investigated user-manager error, see [Himmelblau issue #1900](https://github.com/himmelblau-idm/himmelblau/issues/1900).
