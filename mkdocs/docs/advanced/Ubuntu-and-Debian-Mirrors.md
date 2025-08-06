# Ubuntu and Debian Repository Mirrors

Himmelblau packages for Debian and Ubuntu are distributed through public APT repositories:

- ✅ **Official Repository** – Maintained by the Himmelblau project
- 💡 **Community Mirror** – Maintained independently by a contributor

---

## ✅ Official Repository (GitHub-hosted)

```
https://himmelblau-idm.org/deb
```

- **Maintained by:** Himmelblau Project
- **Bandwidth:** Limited — may be slower during high demand
- **Key:** [`https://himmelblau-idm.org/himmelblau.asc`](https://himmelblau-idm.org/himmelblau.asc)
- **Protocols:** Locked to HTTPS

### 🛠️ Setup Instructions

```bash
# Install the official GPG key
curl -fsSL https://himmelblau-idm.org/himmelblau.asc \
  | gpg --dearmor \
  | sudo tee /usr/share/keyrings/himmelblau.gpg > /dev/null

# Add the APT source
echo "deb [signed-by=/usr/share/keyrings/himmelblau.gpg] https://himmelblau-idm.org/deb ubuntu24.04 main" \
  | sudo tee /etc/apt/sources.list.d/himmelblau.list
```

---

## 💡 Community Mirror (archiesbytes.xyz)

```
https://deb.archiesbytes.xyz/himmelblau/
```

* **Maintained by:** Community contributor [@iLikeToCode](https://github.com/iLikeToCode)
* **Bandwidth:** Generously hosted — may offer better performance in Europe
* **Key:** [`https://himmelblau-idm.org/himmelblau.asc`](https://himmelblau-idm.org/himmelblau.asc)
* **Protocols:** HTTP and HTTPS (Works with transparent caching proxy)
* **Info**: Syncs at 02:00 UTC daily

### 🛠️ Setup Instructions

```bash
# Install the official GPG key
curl -fsSL https://himmelblau-idm.org/himmelblau.asc \
  | gpg --dearmor \
  | sudo tee /usr/share/keyrings/himmelblau.gpg > /dev/null

# Add the APT source
echo "deb [signed-by=/usr/share/keyrings/himmelblau.gpg] https://deb.archiesbytes.xyz/himmelblau/ ubuntu24.04 main" \
  | sudo tee /etc/apt/sources.list.d/himmelblau.list
```

---

## 📌 Notes

* Replace `ubuntu24.04` with your system's codename if needed (e.g., `debian12`, `ubuntu22.04`, etc.).
* Package contents are identical between mirrors.
* Community mirrors are offered as-is and availability may vary.

---

## 📚 See Also

* [Installation Guide](../installation.md)

---

Interested in hosting a mirror? [Let us know](../../../community).
