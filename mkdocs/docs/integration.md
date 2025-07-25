# Transitioning from On-Prem AD to Azure Entra ID

When migrating from traditional Active Directory (AD) to Azure Entra ID, preserving existing UID and GID values is crucial for Linux systems. Himmelblau 1.0 and newer provides support for POSIX attribute migration and identity mapping via the `aad-tool` utility.

## Migration Paths for UID/GID Preservation

Himmelblau offers two strategies for UID/GID migration, depending on whether you want globally consistent attributes or host-specific mappings.

### 1. Sync POSIX Attributes to Entra ID (Recommended)

Use `aad-tool user set-posix-attrs` and `aad-tool group set-posix-attrs` to store UID/GID values directly on Entra ID objects via directory schema extensions. These values are then consistently available across all Entra ID–joined Linux systems.

You have two options for getting POSIX attributes into Entra ID:

- **Option A:** If your users already have `uidNumber`, `gidNumber`, or `unixHomeDirectory` values in on-prem Active Directory, you can [sync them to Entra ID using Entra Connect Sync](advanced/Configuring-Unix-Attribute-Synchronization-with-Azure-Entra-ID-Using-Microsoft-Entra-Connect-Sync.md).
- **Option B:** Manually register schema extensions and assign POSIX attributes using `aad-tool`.

To manually register and assign:

1. Add the schema extensions:

```bash
   aad-tool application add-schema-extensions \
     --client-id <SCHEMA_CLIENT_ID> \
     --schema-app-object-id <APPLICATION_OBJECT_ID>
```

2. Set attributes on users or groups:

```bash
   aad-tool user set-posix-attrs \
     --schema-client-id <SCHEMA_CLIENT_ID> \
     --user-id <USER_OBJECT_ID> \
     --uid <UID> \
     --gid <GID> \
     --home /home/example \
     --shell /bin/bash
```

> 💡 POSIX attributes stored in Entra ID can be retrieved at login time, even before authentication completes — if Himmelblau is configured with Confidential Client Credentials.

### Using Confidential Client Credentials

To enable early attribute lookup (e.g., `uidNumber`, `gidNumber`) before login:

* Use `aad-tool cred secret` or `aad-tool cred cert` to configure confidential client authentication:

```bash
  # Using a client secret
  aad-tool cred secret \
    --client-id <APP_ID> \
    --domain <YOUR_DOMAIN> \
    --secret <SECRET_VALUE>

  # Or using a self-signed client certificate
  aad-tool cred cert \
    --client-id <APP_ID> \
    --domain <YOUR_DOMAIN> \
    --valid-days 365 \
    --cert-out /tmp/my-cert.pem
```

These credentials allow Himmelblau to authenticate securely and perform Graph API lookups before any user logs in.

### Pre-Caching POSIX Attributes (Optional)

If you haven’t configured confidential client credentials, UID/GID attributes won’t be available until after login.

To avoid this, you can pre-cache attribute mappings using:

```bash
aad-tool enumerate
```

This command fetches all users and groups with POSIX attributes from Entra ID and stores them locally for use during authentication.

> ⚠️ `aad-tool enumerate` only works on devices that are already Entra ID–joined, and where the calling user has delegated Graph API access.

### 2. Use Static ID Mapping (Host-Specific)

If UID/GID mappings vary by system or cannot be stored in Entra ID, use the static ID map cache instead:

```bash
aad-tool idmap user-add --name user@domain --uid 10001 --gid 100
aad-tool idmap group-add --name group@domain --gid 100
```

These mappings are stored locally and applied consistently on the host during lookup.

> ⚠️ This approach is best used when global consistency is not feasible.
