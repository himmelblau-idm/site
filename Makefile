all: site docs deb

site:
	make -C main

deb:
	pushd deb; make; popd

docs:
	make -C mkdocs

.PHONY: all site docs deb
