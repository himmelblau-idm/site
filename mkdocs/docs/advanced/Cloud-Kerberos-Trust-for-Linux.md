⚠️ **Warning: This document is a work in progress. Cloud Kerberos Trust for Linux is also a work in progress and likely requires additional configuration and bug fixes to Himmelblau.**

## Cloud Kerberos Trust Setup for Entra ID Joined Linux Devices

This guide outlines the steps to configure Cloud Kerberos Trust between Microsoft Entra ID (formerly Azure AD) and an on-premises Active Directory (AD) for Linux devices joined to Entra ID using Himmelblau.

### Prerequisites

- Microsoft Entra ID is configured.
- On-premises Active Directory is operational.
- Entra Id Connect is installed and synchronizing users from on-premises AD to Entra ID.
- Linux client is joined to Entra ID via Himmelblau.
- Kerberos utilities (e.g., `mit-krb5`) are installed on the Linux client.
- Network connectivity between the Linux client and on-prem AD domain controllers.
- Administrative privileges in both on-prem AD and Entra ID.

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

### Step 2: Configure Kerberos on the Linux Client

1. Edit the Kerberos configuration file (`/etc/krb5.conf`):

```ini
   [libdefaults]
       default_realm = EXAMPLE.COM
       dns_lookup_realm = false
       dns_lookup_kdc = false

   [realms]
       EXAMPLE.COM = {
           kdc = dc1.example.com
           kdc = dc2.example.com
           admin_server = dc1.example.com
       }

   [domain_realm]
       .example.com = EXAMPLE.COM
       example.com = EXAMPLE.COM
```

   - Replace `EXAMPLE.COM` with your AD domain in uppercase.
   - Replace `example.com` with your AD domain in lowercase.
   - Replace `dc1.example.com` and `dc2.example.com` with FQDNs of your domain controllers.

2. Verify that time synchronization between the Linux client and the domain controllers is accurate.

### Step 3: Validate the Configuration on Linux Devices

After configuring the policies, validate that Linux devices can obtain Kerberos tickets:

1. **Log Out and Log In**:

   On the Linux device, log out and then log back in to initiate the authentication process.

2. **Check Kerberos Tickets**:

   Open a terminal and run:

```bash
klist
```


   You should see a valid Kerberos ticket listed, indicating successful authentication.

