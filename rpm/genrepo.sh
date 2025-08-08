#!/bin/bash
set -e

REPO_OWNER=himmelblau-idm
REPO_NAME=himmelblau
OTHER_REPO_NAME=cirrus-scope
ARCH=x86_64
REPO_ROOT=/output
TOKEN_FILE="$REPO_ROOT/.github_token"
GITHUB_TOKEN=$(<"$TOKEN_FILE")

# Include SUSE targets
DISTS=(
  "rocky8" "rocky9" "rocky10"
  "fedora41" "fedora42" "rawhide"
  "tumbleweed" "leap15.6" "sle15sp6" "sle15sp7" "sle16"
)

for DIST in "${DISTS[@]}"; do
    echo "Processing $DIST..."
    OUTDIR=$REPO_ROOT/$DIST/$ARCH
    mkdir -p "$OUTDIR"

    mapfile -t urls < <(
      {
        curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest" |
          jq -r ".assets[] | select(.name | endswith(\"${ARCH}-${DIST}.rpm\")) | .browser_download_url"
        curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$REPO_OWNER/$OTHER_REPO_NAME/releases/latest" |
          jq -r ".assets[] | select(.name | endswith(\"${ARCH}-${DIST}.rpm\")) | .browser_download_url"
      }
    )

    for url in "${urls[@]}"; do
        filename=$(basename "$url")
        curl -L -o "$OUTDIR/$filename" "$url"
    done

    createrepo_c "$OUTDIR"
done
