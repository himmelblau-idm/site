repos: clean
	podman build -t himmelblau-rpm-repos .
	podman run --rm -v "${PWD}":/output himmelblau-rpm-repos
	$(MAKE) sign

sign:
	find ./ -type d -name repodata | while read dir; do \
		xml="$$dir/repomd.xml"; \
		if [ -f "$$xml" ]; then \
			echo "Signing $$xml"; \
			gpg --detach-sign --armor -o "$$xml.asc" "$$xml"; \
		fi \
	done

clean:
	rm -rf rocky8 rocky9 rocky10 fedora41 fedora42 rawhide tumbleweed leap15.6 sle15sp6 sle15sp7 sle16

all: repos sign

.PHONY: all repos sign clean
