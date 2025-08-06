#!/bin/bash
set -e

REPO_OWNER=himmelblau-idm
REPO_NAME=himmelblau
OTHER_REPO_NAME=cirrus-scope
ARCH=x86_64

# Include SUSE targets
DISTS=(
  "rocky8" "rocky9" "rocky10"
  "fedora41" "fedora42" "rawhide"
  "tumbleweed" "leap15.6" "sle15sp6" "sle15sp7" "sle16"
)

REPO_ROOT=/output

for DIST in "${DISTS[@]}"; do
    echo "Processing $DIST..."
    OUTDIR=$REPO_ROOT/$DIST/$ARCH
    mkdir -p "$OUTDIR"

    mapfile -t urls < <(
      {
        curl -s "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest" |
          jq -r ".assets[] | select(.name | endswith(\"${DIST}_${ARCH}.rpm\")) | .browser_download_url"
        curl -s "https://api.github.com/repos/$REPO_OWNER/$OTHER_REPO_NAME/releases/latest" |
          jq -r ".assets[] | select(.name | endswith(\"${DIST}_${ARCH}.rpm\")) | .browser_download_url"
      }
    )

    for url in "${urls[@]}"; do
        filename=$(basename "$url")
        curl -L -o "$OUTDIR/$filename" "$url"
    done

    createrepo_c "$OUTDIR"
done
