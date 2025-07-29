all: man
	mkdocs build --site-dir ../docs

MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
MAN_DIR := $(MAKEFILE_DIR)/../../himmelblau/man/

MAN2MD_URL := https://raw.githubusercontent.com/phillbush/man2md/refs/heads/master/man2md
MAN2MD := tools/man2md
MAN_OUT_DIR := docs/reference

# Ensure output directory exists
$(shell mkdir -p $(OUT_DIR) tools)

# Download man2md script if not already available
$(MAN2MD):
	curl -fsSL $(MAN2MD_URL) -o $@
	chmod +x $@

man: $(MAN2MD) $(MAN_DIR)/man5/himmelblau.conf.5 $(MAN_DIR)/man1/aad-tool.1
	$(MAN2MD) $(MAN_DIR)/man5/himmelblau.conf.5 | sed -E -f tools/clean-manpage.sed > $(MAN_OUT_DIR)/himmelblau-conf.md
	$(MAN2MD) $(MAN_DIR)/man1/aad-tool.1 | sed -E -f tools/clean-manpage.sed > $(MAN_OUT_DIR)/aad-tool.md
	$(MAN2MD) $(MAN_DIR)/man8/himmelblaud.8 | sed -E -f tools/clean-manpage.sed > $(MAN_OUT_DIR)/himmelblaud.md
	$(MAN2MD) $(MAN_DIR)/man8/himmelblaud_tasks.8 | sed -E -f tools/clean-manpage.sed > $(MAN_OUT_DIR)/himmelblaud_tasks.md
	$(MAN2MD) $(MAN_DIR)/man8/pam_himmelblau.8 | tail -n50
	$(MAN2MD) $(MAN_DIR)/man8/pam_himmelblau.8 | sed -E -f tools/clean-manpage.sed > $(MAN_OUT_DIR)/pam_himmelblau.md

.PHONY: all man
