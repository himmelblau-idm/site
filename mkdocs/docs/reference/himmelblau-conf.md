
## NAME

himmelblau.conf - Configuration file for Himmelblau, enabling Azure Entra ID authentication on Linux. 

## SYNOPSIS

**/etc/himmelblau/himmelblau.conf** 

## HOW CONFIGURATION CHANGES ARE APPLIED

Changes to the configuration file **/etc/himmelblau/himmelblau.conf** only take effect after restarting the Himmelblau daemons. This includes the **himmelblaud** daemon, which handles authentication, and the **himmelblaud-tasks** daemon, which processes related tasks. 


#### Restarting the Daemons 

  To apply changes, restart the Himmelblau services using the following systemd commands: 
##### EXAMPLES

    
sudo systemctl restart himmelblaud 

    sudo systemctl restart himmelblaud-tasks 

## DESCRIPTION

The **himmelblau.conf** file is the primary configuration file for the Himmelblau authentication module. It defines global and optional settings required for Azure Entra ID-based authentication and device management. 

## FILE FORMAT

The file consists of sections headed by a name enclosed in square brackets. Each section contains parameters and their values in the format: 

    parameter = value Lines beginning with a '#' are comments and are ignored by the parser. 

## PARAMETERS

### [global]

This section contains settings that apply globally to all operations of Himmelblau. 


#### domains 

  A comma-separated list of primary domains for your Azure Entra ID tenants. This parameter is **REQUIRED** for successful authentication. If this option is not specified, no users will be permitted to authenticate. The first user to authenticate to each domain will become the owner of the device object in the directory. Specify ONLY the primary domain for each tenant. Specifying multiple custom domains which belong to a single tenant will cause an idmap range overlap and the himmelblaud daemon will NOT start. If multiple domains are specified, you **MUST** define an **idmap_range** for each domain to avoid conflicts in user and group ID mappings. Overlapping ID ranges will cause the idmapper to throw a critical error and stop the daemon. This safeguard ensures that two users are not mistakenly mapped to the same UID. 
##### EXAMPLES
domains = example.com,example2.com [example.com] idmap_range = 5000000-5999999 [example2.com] idmap_range = 6000000-6999999 


#### debug 

  A boolean option that enables debug-level logging. When set to **true,** debug messages are output to the system journal. 
##### EXAMPLES
debug = true 


#### pam_allow_groups 

  A comma-separated list of Entra Id Users and Groups permitted to access the system. Users should be specified by UPN. Groups MUST be specified using their Object ID GUID. Group names may not be used because these names are not guaranteed to be unique in Entra Id. 
##### EXAMPLES
pam_allow_groups = f3c9a7e4-7d5a-47e8-832f-3d2d92abcd12,5ba4ef1d-e454-4f43-ba7c-6fe6f1601915,admin@himmelblau-idm.org 


#### id_attr_map 

  Specify whether to map uid/gid based on the object name, the object uuid, or based on the rfc2307 schema extension attributes synchronized from an on-prem Active Directory instance. Mapping by name or by rfc2307 is recommeneded. 
##### EXAMPLES
id_attr_map = &lt;name|uuid|rfc2307&gt; 


#### rfc2307_group_fallback_map 

  Specify whether to map group IDs (GIDs) based on the object name or object UUID when no **gidNumber** attribute is found in an on-prem Active Directory instance synchronized to Azure Entra ID. This option is only applicable if **id_attr_map** is set to **rfc2307.** If **id_attr_map = rfc2307** and a group does not have a **gidNumber** defined in the directory, this setting determines the fallback method for mapping the group ID. If this option is not set, groups without a **gidNumber** will not be available to NSS. 
##### EXAMPLES
rfc2307_group_fallback_map = &lt;name|uuid&gt; 


#### odc_provider 

  Specifies the hostname for sending federationProvider requests. 
##### EXAMPLES
odc_provider = odc.officeapps.live.com 


#### enable_hello 

  Enables or disables user enrollment in Windows Hello authentication. If disabled, users will need to provide MFA for each login. 
##### EXAMPLES
enable_hello = false 


#### hello_pin_min_length 

  The minimum length of the PIN for Windows Hello authentication. The value must be between 6 and 32 characters. 
##### EXAMPLES
hello_pin_min_length = 8 


#### hello_pin_retry_count 

  The number of invalid Hello PIN attempts allowed before the user is required to perform MFA. After successful MFA, the user will be prompted to set a new PIN. The value must be a non-negative integer. 
##### EXAMPLES
hello_pin_retry_count = 3 


#### hello_pin_prompt 

  Customizes the prompt text shown when requesting the user’s Linux Hello PIN. If not set, the default prompt is: 

Use the Linux Hello PIN for this device. 
##### EXAMPLES
hello_pin_prompt = Enter your device unlock PIN 


#### entra_id_password_prompt 

  Customizes the prompt text shown when requesting the user’s Entra ID password. If not set, the default prompt is: 

Use the password for your Office 365 or Microsoft online login. 
##### EXAMPLES
entra_id_password_prompt = Enter your Microsoft 365 password 


#### enable_sfa_fallback 

  Determines whether password-only (single-factor) authentication is permitted when MFA is unavailable. Disabled by default. 
##### EXAMPLES
enable_sfa_fallback = true 


#### cn_name_mapping 

  Allows users to enter the short form of their username (e.g., 'dave') instead of the full UPN. 
##### EXAMPLES
cn_name_mapping = true 


#### local_groups 

  A comma-separated list of local groups that every Entra ID user should be a member of. For example, you may wish for all Entra ID users to be a member of the sudo group. WARNING: This setting will not REMOVE group member entries when groups are removed from this list. You must remove them manually. 
##### EXAMPLES
local_groups = sudo,admin 


#### logon_script 

  A script that will execute every time a user logs on. Two environment variables are set: USERNAME, and ACCESS_TOKEN. The ACCESS_TOKEN environment variable is an access token for the MS Graph. The token scope config option sets the comma-separated scopes that should be requested for the ACCESS_TOKEN. ACCESS_TOKEN will be empty during offline logon. The return code of the script determines how authentication proceeds. 0 is success, 1 is a soft failure and authentication will proceed, while 2 is a hard failure causing authentication to fail. The **app_id** option **MUST** be set for each domain to ensure the **logon_token_scopes** option has the correct API permissions. Failing to do so will prevent the **logon_script** from executing. 
##### EXAMPLES
logon_script = /etc/himmelblau/logon.sh 


#### logon_token_scopes 

  A comma-separated list of the scopes to be requested for the ACCESS_TOKEN during logon. These scopes **MUST** correspond to the API permissions assigned to the Entra Id Application specified by the **app_id** domain option. 
##### EXAMPLES
logon_token_scopes = user.read,mail.read 


#### enable_experimental_mfa 

  A boolean option that enables the experimental multi-factor authentication (MFA) flow, which permits Hello authentication. This experimental flow may encounter failures in certain edge cases. If disabled, the system enforces the Device Authorization Grant (DAG) flow for MFA, which is more robust but does not support Hello authentication. By default, this option is enabled. 
##### EXAMPLES
enable_experimental_mfa = true 


#### enable_experimental_passwordless_fido 

  A boolean option that enables the experimental passwordless FIDO flow for Azure Entra ID authentication. When enabled, Himmelblau will attempt to authenticate with Entra ID using a FIDO2 security key without requiring a password. By default, this option is disabled. 
##### EXAMPLES
enable_experimental_passwordless_fido = true 


#### name_mapping_script 

  Specifies the path to an executable script used for mapping custom names to UPN names. The script MUST accept a single argument, which will always be a mapped name. The script MUST print the corresponding UPN (User Principal Name) to stdout. If the script does not recognize the input name, it MUST simply return the input name unchanged. This option is particularly useful in environments where direct UPN-to-CN mappings are impractical or where custom transformations are required. The script must handle the input gracefully and return the correct UPN or the input name if unrecognized. Errors must be handled to avoid authentication failures. 
##### EXAMPLES
name_mapping_script = /path/to/mapping_script.sh Example Script: 

```
#!/bin/bash
# Convert CN to UPN, or return the input name if unrecognized
if [[ "$1" =~ ^[a-zA-Z0-9._-]+$ ]]; then
    echo "$1@example.com"
else
    echo "$1"
fi
```

* **enable_experimental_policy_application** 

  A boolean option that enables the experimental application and enforcement of Intune policies for the authenticated user. By default, this option is disabled. 
##### EXAMPLES
enable_experimental_policy_application = false 


#### enable_experimental_intune_custom_compliance 

  A boolean option that enables support for Linux Intune Custom Compliance policies. This feature is experimental and not yet fully functional. While policy settings should be applied locally, the compliance status is not reliably reported to Intune, and failed policies do not currently block authentication. By default, this option is disabled. This option requires `enable_experimental_policy_application = true`. 
##### EXAMPLES
enable_experimental_intune_custom_compliance = true 


#### authority_host 

  Specifies the hostname for Microsoft authentication. The default value is **login.microsoftonline.com.** 
##### EXAMPLES
authority_host = login.microsoftonline.com 


#### db_path 

  The location of the cache database. This file is used to store cached authentication data and device state. 
##### EXAMPLES
db_path = /var/cache/himmelblau/himmelblau.cache.db 


#### hsm_type 

  Specifies how Himmelblau should handle secure key storage. This option determines whether to use a software-based HSM, a TPM (Trusted Platform Module), or a hybrid approach. The available options are:

* **soft** – Use a software-based HSM that encrypts key material locally on the system.

* **tpm** – Use a hardware TPM exclusively for storing and binding cryptographic keys.

* **tpm_if_possible** – Attempt to use a hardware TPM if available; if not, fall back to the software HSM. If the TPM has previously been used for key storage, the system will not fall back to the software HSM. The default is **soft** his setting is important for protecting sensitive cryptographic keys in a secure environment, reducing the risk of compromise if the system is breached.
##### EXAMPLES
hsm_type = soft 


#### tpm_tcti_name 

  Specifies the TCTI (Trusted Computing Technology Interface) to use when communicating with a Trusted Platform Module (TPM) for secure key operations. This setting is only relevant when **hsm_type** is set to **tpm** or **tpm_if_possible.** Common values include:

* **device:/dev/tpmrm0** – This uses the kernel TPM resource manager device, which is the recommended default for most Linux systems. Other TCTI strings may be required depending on your system’s TPM driver or configuration. This option allows advanced control over how Himmelblau connects to the TPM for performing cryptographic operations. 
##### EXAMPLES
tpm_tcti_name = device:/dev/tpmrm0 


#### hsm_pin_path 

  The location where the HSM (Hardware Security Module) PIN will be stored. This PIN is used to protect sensitive cryptographic operations. 
##### EXAMPLES
hsm_pin_path = /var/lib/himmelblaud/hsm-pin 


#### socket_path 

  The path to the socket file for communication between the pam and nss modules and the Himmelblau daemon. 
##### EXAMPLES
socket_path = /var/run/himmelblaud/socket 


#### task_socket_path 

  The path to the socket file for communication with the task daemon. 
##### EXAMPLES
task_socket_path = /var/run/himmelblaud/task_sock 


#### broker_socket_path 

  The path to the socket file for communication with the broker DBus service. 
##### EXAMPLES
broker_socket_path = /var/run/himmelblaud/broker_sock 


#### home_prefix 

  The prefix to use for user home directories. 
##### EXAMPLES
home_prefix = /home/ 


#### home_attr 

  The attribute used to create a home directory for a user. Available options include: 

- UUID (default) 

- SPN 

- CN 
##### EXAMPLES
home_attr = UUID 


#### home_alias 

  The symlinked alias for the user's home directory. Available options include: 

- UUID 

- SPN (default) 

- CN 
##### EXAMPLES
home_alias = SPN 


#### shell 

  The default shell for users. This will be assigned when the user logs in. 
##### EXAMPLES
shell = /bin/bash 


#### idmap_range 

  Specifies the range of IDs to be used for the user and group mappings. When this option is modified, you **SHOULD** run: 

sudo aad-tool cache-clear --really To ensure that old cached ID mappings are cleared, preventing potential UID overlaps caused by stale cache data. 
##### EXAMPLES
idmap_range = 5000000-5999999 


#### connection_timeout 

  The timeout for connections to the authentication server. Default is 2 seconds. 
##### EXAMPLES
connection_timeout = 5 


#### cache_timeout 

  The timeout for caching authentication data. Default is 300 seconds (5 minutes). 
##### EXAMPLES
cache_timeout = 10 


#### use_etc_skel 

  If set to **true,** Himmelblau will use the contents of /etc/skel when creating new user directories. 
##### EXAMPLES
use_etc_skel = false 


#### selinux 

  Whether SELinux security labels should be applied to users' home directories. Set to **true** to enable. 
##### EXAMPLES
selinux = true 

## DOMAIN-SPECIFIC SECTIONS

Overrides can be defined for individual domains by using a section named after the domain in square brackets. 

### [example.com]

This section allows customization of specific parameters for the domain **example.com.** Domain-specific sections override global values for the specified domain. 


#### odc_provider 

  Overrides the `odc_provider` value for this domain. 
##### EXAMPLES
[example.com] odc_provider = custom.odcprovider.example.com 


#### home_prefix 

  Overrides the `home_prefix` value for this domain. 
##### EXAMPLES
[example.com] home_prefix = /home/ 


#### home_attr 

  Overrides the `home_attr` value for this domain. 
##### EXAMPLES
[example.com] home_attr = UUID 


#### home_alias 

  Overrides the `home_alias` value for this domain. 
##### EXAMPLES
[example.com] home_alias = SPN 


#### shell 

  Overrides the `shell` value for this domain. 
##### EXAMPLES
[example.com] shell = /bin/bash 


#### idmap_range 

  Overrides the `idmap_range` value for this domain. When this option is modified, you **SHOULD** run: 

sudo aad-tool cache-clear --really To ensure that old cached ID mappings are cleared, preventing potential UID overlaps caused by stale cache data. 
##### EXAMPLES
[example.com] idmap_range = 5000000-5999999 


#### logon_token_app_id 

  Specifies the Entra ID application ID to be used when requesting an ACCESS_TOKEN on behalf of the user for the logon script. If not set, the domain’s **app_id** will be used instead. This option allows configuring a separate application ID specifically for logon token requests, ensuring the correct API permissions are applied. 

**Note:** In the Azure Portal for the application corresponding to **logon_token_app_id**, ensure that the redirect URI _https://login.microsoftonline.com/common/oauth2/nativeclient_ is enabled in the application's Authentication section under “Mobile and desktop applications.” This is required so that Himmelblau can obtain the necessary tokens. 
##### EXAMPLES
[example.com] logon_token_app_id = 544e695f-5d78-442e-b14e-e114e95e640c 


#### app_id 

  Specifies the Entra ID application identifier that permits Himmelblau to fetch the **gidNumber** extended attribute using the **GroupMember.Read.All** API permission for rfc2307 idmapping. If **logon_token_app_id** is not set, this app_id will also be used for requesting access tokens for the logon script. 

**Note:** For the application corresponding to **app_id**, ensure that the redirect URI _himmelblau://Himmelblau.EntraId.BrokerPlugin_ is added in the application's Authentication section under “Mobile and desktop applications” in the Azure Portal. This allows Himmelblau to properly handle token redirection for the extended attribute lookups. 
##### EXAMPLES
[example.com] app_id = d023f7aa-d214-4b59-911d-6074de623765 

## SEE ALSO

**himmelblaud(8),** **himmelblaud-tasks(8)** 