#!/usr/bin/env bash
set -euo pipefail
MANIFEST="${1:-data/external/raw_hdf5_download_manifest.json}"
mkdir -p data/external/raw_hdf5 outputs/raw_hdf5_download
if [[ ! -f "$MANIFEST" ]]; then
  echo "Manifest not found: $MANIFEST" >&2
  echo "Create it from: data/templates/v47_raw_hdf5_download_manifest_template.json" >&2
  exit 2
fi
python - "$MANIFEST" <<'PY_CHECK_URL'
import json, sys, pathlib
m=json.loads(pathlib.Path(sys.argv[1]).read_text())
url=m.get('official_download_url','').strip()
if not url or url.startswith('FILL_'):
    raise SystemExit('official_download_url is empty. Fill manifest from official Zenodo record before download.')
print(url)
PY_CHECK_URL
URL=$(python - "$MANIFEST" <<'PY_GET_URL'
import json,sys,pathlib
print(json.loads(pathlib.Path(sys.argv[1]).read_text()).get('official_download_url','').strip())
PY_GET_URL
)
OUT="data/external/raw_hdf5/Raw_data_MEA_data.zip"
if command -v aria2c >/dev/null 2>&1; then
  aria2c -c -x 8 -s 8 -o "$(basename "$OUT")" -d "$(dirname "$OUT")" "$URL"
else
  curl -L -C - --retry 5 --retry-delay 5 -o "$OUT" "$URL"
fi
python - "$MANIFEST" "$OUT" <<'PY_VALIDATE_RAW'
import hashlib,json,pathlib,sys
m=json.loads(pathlib.Path(sys.argv[1]).read_text())
p=pathlib.Path(sys.argv[2])
sha=m.get('expected_sha256','').strip()
size=m.get('expected_size_bytes')
h=hashlib.sha256(p.read_bytes()).hexdigest()
print({'file':str(p),'bytes':p.stat().st_size,'sha256':h})
if sha and not sha.startswith('FILL_') and h.lower()!=sha.lower():
    raise SystemExit('SHA256 mismatch')
if isinstance(size,int) and size>0 and p.stat().st_size!=size:
    raise SystemExit('Size mismatch')
PY_VALIDATE_RAW
