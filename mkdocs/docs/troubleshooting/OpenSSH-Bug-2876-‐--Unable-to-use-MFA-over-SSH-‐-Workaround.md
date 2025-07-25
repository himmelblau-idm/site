## Summary of Bug 2876

**Bug 2876** in OpenSSH pertains to an issue with PAM info messages not being flushed to the console until further interaction is required. This leads to problems in scenarios where multiple authentication prompts are expected, such as with Microsoft Authenticator's Push MFA.

### Problem Behavior

When attempting to authenticate via SSH with an account that requires **Microsoft Authenticator (Push) MFA**, the prompt displaying the number to enter into the app is delayed or not shown until after the initial authentication fails. This leads to confusion, as the user receives the MFA push notification on their device but cannot complete the authentication due to the missing prompt.

#### Local Login (Working as Expected)
When logging in locally (e.g., via `su -l`), the password prompt and the MFA number prompt are displayed as expected, and the user is able to complete the login process:
```
admin@dev01:~$ su -l user@domain.onmicrosoft.com
Password:
Open your Authenticator app, and enter the number '73' to sign in.
user@domain.onmicrosoft.com@dev01:~$ whoami
user@domain.onmicrosoft.com
```

#### Remote SSH Login (Delayed MFA Prompt)
When logging in remotely via SSH, only the password prompt is shown initially, and the MFA number prompt is delayed until the authentication fails:
```
localuser@workstation:~$ ssh user@domain.onmicrosoft.com@dev01
(user@domain.onmicrosoft.com@dev01) Password:
## Note: The MFA push notification is received, but no number is shown to complete the authentication.
(user@domain.onmicrosoft.com@dev01) Open your Authenticator app, and enter the number '59' to sign in.
Password: ^C
```

This behavior disrupts the MFA flow, as the number needed to complete the login is not shown to the user until the session has already failed.

### Upstream Status

The fix for this issue has been proposed in [Pull Request 452 on GitHub](https://github.com/openssh/openssh-portable/pull/452), but the upstream OpenSSH community has been slow to review and merge the patch. This means that users on most systems will continue to face this issue unless they apply the fix downstream.

### Downstream Fixes

**openSUSE** and **Ubuntu** have both applied the patch in their respective distributions. Users running OpenSSH on these systems should be free of this bug on recent versions of the distributions.

## Working Around Bug 2876 in Himmelblau (introduced in Himmelblau 0.6.0)

This bug can cause significant disruption to SSH-based logins. If you're using a system affected by Bug 2876 and the patch has not been applied upstream, you can work around the issue by configuring the `pam_himmelblau.so` module with the `mfa_poll_prompt` option. This forces the prompt to be shown to the user at the appropriate time.

### Step-by-Step Instructions

1. **Locate the PAM Configuration**:
	See the [Himmelblau instructions for configuring PAM](https://github.com/himmelblau-idm/himmelblau/wiki#setup-pam). You could apply a targeted work around by modifying the file `/etc/pam.d/sshd`.

2. **Add the `mfa_poll_prompt` Option**:
	To avoid the prompt delay caused by Bug 2876, modify the PAM configuration for Himmelblau by adding the `mfa_poll_prompt` option to the `pam_himmelblau.so` module.

	Example PAM configuration:

	```
	auth	 required	 pam_himmelblau.so	 ignore_unknown_user mfa_poll_prompt
	```

3. **Test the Setup**:
	Attempt an SSH login using an account with Microsoft Authenticator Push MFA enabled and ensure that the MFA number prompt is displayed as expected.

The `mfa_poll_prompt` option in the workaround introduces a "Press enter to continue" prompt during the MFA flow, which forces user interaction. This interaction triggers OpenSSH to flush its buffered output, causing the previously delayed MFA number prompt to be displayed. As a result, the user can view the MFA prompt and complete the authentication process without waiting for a failed login attempt.

Here’s an example of what the login process will look like to the user with the workaround in place:

```
localuser@workstation:~$ ssh user@domain.onmicrosoft.com@dev01
(user@domain.onmicrosoft.com@dev01) Password:
Open your Authenticator app, and enter the number '59' to sign in.
Press enter to continue
## Note: The user must now press enter to continue the MFA authentication.
```
