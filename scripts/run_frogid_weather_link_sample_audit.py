#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, math, re, urllib.request, zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

URL="https://dwca-exports.ala.org.au/dr14760.zip"
SOURCE_SHA="f5dd70ed07956e3e37de4fb04692b83a9d726eae2312767c9eda2dcbf61f759d"
NS={"dwc":"http://rs.tdwg.org/dwc/text/"}

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"frogid-weather-link-structural-audit/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()

def local_term(term):
    return term.rsplit("/",1)[-1].rsplit("#",1)[-1] if term else ""

def dec(v,default):
    if v is None:return default
    return bytes(v,"utf-8").decode("unicode_escape")

def core_rows(zf):
    meta=ET.fromstring(zf.read("meta.xml"))
    core=meta.find("dwc:core",NS)
    files=core.find("dwc:files",NS); loc=files.find("dwc:location",NS)
    fn=loc.text.strip()
    fields={local_term(f.attrib.get("term","")):int(f.attrib["index"]) for f in core.findall("dwc:field",NS)}
    delim=dec(core.attrib.get("fieldsTerminatedBy"),"\t")
    quote=dec(core.attrib.get("fieldsEnclosedBy"),'"')
    ignore=int(core.attrib.get("ignoreHeaderLines","0"))
    enc=core.attrib.get("encoding","UTF-8").replace("-","")
    reader=csv.reader(io.StringIO(zf.read(fn).decode(enc,errors="replace")),delimiter=delim,quotechar=quote or '"')
    for _ in range(ignore):next(reader,None)
    return fields,reader

def get(row,fields,name):
    i=fields.get(name)
    return row[i].strip() if i is not None and i<len(row) else ""

def selected(event):
    return hashlib.sha256(event.encode("utf-8")).digest()[0] < 16

def cell(x):
    return round(x*4.0)/4.0

def main():
    data=fetch()
    if hashlib.sha256(data).hexdigest()!=SOURCE_SHA:
        raise SystemExit("FrogID archive hash drift")
    z=zipfile.ZipFile(io.BytesIO(data))
    fields,reader=core_rows(z)

    # Build selected event metadata and species without using weather.
    events={}
    species=defaultdict(set)
    recorder_events=set()
    uncertainty_hist=Counter()

    for row in reader:
        event=get(row,fields,"eventID")
        if not event or not selected(event):
            continue
        sp=get(row,fields,"scientificName")
        if sp: species[event].add(sp)
        if event in events:
            continue

        try:
            lat=float(get(row,fields,"decimalLatitude"))
            lon=float(get(row,fields,"decimalLongitude"))
            unc=float(get(row,fields,"coordinateUncertaintyInMeters"))
        except Exception:
            continue
        if not(-90<=lat<=90 and -180<=lon<=180):
            continue
        if not math.isfinite(unc) or unc>25000:
            continue

        date=get(row,fields,"eventDate")
        state=get(row,fields,"stateProvince")
        time=get(row,fields,"eventTime")
        recorder=get(row,fields,"recordedBy")
        if not date or not state:
            continue

        events[event]={
          "lat":lat,"lon":lon,"cell_lat":cell(lat),"cell_lon":cell(lon),
          "date":date,"time":time,"state":state,"recorder":recorder,
          "uncertainty_m":unc
        }
        uncertainty_hist[str(int(unc) if unc.is_integer() else unc)]+=1
        if recorder: recorder_events.add(event)

    # Species rows can precede/continue after the first event metadata row; discard
    # selected species sets for events that failed the structural filters.
    kept=set(events)
    richness=Counter()
    weather_cells=Counter()
    states=Counter()
    years=Counter()
    time_parseable=0
    multi=0
    for event,m in events.items():
        r=len(species.get(event,set()))
        if r<1:
            continue
        richness[r]+=1
        if r>=2:multi+=1
        weather_cells[(m["cell_lat"],m["cell_lon"])]+=1
        states[m["state"]]+=1
        ymatch=re.search(r"(?:19|20)\d{2}",m["date"])
        if ymatch: years[int(ymatch.group(0))]+=1
        if re.search(r"\d{1,2}:\d{2}",m["time"] or ""): time_parseable+=1

    n=sum(richness.values())
    result={
      "audit":"frogid_weather_link_sample_structural_v0_1",
      "sample_rule":"SHA256(eventID)[0] < 16",
      "max_coordinate_uncertainty_m":25000,
      "retained_recordings":n,
      "multispecies_recordings":multi,
      "richness_histogram":{str(k):v for k,v in sorted(richness.items())},
      "weather_cells_0p25deg":len(weather_cells),
      "weather_cell_event_count_summary":{
        "min":min(weather_cells.values()) if weather_cells else 0,
        "max":max(weather_cells.values()) if weather_cells else 0,
        "median":sorted(weather_cells.values())[len(weather_cells)//2] if weather_cells else 0
      },
      "state_counts":dict(sorted(states.items())),
      "year_counts":dict(sorted(years.items())),
      "event_time_parseable_fraction":time_parseable/n if n else 0,
      "recordedBy_coverage_fraction":len(recorder_events & kept)/n if n else 0,
      "structural_sample_gate_pass":(
        n>=25000 and multi>=10000 and len(weather_cells)>=200 and len(weather_cells)<=8000
      ),
      "weather_values_read":False,
      "weather_synchrony_association_opened":False
    }
    Path("frog_frogid_weather_link_sample_v0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
