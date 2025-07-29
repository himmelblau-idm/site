
## NAME

himmelblaud - Himmelblau Authentication Daemon for Azure Entra ID 

## SYNOPSIS

**himmelblaud** [_OPTIONS_] 

## DESCRIPTION

The `himmelblaud` daemon is responsible for authenticating users against Azure Entra ID and managing group and user information. It operates as a background service, handling authentication requests and maintaining a cache of user and group data. 

## OPTIONS

* **-r**, **--skip-root-check** 

  Bypass the check that prevents running the daemon as the root user. This option is risky and should never be used in production environments due to potential security vulnerabilities. It can also be set through the environment variable **HIMMELBLAU_SKIP_ROOT_CHECK**. 


#### -d**, **--debug 

  Enable verbose debug output. This option will show detailed diagnostic information useful for troubleshooting and debugging. Can also be set via the environment variable **HIMMELBLAU_DEBUG**. 


#### -t**, **--configtest 

  Display the daemon’s current configuration and exit. This is useful for verifying that the configuration file is correctly formatted and contains valid options. 


#### -c**, **--config &lt;config&gt; 

  Specify the path to the configuration file for the daemon. The default configuration file is located at _/etc/himmelblau/himmelblaud.conf_. This option can also be set via the environment variable **HIMMELBLAU_CONFIG**. 


#### -h**, **--help 

  Show the help message with information about available options. 


#### -V**, **--version 

  Print the version of the `himmelblaud` daemon and exit. 

## USAGE EXAMPLES

* **Start the daemon:** 

  # systemctl start himmelblaud 


#### Run with a specific config file: 

  # himmelblaud --config /custom/path/himmelblaud.conf 


#### Test the configuration: 

  # himmelblaud --configtest 


#### Enable debug mode: 

  # himmelblaud --debug 

## SEE ALSO

**himmelblaud-tasks(8)** 