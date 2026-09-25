#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"incubator"/"frog_chorus_synchrony"
MS=BASE/"MANUSCRIPT_JAE_V0_3.md"
text=MS.read_text(encoding="utf-8")

def words(s):
    return re.findall(r"\b[\w’'-]+\b",s)

m=re.search(r"## Abstract\n(.*?)\n## Keywords",text,re.S)
assert m, "abstract block missing"
abstract=m.group(1)
abstract_words=len(words(abstract))
assert abstract_words<=350, f"abstract too long: {abstract_words}"
for i in range(1,6):
    assert re.search(rf"(?m)^{i}\. ",abstract), f"missing numbered abstract point {i}"

km=re.search(r"## Keywords\n\n([^\n]+)",text)
assert km, "keywords missing"
keywords=[x.strip() for x in km.group(1).split(";") if x.strip()]
assert len(keywords)<=8, f"too many keywords: {len(keywords)}"
assert keywords==sorted(keywords,key=str.lower), "keywords must be alphabetical"

total=len(words(text))
assert total<=8500, f"manuscript exceeds JAE 8500-word initial-submission limit: {total}"
for section in ["## Introduction","## Materials and Methods","## Results","## Discussion","## Data Availability","## References","## Figure legends"]:
    assert section in text, f"missing section {section}"

assert "ZHANG" not in text.upper()
assert "@" not in text, "main manuscript must not contain email addresses"
assert "Rainfall predicts greater short-window co-calling" not in text  # guard old title fragment
assert "Recent rainfall predicts greater short-window co-calling" in text
assert "10.5066/F7G44NG0" in text
assert "10.15468/wazqft" in text
assert "10.1002/qj.3803" in text
assert "Zenodo" in text
assert "Figure 1." in text and "Figure 2." in text

print({
    "abstract_words":abstract_words,
    "keywords":len(keywords),
    "total_words":total,
    "jae_initial_word_limit":8500,
    "status":"PASS",
})
