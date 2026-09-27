# RMNP stage-code receipt v0.2

The fixed ScienceBase CSV has **1177 post-2002 site-years**, including **577** with at least two visits.

Publisher FGDC metadata explicitly defines:
- `A` = Adult
- `E` = Egg / Egg Mass
- `L` = Larva
- `M` = Metamorph (frogs)
- `P` = Paedomorph (tiger salamander)

All three focal taxa have observed adult and downstream stage codes. Marginal structural coverage after 2002 is:

| Taxon | Adult site-years | Egg site-years | Larva site-years |
|---|---:|---:|---:|
| *Pseudacris maculata* | 77 | 13 | 42 |
| *Lithobates sylvaticus* | 7 | 9 | 16 |
| *Ambystoma mavortium* | 12 | 13 | 4 |

The v0.10.2 gate failed only because some raw cells contain comma-separated combinations such as `A, E`, `A, L`, or `J, L`. These are not new undocumented biological categories; they are combinations of documented stage tokens.

No adult→downstream joint-state association or environmental effect has been opened.

## Prospective repair

v0.10.3 will split stage strings on commas, trim whitespace, and require **every resulting token** to be one of the publisher-documented codes. No other normalization is permitted.

## Primary-species decision

Before any joint-state outcome is opened, *Pseudacris maculata* is selected as the confirmatory primary taxon **solely from structural stage coverage**. It has substantially more adult and larval site-years than the other two taxa.

*Lithobates sylvaticus* is reserved as a parallel validation taxon if its normalized stage structure remains estimable. *Ambystoma mavortium* is biologically less comparable because paedomorphosis changes adult-stage semantics and is therefore secondary only.
