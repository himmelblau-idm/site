# ---- Defaults ---------------------------------------------------------------

.PHONY: all man mkdocs man_repo man_repo_clean clean
.SILENT:

all: man
	mkdocs build --site-dir ../docs

# ---- Paths & tools ----------------------------------------------------------

MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
HB_DIR       := $(abspath $(MAKEFILE_DIR)/himmelblau)
LATEST_STABLE:= stable-2.x

MAN_DIR      := $(HB_DIR)/man
MAN_OUT_DIR  := docs/reference

MAN2MD_URL   := https://raw.githubusercontent.com/phillbush/man2md/refs/heads/master/man2md
MAN2MD       := tools/man2md

# ---- Bootstrap local dirs ---------------------------------------------------

$(shell mkdir -p tools $(MAN_OUT_DIR))

# ---- Acquire man2md if missing ----------------------------------------------

$(MAN2MD):
	echo "Downloading man2md …"
	curl -fsSL $(MAN2MD_URL) -o $@
	chmod +x $@

# ---- Acquire Himmelblau (shallow) and check out latest stable ---------------

man_repo:
	echo "Creating shallow clone of himmelblau in $(HB_DIR) …"
	git clone --depth=1 --filter=blob:none https://github.com/himmelblau-idm/himmelblau.git "$(HB_DIR)" --branch="$(LATEST_STABLE)";

man_repo_clean:
	rm -rf $(HB_DIR)

man: $(MAN2MD) man_repo $(MAN_DIR)/man5/himmelblau.conf.5 $(MAN_DIR)/man1/aad-tool.1
	$(MAN2MD) $(MAN_DIR)/man5/himmelblau.conf.5 | sed -E -f tools/clean-manpage.sed > $(MAN_OUT_DIR)/himmelblau-conf.md
	$(MAN2MD) $(MAN_DIR)/man1/aad-tool.1 | sed -E -f tools/clean-manpage.sed > $(MAN_OUT_DIR)/aad-tool.md
	$(MAN2MD) $(MAN_DIR)/man8/himmelblaud.8 | sed -E -f tools/clean-manpage.sed > $(MAN_OUT_DIR)/himmelblaud.md
	$(MAN2MD) $(MAN_DIR)/man8/himmelblaud_tasks.8 | sed -E -f tools/clean-manpage.sed > $(MAN_OUT_DIR)/himmelblaud_tasks.md
	$(MAN2MD) $(MAN_DIR)/man8/pam_himmelblau.8 | sed -E -f tools/clean-manpage.sed > $(MAN_OUT_DIR)/pam_himmelblau.md
	make man_repo_clean
