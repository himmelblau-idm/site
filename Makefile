all: site docs deb

site:
	make -C main

docs:
	make -C mkdocs

.PHONY: all site docs deb rpm
