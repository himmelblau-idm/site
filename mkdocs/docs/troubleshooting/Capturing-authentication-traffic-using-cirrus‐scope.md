Capturing OAuth2 traffic when authenticating to Azure Entra ID is essential for debugging and resolving issues in the `libhimmelblau` library. By inspecting the detailed HTTP requests and responses exchanged during the authentication process, developers can identify discrepancies, such as malformed requests, unexpected status codes, or incorrect parameters. This comprehensive view helps pinpoint where errors occur, enabling targeted fixes and enhancements to improve the reliability and functionality of Himmelblau, ultimately leading to smoother integrations and user experiences.

> This guide walks you through how to capture and inspect authentication traffic using the `cirrus-scope` diagnostic tool along with `mitmproxy`.

> **New:** `cirrus-scope` now includes an `obfuscate` command to help automatically mask sensitive data from these captures before sharing them.

### Step-by-Step Instructions

You’ll learn how to capture traffic, then obfuscate sensitive details using `cirrus-scope obfuscate`.

1. **Download `cirrus-scope`**:

	Prebuilt binaries are available from the official Himmelblau downloads page:

	👉 [https://himmelblau-idm.org/downloads.html](https://himmelblau-idm.org/downloads.html)

2. **Download `mitmproxy`**:

	Download `mitmproxy` from [their website](https://mitmproxy.org/), and extract the binaries.

	```
	tar -xf mitmproxy-11.0.0-linux-x86_64.tar.gz
	```

3. **Start `mitmweb`**:

	Run the following command to start `mitmweb`:

	```
	./mitmweb
	```

	This starts `mitmweb` and opens a web interface for monitoring HTTP and HTTPS traffic.

4. **Install the mitmproxy CA Certificate**:

	On Ubuntu,

	```
	sudo cp $HOME/.mitmproxy/mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
	sudo update-ca-certificates
	```

	Or on Fedora,

	```
	sudo cp $HOME/.mitmproxy/mitmproxy-ca-cert.pem /etc/pki/ca-trust/source/anchors/
	sudo update-ca-trust
	```

	Or on openSUSE Leap,

	```
	sudo cp $HOME/.mitmproxy/mitmproxy-ca-cert.pem /usr/share/pki/trust/anchors/mitmproxy.crt
	sudo update-ca-certificates
	```

5. **Access the Web Interface**:

	Open your web browser and go to:

	```
	http://127.0.0.1:8081/
	```

	You should see the `mitmweb` dashboard for viewing captured traffic.

6. **Run `cirrus-scope` with Proxy Enabled**:

	Run the desired test command from `cirrus-scope`, routing its traffic through `mitmproxy` by setting the `HTTPS_PROXY` environment variable.

	Example:

	```
	HTTPS_PROXY=http://127.0.0.1:8080 cirrus-scope auth-test --name your_user@example.com
	```

	You will be prompted to enter credentials interactively. You can add `--debug` for detailed logs:

	```
	HTTPS_PROXY=http://127.0.0.1:8080 cirrus-scope auth-test --name your_user@example.com --debug
	```

	Other available test commands include:

	- `enrollment-test`: Simulates device enrollment
	- `refresh-token-acquire`: Acquires new access tokens using a refresh token
	- `provision-hello-key-test`: Tests Hello for Business key provisioning

7. **Capture and Save the HAR File**:

	- Go to the `mitmweb` dashboard in your web browser.
	- Click on the "File" drop down menu, then "Save".
	- Your browser will download a file called 'flows'

8. **Obfuscate the capture using `cirrus-scope`**:

	To help protect sensitive information, run the built-in obfuscator on your captured flows file. This will automatically replace known tokens (like JWTs, Kerberos tickets, flow tokens, request blobs, and your tenant ID) with equal-length asterisk sequences so that the file remains structurally valid.

	Example:
	```bash
	cirrus-scope obfuscate -i flows -o flows.obfuscated
	```

You can also specify explicit secrets to obfuscate using the `--custom` option, for example:

	 ```bash
	 cirrus-scope obfuscate -i flows -o flows.obfuscated \
		  --custom "your_user@example.com" \
		  --custom "SuperSecretPassword"
	 ```

This ensures additional sensitive data like emails or passwords are masked. The resulting file `flows.obfuscated` will be safe to share for debugging, while still maintaining the exact format required for tools like mitmproxy.

That's it! You have now captured, obfuscated, and saved HTTP(S) traffic as a HAR file.

#### **Important:**
Always use `cirrus-scope obfuscate` to sanitize your capture. Manually editing the file to remove secrets can corrupt the format, making it unreadable by mitmproxy or other tools. This tool replaces sensitive data with exact-length values to keep the file structurally valid.

It remains your responsibility to review the file to ensure no secrets remain. Passwords and plaintext credentials are **not detected automatically** — always provide them explicitly via `--custom` if needed.
