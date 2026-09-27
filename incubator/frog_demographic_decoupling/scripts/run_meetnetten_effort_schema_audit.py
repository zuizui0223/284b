#!/usr/bin/env python3
"""Inspect only the MeasurementOrFact schema/coverage in fixed downstream DwC-A v1.24.

Forbidden: occurrence individualCount, adult/larval abundance associations, effect directions.
Allowed: extension row types, measurementType labels, non-empty indicator, event coverage.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

URL = "https://ipt.inbo.be/archive.do?r=meetnetten-amfibieen-larven-metamorfen-occurrences&v=1.24"
EXPECTED_SHA256 = "c2cc960122ea398545edb661318160cd2b5b66a75a73dba8f7a3f61bd9c4f920"
NS = {"dwc":"http://rs.tdwg.org/dwc/text/"}


def download() -> bytes:
    req=urllib.request.Request(URL,headers={"User-Agent":"frog-effort-schema-audit/0.1"})
    with urllib.request.urlopen(req,timeout=60) as response:
        return response.read()


def local(term:str)->str:
    return term.rsplit("/",1)[-1].rsplit("#",1)[-1] if term else ""


def dec(value, default):
    if value is None:
        return default
    return bytes(value,"utf-8").decode("unicode_escape")


def rows(zf, section):
    files=section.find("dwc:files",NS)
    loc=files.find("dwc:location",NS)
    filename=loc.text.strip()
    delimiter=dec(section.attrib.get("fieldsTerminatedBy"),"\t")
    quote=dec(section.attrib.get("fieldsEnclosedBy"),'"')
    ignore=int(section.attrib.get("ignoreHeaderLines","0"))
    encoding=section.attrib.get("encoding","UTF-8").replace("-","")
    coreid=section.find("dwc:coreid",NS)
    coreid_index=int(coreid.attrib["index"]) if coreid is not None else None
    fields={local(f.attrib.get("term","")):int(f.attrib["index"]) for f in section.findall("dwc:field",NS)}
    reader=csv.reader(io.StringIO(zf.read(filename).decode(encoding)),delimiter=delimiter,quotechar=quote or '"')
    for _ in range(ignore):
        next(reader,None)
    for row in reader:
        yield row,fields,coreid_index


def get(row, fields, name):
    idx=fields.get(name)
    if idx is None or idx>=len(row):
        return ""
    return row[idx].strip()


def main():
    data=download()
    sha=hashlib.sha256(data).hexdigest()
    if sha != EXPECTED_SHA256:
        raise SystemExit(f"source hash drift: {sha}")
    zf=zipfile.ZipFile(io.BytesIO(data))
    meta=ET.fromstring(zf.read("meta.xml"))

    extension_summary=[]
    mof=None
    for ext in meta.findall("dwc:extension",NS):
        row_type=ext.attrib.get("rowType","")
        field_names=sorted(local(f.attrib.get("term","")) for f in ext.findall("dwc:field",NS))
        extension_summary.append({"rowType":row_type,"fields":field_names})
        if "MeasurementOrFact" in row_type:
            mof=ext

    if mof is None:
        result={
            "audit":"meetnetten_effort_schema_v0_1",
            "source_sha256":sha,
            "measurement_extension_found":False,
            "extensions":extension_summary,
            "occurrence_abundance_read":False,
            "ecological_association_opened":False
        }
    else:
        type_rows=Counter()
        type_nonempty=Counter()
        type_events=defaultdict(set)
        type_nonempty_events=defaultdict(set)
        for row,fields,coreid_index in rows(zf,mof):
            measurement_type=get(row,fields,"measurementType")
            measurement_value=get(row,fields,"measurementValue")
            core_id=row[coreid_index].strip() if coreid_index is not None else ""
            type_rows[measurement_type]+=1
            type_events[measurement_type].add(core_id)
            if measurement_value!="":
                type_nonempty[measurement_type]+=1
                type_nonempty_events[measurement_type].add(core_id)

        result={
            "audit":"meetnetten_effort_schema_v0_1",
            "source_sha256":sha,
            "measurement_extension_found":True,
            "extensions":extension_summary,
            "measurement_types":{
                key:{
                    "rows":type_rows[key],
                    "nonempty_value_rows":type_nonempty[key],
                    "event_count":len(type_events[key]),
                    "events_with_nonempty_value":len(type_nonempty_events[key])
                }
                for key in sorted(type_rows)
            },
            "number_of_sweeps_exact_label_present":"number of sweeps" in type_rows,
            "number_of_sweeps_nonempty_events":len(type_nonempty_events["number of sweeps"]),
            "occurrence_abundance_read":False,
            "ecological_association_opened":False,
            "environment_effect_direction_opened":False
        }

    out=Path("frog_meetnetten_effort_schema_v0_1.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__=="__main__":
    main()
