#!/usr/bin/env python3
"""Build a noncanonical invited-manuscript v0.8 candidate from frozen v0.7.

This builder is intentionally prospective. It does not alter PREFIELD_FLAGSHIP_V0_7.md
and does not open any Level-C focal values. It only applies the editorial/method
integration already frozen in Stage-1 proposal assets:

- promote the relation-endpoint title;
- add the formal relation-layer separation paragraph using classical
  Frechet-Hoeffding bounds;
- explicitly position JSDMs/data fusion/co-occurrence as antecedent/upstream layers;
- add the corresponding references.

The generated candidate is not canonical unless an Ecology Letters Method invitation
is received and a subsequent promotion audit explicitly authorizes it.
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_7.md"
DEFAULT_OUT = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_8_CANDIDATE.md"

OLD_TITLE = "Prospective validation of ecological answers: from cross-source reproducibility to identifiable biological absence"
NEW_TITLE = "Relation endpoints for ecological inference: when independent answers can support joint biological claims"

INTRO_ANTECEDENT_ANCHOR = (
    "The ingredients are established. Occupancy models separate latent ecological state from observation "
    "(MacKenzie et al. 2004; Guillera-Arroita 2017), multispecies models accommodate co-occurrence under imperfect "
    "detection (Rota et al. 2016), and interaction work distinguishes missed interactions from non-occurrence "
    "(Weinstein & Graham 2017). Getz et al. (2018) made model adequacy and data determinacy explicit methodological "
    "concerns. Chadwick et al. (2024) systematized observation-process problems through LIES—Latency, Identifiability, "
    "Effort and Scale. Preregistration and Registered Reports separately establish outcome-blind design. We therefore "
    "do **not** claim novelty for imperfect detection, observation-process identifiability, model adequacy, external "
    "validation or prospectivity."
)

INTRO_ANTECEDENT_REPLACEMENT = (
    "The ingredients are established. Occupancy models separate latent ecological state from observation "
    "(MacKenzie et al. 2004; Guillera-Arroita 2017), multispecies models accommodate co-occurrence under imperfect "
    "detection (Rota et al. 2016), and interaction work distinguishes missed interactions from non-occurrence "
    "(Weinstein & Graham 2017). Data-fusion methods combine heterogeneous observation sources for common latent "
    "inference (Pacifici et al. 2017), while joint species distribution models distinguish marginal from joint "
    "prediction (Wilkinson et al. 2021). Getz et al. (2018) made model adequacy and data determinacy explicit "
    "methodological concerns. Chadwick et al. (2024) systematized observation-process problems through LIES—Latency, "
    "Identifiability, Effort and Scale. Preregistration and Registered Reports separately establish outcome-blind "
    "design. We therefore do **not** claim novelty for imperfect detection, joint-distribution modelling, data fusion, "
    "observation-process identifiability, model adequacy, external validation or prospectivity."
)

OLD_SOFT_HEADING = "### 2.2 Soft coherence and hard dependency"
SEPARATION_SECTION = r"""### 2.2 Why accurate answers do not eliminate the relation layer

Even exact role-specific marginal answers need not identify a directional biological endpoint. Let `p_E=P(E=1)` and `p_F=P(F=1)` be perfectly known marginals for a dependent event and required function, and let `v=P(E=1,F=0)` be the hard-violation probability. Classical Fréchet–Hoeffding coupling bounds imply

`max(0,p_E-p_F) <= v <= min(p_E,1-p_F)`.

At `p_E=p_F=0.5`, the same perfect marginal answers admit both `v=0`, for which `E -> F` holds, and `v=0.5`, for which every positive `E` key violates it (Nelsen 2006). This is a separation argument using established probability theory, not a new coupling theorem. A JSDM can estimate joint rather than marginal structure (Wilkinson et al. 2021), but statistical coupling still does not by itself choose whether the licensed ecological endpoint is co-occurrence, interaction or a directional functional dependency (cf. Galiana et al. 2024). The endpoint contract supplies that biological relation, common key and contradiction rule.

### 2.3 Soft coherence and hard dependency"""

REFERENCE_INSERTIONS = [
    "- Galiana N, Arnoldi J-F, Mestre F, Rozenfeld A, Araújo MB. 2024. Power laws in species' biotic interaction networks can be inferred from co-occurrence data. *Nature Ecology & Evolution* 8:209–217. doi:10.1038/s41559-023-02254-y.",
    "- Nelsen RB. 2006. *An Introduction to Copulas*, 2nd ed. Springer Series in Statistics. Springer, New York. doi:10.1007/0-387-28678-0.",
    "- Pacifici K, Reich BJ, Miller DAW, Gardner B, Stauffer G, Singh S, McKerrow A, Collazo JA. 2017. Integrating multiple data sources in species distribution modeling: a framework for data fusion. *Ecology* 98:840–850. doi:10.1002/ecy.1710.",
    "- Wilkinson DP, Golding N, Guillera-Arroita G, Tingley R, McCarthy MA. 2021. Defining and evaluating predictions of joint species distribution models. *Methods in Ecology and Evolution* 12:394–404. doi:10.1111/2041-210X.13518.",
]


def build_candidate(source_text: str) -> str:
    if source_text.count(OLD_TITLE) < 1:
        raise ValueError("v0.7 title anchor not found")
    if source_text.count(INTRO_ANTECEDENT_ANCHOR) != 1:
        raise ValueError("introduction antecedent anchor changed; manual audit required")
    if source_text.count(OLD_SOFT_HEADING) != 1:
        raise ValueError("section 2.2 anchor changed; manual audit required")
    if "## Working references" not in source_text:
        raise ValueError("working-reference section not found")

    out = source_text.replace(OLD_TITLE, NEW_TITLE, 1)
    out = out.replace(
        "**Stage:** pre-field manuscript v0.7 — Reviewer-2 hardened",
        "**Stage:** invited-manuscript candidate v0.8 — not canonical until invitation/promotion audit",
        1,
    )
    out = out.replace(INTRO_ANTECEDENT_ANCHOR, INTRO_ANTECEDENT_REPLACEMENT, 1)
    out = out.replace(OLD_SOFT_HEADING, SEPARATION_SECTION, 1)

    refs_anchor = "## Working references\n"
    insertion = refs_anchor + "\n" + "\n".join(REFERENCE_INSERTIONS) + "\n"
    out = out.replace(refs_anchor, insertion, 1)

    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    source_text = args.source.read_text(encoding="utf-8")
    candidate = build_candidate(source_text)
    args.out.write_text(candidate, encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
