#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
npx --yes tailwindcss@3.4.17 \
    --config tinyaquarium/tailwind.config.cjs \
    --input tools/tinyaquarium.css \
    --output tinyaquarium/assets/site.css --minify
