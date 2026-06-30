⚠️ **Warning: This document is a work in progress. Cloud Kerberos Trust for Linux is also a work in progress and may require additional configuration and bug fixes in Himmelblau, cifs-utils, or the Linux CIFS kernel client.**

## Cloud Kerberos Trust Setup for Entra ID Joined Linux Devices

This guide outlines the steps to configure Cloud Kerberos Trust between Microsoft Entra ID (formerly Azure AD) and an on-premises Active Directory (AD) for Linux devices joined to Entra ID using Himmelblau.

The main supported test case today is obtaining an Entra Kerberos cloud TGT at login and using that TGT to request a `cifs` service ticket for Azure Files.

### Prerequisites

- Microsoft Entra ID is configured.
- On-premises Active Directory is operational.
- Entra ID Connect is installed and synchronizing users from on-premises AD to Entra ID.
- Linux client is joined to Entra ID via Himmelblau.
- Kerberos utilities (e.g., `mit-krb5`) are installed on the Linux client.
- `cifs-utils` 7.6 or newer is installed when mounting Azure Files with Kerberos.
- `keyutils` is installed and the system has the standard CIFS request-key configuration for `cifs.spnego` upcalls.
- Network connectivity between the Linux client and on-prem AD domain controllers.
- Administrative privileges in both on-prem AD and Entra ID.
- For Azure Files, the storage account is configured for Microsoft Entra Kerberos authentication for hybrid identities. Follow Microsoft's Azure Files guide first: [Enable Microsoft Entra Kerberos authentication for hybrid identities on Azure Files](https://learn.microsoft.com/en-us/azure/storage/files/storage-files-identity-auth-hybrid-identities-enable).
- The user has the required Azure RBAC role assignment on the storage account or file share. For example, assign the appropriate Storage File Data SMB role for the access level the user needs.

### Step 1: Configure Microsoft Entra Kerberos Server Object

1. Install the AzureADHybridAuthenticationManagement PowerShell module on a Windows machine with AD access:

```powershell
Install-Module -Name AzureADHybridAuthenticationManagement -AllowClobber
```

2. Create the Kerberos server object:

```powershell
# Specify the on-premises Active Directory domain. A new Azure AD
# Kerberos Server object will be created in this Active Directory domain.
$domain = $env:USERDNSDOMAIN

# Enter a UPN of an Azure Active Directory global administrator
$userPrincipalName = "administrator@contoso.onmicrosoft.com"

# Enter a domain administrator username and password.
$domainCred = Get-Credential

# Create the new Azure AD Kerberos Server object in Active Directory
# and then publish it to Azure Active Directory.
# Open an interactive sign-in prompt with given username to access the Azure AD.
Set-AzureADKerberosServer -Domain $domain -UserPrincipalName $userPrincipalName -DomainCredential $domainCred
```

3. Verify that the Kerberos server RODC object was created successfully.

```powershell
Get-AzureADKerberosServer -Domain $domain -UserPrincipalName $userPrincipalName
```

### Step 2: Confirm Linux Client Readiness

Himmelblau configures the Kerberos client configuration automatically. Do not manually edit `/etc/krb5.conf` for the Entra Kerberos cloud TGT path unless you are debugging a specific local override.

Before testing, verify that time synchronization between the Linux client and the domain controllers is accurate.

### Step 3: Validate the Cloud TGT on Linux Devices

After configuring the policies, validate that Linux devices can obtain an Entra Kerberos cloud TGT:

1. **Log Out and Log In**:

   On the Linux device, log out and then log back in to initiate the authentication process.

2. **Check Kerberos Tickets**:

   Open a terminal and run:

```bash
klist
```

   You should see a valid Kerberos ticket similar to:

```text
Ticket cache: KEYRING:persistent:<uid>
Default principal: user@KERBEROS.MICROSOFTONLINE.COM

Valid starting       Expires              Service principal
...                  ...                  krbtgt/KERBEROS.MICROSOFTONLINE.COM@KERBEROS.MICROSOFTONLINE.COM
```

   Himmelblau currently issues Kerberos tickets into a keyring credential cache. File-based credential caches such as `FILE:/tmp/krb5cc_<uid>` are not supported by Himmelblau.

### Step 4: Mount Azure Files with Kerberos

After the user has logged in and `klist` shows the cloud TGT, mount the Azure Files share with `sec=krb5`, the user's numeric UID as `cruid`, and the same numeric UID as `username`:

```bash
uid="$(id -u)"
sudo mount.cifs //<storage-account>.file.core.windows.net/<share> <mount-point> \
    -o sec=krb5,cruid="$uid",username="$uid"
```

For example:

```bash
uid="$(id -u)"
sudo mkdir -p /mnt/azfiles
sudo mount.cifs //contosostorage.file.core.windows.net/files /mnt/azfiles \
    -o sec=krb5,cruid="$uid",username="$uid"
```

Important details:

- Use the storage account FQDN exactly as `<storage-account>.file.core.windows.net`.
- Run the mount after the Himmelblau user has logged in and has a cloud TGT in the keyring cache.
- Keep `cruid` set to the UID of the logged-in Himmelblau user. This tells the CIFS upcall which user's credential cache should be used.
- Do not switch Himmelblau to a file credential cache to work around CIFS failures. Himmelblau does not currently support issuing file-based ccaches.
- If your distribution provides `cifs-utils` older than 7.6, upgrade it before testing Azure Files Kerberos mounts.

### Troubleshooting Azure Files Mounts

If the mount fails with `mount error(126): Required key not available`, inspect the CIFS logs:

```bash
sudo journalctl -xe | grep -i cifs
```

A failure like this means `cifs.upcall` did not find a usable TGT for the requested user:

```text
cifs.upcall: main: valid TGT is not present in credential cache
cifs.upcall: Unable to obtain service ticket
CIFS: VFS: \\<storage-account>.file.core.windows.net failed to create a new SMB session with Kerberos: -126
```

Check the following before assuming the storage account is misconfigured:

- `klist` for the logged-in user shows `KEYRING:` as the ticket cache type and contains `krbtgt/KERBEROS.MICROSOFTONLINE.COM@KERBEROS.MICROSOFTONLINE.COM`.
- The mount command uses `cruid="$(id -u)"` for the logged-in user who owns the TGT.
- The mount command includes `username="$(id -u)"`.
- The installed `cifs-utils` package is version 7.6 or newer.
- `keyutils` is installed and `/etc/request-key.conf` or `/etc/request-key.d/` contains a `cifs.spnego` rule that invokes `cifs.upcall`.
- The Azure Files share works from a Windows client with the same identity.
- The user has the required Storage File Data SMB role assignment on the storage account or share.

If these checks pass and `cifs.upcall` still reports that a valid TGT is not present, collect the `klist` output, the exact `mount.cifs` command, the `cifs-utils` version, and the relevant `journalctl` CIFS lines when reporting the issue.
