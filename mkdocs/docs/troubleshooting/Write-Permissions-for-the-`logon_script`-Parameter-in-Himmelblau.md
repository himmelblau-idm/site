### Overview
In Himmelblau, the `logon_script` parameter in `himmelblau.conf` specifies a script that is executed by the `himmelblaud-tasks` service at logon time. To ensure the script has the appropriate write access, it may be necessary to modify the `himmelblaud-tasks.service` file to include specific directories in the `ReadWritePaths` directive.

### Steps to Modify the Service File for `logon_script`

1. **Locate the `himmelblaud-tasks.service` File**
   - On Rocky/SUSE Linux: 

     ```
     sudo vim /usr/lib/systemd/system/himmelblaud-tasks.service
     ```

   - On Debian/Ubuntu:

     ```
     sudo nano /etc/systemd/system/himmelblaud-tasks.service
     ```

2. **Edit the `ReadWritePaths` Directive**
   - Add the paths that need write access for the script specified by `logon_script`. For example, if the script logs output to `/var/log`, include `/var/log` in `ReadWritePaths`.
   - Updated section of the service file:

     ```
     [Service]
     ReadWritePaths=/home /var/run/himmelblaud /var/log
     ```

3. **Save and Close the File**

4. **Reload `systemd` and Restart the Service**
   - Reload `systemd` to apply the changes:

     ```
     sudo systemctl daemon-reload
     ```

   - Restart the service:

     ```
     sudo systemctl restart himmelblaud-tasks
     ```

Following these steps will ensure that the `logon_script` has the necessary permissions to write to the specified paths.
