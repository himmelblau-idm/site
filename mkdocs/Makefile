# ---- Defaults ---------------------------------------------------------------

.PHONY: all man mkdocs man_repo man_repo_clean clean
.SILENT:

all: man
	mkdocs build --site-dir ../docs

# ---- Paths & tools ----------------------------------------------------------

MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
HB_DIR       := $(abspath $(MAKEFILE_DIR)/himmelblau)
LATEST_STABLE:= stable-3.x

MAN_DIR      := $(HB_DIR)/man
MAN_OUT_DIR  := docs/reference

# Use the venv-bundled pandoc from pypandoc_binary
VENV_PKGS    := $(abspath $(MAKEFILE_DIR)/../.venv/lib/python*/site-packages)
PANDOC       := $(wildcard $(VENV_PKGS)/pypandoc/files/pandoc)
POSTPROCESS  := tools/postprocess.py

# ---- Bootstrap local dirs ---------------------------------------------------

$(shell mkdir -p $(MAN_OUT_DIR))

# ---- Acquire Himmelblau (shallow) and check out latest stable ---------------

man_repo:
	echo "Creating shallow clone of himmelblau in $(HB_DIR) …"
	git clone --depth=1 --filter=blob:none https://github.com/himmelblau-idm/himmelblau.git "$(HB_DIR)" --branch="$(LATEST_STABLE)";

man_repo_clean:
	rm -rf $(HB_DIR)

man: man_repo
	$(PANDOC) -f man -t gfm $(MAN_DIR)/man5/himmelblau.conf.5 | python3 $(POSTPROCESS) > $(MAN_OUT_DIR)/himmelblau-conf.md
	$(PANDOC) -f man -t gfm $(MAN_DIR)/man1/aad-tool.1        | python3 $(POSTPROCESS) > $(MAN_OUT_DIR)/aad-tool.md
	$(PANDOC) -f man -t gfm $(MAN_DIR)/man8/himmelblaud.8      | python3 $(POSTPROCESS) > $(MAN_OUT_DIR)/himmelblaud.md
	$(PANDOC) -f man -t gfm $(MAN_DIR)/man8/himmelblaud_tasks.8 | python3 $(POSTPROCESS) > $(MAN_OUT_DIR)/himmelblaud_tasks.md
	$(PANDOC) -f man -t gfm $(MAN_DIR)/man8/pam_himmelblau.8   | python3 $(POSTPROCESS) > $(MAN_OUT_DIR)/pam_himmelblau.md
	make man_repo_clean
