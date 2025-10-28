# ===== Config =====
VENV                  ?= $(CURDIR)/.venv
PYTHON                ?= python3
MKDOCS_VERSION        ?= 1.6.1
MATERIAL_VERSION      ?= 9.6.15
PYMDOWN_VERSION       ?= 10.11
MINIFY_PLUGIN_VERSION ?= 0.8.0
AWESOME_PAGES_VERSION ?= 2.9.3

VENV_BIN := $(VENV)/bin
PIP      := $(VENV_BIN)/pip
PY       := $(VENV_BIN)/python
MKDOCS   := $(PY) -m mkdocs

# Don't rely on inherited PATH; call tools via venv paths
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: all site docs venv deps check-versions clean-venv print-versions

all: deps site docs

# Force site build to use the venv mkdocs explicitly
site: deps
	@echo "==> Building site (main/) with pinned mkdocs-material $(MATERIAL_VERSION)"
	@cd main && $(MKDOCS) build --clean --site-dir ../s
	@cd main && cp -rf ../s/* ../ && rm -rf ../s

# Force docs build to use the venv mkdocs explicitly
docs: deps check-versions
	@echo "==> Building docs (mkdocs/) with pinned mkdocs-material $(MATERIAL_VERSION)"
	@cd mkdocs && $(MAKE) man
	@cd mkdocs && $(MKDOCS) build --clean --site-dir ../docs

# --- Environment management ---
venv:
	@if [ ! -d "$(VENV)" ]; then \
	  echo "==> Creating Python venv at $(VENV)"; \
	  $(PYTHON) -m venv "$(VENV)"; \
	  "$(PIP)" install --upgrade pip; \
	else \
	  echo "==> Using existing venv at $(VENV)"; \
	fi

deps: venv
	@echo "==> Installing pinned docs toolchain into venv"
	@$(PIP) install --disable-pip-version-check \
		"mkdocs==$(MKDOCS_VERSION)" \
		"mkdocs-material==$(MATERIAL_VERSION)" \
		"pymdown-extensions==$(PYMDOWN_VERSION)" \
		"mkdocs-minify-plugin==$(MINIFY_PLUGIN_VERSION)" \
		"mkdocs-awesome-pages-plugin==$(AWESOME_PAGES_VERSION)"

check-versions:
	@$(PY) -c "import sys; \
from importlib.metadata import version; \
got=version('mkdocs-material'); want='$(MATERIAL_VERSION)'; \
sys.exit(0) if got==want else (print(f'ERROR: mkdocs-material {got} != {want}', file=sys.stderr) or sys.exit(1))"
	@echo "mkdocs-material pinned OK: $(MATERIAL_VERSION)"

# Utilities
print-versions: deps
	@$(PY) --version
	@$(PIP) show mkdocs mkdocs-material pymdown-extensions mkdocs-minify-plugin | awk -F': ' '/^(Name|Version)/{printf "%s %s%s", $$1, $$2, (/Version/?"\n":" ")}'

clean-venv:
	@rm -rf "$(VENV)"
	@echo "==> Removed $(VENV)"
