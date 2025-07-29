all: docs deb

deb:
	pushd deb; make; popd

docs:
	make -C mkdocs

.PHONY: all docs deb
