
## NAME

aad-tool - Azure Entra ID (AAD) management utility for Himmelblau 

## SYNOPSIS

**aad-tool** _&lt;COMMAND&gt;_ [OPTIONS] 

## DESCRIPTION

The `aad-tool` utility is part of the Himmelblau project, designed to manage and interact with Azure Entra ID through various commands. It allows you to test authentication, manage caches, and check the status of services related to the `himmelblaud` resolver. 

## SYNOPSIS

**aad-tool _&lt;COMMAND&gt;_** 

## DESCRIPTION

Himmelblau Management Utility 

### Commands:

* application 

  Manage Entra ID application registrations, including creation, listing, and extension schema configuration 


* auth-test 

  Test authentication of a user via the himmelblaud resolver "pam" channel. This does not test that your pam configuration is correct - only that himmelblaud is correctly processing and validating authentications 


* cache-clear 

  Clear or invalidate the himmelblaud resolver cache 


* cache-invalidate 

  (Deprecated) Previously used to mark cache entries as stale for immediate refresh. Now behaves identically to `cache-clear` and will be removed in a future release 


* configure-pam 

  Configure PAM to use pam_himmelblau 


* cred 

  Manage confidential client credentials for authenticating to Entra ID 


* enumerate 

  Enumerate all users and groups in Entra ID that have `rfc2307` attributes, and cache their values locally. This addresses the issue where UID/GID mappings are needed before authentication can succeed, but are normally only retrievable after login 


* user 

  Manage Entra ID user accounts, including POSIX attribute assignment and UID mapping 


* group 

  Manage Entra ID groups, including POSIX attribute assignment and GID mapping 


* idmap 

  Manage the static idmapping cache used to map Entra ID accounts to static UID/GID values. This is useful for migrations from on-prem AD to Entra ID, where existing UID/GID mappings need to be preserved 


* status 

  Check that the himmelblaud daemon is online and able to connect correctly to the himmelblaud server 


* version 

  Show the version of this tool 


* help 

  Print this message or the help of the given subcommand(s) 

## OPTIONS

* **-h**, **--help** 

  Print help 

## SUBCOMMAND

**aad-tool _application add-schema-extensions _[_OPTIONS_] _--client-id &lt;CLIENT_ID&gt; --schema-app-object-id &lt;SCHEMA_APP_OBJECT_ID&gt;_** 

### DESCRIPTION

Adds a standard set of POSIX-related schema extensions to an existing Entra ID application. 

This command registers directory extension attributes (e.g., `uidNumber`, `gidNumber`, `unixHomeDirectory`, `loginShell`, `gecos`) on the application specified by `--schema-app-object-id`. These extensions will be usable on user and/or group objects, as appropriate. 

The application specified by `--schema-app-object-id` must already exist in the tenant, and must be identified by its Object ID (not the Client ID). This value is labeled as "Object ID" in the Entra Admin Center and corresponds to the `id` field in Graph API responses. 

You must also supply a separate `--client-id` that grants `Application.ReadWrite.All` permissions to perform the extension registration. 

If the `--name` parameter is omitted, the command authenticates as the currently logged-in user via the Himmelblau SSO broker. If the `--name` parameter is provided, the command attempts to authenticate as the specified Entra ID user. In this case, the command must be run as `root` to impersonate another user. 

This command must be run from a device that has already been joined to Entra ID. 

### OPTIONS

**-d**, **--debug** **-D**, **--name** &lt;ACCOUNT_ID&gt; **--client-id** &lt;CLIENT_ID&gt; **--schema-app-object-id** &lt;SCHEMA_APP_OBJECT_ID&gt; **-h**, **--help** 

Print help (see a summary with '-h') 

## SUBCOMMAND

**aad-tool _application create _[_OPTIONS_] _--client-id &lt;CLIENT_ID&gt; --display-name &lt;DISPLAY_NAME&gt;_** 

### DESCRIPTION

Creates a new Entra ID application registration in the current tenant. 

This command performs a delegated Microsoft Graph API request using an access token acquired via the specified client application (`--client-id`), which must have `Application.ReadWrite.All` permissions in the tenant. 

The new application will be created with the provided `--display-name`. 

You may specify one or more `--redirect-uri` options to configure redirect URIs for the application (used for public client authentication). If no redirect URIs are provided, the application will not include any by default. 

Use the `--user-read-write` and/or `--group-read-write` flags to grant the application additional Microsoft Graph API permissions at registration time, including `User.ReadWrite.All` and `Group.ReadWrite.All`. 

NOTE: If you grant these permissions, it is strongly recommended that you restrict access to the application to specific administrators or groups: 

1. In the Microsoft Entra admin portal, go to Entra???ID -> Enterprise applications and find your app's entry. 2. Under Properties, set "Assignment required?" to Yes. 3. Go to Users and groups, click Add, and assign only the specific users or groups you want to have access. 

If the `--name` parameter is omitted, the command authenticates as the currently logged-in user via the Himmelblau SSO broker. If the `--name` parameter is provided, the command attempts to authenticate as the specified Entra ID user. In this case, the command must be run as `root` to impersonate another user. 

This command must be run from a device that has already been joined to Entra ID. 

### OPTIONS

**-d**, **--debug** **-D**, **--name** &lt;ACCOUNT_ID&gt; **--client-id** &lt;CLIENT_ID&gt; **--display-name** &lt;DISPLAY_NAME&gt; **--redirect-uri** &lt;URI&gt; **--user-read-write** **--group-read-write** **-h**, **--help** 

Print help (see a summary with '-h') 

## SUBCOMMAND

**aad-tool _application list-schema-extensions _[_OPTIONS_] _--client-id &lt;CLIENT_ID&gt; --schema-app-object-id &lt;SCHEMA_APP_OBJECT_ID&gt;_** 

### DESCRIPTION

Lists the schema extension attributes registered on an Entra ID application. 

This command retrieves the directory extension attributes (e.g., `uidNumber`, `gidNumber`, etc.) that have been added to the application identified by `--schema-app-object-id`. 

The `--schema-app-object-id` parameter must be the Object ID of the application (not the Client ID), as shown in the Entra Admin Center. This value corresponds to the `id` field in Microsoft Graph and is required to query extension properties. 

You must also supply a separate `--client-id` that grants `Application.Read.All` or `Application.ReadWrite.All` permissions in the tenant to perform this query. 

If the `--name` parameter is omitted, the command authenticates as the currently logged-in user via the Himmelblau SSO broker. If the `--name` parameter is provided, the command attempts to authenticate as the specified Entra ID user. In this case, the command must be run as `root` to impersonate another user. 

This command must be run from a device that has already been joined to Entra ID. 

### OPTIONS

**-d**, **--debug** **-D**, **--name** &lt;ACCOUNT_ID&gt; **--client-id** &lt;CLIENT_ID&gt; **--schema-app-object-id** &lt;SCHEMA_APP_OBJECT_ID&gt; **-h**, **--help** 

Print help (see a summary with '-h') 

## SUBCOMMAND

**aad-tool _application list _[_OPTIONS_] _--client-id &lt;CLIENT_ID&gt;_** 

### DESCRIPTION

Lists Entra ID application registrations in the current tenant. 

This command performs a delegated Microsoft Graph API request using an access token acquired via the specified client application (`--client-id`), which must have `Application.Read.All` permissions in the tenant. 

If the `--name` parameter is omitted, the command authenticates as the currently logged-in user via the Himmelblau SSO broker. If the `--name` parameter is provided, the command attempts to authenticate as the specified Entra ID user. In this case, the command must be run as `root` to impersonate another user. 

This command must be run from a device that has already been joined to Entra ID. 

### OPTIONS

**-d**, **--debug** **-D**, **--name** &lt;ACCOUNT_ID&gt; **--client-id** &lt;CLIENT_ID&gt; **-h**, **--help** 

Print help (see a summary with '-h') 

## SUBCOMMAND

**aad-tool _auth-test _[_OPTIONS_] _--name &lt;ACCOUNT_ID&gt;_** 

### DESCRIPTION

Test authentication of a user via the himmelblaud resolver "pam" channel. This does not test that your pam configuration is correct - only that himmelblaud is correctly processing and validating authentications 

### OPTIONS

**-d**, **--debug** **-D**, **--name** &lt;ACCOUNT_ID&gt; 


#### -h**, **--help 

  Print help 

## SUBCOMMAND

**aad-tool _cache-clear _[_OPTIONS_]** 

### DESCRIPTION

Clear or invalidate the himmelblaud resolver cache. 

By default, this marks all cached user and group entries as stale, forcing them to refresh immediately when next used. 

Specify **--enumerate**, **--idmap**, **--nss**, or **--mapped** to clear these individual caches as well. Omit all these to clear them all. 

Use `--full` to completely purge the user and group cache entries and unjoin the host from Entra ID. This is irreversible. 

### OPTIONS

**-d**, **--debug** **--enumerate** 

Only clear the enumerated users/groups cache **--idmap** 

Only clear the idmap cache (alias for **--enumerate**) **--nss** 

Only clear the nss cache **--mapped** 

Only clear the mapped name cache **--full** 

Force a full cache wipe and unjoin the host from Entra ID. This is probably not what you want **-h**, **--help** 

Print help (see a summary with '-h') 

## SUBCOMMAND

**aad-tool _cache-invalidate _[_OPTIONS_]** 

### DESCRIPTION

(Deprecated) Previously used to mark cache entries as stale for immediate refresh. Now behaves identically to `cache-clear` and will be removed in a future release 

### OPTIONS

**-d**, **--debug** **--enumerate** **--idmap** **--nss** **--mapped** **--full** 


#### -h**, **--help 

  Print help 

## SUBCOMMAND

**aad-tool _configure-pam _[_OPTIONS_]** 

### DESCRIPTION

Configure PAM to use pam_himmelblau 

### OPTIONS

**-d**, **--debug** **--really** **--auth-file** &lt;AUTH_FILE&gt; **--account-file** &lt;ACCOUNT_FILE&gt; **--session-file** &lt;SESSION_FILE&gt; **--password-file** &lt;PASSWORD_FILE&gt; 


#### -h**, **--help 

  Print help 

## SUBCOMMAND

**aad-tool _cred cert _[_OPTIONS_] _--client-id &lt;CLIENT_ID&gt; --domain &lt;DOMAIN&gt; --valid-days &lt;VALID_DAYS&gt; --cert-out &lt;CERT_OUT&gt;_** 

### DESCRIPTION

Generate an RS256 HSM-backed key pair with a self-signed certificate for confidential client authentication. 

To set this up: 

1. In the Entra ID portal, navigate to Azure Active Directory -> App registrations, then open (or create) your application. 

2. Under Manage > Certificates & secrets, go to the Certificates tab. 

3. Click Upload certificate and select the PEM file generated by this command. 

4. Azure will store this cert for authenticating via public key. 

The private key never leaves your TPM (or SoftHSM). 

When this cred needs renewed in the future, simple run this command again to replace the expired certificate. 

Example: aad-tool cred cert **--client-id** &lt;CLIENT_ID&gt; **--valid-days** 365 **--cert-out** _/tmp/my-cert.crt_ 

### OPTIONS

**-d**, **--debug** **--client-id** &lt;CLIENT_ID&gt; 

The Azure AD application (client) ID this certificate is associated with **--domain** &lt;DOMAIN&gt; 

The tenant domain this certificate is associated with **--valid-days** &lt;VALID_DAYS&gt; 

Number of days the self-signed certificate will be valid **--cert-out** &lt;CERT_OUT&gt; 

Path to write the generated PEM certificate file. This is the file you will upload to Entra ID **-h**, **--help** 

Print help (see a summary with '-h') 

## SUBCOMMAND

**aad-tool _cred delete _[_OPTIONS_] _--domain &lt;DOMAIN&gt;_** 

### DESCRIPTION

Delete confidential client credentials (secret, certificate, or both) 

This deletes stored confidential client credentials from Himmelblau's encrypted cache. If neither `--secret` nor `--cert` is specified, both will be deleted. 

Example: aad-tool cred delete **--domain** &lt;DOMAIN&gt; aad-tool cred delete **--domain** &lt;DOMAIN&gt; **--secret** aad-tool cred delete **--domain** &lt;DOMAIN&gt; **--cert** 

### OPTIONS

**-d**, **--debug** **--domain** &lt;DOMAIN&gt; 

The tenant domain whose creds will be deleted **--secret** 

Delete only the client secret (not the certificate) **--cert** 

Delete only the client certificate (not the secret) **-h**, **--help** 

Print help (see a summary with '-h') 

## SUBCOMMAND

**aad-tool _cred list _[_OPTIONS_] _--domain &lt;DOMAIN&gt;_** 

### DESCRIPTION

List the presence of confidential client credentials 

This checks Himmelblau's encrypted cache to see whether a client secret and/or client certificate exists for the given domain. 

Example: aad-tool cred list **--domain** &lt;DOMAIN&gt; 

### OPTIONS

**-d**, **--debug** **--domain** &lt;DOMAIN&gt; **-h**, **--help** 

Print help (see a summary with '-h') 

## SUBCOMMAND

**aad-tool _cred secret _[_OPTIONS_] _--client-id &lt;CLIENT_ID&gt; --domain &lt;DOMAIN&gt; --secret &lt;SECRET&gt;_** 

### DESCRIPTION

Store a client secret for confidential client authentication. 

To set this up: 

1. In the Entra ID portal, navigate to Azure Active Directory -> App registrations, then open (or create) your application. 

2. Under Manage > Certificates & secrets, go to the Client secrets tab. 

3. Click New client secret, choose an expiry, and click Add. 

4. Copy the Value (not Secret ID) immediately. You won't be able to see it again. 

5. Use that value with this command to store it in Himmelblau???s encrypted cache. 

When this cred needs renewed in the future, simple run this command again to replace the expired secret. 

Example: aad-tool cred secret **--client-id** &lt;CLIENT_ID&gt; **--secret** &lt;SECRET_VALUE&gt; 

### OPTIONS

**-d**, **--debug** **--client-id** &lt;CLIENT_ID&gt; 

The Azure AD application (client) ID this secret is associated with **--domain** &lt;DOMAIN&gt; 

The tenant domain this secret is associated with **--secret** &lt;SECRET&gt; 

The client secret value copied from the Entra ID portal **-h**, **--help** 

Print help (see a summary with '-h') 

## SUBCOMMAND

**aad-tool _enumerate _[_OPTIONS_]** 

### DESCRIPTION

Enumerate all users and groups in Entra ID that have `rfc2307` attributes, and cache their values locally. This addresses the issue where UID/GID mappings are needed before authentication can succeed, but are normally only retrievable after login. 

The `--client-id` parameter is optional and must refer to a registered Entra ID application with `User.Read.All` and `Group.Read.All` permissions. 

The `--name` parameter specifies the Entra ID user on whose behalf the token is requested, enabling delegated access through the specified client application. 

This command can only be executed from an Entra Id enrolled host. 

### OPTIONS

**-d**, **--debug** **-D**, **--name** &lt;ACCOUNT_ID&gt; **--client-id** &lt;CLIENT_ID&gt; **-h**, **--help** 

Print help (see a summary with '-h') 

## SUBCOMMAND

**aad-tool _group set-posix-attrs _[_OPTIONS_] _--schema-client-id &lt;SCHEMA_CLIENT_ID&gt; --group-id &lt;GROUP_ID&gt; --gid &lt;GID&gt;_** 

### DESCRIPTION

Sets POSIX-related attributes on a specified Entra ID group object. 

This command updates the `gidNumber` attribute on the Entra ID group identified by `--group-id`, which must be a valid Object ID. 

You must also provide the `--schema-client-id`, which identifies the application where the extension properties were registered. This value must be the Client ID of the application used for schema registration. The application associated with `--schema-client-id` must supply `Group.ReadWrite.All` permissions in the tenant. 

If the `--name` parameter is omitted, the command authenticates as the currently logged-in user via the Himmelblau SSO broker. If the `--name` parameter is provided, the command must be run as `root` to impersonate another user. 

This command must be run from a device that has already been joined to Entra ID. 

### OPTIONS

**-d**, **--debug** **-D**, **--name** &lt;ACCOUNT_ID&gt; **--schema-client-id** &lt;SCHEMA_CLIENT_ID&gt; **--group-id** &lt;GROUP_ID&gt; **--gid** &lt;GID&gt; **-h**, **--help** 

Print help (see a summary with '-h') 

## SUBCOMMAND

**aad-tool _idmap group-add _[_OPTIONS_] _--name &lt;ACCOUNT_ID&gt; --gid &lt;GID&gt;_** 

### DESCRIPTION

Add a static group mapping to the idmap cache. This maps an Entra ID group (by name) to a fixed GID. This can be used to maintain group identity and membership compatibility after moving to Entra ID 

### OPTIONS

**-d**, **--debug** **-D**, **--name** &lt;ACCOUNT_ID&gt; **-g**, **--gid** &lt;GID&gt; 


#### -h**, **--help 

  Print help 

## SUBCOMMAND

**aad-tool _idmap user-add _[_OPTIONS_] _--name &lt;ACCOUNT_ID&gt; --uid &lt;UID&gt; --gid &lt;GID&gt;_** 

### DESCRIPTION

Add a static user mapping to the idmap cache. This maps an Entra ID user (by UPN or SAM-compatible name) to a fixed UID and primary group GID 

### OPTIONS

**-d**, **--debug** **-D**, **--name** &lt;ACCOUNT_ID&gt; **-u**, **--uid** &lt;UID&gt; **-g**, **--gid** &lt;GID&gt; 


#### -h**, **--help 

  Print help 

## SUBCOMMAND

**aad-tool _status _[_OPTIONS_]** 

### DESCRIPTION

Check that the himmelblaud daemon is online and able to connect correctly to the himmelblaud server 

### OPTIONS

**-d**, **--debug** 


#### -h**, **--help 

  Print help 

## SUBCOMMAND

**aad-tool _user set-posix-attrs _[_OPTIONS_] _--schema-client-id &lt;SCHEMA_CLIENT_ID&gt; --user-id &lt;USER_ID&gt;_** 

### DESCRIPTION

Sets POSIX-related attributes on a specified Entra ID user object. 

This command updates POSIX attributes (`uidNumber`, `gidNumber`, `unixHomeDirectory`, `loginShell`, and `gecos`) on the Entra ID user identified by `--user-id`, which must be a valid Object ID or UPN. 

You must also provide the `--schema-client-id`, which identifies the application where the extension properties were registered. This value must be the Client ID of the application used for schema registration. The application associated with `--schema-client-id` must supply `User.ReadWrite.All` permissions in the tenant. 

If the `--name` parameter is omitted, the command authenticates as the currently logged-in user via the Himmelblau SSO broker. If the `--name` parameter is provided, the command must be run as `root` to impersonate another user. 

This command must be run from a device that has already been joined to Entra ID. 

### OPTIONS

**-d**, **--debug** **-D**, **--name** &lt;ACCOUNT_ID&gt; **--schema-client-id** &lt;SCHEMA_CLIENT_ID&gt; **--user-id** &lt;USER_ID&gt; **--uid** &lt;UID&gt; **--gid** &lt;GID&gt; **--home** &lt;HOME&gt; **--shell** &lt;SHELL&gt; **--gecos** &lt;GECOS&gt; **-h**, **--help** 

Print help (see a summary with '-h') 

## SEE ALSO

**himmelblau.conf**(5), **himmelblaud**(8), **himmelblaud-tasks**(8) 

## AUTHOR

David Mulder &lt;dmulder@himmelblau-idm.org&gt;, &lt;dmulder@samba.org&gt; 