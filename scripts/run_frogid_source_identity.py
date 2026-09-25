#!/usr/bin/env python3
from __future__ import annotations
import hashlib, io, json, time, urllib.request, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

URL="https://dwca-exports.ala.org.au/dr14760.zip"
NS={"dwc":"http://rs.tdwg.org/dwc/text/"}

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"frogid-source-identity-audit/0.1"})
    with urllib.request.urlopen(req,timeout=240) as r:
        return r.read()

def core_name(z):
    root=ET.fromstring(z.read("meta.xml"))
    core=root.find("dwc:core",NS)
    if core is None: raise RuntimeError("missing core")
    files=core.find("dwc:files",NS)
    loc=files.find("dwc:location",NS) if files is not None else None
    if loc is None or not (loc.text or "").strip():
        raise RuntimeError("missing core location")
    return loc.text.strip()

def snapshot(data):
    z=zipfile.ZipFile(io.BytesIO(data))
    core=core_name(z)
    required=["meta.xml",core,"verbatim_occurrence.txt"]
    missing=[n for n in required if n not in z.namelist()]
    if missing: raise RuntimeError(f"missing inner files {missing}")
    return {
      "zip_sha256":hashlib.sha256(data).hexdigest(),
      "zip_bytes":len(data),
      "core_filename":core,
      "inner":{
        n:{
          "sha256":hashlib.sha256(z.read(n)).hexdigest(),
          "bytes":len(z.read(n))
        } for n in required
      }
    }

def main():
    first=snapshot(fetch())
    time.sleep(2)
    second=snapshot(fetch())
    same_core=first["core_filename"]==second["core_filename"]
    stable={}
    for n in first["inner"]:
        stable[n]=(
          n in second["inner"]
          and first["inner"][n]["sha256"]==second["inner"][n]["sha256"]
        )
    result={
      "audit":"frogid_v6_inner_file_identity_v0_1",
      "source_url":URL,
      "first":first,
      "second":second,
      "zip_sha_equal":first["zip_sha256"]==second["zip_sha256"],
      "core_filename_equal":same_core,
      "inner_file_stability":stable,
      "identity_gate_pass":same_core and all(stable.values()),
      "biological_values_read":False,
      "weather_values_read":False
    }
    Path("frog_frogid_source_identity_v0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
