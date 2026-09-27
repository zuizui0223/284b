#!/usr/bin/env python3
from __future__ import annotations
import hashlib, io, json, re, urllib.request, zipfile
from pathlib import Path

URL="https://dwca-exports.ala.org.au/dr24697.zip"
EXPECTED_SHA="ef55f7fc903583ade788d2ed0c32668bc6a9a48fca8706c07a706e365fa6d97b"
CODES=["HEA","SEE","HAN","SHD","OPP"]

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"frog-sunshine-semantic-audit/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def snippets(text,code,window=300):
    out=[]
    lower=text.lower()
    target=code.lower()
    pos=0
    while True:
        i=lower.find(target,pos)
        if i<0: break
        lo=max(0,i-window); hi=min(len(text),i+len(code)+window)
        out.append(" ".join(text[lo:hi].split()))
        pos=i+len(code)
        if len(out)>=20: break
    return out

def main():
    data=fetch()
    sha=hashlib.sha256(data).hexdigest()
    if sha!=EXPECTED_SHA:
        raise SystemExit(f"source hash drift: {sha}")
    z=zipfile.ZipFile(io.BytesIO(data))
    names=z.namelist()

    documentation={}
    for name in names:
        low=name.lower()
        if not any(k in low for k in ("readme","metadata","eml","data_package","datapackage","xml","json","txt","md")):
            continue
        try:
            raw=z.read(name)
            text=raw.decode("utf-8",errors="replace")
        except Exception:
            continue
        hits={}
        for code in CODES:
            s=snippets(text,code)
            if s: hits[code]=s
        if hits:
            documentation[name]=hits

    result={
      "audit":"sunshine_coast_call_code_metadata_v0_1",
      "source_sha256":sha,
      "archive_files":names,
      "documentation_code_hits":documentation,
      "codes_sought":CODES,
      "call_semantics_opened_from_outcomes":False,
      "rainfall_values_read":False,
      "weather_synchrony_association_opened":False
    }
    Path("frog_sunshine_call_code_metadata_v0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
