1. **Download and install the extension package**

   [Download the appropriate package for your distribution](https://himmelblau-idm.org/downloads.html)

   The package is called `himmelblau-qr-greeter`. Follow your distribution's instructions for installing system packages.

2. **Restart GDM (required)**

   The extension is enabled automatically at install time. You must restart GDM once after installation, otherwise the QR login option may not appear on first use.

   ```bash
   sudo systemctl restart gdm3
   ```

After this restart, the Himmelblau QR Greeter extension will be active on your login and lock screens.

![Login Screen](https://github.com/user-attachments/assets/382cdf17-f6d7-44e8-aa7c-204bd37bad9c)
![Lock Screen](https://github.com/user-attachments/assets/676e4573-9c48-4122-9f68-c21cee1e1846)
