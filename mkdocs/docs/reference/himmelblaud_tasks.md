
## NAME

himmelblaud_tasks - Home directory creation daemon for Himmelblau 

## SYNOPSIS

**himmelblaud_tasks** 

## DESCRIPTION

The `himmelblaud-tasks` daemon is responsible for managing user accounts and authentication tasks in a Linux environment. Upon successful authentication via Azure Entra ID, it automatically creates home directories for users, adds them to configured local groups, executes the configured logon script, and handles the caching of Kerberos ccache files. This service requires root privileges to perform actions such as creating directories in system locations and managing group memberships. The daemon operates as a background service and does not accept any command-line arguments. It is automatically invoked by the system when required. 

## USAGE

The `himmelblaud-tasks` daemon must be run as the root user. If the daemon is started without root privileges, it will fail with an error. No user interaction is needed beyond ensuring the daemon is active and running correctly. 

## EXAMPLES

* **Start the daemon:** 

  # systemctl start himmelblaud-tasks 


#### Verify the status of the daemon: 

  # systemctl status himmelblaud-tasks 

## NOTES

This daemon is a key component of Himmelblau, handling several critical tasks for user authentication. In addition to creating user home directories, it adds users to the configured local groups, executes the configured logon script, and manages the caching of Kerberos ccache files. These functions ensure that users have the necessary environment and access rights in place for a seamless login experience after authentication. 

## SEE ALSO

**himmelblaud(8),** 