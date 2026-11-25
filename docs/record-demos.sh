#!/usr/bin/env bash
# Re-record the three demo GIFs and the social card.
# Needs: vhs, ffmpeg, python3, and the DejaVu Sans Mono font
#   brew install vhs ffmpeg && brew install --cask font-dejavu
# Records from a neutral copy at /tmp/claude-business-skills so no local
# path can appear in a frame, then copies the GIFs to docs/ and site/.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
work=/tmp/claude-business-skills
demos=(invoice-extraction qa-test-generation talking-head-edit-plan)

rm -rf "$work"
mkdir -p "$work"
git -C "$repo" archive HEAD | tar -x -C "$work"

for name in "${demos[@]}"; do
  (cd "$work" && vhs "docs/$name.tape")
  cp "$work/docs/$name.gif" "$repo/docs/$name.gif"
  cp "$work/docs/$name.gif" "$repo/site/$name.gif"
done

# Social card (1200x630): the last frame of the invoice run, fitted to height
# and padded with the terminal background.
ffmpeg -v error -y -sseof -0.1 -i "$repo/docs/invoice-extraction.gif" \
  -vf "scale=-1:630:flags=lanczos,pad=1200:630:(ow-iw)/2:0:color=0x1e1e2e,format=rgb24" \
  -frames:v 1 -update 1 "$repo/site/og.png"

rm -rf "$work"
echo "Updated docs/*.gif, site/*.gif and site/og.png"
