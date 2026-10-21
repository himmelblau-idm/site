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

## How the systemd credential settings work

On systems with systemd support for encrypted credentials, the **packaged** `himmelblaud.service` uses these settings:

```ini
[Service]
LoadCredentialEncrypted=hsm-pin:/var/lib/himmelblaud/hsm-pin-nopcr.enc
Environment=HIMMELBLAU_HSM_PIN_PATH=%d/hsm-pin
```

- `LoadCredentialEncrypted=NAME:SOURCE` tells systemd to decrypt an encrypted credential from `SOURCE` and provide the resulting plaintext as a protected, service-scoped file named `NAME`. The source is *persistent encrypted state*; the destination under `/run/credentials/himmelblaud.service/` is *temporary* and managed by systemd.
- `%d` is systemd's credential-directory specifier. It expands for this service to its credentials directory; `HIMMELBLAU_HSM_PIN_PATH=%d/hsm-pin` therefore directs Himmelblau to **read** the decrypted PIN from that directory, rather than generate one there.
- `LoadCredential=` loads an unencrypted credential file or supplied value. It is a separate directive, not a synonym for `LoadCredentialEncrypted=`. Using plaintext credential loading is generally **not appropriate** for Himmelblau's persistent HSM PIN; prefer the packaged encrypted credential path.
- **Empty** `LoadCredential=` and `LoadCredentialEncrypted=` directives in a drop-in *clear previously configured entries* of their respective lists. They do not mean "leave the package defaults unchanged." If the loaded credential is canceled but `HIMMELBLAU_HSM_PIN_PATH` still points to `%d/hsm-pin`, the daemon can fail when it tries to create a PIN in a directory it does not own.

Himmelblau's separate `himmelblau-hsm-pin-init.service` creates or migrates the encrypted *source* credential before the daemon starts. The `hsm-pin-nopcr.enc` name reflects its no-PCR-lock policy: when available, the initialization script uses a machine host key and TPM storage root key (`host+tpm2`, without PCR binding), otherwise it may fall back to systemd's automatic key selection. **No PCR binding does not mean no TPM binding.** The script also attempts to provision a missing storage root key on TPM-capable systems; its behavior depends on the systemd version, TPM availability, and installed TPM tools.

### When to modify these settings

In normal installations, **do not override these settings**. The package selects the right mode for the detected systemd capabilities. Inspect them when debugging a custom unit, a local systemd drop-in, an upgrade from older credential handling, or an intentionally customized service.

If you must provide a different encrypted credential source, supply a matching `LoadCredentialEncrypted=hsm-pin:/path/to/credential.enc` and leave `HIMMELBLAU_HSM_PIN_PATH=%d/hsm-pin` pointing to the systemd-provided runtime file. Changing the destination name requires changing both entries consistently. Ensure the source is readable to the systemd service manager, and securely provision encrypted content using `systemd-creds`; never paste the PIN into the unit or an environment variable. Be aware that an absolute path under `/var/lib/private` may reflect systemd DynamicUser state redirection; do not hard-code permissions or aliases based on appearances alone.

Avoid using `systemctl edit` merely to "disable" credential settings during troubleshooting. Inspect the *effective* unit with `systemctl cat` and check the actual result after `daemon-reload`.

## Recovery after a TPM/vTPM replacement or loss

A reset, replacement, clone, restore or migration of a physical TPM or Hyper-V vTPM can make an existing TPM-bound encrypted credential impossible to decrypt. A loss of the host's systemd credential secret can have a similar effect. First confirm that this is an actual **decryption/key-binding** failure, not a systemd override like the one above.

!!! danger "Rekeying can invalidate enrollment and stored credentials"
    The HSM PIN protects machine key material. Replacing it does **not** magically decrypt or migrate state protected by the previous PIN or TPM. Existing machine enrollment, keys, cached tokens and offline logins may stop working. On a host that must retain its identity, recover the **original** TPM/vTPM and host secrets (for example from a compatible complete VM backup), or use a supported re-enrollment path. Do not reset a production host solely because a credential file looks old.

### Diagnose without destroying state

1. Keep local console/admin access and make a backup or VM snapshot **with access controls that protect the encrypted files and database**. Avoid copying secrets into issue comments or shell history.
2. Check the full init/daemon journals and `systemctl cat`, as in steps 1–3. Look specifically for a systemd credential decryption error, a changed TPM/SRK, or a changed host key. A message about writing to `/run/credentials` is *not*, by itself, proof of TPM loss.
3. Inspect the presence of the TPM and persistent key handle without exporting keys:

   ```sh
   ls -l /dev/tpm0 /dev/tpmrm0 2>/dev/null || true
   command -v tpm2_getcap && sudo tpm2_getcap handles-persistent
   sudo journalctl -b -u himmelblau-hsm-pin-init.service -u himmelblaud.service --no-pager -n 200
   ```

   `tpm2_getcap` comes from your distribution's TPM2 tooling; the initialization script checks for SRK handle `0x81000001`. An absent handle alone does not prove a lost credential, and manually clearing or overwriting it can make things worse.
4. Restore the original TPM/vTPM or complete machine snapshot where feasible, and retest. Do not delete the PIN file merely to make the initialization condition run.

### Deliberately provision a **new** HSM PIN (only if re-enrollment is acceptable)

If the original TPM-backed material is **irretrievably lost**, you have an independently verified administrative recovery path, and you explicitly accept losing access to existing protected state, you can ask the initializer to generate a new encrypted credential. This is a **last-resort rekey**, not a cache-clearing procedure or a guaranteed complete re-enrollment.

The initializer's version-4.0.6 condition checks for the absence of `/var/lib/private/himmelblaud/hsm-pin-nopcr.enc`. Its script also recognizes older state named `hsm-pin` and `hsm-pin.enc`. Do not accidentally promote an obsolete legacy file or mix state from different VMs.

```sh
# Only after securing a state backup and accepting potential enrollment loss:
sudo systemctl stop himmelblaud.service
sudo systemctl stop himmelblau-hsm-pin-init.service
sudo install -d -m 0700 /root/himmelblau-hsm-recovery
# Preserve the encrypted credential rather than deleting it.
sudo test ! -e /var/lib/private/himmelblaud/hsm-pin-nopcr.enc || \
  sudo mv /var/lib/private/himmelblaud/hsm-pin-nopcr.enc \
    /root/himmelblau-hsm-recovery/hsm-pin-nopcr.enc
```

**Before starting the initializer**, inspect whether either legacy source exists:

```sh
sudo ls -ld /var/lib/private/himmelblaud/
sudo ls -l /var/lib/private/himmelblaud/hsm-pin \
  /var/lib/private/himmelblaud/hsm-pin.enc 2>/dev/null || true
```

If a legacy source exists, **do not continue automatically**: the script may migrate that old PIN instead of generating a new one. Determine which generation of state it belongs to, back it up securely and plan the recovery accordingly. Once no old PIN sources remain in the initializer's input paths, start the initializer and inspect its journal:

```sh
sudo systemctl reset-failed himmelblau-hsm-pin-init.service himmelblaud.service
sudo systemctl start himmelblau-hsm-pin-init.service
sudo journalctl -b -u himmelblau-hsm-pin-init.service --no-pager -n 100
sudo systemctl start himmelblaud.service
sudo journalctl -b -u himmelblaud.service --no-pager -n 100
```

A new credential can restore the *credential-loading step* while other persistent TPM/HSM material remains unusable. Do not immediately wipe databases or recursively alter file ownership in response. If enrollment or protected key loading still fails, follow the project's supported unregister/re-enroll procedure appropriate to that release and preserve diagnostics. Expect re-registration and potentially users re-establishing Hello PINs/offline capabilities; check access for every affected user.

For the 4.0.6 implementation details, see the [HSM PIN initialization script](https://github.com/himmelblau-idm/himmelblau/blob/4.0.6/src/daemon/scripts/himmelblau-init-hsm-pin) and [service unit generator](https://github.com/himmelblau-idm/himmelblau/blob/4.0.6/scripts/gen_servicefiles.py).

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
