1. **Download and Install the Extension Package**

   [Download the appropriate package for your distribution](https://himmelblau-idm.org/downloads)

   The package is called `himmelblau-qr-greeter`. Follow your distribution’s instructions for installing system packages.

2. **Enable the Extension for the GDM User**

   Since the extension runs on the GDM (login) screen, you must enable it as the gdm user. Run the following commands:

   1. **Open a shell as the gdm user:**

      ```
      sudo machinectl shell gdm@ /bin/bash
      ```
      
   2. **Enable the extension for GDM:**

      ```
      gsettings set org.gnome.shell enabled-extensions "['qr-greeter@himmelblau-idm.org']"
      ```
      
   3. **Exit the shell:**

      ```
      exit
      ```

3. **Restart GDM**

   To apply the changes, restart GDM:

   ```
   sudo systemctl restart gdm3
   ```

After these steps, the Himmelblau QR Greeter extension will be active on your login and lock screens.

![Login Screen](https://github.com/user-attachments/assets/382cdf17-f6d7-44e8-aa7c-204bd37bad9c)
![Lock Screen](https://github.com/user-attachments/assets/676e4573-9c48-4122-9f68-c21cee1e1846)
