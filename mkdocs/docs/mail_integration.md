# Setting Up Office 365 Email in Evolution

This guide explains how to configure **Office 365 email** in the **Evolution** mail client when you are **already signed in on your system using Himmelblau**. Evolution integrates with Himmelblau's Entra ID authentication, but a brief one-time setup is required.

---

## Prerequisites

* You are logged into your Linux system using Himmelblau.
* Evolution (3.53.2+) is installed.

No passwords will be required during this setup. Himmelblau provides the authentication tokens; Evolution only needs application authorization.

---

## Step-by-Step Setup Instructions

### 1. Open Evolution Account Settings

1. Launch **Evolution**.
2. In the top‑right corner, click the **menu button** (three horizontal bars).
3. Select **Edit → Accounts**.

### 2. Add a New Mail Account

1. Click **Add → Mail Account**.
2. At the welcome screen, click **Next**.
3. Enter the following:

   * **Full Name**: Your name
   * **Email Address**: Your Office 365 / Entra ID email address
4. Click **Next**.

### 3. Configure the Account as Microsoft 365

1. When prompted for account type settings, change **Server Type** to:
   **Microsoft 365**
2. Click **Finish**.

### 4. Save Account Changes

* Click **Apply**.

---

## Authorizing Evolution

You may see an error immediately after clicking **Apply**. This is expected.

1. A dialog will appear asking you to authorize Evolution.
2. Click to open the **connection / authorization dialog**.
3. You will be redirected to the **Office 365 login authorization page**.

   * You **will not** be asked for your username or password. Himmelblau automatically provides authentication.
   * You **will** be asked to confirm that Evolution is allowed to access your account.
4. Approve the authorization.

Once authorized, Evolution will connect normally and begin syncing your mailbox.

---

## Summary

With Himmelblau handling authentication, setting up Office 365 in Evolution takes only a few steps:

1. Add account → enter name/email.
2. Select **Microsoft 365** server type.
3. Apply.
4. Authorize the Evolution app when prompted.

After authorization, your mail, calendar, and contacts will sync automatically.
