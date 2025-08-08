# RPM Repositories

Official RPM repositories for installing Himmelblau on major RPM-based distributions.

* **Main repo**: [`https://himmelblau-idm.org/rpm/`](https://himmelblau-idm.org/rpm/)
* **GPG key**: [`https://himmelblau-idm.org/himmelblau.asc`](https://himmelblau-idm.org/himmelblau.asc)

---

## 🖥️ openSUSE & SUSE Linux Enterprise

### 🔁 Tumbleweed

```bash
sudo rpm --import https://himmelblau-idm.org/himmelblau.asc
sudo zypper ar https://himmelblau-idm.org/rpm/tumbleweed/x86_64/ himmelblau
sudo zypper ref
sudo zypper in himmelblau nss-himmelblau pam-himmelblau himmelblau-sso
```

---

### 🧱 openSUSE Leap 15.6 / SLE 15 SP6

```bash
sudo rpm --import https://himmelblau-idm.org/himmelblau.asc
sudo zypper ar https://himmelblau-idm.org/rpm/leap15.6/x86_64/ himmelblau
sudo zypper ref
sudo zypper in himmelblau
```

---

## 🧱 RHEL / Rocky / Oracle Linux

Replace `rocky9` with your actual version (`rocky8`, `rocky10`, etc.) if needed:

```bash
sudo rpm --import https://himmelblau-idm.org/himmelblau.asc

echo '[himmelblau]
name=Himmelblau RPM Repo
baseurl=https://himmelblau-idm.org/rpm/rocky9/x86_64/
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://himmelblau-idm.org/himmelblau.asc' | sudo tee /etc/yum.repos.d/himmelblau.repo

sudo dnf clean all
sudo dnf makecache
sudo dnf install himmelblau
```

---

## 🐧 Fedora (41, 42, Rawhide)

Replace `fedora42` with your version if different:

```bash
sudo rpm --import https://himmelblau-idm.org/himmelblau.asc

echo '[himmelblau]
name=Himmelblau RPM Repo
baseurl=https://himmelblau-idm.org/rpm/fedora42/x86_64/
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://himmelblau-idm.org/himmelblau.asc' | sudo tee /etc/yum.repos.d/himmelblau.repo

sudo dnf clean all
sudo dnf makecache
sudo dnf install himmelblau
```

---

## 📌 Notes

* `gpgcheck=1` ensures individual RPMs are signed
* `repo_gpgcheck=1` ensures `repomd.xml` is signed and verified
* All packages are served over HTTPS from [`https://himmelblau-idm.org`](https://himmelblau-idm.org)
* Packages and repo metadata are signed with the same GPG key

---

Interested in hosting a mirror? [Let us know](../../../community).