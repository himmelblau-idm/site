## Overview

Hello PINs (and associated keys) for Himmelblau are stored in the SQLite database:

```
/var/cache/himmelblaud/himmelblau.cache.db
```

They are stored and encrypted as entries in the `hsm_data_t` table with keys like:

* `<user>/hello`
* `<user>/hello_decoupled`
* `<user>/hello_prt`

Where `<user>` is the full UPN (e.g. `alice@domain.com`).

This guide provides a script to remove **all** Hello PINs (regular & decoupled) and cached PRTs, regardless of the user.

---

## What exactly gets deleted?

| Key pattern			| Meaning										  |
| ------------------- | -------------------------------------- |
| `%/hello`			  | Hello PIN (normal, linked to Entra Id) |
| `%/hello_decoupled` | Hello PIN (offline / decoupled, for DAG MFA) |
| `%/hello_prt`		 | Cached PRT for offline login with SSO  |

This ensures the host no longer has stored Hello PINs or cached tokens, forcing fresh authentication.

---

## The cleanup script

Below is a simple shell script that will safely delete these keys using `sqlite3`.
It requires root privileges because `/var/cache/himmelblaud/himmelblau.cache.db` is owned by the `himmelblaud` user.

> 💡 **Make sure the Himmelblau daemon is stopped while running this, to avoid database locking issues.**
>
> ```
> sudo systemctl stop himmelblaud
> ```

```
#!/usr/bin/env bash
set -euo pipefail

DB_PATH="/var/cache/himmelblaud/himmelblau.cache.db"

if [[ ! -f "$DB_PATH" ]]; then
	 echo "Error: Database not found at $DB_PATH"
	 exit 1
fi

echo "Removing all Hello PINs and cached PRTs from $DB_PATH ..."

sqlite3 "$DB_PATH" <<EOF
DELETE FROM hsm_data_t WHERE key LIKE '%/hello';
DELETE FROM hsm_data_t WHERE key LIKE '%/hello_decoupled';
DELETE FROM hsm_data_t WHERE key LIKE '%/hello_prt';
EOF

echo "Cleanup completed."
```

---

## How to use

1. **Save the script** to a file, e.g. `remove_himmelblau_hello_pins.sh`
2. **Make it executable:**

	```
	chmod +x remove_himmelblau_hello_pins.sh
	```

3. **Stop Himmelblau daemon:**

	```
	sudo systemctl stop himmelblaud
	```

4. **Run the script:**

	```
	sudo ./remove_himmelblau_hello_pins.sh
	```

5. **Restart Himmelblau daemon:**

	```
	sudo systemctl start himmelblaud
	```

---

## Notes for Himmelblau versions

| Himmelblau Version | Key types present									  |
| ------------------ | --------------------------------------------- |
| 0.9.x				  | Only `%/hello` (regular PINs)					  |
| >=1.0.x				| `%/hello`, `%/hello_decoupled`, `%/hello_prt` |

---

**Done!**
The host is now wiped of all Hello PINs and cached PRTs.
New PIN enrollments or sign-ins will need to occur on next use.
