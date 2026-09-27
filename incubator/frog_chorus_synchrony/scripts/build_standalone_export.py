#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"incubator"/"frog_chorus_synchrony"
MANIFEST=BASE/"STANDALONE_EXPORT_MANIFEST_V0_1.json"
OUT=ROOT/"build"/"frog-chorus-synchrony-standalone"

spec=json.loads(MANIFEST.read_text(encoding="utf-8"))
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

hashes={}
missing=[]
for rel in spec["core_files"]+spec.get("generated_optional",[]):
    src=ROOT/rel
    if not src.exists():
        if rel in spec.get("generated_optional",[]):
            continue
        missing.append(rel)
        continue
    dest=OUT/Path(rel).relative_to("incubator/frog_chorus_synchrony")
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dest)
    hashes[str(dest.relative_to(OUT))]=hashlib.sha256(dest.read_bytes()).hexdigest()

if missing:
    raise SystemExit("missing core export files: "+", ".join(missing))

readme=OUT/"README.md"
readme.write_text("""# Frog chorus synchrony reproducibility package

This directory is generated from the 284b incubator and contains only the final
frog acoustic-community manuscript, frozen analysis contracts, result receipts,
reproduction scripts and submission-figure code.

Primary ecological claim:
More recent rainfall is associated with greater short-window multispecies frog
co-calling across independent North American and Australian acoustic systems.

Data are not redistributed here. Retrieve NAAMP from DOI 10.5066/F7G44NG0 and
FrogID from DOI 10.15468/wazqft. ERA5 source identity and linkage rules are pinned
in the included contracts.

The two system-specific effect sizes are not intended for direct meta-analysis.
""",encoding="utf-8")
hashes["README.md"]=hashlib.sha256(readme.read_bytes()).hexdigest()

(OUT/"FILE_SHA256.json").write_text(
    json.dumps(dict(sorted(hashes.items())),indent=2)+"\n",encoding="utf-8"
)
print(json.dumps({
  "output":str(OUT),
  "files":len(hashes),
  "missing_core":missing,
  "status":"PASS"
},indent=2))
