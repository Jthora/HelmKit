#!/usr/bin/env bash
# build.sh — render HelmKit Field Notes Vol. I to PDF via pandoc.
#
# Requires: pandoc >= 3.0 and one of: tectonic, xelatex, lualatex.
# macOS:    brew install pandoc tectonic
# Linux:    apt-get install pandoc && cargo install tectonic
#
# Output:   out/HelmKit_FieldNotes_Vol1.pdf

set -euo pipefail

cd "$(dirname "$0")"

OUT_DIR="out"
OUT_PDF="${OUT_DIR}/HelmKit_FieldNotes_Vol1.pdf"

mkdir -p "${OUT_DIR}"

# Pick the first available PDF engine. Tectonic is preferred because it
# downloads its own packages and gives reproducible builds across machines.
if command -v tectonic >/dev/null 2>&1; then
  PDF_ENGINE="tectonic"
elif command -v xelatex >/dev/null 2>&1; then
  PDF_ENGINE="xelatex"
elif command -v lualatex >/dev/null 2>&1; then
  PDF_ENGINE="lualatex"
else
  echo "build.sh: no PDF engine found. Install one of: tectonic, xelatex, lualatex." >&2
  exit 2
fi

echo "build.sh: using PDF engine: ${PDF_ENGINE}"

# Section files in reading order. 10_*.md comes after 09_*.md.
SECTIONS=(
  "00_frontmatter.md"
  "01_manifesto.md"
  "02_platform.md"
  "03_sister_modules.md"
  "04_wiki_as_spec.md"
  "05_field_theory.md"
  "06_safety_floor.md"
  "07_roadmap.md"
  "08_field_notes.md"
  "09_prior_art.md"
  "10_support.md"
)

# Verify everything exists before invoking pandoc.
for f in "${SECTIONS[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "build.sh: missing section file: $f" >&2
    exit 1
  fi
done

echo "build.sh: rendering ${#SECTIONS[@]} sections -> ${OUT_PDF}"

pandoc \
  --metadata-file=metadata.yml \
  --pdf-engine="${PDF_ENGINE}" \
  --toc \
  --toc-depth=2 \
  --number-sections \
  --resource-path=".:figures" \
  --variable=linkcolor:NavyBlue \
  -V geometry:margin=1in \
  -o "${OUT_PDF}" \
  "${SECTIONS[@]}"

echo "build.sh: wrote ${OUT_PDF}"
