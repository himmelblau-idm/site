#!/bin/bash
set -e

REPO_OWNER=himmelblau-idm
REPO_NAME=himmelblau
OTHER_REPO_NAME=cirrus-scope
ARCH=amd64
COMPONENT=main
DISTS=("ubuntu22.04" "ubuntu24.04" "debian12")
REPO_ROOT=/output
TOKEN_FILE="$REPO_ROOT/.github_token"
GITHUB_TOKEN=$(<"$TOKEN_FILE")

for DIST in "${DISTS[@]}"; do
    echo "Processing $DIST..."
    OUTDIR=$REPO_ROOT/dists/$DIST/$COMPONENT/binary-$ARCH
    mkdir -p "$OUTDIR"

    mapfile -t urls < <(
      {
        curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest" |
          jq -r ".assets[] | select(.name | endswith(\"${DIST}_${ARCH}.deb\")) | .browser_download_url"
        curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$REPO_OWNER/$OTHER_REPO_NAME/releases/latest" |
          jq -r ".assets[] | select(.name | endswith(\"${DIST}_${ARCH}.deb\")) | .browser_download_url"
      }
    )

    for url in "${urls[@]}"; do
        filename=$(basename "$url")
        curl -L -o "$REPO_ROOT/dists/$DIST/$COMPONENT/binary-$ARCH/$filename" "$url"
    done

    pushd $REPO_ROOT; dpkg-scanpackages "dists/$DIST/$COMPONENT/binary-$ARCH" /dev/null > "$OUTDIR/Packages"; popd
    gzip -kf "$OUTDIR/Packages"

    # Generate Release file
    DIST_DIR=$REPO_ROOT/dists/$DIST
    cat > "$DIST_DIR/Release" <<EOF
Origin: Himmelblau
Label: Himmelblau
Suite: $DIST
Codename: $DIST
Architectures: $ARCH
Components: $COMPONENT
Date: $(date -Ru)
EOF
    apt-ftparchive release "$DIST_DIR" >> "$DIST_DIR/Release"

done
