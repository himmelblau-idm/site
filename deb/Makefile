repos: clean
	podman build -t himmelblau-deb-repos .
	podman run --rm -v "${PWD}":/output himmelblau-deb-repos
	$(MAKE) sign

sign:
	for i in $$(find . -name Release); do \
		echo "Signing $$i"; \
		gpg --clearsign -o "$$(dirname $$i)/InRelease" "$$i"; \
		gpg -abs -o "$$i.gpg" "$$i"; \
	done

clean:
	rm -rf ./dists

all: repos sign

.PHONY: all repos sign clean
