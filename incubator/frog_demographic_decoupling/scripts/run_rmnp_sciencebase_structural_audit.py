#!/usr/bin/env python3
"""Outcome-blind file/schema audit for USGS RMNP amphibian ScienceBase release.

This script may inspect file metadata, tabular headers, categorical stage/method labels,
site/date identifiers and structural replication. It must not report biological
abundance values or adult-to-reproductive associations.
"""
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request, zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ITEM_ID="657ca143d34e23d35331ce9d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
TAXA={"Pseudacris maculata","Lithobates sylvaticus","Ambystoma mavortium"}
YEAR_MIN=2003
NUMERIC_SENSITIVE=re.compile(r"(count|number|abund|quantity|total|n$)",re.I)
STAGE_HINT=re.compile(r"(stage|age|life|egg|larv|tad|adult|juven|meta|aural|call|detect|method|survey)",re.I)
SITE_HINT=re.compile(r"(site|wetland|waterbody|water_body|pond|location|station)",re.I)
DATE_HINT=re.compile(r"(date|year|visit|survey)",re.I)
SPECIES_HINT=re.compile(r"(species|scientific|taxon)",re.I)


def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-structural-audit/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-structural-audit/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()


def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")


def read_tables(name,data):
    low=name.lower()
    if low.endswith(".zip"):
        out=[]
        z=zipfile.ZipFile(io.BytesIO(data))
        for member in z.namelist():
            ml=member.lower()
            if ml.endswith(".csv") or ml.endswith(".txt") or ml.endswith(".tsv"):
                out.extend(read_tables(member,z.read(member)))
        return out
    if not (low.endswith(".csv") or low.endswith(".txt") or low.endswith(".tsv")):
        return []
    text=data.decode("utf-8-sig",errors="replace")
    sample=text[:10000]
    try:
        dialect=csv.Sniffer().sniff(sample,delimiters=",\t;|")
    except Exception:
        dialect=csv.excel_tab if "\t" in sample else csv.excel
    reader=csv.DictReader(io.StringIO(text),dialect=dialect)
    rows=list(reader)
    return [(name,reader.fieldnames or [],rows)]


def maybe_year(v):
    if v is None: return None
    s=str(v).strip()
    if not s: return None
    m=re.search(r"(19|20)\d{2}",s)
    if not m: return None
    y=int(m.group(0))
    return y if 1900 <= y <= 2100 else None


def main():
    item=get_json(ITEM_URL)
    files=item.get("files") or []
    inventory=[]
    tables=[]
    for f in files:
        name=f.get("name") or ""
        url=file_url(f)
        rec={
            "name":name,
            "size":f.get("size"),
            "contentType":f.get("contentType"),
            "has_download_uri":bool(url)
        }
        if url and any(name.lower().endswith(ext) for ext in (".csv",".txt",".tsv",".zip")):
            data=get_bytes(url)
            rec["sha256"]=hashlib.sha256(data).hexdigest()
            rec["downloaded_bytes"]=len(data)
            tables.extend(read_tables(name,data))
        inventory.append(rec)

    table_receipts=[]
    global_site_year_visits=defaultdict(set)
    taxon_stage_labels=defaultdict(Counter)
    taxon_rows=Counter()
    discovered_taxa=set()

    for name,headers,rows in tables:
        # Structural candidate columns only. Sensitive numeric value columns are never read.
        species_cols=[h for h in headers if SPECIES_HINT.search(h or "")]
        site_cols=[h for h in headers if SITE_HINT.search(h or "")]
        date_cols=[h for h in headers if DATE_HINT.search(h or "")]
        stage_cols=[
            h for h in headers
            if STAGE_HINT.search(h or "") and not NUMERIC_SENSITIVE.search(h or "")
        ]

        categorical_values={h:Counter() for h in stage_cols}
        table_taxon_rows=Counter()
        site_year_visit=defaultdict(set)

        for idx,row in enumerate(rows):
            species=""
            for h in species_cols:
                v=(row.get(h) or "").strip()
                if v in TAXA:
                    species=v
                    break
            if species:
                discovered_taxa.add(species)
                taxon_rows[species]+=1
                table_taxon_rows[species]+=1
                for h in stage_cols:
                    v=(row.get(h) or "").strip()
                    if v:
                        # categorical only; redact strings that parse as pure numeric
                        try:
                            float(v)
                            numeric=True
                        except ValueError:
                            numeric=False
                        if not numeric:
                            categorical_values[h][v]+=1
                            taxon_stage_labels[species][f"{h}={v}"]+=1

            site=""
            for h in site_cols:
                v=(row.get(h) or "").strip()
                if v:
                    site=v
                    break
            year=None
            visit=""
            for h in date_cols:
                v=(row.get(h) or "").strip()
                if year is None:
                    year=maybe_year(v)
                if v and ("visit" in h.lower() or "survey" in h.lower() or "date" in h.lower()):
                    visit=v
                    if "date" in h.lower():
                        break
            if site and year and year>=YEAR_MIN:
                token=visit or str(idx)
                site_year_visit[(site,year)].add(token)
                global_site_year_visits[(site,year)].add(token)

        table_receipts.append({
            "name":name,
            "headers":headers,
            "species_candidate_columns":species_cols,
            "site_candidate_columns":site_cols,
            "date_visit_candidate_columns":date_cols,
            "stage_method_candidate_columns":stage_cols,
            "categorical_stage_method_values":{
                h:dict(sorted(c.items()))
                for h,c in categorical_values.items()
            },
            "target_taxon_row_counts":dict(sorted(table_taxon_rows.items())),
            "post2002_site_years":len(site_year_visit),
            "post2002_site_years_ge2_visits":sum(len(v)>=2 for v in site_year_visit.values())
        })

    retained_structurally=[]
    for sp in sorted(discovered_taxa):
        labels=" ".join(taxon_stage_labels[sp]).lower()
        has_upstream=any(x in labels for x in ("adult","aural","call"))
        has_downstream=any(x in labels for x in ("egg","larv","tad"))
        if has_upstream and has_downstream:
            retained_structurally.append(sp)

    result={
        "audit":"rmnp_sciencebase_structural_v0_1",
        "sciencebase_item_id":ITEM_ID,
        "title":item.get("title"),
        "file_inventory":inventory,
        "table_receipts":table_receipts,
        "target_taxa_discovered":sorted(discovered_taxa),
        "target_taxon_row_counts":dict(sorted(taxon_rows.items())),
        "target_taxon_stage_label_counts":{
            sp:dict(sorted(c.items()))
            for sp,c in sorted(taxon_stage_labels.items())
        },
        "post2002_site_years":len(global_site_year_visits),
        "post2002_site_years_ge2_visits":sum(len(v)>=2 for v in global_site_year_visits.values()),
        "taxa_with_explicit_upstream_and_downstream_labels":retained_structurally,
        "structural_gate_pass":(
            len(global_site_year_visits)>=100
            and sum(len(v)>=2 for v in global_site_year_visits.values())>=50
            and len(retained_structurally)>=2
        ),
        "abundance_values_read":False,
        "adult_reproductive_association_opened":False,
        "environment_effect_direction_opened":False
    }
    out=Path("frog_rmnp_sciencebase_structural_v0_1.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__=="__main__":
    main()
