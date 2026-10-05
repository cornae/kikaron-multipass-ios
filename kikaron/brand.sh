#!/usr/bin/env bash
# Brand a checkout of bitwarden/ios (a -bwpm tag) as Kikaron Multipass.
#
#   kikaron/brand.sh [ICON.png]
#
# ICON.png is a 1024x1024 app icon (alpha is dropped: App Store icons are
# opaque). Default: kikaron/icon.png, a copy of the Kikaron repo's
# multipass/brand/icon-1024.png (make_icon.py there). Placeholder: concept A,
# `python3 kikaron/icon.py concept-a kikaron/icon-concept-a.png`.
# Idempotent and deterministic: run it on every new upstream tag.
set -euo pipefail
cd "$(dirname "$0")/.."

ICON="${1:-kikaron/icon.png}"
# The marketing version follows the upstream tag (v2026.9.1-bwpm -> 2026.9.1).
TAG="$(git describe --tags --abbrev=0 --match 'v*-bwpm' 2>/dev/null || true)"
export MARKETING_VERSION="${MARKETING_VERSION:-$(sed -E 's/^v([0-9.]+)-bwpm$/\1/' <<<"$TAG")}"

python3 kikaron/brand.py
python3 kikaron/icon.py derive "$ICON"

# Licence guard rail: nothing under the Bitwarden SDK License / commercial SDK.
if grep -rIl --exclude-dir=.git --exclude-dir=build --exclude-dir=kikaron \
     -e 'bitwarden_license' -e 'commercial-sdk-internal' -e 'LicenseRef-Bitwarden-SDK-only' \
     --include='*.yml' --include='*.swift' --include='Package.resolved' --include='*.xcconfig' . ; then
  echo "licence check: commercial / bitwarden_license reference found (above)" >&2
  exit 1
fi
echo "kikaron/brand.sh: done (version ${MARKETING_VERSION:-unchanged}, icon $ICON)"
