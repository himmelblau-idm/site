#!/bin/bash
set -e

REPO_OWNER=himmelblau-idm
REPO_NAME=himmelblau
ARCH=amd64
COMPONENT=main
DISTS=("ubuntu22.04" "ubuntu24.04" "debian12")
REPO_ROOT=/output

for DIST in "${DISTS[@]}"; do
    echo "Processing $DIST..."
    TMPDIR=$(mktemp -d)
    OUTDIR=$REPO_ROOT/dists/$DIST/$COMPONENT/binary-$ARCH
    mkdir -p "$OUTDIR"
    declare -A FILE_URLS

    mapfile -t urls < <(curl -s "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest" |
        jq -r ".assets[] | select(.name | endswith(\"${DIST}_${ARCH}.deb\")) | .browser_download_url")

    for url in "${urls[@]}"; do
        filename=$(basename "$url")
        curl -L -o "$TMPDIR/$filename" "$url"
        FILE_URLS["$filename"]="$url"
    done

    dpkg-scanpackages "$TMPDIR" /dev/null > "$OUTDIR/Packages"

    # Replace filenames with GitHub URLs
    tmpfile=$(mktemp)
    while IFS= read -r line; do
        if [[ "$line" =~ ^Filename:\ (.+)$ ]]; then
            old_path="${BASH_REMATCH[1]}"
            filename=$(basename "$old_path")
            url="${FILE_URLS[$filename]}"
            if [[ -n "$url" ]]; then
                echo "Filename: $url" >> "$tmpfile"
            else
                echo "$line" >> "$tmpfile"
            fi
        else
            echo "$line" >> "$tmpfile"
        fi
    done < "$OUTDIR/Packages"
    mv "$tmpfile" "$OUTDIR/Packages"
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
