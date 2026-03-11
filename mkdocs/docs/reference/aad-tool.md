## NAME

aad-tool - Azure Entra ID (AAD) management utility for Himmelblau

## SYNOPSIS

```text
aad-tool <COMMAND> [OPTIONS]
```

## DESCRIPTION

The `aad-tool` utility is part of the Himmelblau project, designed to
manage and interact with Azure Entra ID through various commands. It
allows you to test authentication, manage caches, and check the status
of services related to the `himmelblaud` resolver.

### Commands:

application  
Manage Entra ID application registrations, including creation, listing,
and extension schema configuration

auth-test  
Test authentication of a user via the himmelblaud resolver "pam"
channel. This does not test that your pam configuration is correct -
only that himmelblaud is correctly processing and validating
authentications

cache-clear  
Clear or invalidate the himmelblaud resolver cache

cache-invalidate  
(Deprecated) Previously used to mark cache entries as stale for
immediate refresh. Now behaves identically to `cache-clear` and will
be removed in a future release

configure-pam  
Configure PAM to use pam_himmelblau

cred  
Manage confidential client credentials for authenticating to Entra ID

enumerate  
Enumerate all users and groups in Entra ID that have `rfc2307`
attributes, and cache their values locally. This addresses the issue
where UID/GID mappings are needed before authentication can succeed, but
are normally only retrievable after login

user  
Manage Entra ID user accounts, including POSIX attribute assignment and
UID mapping

group  
Manage Entra ID groups, including POSIX attribute assignment and GID
mapping

idmap  
Manage the static idmapping cache used to map Entra ID accounts to
static UID/GID values. This is useful for migrations from on-prem AD to
Entra ID, where existing UID/GID mappings need to be preserved

offline-breakglass  
Activate or deactivate Himmelblau's offline breakglass mode

status  
Check that the himmelblaud daemon is online and able to connect
correctly to the himmelblaud server

tpm  
Check whether Himmelblau is utilizing the TPM

version  
Show the version of this tool

help  
Print this message or the help of the given subcommand(s)

## OPTIONS

**-h**, **--help**  
Print help

## aad-tool application add-schema-extensions

```text
aad-tool application add-schema-extensions [OPTIONS] --client-id <CLIENT_ID> --schema-app-object-id <SCHEMA_APP_OBJECT_ID>
```

### DESCRIPTION

Adds a standard set of POSIX-related schema extensions to an existing
Entra ID application.

This command registers directory extension attributes (e.g.,
`uidNumber`, `gidNumber`, `unixHomeDirectory`, `loginShell`,
`gecos`) on the application specified by `--schema-app-object-id`.
These extensions will be usable on user and/or group objects, as
appropriate.

The application specified by `--schema-app-object-id` must already
exist in the tenant, and must be identified by its Object ID (not the
Client ID). This value is labeled as "Object ID" in the Entra Admin
Center and corresponds to the `id` field in Graph API responses.

You must also supply a separate `--client-id` that grants
`Application.ReadWrite.All` permissions to perform the extension
registration.

If the `--name` parameter is omitted, the command authenticates as the
currently logged-in user via the Himmelblau SSO broker. If the
`--name` parameter is provided, the command attempts to authenticate
as the specified Entra ID user. In this case, the command must be run as
`root` to impersonate another user.

This command must be run from a device that has already been joined to
Entra ID.

### OPTIONS

**-d**, **--debug**

**-D**, **--name** <ACCOUNT_ID>

**--client-id** <CLIENT_ID>

**--schema-app-object-id** <SCHEMA_APP_OBJECT_ID>

**-h**, **--help**

> Print help (see a summary with '-h')

## aad-tool application create

```text
aad-tool application create [OPTIONS] --client-id <CLIENT_ID> --display-name <DISPLAY_NAME>
```

### DESCRIPTION

Creates a new Entra ID application registration in the current tenant.

This command performs a delegated Microsoft Graph API request using an
access token acquired via the specified client application
(`--client-id`), which must have `Application.ReadWrite.All`
permissions in the tenant.

The new application will be created with the provided
`--display-name`.

You may specify one or more `--redirect-uri` options to configure
redirect URIs for the application (used for public client
authentication). If no redirect URIs are provided, the application will
not include any by default.

Use the `--user-read-write` and/or `--group-read-write` flags to
grant the application additional Microsoft Graph API permissions at
registration time, including `User.ReadWrite.All` and
`Group.ReadWrite.All`.

NOTE: If you grant these permissions, it is strongly recommended that
you restrict access to the application to specific administrators or
groups:

1. In the Microsoft Entra admin portal, go to Entra???ID -> Enterprise
applications and find your app's entry. 2. Under Properties, set
"Assignment required?" to Yes. 3. Go to Users and groups, click Add, and
assign only the specific users or groups you want to have access.

If the `--name` parameter is omitted, the command authenticates as the
currently logged-in user via the Himmelblau SSO broker. If the
`--name` parameter is provided, the command attempts to authenticate
as the specified Entra ID user. In this case, the command must be run as
`root` to impersonate another user.

This command must be run from a device that has already been joined to
Entra ID.

### OPTIONS

**-d**, **--debug**

**-D**, **--name** <ACCOUNT_ID>

**--client-id** <CLIENT_ID>

**--display-name** <DISPLAY_NAME>

**--redirect-uri** <URI>

**--user-read-write**

**--group-read-write**

**-h**, **--help**

> Print help (see a summary with '-h')

## aad-tool application list-schema-extensions

```text
aad-tool application list-schema-extensions [OPTIONS] --client-id <CLIENT_ID> --schema-app-object-id <SCHEMA_APP_OBJECT_ID>
```

### DESCRIPTION

Lists the schema extension attributes registered on an Entra ID
application.

This command retrieves the directory extension attributes (e.g.,
`uidNumber`, `gidNumber`, etc.) that have been added to the
application identified by `--schema-app-object-id`.

The `--schema-app-object-id` parameter must be the Object ID of the
application (not the Client ID), as shown in the Entra Admin Center.
This value corresponds to the `id` field in Microsoft Graph and is
required to query extension properties.

You must also supply a separate `--client-id` that grants
`Application.Read.All` or `Application.ReadWrite.All` permissions in
the tenant to perform this query.

If the `--name` parameter is omitted, the command authenticates as the
currently logged-in user via the Himmelblau SSO broker. If the
`--name` parameter is provided, the command attempts to authenticate
as the specified Entra ID user. In this case, the command must be run as
`root` to impersonate another user.

This command must be run from a device that has already been joined to
Entra ID.

### OPTIONS

**-d**, **--debug**

**-D**, **--name** <ACCOUNT_ID>

**--client-id** <CLIENT_ID>

**--schema-app-object-id** <SCHEMA_APP_OBJECT_ID>

**-h**, **--help**

> Print help (see a summary with '-h')

## aad-tool application list

```text
aad-tool application list [OPTIONS] --client-id <CLIENT_ID>
```

### DESCRIPTION

Lists Entra ID application registrations in the current tenant.

This command performs a delegated Microsoft Graph API request using an
access token acquired via the specified client application
(`--client-id`), which must have `Application.Read.All` permissions
in the tenant.

If the `--name` parameter is omitted, the command authenticates as the
currently logged-in user via the Himmelblau SSO broker. If the
`--name` parameter is provided, the command attempts to authenticate
as the specified Entra ID user. In this case, the command must be run as
`root` to impersonate another user.

This command must be run from a device that has already been joined to
Entra ID.

### OPTIONS

**-d**, **--debug**

**-D**, **--name** <ACCOUNT_ID>

**--client-id** <CLIENT_ID>

**-h**, **--help**

> Print help (see a summary with '-h')

## aad-tool auth-test

```text
aad-tool auth-test [OPTIONS] --name <ACCOUNT_ID>
```

### DESCRIPTION

Test authentication of a user via the himmelblaud resolver "pam"
channel. This does not test that your pam configuration is correct -
only that himmelblaud is correctly processing and validating
authentications

### OPTIONS

**-d**, **--debug**

**-D**, **--name** <ACCOUNT_ID>

**-h**, **--help**  
Print help

## aad-tool cache-clear

```text
aad-tool cache-clear [OPTIONS]
```

### DESCRIPTION

Clear or invalidate the himmelblaud resolver cache.

By default, this marks all cached user and group entries as stale,
forcing them to refresh immediately when next used.

Specify **--nss** or **--mapped** to clear these individual caches as
well. Omit both these to clear them all.

Use `--full` to completely purge the user and group cache entries and
unjoin the host from Entra ID. This is irreversible.

### OPTIONS

**-d**, **--debug**

**--nss**

> Only clear the nss cache

**--mapped**

> Only clear the mapped name cache

**--full**

> Force a full cache wipe and unjoin the host from Entra ID. This is
> probably not what you want

**-h**, **--help**

> Print help (see a summary with '-h')

## aad-tool cache-invalidate

```text
aad-tool cache-invalidate [OPTIONS]
```

### DESCRIPTION

(Deprecated) Previously used to mark cache entries as stale for
immediate refresh. Now behaves identically to `cache-clear` and will
be removed in a future release

### OPTIONS

**-d**, **--debug**

**--nss**

**--mapped**

**--full**

**-h**, **--help**  
Print help

## aad-tool configure-pam

```text
aad-tool configure-pam [OPTIONS]
```

### DESCRIPTION

Configure PAM to use pam_himmelblau

### OPTIONS

**-d**, **--debug**

**--really**

**--auth-file** <AUTH_FILE>

**--account-file** <ACCOUNT_FILE>

**--session-file** <SESSION_FILE>

**--password-file** <PASSWORD_FILE>

**-h**, **--help**  
Print help

## aad-tool cred cert

```text
aad-tool cred cert [OPTIONS] --client-id <CLIENT_ID> --domain <DOMAIN> --valid-days <VALID_DAYS> --cert-out <CERT_OUT>
```

### DESCRIPTION

Generate an RS256 HSM-backed key pair with a self-signed certificate for
confidential client authentication.

To set this up:

1. In the Entra ID portal, navigate to Azure Active Directory -> App
registrations, then open (or create) your application.

2. Under Manage > Certificates & secrets, go to the Certificates tab.

3. Click Upload certificate and select the PEM file generated by this
command.

4. Azure will store this cert for authenticating via public key.

The private key never leaves your TPM (or SoftHSM).

When this cred needs renewed in the future, simple run this command
again to replace the expired certificate.

Example: aad-tool cred cert **--client-id** <CLIENT_ID>
**--valid-days** 365 **--cert-out** */tmp/my-cert.crt*

### OPTIONS

**-d**, **--debug**

**--client-id** <CLIENT_ID>

> The Azure AD application (client) ID this certificate is associated
> with

**--domain** <DOMAIN>

> The tenant domain this certificate is associated with

**--valid-days** <VALID_DAYS>

> Number of days the self-signed certificate will be valid

**--cert-out** <CERT_OUT>

> Path to write the generated PEM certificate file. This is the file you
> will upload to Entra ID

**-h**, **--help**

> Print help (see a summary with '-h')

## aad-tool cred delete

```text
aad-tool cred delete [OPTIONS] --domain <DOMAIN>
```

### DESCRIPTION

Delete confidential client credentials (secret, certificate, or both)

This deletes stored confidential client credentials from Himmelblau's
encrypted cache. If neither `--secret` nor `--cert` is specified,
both will be deleted.

Example: aad-tool cred delete **--domain** <DOMAIN> aad-tool cred
delete **--domain** <DOMAIN> **--secret** aad-tool cred delete
**--domain** <DOMAIN> **--cert**

### OPTIONS

**-d**, **--debug**

**--domain** <DOMAIN>

> The tenant domain whose creds will be deleted

**--secret**

> Delete only the client secret (not the certificate)

**--cert**

> Delete only the client certificate (not the secret)

**-h**, **--help**

> Print help (see a summary with '-h')

## aad-tool cred list

```text
aad-tool cred list [OPTIONS] --domain <DOMAIN>
```

### DESCRIPTION

List the presence of confidential client credentials

This checks Himmelblau's encrypted cache to see whether a client secret
and/or client certificate exists for the given domain.

Example: aad-tool cred list **--domain** <DOMAIN>

### OPTIONS

**-d**, **--debug**

**--domain** <DOMAIN>

**-h**, **--help**

> Print help (see a summary with '-h')

## aad-tool cred secret

```text
aad-tool cred secret [OPTIONS] --client-id <CLIENT_ID> --domain <DOMAIN> --secret <SECRET>
```

### DESCRIPTION

Store a client secret for confidential client authentication.

To set this up:

1. In the Entra ID portal, navigate to Azure Active Directory -> App
registrations, then open (or create) your application.

2. Under Manage > Certificates & secrets, go to the Client secrets
tab.

3. Click New client secret, choose an expiry, and click Add.

4. Copy the Value (not Secret ID) immediately. You won't be able to see
it again.

5. Use that value with this command to store it in Himmelblau's
encrypted cache.

When this cred needs renewed in the future, simple run this command
again to replace the expired secret.

Example: aad-tool cred secret **--client-id** <CLIENT_ID> **--secret**
<SECRET_VALUE>

### OPTIONS

**-d**, **--debug**

**--client-id** <CLIENT_ID>

> The Azure AD application (client) ID this secret is associated with

**--domain** <DOMAIN>

> The tenant domain this secret is associated with

**--secret** <SECRET>

> The client secret value copied from the Entra ID portal

**-h**, **--help**

> Print help (see a summary with '-h')

## aad-tool enumerate

```text
aad-tool enumerate [OPTIONS]
```

### DESCRIPTION

Enumerate all users and groups in Entra ID that have `rfc2307`
attributes, and cache their values locally. This addresses the issue
where UID/GID mappings are needed before authentication can succeed, but
are normally only retrievable after login.

The `--client-id` parameter is optional and must refer to a registered
Entra ID application with `User.Read.All` and `Group.Read.All`
permissions.

The `--name` parameter specifies the Entra ID user on whose behalf the
token is requested, enabling delegated access through the specified
client application.

This command can only be executed from an Entra Id enrolled host.

### OPTIONS

**-d**, **--debug**

**-D**, **--name** <ACCOUNT_ID>

**--client-id** <CLIENT_ID>

**-h**, **--help**

> Print help (see a summary with '-h')

## aad-tool group set-posix-attrs

```text
aad-tool group set-posix-attrs [OPTIONS] --schema-client-id <SCHEMA_CLIENT_ID> --group-id <GROUP_ID> --gid <GID>
```

### DESCRIPTION

Sets POSIX-related attributes on a specified Entra ID group object.

This command updates the `gidNumber` attribute on the Entra ID group
identified by `--group-id`, which must be a valid Object ID.

You must also provide the `--schema-client-id`, which identifies the
application where the extension properties were registered. This value
must be the Client ID of the application used for schema registration.
The application associated with `--schema-client-id` must supply
`Group.ReadWrite.All` permissions in the tenant.

If the `--name` parameter is omitted, the command authenticates as the
currently logged-in user via the Himmelblau SSO broker. If the
`--name` parameter is provided, the command must be run as `root` to
impersonate another user.

This command must be run from a device that has already been joined to
Entra ID.

### OPTIONS

**-d**, **--debug**

**-D**, **--name** <ACCOUNT_ID>

**--schema-client-id** <SCHEMA_CLIENT_ID>

**--group-id** <GROUP_ID>

**--gid** <GID>

**-h**, **--help**

> Print help (see a summary with '-h')

## aad-tool idmap clear

```text
aad-tool idmap clear [OPTIONS]
```

### DESCRIPTION

Clear the contents of the idmap static cache

### OPTIONS

**-d**, **--debug**

**-h**, **--help**  
Print help

## aad-tool idmap group-add

```text
aad-tool idmap group-add [OPTIONS] --object_id <OBJECT_ID> --gid <GID>
```

### DESCRIPTION

Add a static group mapping to the idmap cache. This maps an Entra ID
group (by Object Id GUID) to a fixed GID. This can be used to maintain
group identity and membership compatibility after moving to Entra ID

### OPTIONS

**-d**, **--debug**

**-D**, **--object_id** <OBJECT_ID>

**-g**, **--gid** <GID>

**-h**, **--help**  
Print help

## aad-tool idmap user-add

```text
aad-tool idmap user-add [OPTIONS] --name <ACCOUNT_ID> --uid <UID> --gid <GID>
```

### DESCRIPTION

Add a static user mapping to the idmap cache. This maps an Entra ID user
(by UPN or SAM-compatible name) to a fixed UID and primary group GID

### OPTIONS

**-d**, **--debug**

**-D**, **--name** <ACCOUNT_ID>

**-u**, **--uid** <UID>

**-g**, **--gid** <GID>

**-h**, **--help**  
Print help

## aad-tool offline-breakglass

```text
aad-tool offline-breakglass [OPTIONS]
```

### DESCRIPTION

Activate or deactivate Himmelblau's offline breakglass mode.

This command enables temporary offline password authentication when
Azure Entra ID is unreachable. When invoked, Himmelblau enters a
controlled "breakglass" state, allowing cached Entra ID user passwords
to be used for login until the TTL expires.

Breakglass mode can only be activated if it was previously enabled in
`/etc/himmelblau/himmelblau.conf` under the `[offline_breakglass]`
section. If the feature was disabled, calling this command will have no
effect, and no password verifiers will have been cached.

Once activated, Himmelblau will: \* Allow cached Entra ID users to log
in using their known password. \* Automatically exit breakglass mode
after the TTL expires or once Entra ID connectivity has been restored.

Use `--ttl` to override the configured duration for this session. The
TTL value accepts a time unit suffix (`m`, `h`, or `d`) and
defaults to the value defined in `himmelblau.conf` if omitted.

To manually exit breakglass mode before TTL expiry, run: aad-tool
offline-breakglass **--ttl** 0

### OPTIONS

**-d**, **--debug**

**--ttl** <TTL>

**-h**, **--help**

> Print help (see a summary with '-h')

## EXAMPLES

```text
# Activate breakglass mode for 2 hours aad-tool offline-breakglass
```
--ttl 2h

```text
# Force disable breakglass mode immediately aad-tool offline-breakglass
```
--ttl 0

```text
# Use the configured default TTL (from himmelblau.conf) aad-tool
```
offline-breakglass

Notes: - If `[offline_breakglass] enabled = false` in
himmelblau.conf, this command will do nothing. - Himmelblau will not
cache Entra ID password hashes unless offline breakglass has been
explicitly enabled in advance. - This feature should only be used for
emergency access during verified outages.

## aad-tool status

```text
aad-tool status [OPTIONS]
```

### DESCRIPTION

Check that the himmelblaud daemon is online and able to connect
correctly to the himmelblaud server

### OPTIONS

**-d**, **--debug**

**-h**, **--help**  
Print help

## aad-tool tpm

```text
aad-tool tpm [OPTIONS]
```

### DESCRIPTION

Check whether Himmelblau is utilizing the TPM

### OPTIONS

**-d**, **--debug**

**-h**, **--help**  
Print help

## aad-tool user set-posix-attrs

```text
aad-tool user set-posix-attrs [OPTIONS] --schema-client-id <SCHEMA_CLIENT_ID> --user-id <USER_ID>
```

### DESCRIPTION

Sets POSIX-related attributes on a specified Entra ID user object.

This command updates POSIX attributes (`uidNumber`, `gidNumber`,
`unixHomeDirectory`, `loginShell`, and `gecos`) on the Entra ID
user identified by `--user-id`, which must be a valid Object ID or
UPN.

You must also provide the `--schema-client-id`, which identifies the
application where the extension properties were registered. This value
must be the Client ID of the application used for schema registration.
The application associated with `--schema-client-id` must supply
`User.ReadWrite.All` permissions in the tenant.

If the `--name` parameter is omitted, the command authenticates as the
currently logged-in user via the Himmelblau SSO broker. If the
`--name` parameter is provided, the command must be run as `root` to
impersonate another user.

This command must be run from a device that has already been joined to
Entra ID.

### OPTIONS

**-d**, **--debug**

**-D**, **--name** <ACCOUNT_ID>

**--schema-client-id** <SCHEMA_CLIENT_ID>

**--user-id** <USER_ID>

**--uid** <UID>

**--gid** <GID>

**--home** <HOME>

**--shell** <SHELL>

**--gecos** <GECOS>

**-h**, **--help**

> Print help (see a summary with '-h')

## SEE ALSO

[himmelblau.conf(5)](himmelblau-conf.md), [himmelblaud(8)](himmelblaud.md), [himmelblaud-tasks(8)](himmelblaud_tasks.md)

## AUTHOR

David Mulder <dmulder@himmelblau-idm.org>, <dmulder@samba.org>
