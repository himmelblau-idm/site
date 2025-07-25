A **Himmelblau developer build** allows you to proxy all communication between `himmelblaud` and Azure Entra ID. This is critical for diagnosing low-level authentication or policy issues.

These instructions will walk you through setting up `mitmproxy`, ensuring your `himmelblaud` service is routed through it, installing the proxy certificate, and finally capturing and obfuscating the traffic.

---

# 🚧 Developer Build Notice

⚠️ **IMPORTANT WARNING:**
This special Himmelblau developer build is **strictly for debugging and diagnostics.**
It proxies authentication traffic through `mitmproxy`, exposing sensitive credentials and tokens.

➡️ **Never run this in production.** Use it only in controlled test environments to diagnose problems.

---

## 📨 How to get a developer build

Developer builds are **not public binaries.**
To obtain one:

* **Contact David Mulder (project maintainer):**

  * 📧 Email: [dmulder@himmelblau-idm.org](mailto:dmulder@himmelblau-idm.org)
  * 💬 Matrix: [#himmelblau\:matrix.org](https://matrix.to/#/#himmelblau:matrix.org)

---

## 1. Verify your `HTTPS_PROXY` is set in the service file

Open your `himmelblaud` systemd service file and confirm it is configured to use your local mitmproxy.

* On **Ubuntu/Debian**:

  ```
  sudo nano /etc/systemd/system/himmelblaud.service
  ```

* On **RHEL/Fedora/openSUSE**:

  ```
  sudo nano /usr/lib/systemd/system/himmelblaud.service
  ```

Make sure it includes, and that the HTTPS_PROXY setting is correct for your mitmproxy instance:

```
Environment="HTTPS_PROXY=http://127.0.0.1:8080"
```

Then reload systemd and restart `himmelblaud`:

```
sudo systemctl daemon-reload
sudo systemctl restart himmelblaud himmelblaud-tasks
```

---

## 2. Install and start `mitmweb`

Download `mitmproxy` from [https://mitmproxy.org/](https://mitmproxy.org/), extract it, and run:

```
./mitmweb
```

This launches a local web interface at `http://127.0.0.1:8081/`.

---

## 3. Install the mitmproxy CA certificate

This ensures your system trusts mitmproxy’s TLS interception.

* **Ubuntu/Debian:**

  ```
  sudo cp ~/.mitmproxy/mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
  sudo update-ca-certificates
  ```

* **Fedora/RHEL:**

  ```
  sudo cp ~/.mitmproxy/mitmproxy-ca-cert.pem /etc/pki/ca-trust/source/anchors/
  sudo update-ca-trust
  ```

* **openSUSE:**

  ```
  sudo cp ~/.mitmproxy/mitmproxy-ca-cert.pem /usr/share/pki/trust/anchors/mitmproxy.crt
  sudo update-ca-certificates
  ```

---

## 4. Reproduce your Himmelblau issue

At this point:

* `himmelblaud` is routing traffic through `127.0.0.1:8080`
* `mitmweb` is running to intercept traffic

Trigger the behavior you’re testing — e.g. SSH login, `sudo`, or any other process that hits `pam_himmelblau`.

Watch the traffic appear in the `mitmweb` dashboard at `http://127.0.0.1:8081/`.

---

## 5. Save the flow file

In the `mitmweb` interface:

1. Click **File → Save**.
2. This downloads a file typically called `flows`.

---

## 6. Obfuscate sensitive data with `cirrus-scope`

Before sharing your capture, sanitize it using:

```
cirrus-scope obfuscate -i flows -o flows.obfuscated
```

This automatically masks known sensitive data like JWTs, flow tokens, tenant IDs, etc.

You can also specify explicit items to redact (emails, passwords, etc):

```
cirrus-scope obfuscate -i flows -o flows.obfuscated \
    --custom "admin@contoso.com" \
    --custom "SuperSecretPassword"
```

---

## Done!

You can now safely provide `flows.obfuscated` for debugging.
It maintains the structure needed for tools like `mitmproxy` to replay or analyze, while protecting your secrets.

---

### 🚨 **Important Note**

* Always run `cirrus-scope obfuscate` before sharing captures.
* Manually editing the file may break its format. This tool preserves lengths to ensure it remains valid for protocol testing.
