#### Overview

When using Himmelblau, you might encounter the error:

```
useradd: user 'test1' already exists
```

or similar behavior when attempting to create local users. You might also notice that nss responds affirmatively to the existence of fake users:

```
$ getent passwd fake_user1
fake_user1@example.com:x:955955525:955955525::/home/fake_user1:/bin/bash
$ getent passwd fake_user2
fake_user2@example.com:x:1881368896:1881368896::/home/fake_user2:/bin/bash
```

This problem occurs even for users that neither exist locally nor in your Azure Entra ID tenant. Additionally, this issue can lead to complications with package management tools (e.g., `apt` or `dnf`) that need to create system users during installation.

#### Root Cause

This behavior arises from the `cn_name_mapping` parameter in your **himmelblau.conf** configuration file. By default, this parameter is enabled (`true`) unless explicitly set to `false`. When enabled, it automatically maps common names (CN) to user principal names (UPN).

The issue appears to occur because **user enumeration is disabled in Azure Entra ID**.

Azure Entra ID is responding to all user existence requests as if the user **does exist**, regardless of whether the user truly exists in the directory.
It's unknown which setting in Azure Entra Id is causing this behavior, but it is assumed that Microsoft has implemented this behavior to ensure authentication does not fail for valid users. If the system always responded that users do not exist, authentication would fail even for legitimate accounts. It's assumed that the purpose of this behavior is to prevent the enumeration of valid UPN names from the directory. When an attacker is able to enumerate a list of valid UPN names, it can enable password spray attacks, brute force attacks, phishing attacks, and password reuse attacks.

#### Impact

1. **Local User Management**: System tools like `useradd` fail to create new users.
2. **Package Installation**: Software installations that create system users for daemons may fail, causing package dependency issues.
3. **General User Queries**: Tools like `getent passwd` may list users that do not exist.

#### Solution: Disable `cn_name_mapping`

To mitigate this issue, disable the `cn_name_mapping` parameter in your Himmelblau configuration file.

1. **Locate the Configuration File**:
	The default configuration file is located at:

	```
	/etc/himmelblau/himmelblau.conf
	```

2. **Edit the File**:
	Open the file in your preferred text editor:

	```
	sudo nano /etc/himmelblau/himmelblau.conf
	```

3. **Disable ****`cn_name_mapping`**:
	Locate the `[global]` section and add or modify the following line:

	```
	cn_name_mapping = false
	```

4. **Restart Himmelblau Services**:
	After saving the changes, restart the Himmelblau services to apply the new configuration:

	```
	sudo systemctl restart himmelblaud
	sudo systemctl restart himmelblaud-tasks
	```

After disabling `cn_name_mapping`, all users will be required to authenticate to the host using their UPN.

#### Verification

- Check user enumeration again:

  ```
  getent passwd test1
  ```

  Ensure the user is not falsely listed.

- Retry adding a new user:

  ```
  sudo useradd test1
  ```

  It should now succeed without errors.

#### Notes

Disabling `cn_name_mapping` prevents Himmelblau from making optimistic assumptions about user existence. This adjustment ensures compatibility with environments where Azure Entra ID has user enumeration disabled, aligning expected behavior with the tenant’s security configuration.

#### Additional References

- For more details about `himmelblau.conf` parameters, refer to the [Himmelblau Configuration Guide](https://himmelblau-idm.org/docs.html#configuration) or the [`himmelblau.conf` man page](https://manpages.opensuse.org/Tumbleweed/himmelblau/himmelblau.conf.5.en.html).
- If you continue experiencing issues, consider clearing or invalidating the Himmelblau cache using the `aad-tool` utility:
  ```
  sudo aad-tool cache-clear
  ```
