all:
	make -C mkdocs
	pushd deb; make; popd
