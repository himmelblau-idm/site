GPG_KEY_ID := YOUR_KEY_ID  # Replace with your actual GPG key ID or set via environment

repos: clean
	podman build -t himmelblau-rpm-repos .
	podman run --rm -v "${PWD}":/output himmelblau-rpm-repos
	$(MAKE) sign

sign:
	find ./rpm -type d -name repodata | while read dir; do \
		xml="$$dir/repomd.xml"; \
		if [ -f "$$xml" ]; then \
			echo "Signing $$xml"; \
			gpg --detach-sign --armor --local-user $(GPG_KEY_ID) -o "$$xml.asc" "$$xml"; \
		fi \
	done

clean:
	rm -rf ./rpm

all: repos sign

.PHONY: all repos sign clean
