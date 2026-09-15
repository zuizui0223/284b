# Paper 1 bibliography audit v0.1

**Purpose:** submission-hygiene audit for the v0.9 Ecology Letters Method candidate. This file verifies bibliographic metadata and separates direct conceptual antecedents from complementary examples. It changes no empirical claim.

## Direct antecedents / method positioning

| Reference | Verified metadata for final bibliography | Manuscript role | Audit decision |
|---|---|---|---|
| Nelsen 2006 | Nelsen RB. 2006. *An Introduction to Copulas*, 2nd ed. Springer Series in Statistics. Springer, New York. DOI `10.1007/0-387-28678-0`. | Classical Fréchet–Hoeffding / copula bounds. | **Keep.** State explicitly that the bounds are established mathematics. |
| Wilkinson et al. 2021 | Wilkinson DP, Golding N, Guillera-Arroita G, Tingley R, McCarthy MA. 2021. Defining and evaluating predictions of joint species distribution models. *Methods in Ecology and Evolution* 12:394–404. DOI `10.1111/2041-210X.13518`. | JSDMs already distinguish marginal and joint prediction. | **Keep.** Essential concession: joint statistical structure is not being claimed as novel. |
| Pacifici et al. 2017 | Pacifici K, Reich BJ, Miller DAW, Gardner B, Stauffer GE, Singh S, McKerrow A, Collazo JA. 2017. Integrating multiple data sources in species distribution modeling: a framework for data fusion. *Ecology* 98:840–850. DOI `10.1002/ecy.1710`. | Established heterogeneous-source data fusion. | **Keep.** Use to distinguish upstream data integration from downstream relation authorization. |
| Blanchet et al. 2020 | Blanchet FG, Cazelles K, Gravel D. 2020. Co-occurrence is not evidence of ecological interactions. *Ecology Letters* 23:1050–1063. DOI `10.1111/ele.13525`. | Direct antecedent for statistical co-occurrence not determining biological interaction semantics. | **Add to main-text antecedent paragraph.** This is a more direct support for the semantic distinction than Galiana 2024 alone. |
| Galiana et al. 2024 | Galiana N, Arnoldi J-F, Mestre F, Rozenfeld A, Araújo MB. 2024. Power laws in species' biotic interaction networks can be inferred from co-occurrence data. *Nature Ecology & Evolution* 8:209–217. DOI `10.1038/s41559-023-02254-y`. | Example that co-occurrence may contain information about interaction structure. | **Retain as complementary, not primary caution citation.** Pairing with Blanchet 2020 avoids implying that co-occurrence and interaction are interchangeable. |
| Chadwick et al. 2024 | Chadwick FJ, Haydon DT, Husmeier D, Ovaskainen O, Matthiopoulos J. 2024. LIES of omission: complex observation processes in ecology. *Trends in Ecology & Evolution* 39:368–380. DOI `10.1016/j.tree.2023.10.009`. | Observation-process Latency, Identifiability, Effort and Scale. | **Keep.** Closest observation-process conceptual antecedent; novelty must remain downstream relation authorization. |
| Getz et al. 2018 | Getz WM, Marshall CR, Carlson CJ, Giuggioli L, Ryan SJ, Romañach SS, Boettiger C, Chamberlain SD, Larsen L, D'Odorico P, O'Sullivan D. 2018. Making ecological models adequate. *Ecology Letters* 21:153–166. DOI `10.1111/ele.12893`. | Model adequacy / data determinacy. | **Keep.** Explicitly concede upstream adequacy as established. |
| Gould et al. 2026 | Gould E, Jones CS, Yen JDL, Fraser HS, Wootton HF, Good MK, Duncan DH, Hauser CE, Wintle BC, Rumpff L. 2026. ‘But I can't preregister my research’: Improving the reproducibility and transparency of ecology and conservation with adaptive preregistration for model-based research. *Methods in Ecology and Evolution* 17(6):1768–1787. DOI `10.1111/2041-210X.70311`. | Modern ecology-specific adaptive preregistration antecedent. | **Keep, update final bibliography from “Gould et al.” working shorthand to full metadata.** |

## Observation/detection and empirical-context references

| Reference | Verified metadata | Role |
|---|---|---|
| MacKenzie et al. 2004 | *Journal of Animal Ecology* 73:546–555. DOI `10.1111/j.0021-8790.2004.00828.x`. | Co-occurrence under imperfect detection. |
| Guillera-Arroita 2017 | *Ecography* 40:281–295. DOI `10.1111/ecog.02445`. | Distribution/range/community modelling under imperfect detection. |
| Guillera-Arroita et al. 2017 | *Methods in Ecology and Evolution* 8:1081–1091. DOI `10.1111/2041-210X.12743`. | False-positive and false-negative occurrence errors. |
| Rota et al. 2016 | *Methods in Ecology and Evolution* 7:1164–1173. DOI `10.1111/2041-210X.12587`. | Multispecies occupancy for interacting species. |
| Weinstein & Graham 2017 | *Food Webs* 11:17–25. DOI `10.1016/j.fooweb.2017.05.002`. | Missed interactions versus true non-occurrence. |
| Erickson & Smith 2021 | *Ecography* 44:1341–1352. DOI `10.1111/ecog.05679`. | Museum/herbarium data and imperfect detection/bias correction. |
| Matutini et al. 2021 | Matutini F, Baudry J, Pain G, Sineau M, Pithon J. *Ecology and Evolution* 11:3028–3039. DOI `10.1002/ece3.7210`. | Citizen-science data and independent SDM assessment. |
| Gaier & Resasco 2023 | *Ecosphere* 14:e4419. DOI `10.1002/ecs2.4419`. | Community-science observations added to museum records for SDM. |

## Citation-placement repair for the v0.9 manuscript

The relation-layer paragraph should use the following logic:

> A suitable JSDM can estimate joint statistical structure (Wilkinson et al. 2021), but co-occurrence and statistical association are not themselves evidence of a biological interaction (Blanchet et al. 2020). Co-occurrence can nevertheless contain information about interaction-network structure under explicit assumptions (Galiana et al. 2024). The remaining relation-endpoint question is therefore semantic and biological: which joint relation is licensed, at what event key, and what state counts as support or contradiction?

This is stronger than citing Galiana 2024 alone because it concedes both sides of the antecedent literature: statistical joint structure can be informative, while biological interaction semantics require additional justification.

## No-change findings

- DOI/title/year metadata checked above are internally consistent with the current manuscript references.
- The central novelty boundary remains unchanged: the paper does **not** claim novelty for imperfect detection, JSDMs, data fusion, model adequacy, observation-process identifiability or preregistration.
- No reference audit result changes Level-A, Level-B or Level-C endpoint state; empirical ledger increment = 0.
