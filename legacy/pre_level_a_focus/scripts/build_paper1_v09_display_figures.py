#!/usr/bin/env python3
"""Build the two Paper-1 v0.9 display figures whose logic changed after manuscript sharpening.

This builder is editorial only. It reads no focal Level-C values and does not modify
any frozen empirical receipt. Figure 1 emphasizes the executable/fingerprintable
relation-endpoint contract. Figure 3 combines the classical relation-layer separation
argument with the event/function semantics needed for directional dependency.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manuscript" / "figures"

STYLE = """<style>text{font-family:Arial,sans-serif;fill:#111}.h{font-size:24px;font-weight:bold}.sh{font-size:18px;font-weight:bold}.b{font-size:14px}.s{font-size:12px}.xs{font-size:10.5px}.n{font-size:26px;font-weight:bold}.box{fill:white;stroke:#333;stroke-width:1.4}.soft{fill:#f7f7f7;stroke:#777;stroke-width:1.1}.dashbox{fill:white;stroke:#777;stroke-width:1.1;stroke-dasharray:5 4}.arrow{stroke:#222;stroke-width:1.7;fill:none;marker-end:url(#m)}.dash{stroke:#777;stroke-width:1.3;stroke-dasharray:5 4;fill:none;marker-end:url(#m)}.cell{fill:white;stroke:#555;stroke-width:1.1}.hit{fill:#efefef;stroke:#333;stroke-width:1.2}</style>
<defs><marker id="m" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#222"/></marker></defs>"""


def figure1() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900">
<rect width="1200" height="900" fill="white"/>
{STYLE}
<text x="45" y="42" class="h">Figure 1. Relation-endpoint authorization is frozen before focal opening</text>
<text x="45" y="70" class="b">Upstream models generate answers; the contract fixes what joint biological claim those answers may test and which states are admissible.</text>

<text x="45" y="112" class="sh">A  Five-part relation-endpoint contract</text>
<rect x="50" y="132" width="1100" height="158" rx="10" class="soft"/>
<rect x="76" y="169" width="186" height="82" rx="7" class="box"/><text x="169" y="196" class="sh" text-anchor="middle">1  Relation</text><text x="169" y="220" class="s" text-anchor="middle">coherence / dependency /</text><text x="169" y="238" class="s" text-anchor="middle">other declared biology</text>
<line x1="262" y1="210" x2="292" y2="210" class="arrow"/>
<rect x="300" y="169" width="186" height="82" rx="7" class="box"/><text x="393" y="196" class="sh" text-anchor="middle">2  Key space</text><text x="393" y="220" class="s" text-anchor="middle">site × opportunity</text><text x="393" y="238" class="s" text-anchor="middle">where relation applies</text>
<line x1="486" y1="210" x2="516" y2="210" class="arrow"/>
<rect x="524" y="169" width="186" height="82" rx="7" class="box"/><text x="617" y="196" class="sh" text-anchor="middle">3  Adapters</text><text x="617" y="220" class="s" text-anchor="middle">role-specific answer →</text><text x="617" y="238" class="s" text-anchor="middle">common relation space</text>
<line x1="710" y1="210" x2="740" y2="210" class="arrow"/>
<rect x="748" y="169" width="186" height="82" rx="7" class="box"/><text x="841" y="196" class="sh" text-anchor="middle">4  Adequacy</text><text x="841" y="220" class="s" text-anchor="middle">is each answer eligible</text><text x="841" y="238" class="s" text-anchor="middle">for this endpoint?</text>
<line x1="934" y1="210" x2="964" y2="210" class="arrow"/>
<rect x="972" y="169" width="154" height="82" rx="7" class="box"/><text x="1049" y="196" class="sh" text-anchor="middle">5  Opening</text><text x="1049" y="220" class="s" text-anchor="middle">calibration +</text><text x="1049" y="238" class="s" text-anchor="middle">state rule</text>

<text x="45" y="338" class="sh">B  Prospectivity is inspectable</text>
<rect x="50" y="358" width="1100" height="145" rx="10" class="soft"/>
<rect x="88" y="395" width="260" height="70" rx="7" class="box"/><text x="218" y="421" class="b" text-anchor="middle">complete validated contract</text><text x="218" y="443" class="s" text-anchor="middle">including opening_rule_reference</text>
<line x1="348" y1="430" x2="430" y2="430" class="arrow"/>
<rect x="440" y="395" width="265" height="70" rx="7" class="box"/><text x="572" y="421" class="b" text-anchor="middle">canonical deterministic JSON</text><text x="572" y="443" class="s" text-anchor="middle">missing/unknown fields rejected</text>
<line x1="705" y1="430" x2="787" y2="430" class="arrow"/>
<rect x="797" y="395" width="300" height="70" rx="7" class="box"/><text x="947" y="421" class="sh" text-anchor="middle">SHA-256 fingerprint</text><text x="947" y="443" class="s" text-anchor="middle">timestampable/versionable audit identity</text>
<text x="600" y="489" class="xs" text-anchor="middle">Fingerprinting makes endpoint drift inspectable; it is not proof that investigators were outcome-blind.</text>

<text x="45" y="554" class="sh">C  The same contract preserves unresolved states for soft and hard endpoints</text>
<rect x="50" y="574" width="530" height="236" rx="10" class="soft"/>
<text x="315" y="605" class="sh" text-anchor="middle">Calibrated soft relation</text>
<rect x="82" y="630" width="160" height="55" rx="7" class="box"/><text x="162" y="653" class="b" text-anchor="middle">adequate answers +</text><text x="162" y="673" class="s" text-anchor="middle">frozen relation ceiling</text>
<line x1="242" y1="658" x2="315" y2="658" class="arrow"/>
<rect x="325" y="630" width="205" height="55" rx="7" class="box"/><text x="427" y="654" class="b" text-anchor="middle">discordance ≤ ceiling?</text><text x="427" y="673" class="s" text-anchor="middle">relation-specific rule</text>
<rect x="92" y="724" width="130" height="50" rx="6" class="box"/><text x="157" y="755" class="s" text-anchor="middle">consistent</text>
<rect x="232" y="724" width="150" height="50" rx="6" class="box"/><text x="307" y="747" class="xs" text-anchor="middle">attention_required</text><text x="307" y="763" class="xs" text-anchor="middle">≠ automatic falsification</text>
<rect x="392" y="724" width="145" height="50" rx="6" class="box"/><text x="464" y="755" class="sh" text-anchor="middle">unresolved</text>

<rect x="625" y="574" width="525" height="236" rx="10" class="soft"/>
<text x="887" y="605" class="sh" text-anchor="middle">Directional hard relation  E(k) → F(k)</text>
<rect x="654" y="630" width="144" height="55" rx="7" class="box"/><text x="726" y="653" class="b" text-anchor="middle">E(k) adequate</text><text x="726" y="673" class="s" text-anchor="middle">and positive?</text>
<line x1="798" y1="658" x2="840" y2="658" class="arrow"/>
<rect x="850" y="630" width="168" height="55" rx="7" class="box"/><text x="934" y="653" class="b" text-anchor="middle">F(k) state</text><text x="934" y="673" class="s" text-anchor="middle">present / absent / unresolved</text>
<line x1="1018" y1="658" x2="1050" y2="658" class="arrow"/>
<rect x="1058" y="630" width="68" height="55" rx="7" class="box"/><text x="1092" y="649" class="xs" text-anchor="middle">negative</text><text x="1092" y="665" class="xs" text-anchor="middle">qualified</text><text x="1092" y="681" class="xs" text-anchor="middle">?</text>
<rect x="649" y="724" width="145" height="50" rx="6" class="box"/><text x="721" y="747" class="xs" text-anchor="middle">E=false</text><text x="721" y="763" class="xs" text-anchor="middle">noninformative</text>
<rect x="804" y="724" width="145" height="50" rx="6" class="box"/><text x="876" y="747" class="xs" text-anchor="middle">F=present</text><text x="876" y="763" class="xs" text-anchor="middle">no violation observed</text>
<rect x="959" y="724" width="168" height="50" rx="6" class="box"/><text x="1043" y="747" class="xs" text-anchor="middle">F=absent + qualified</text><text x="1043" y="763" class="xs" text-anchor="middle">hard violation authorized</text>
<text x="887" y="797" class="s" text-anchor="middle">Any inadequate, missing or unqualified negative remains unresolved.</text>

<rect x="210" y="840" width="780" height="42" rx="8" class="dashbox"/>
<text x="600" y="866" class="b" text-anchor="middle">One layer above model fitting: answer construction first, biological relation authorization second.</text>
</svg>'''


def figure3() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="960" viewBox="0 0 1200 960">
<rect width="1200" height="960" fill="white"/>
{STYLE}
<text x="45" y="42" class="h">Figure 3. Accurate answers do not determine the biological relation they may jointly test</text>
<text x="45" y="70" class="b">The relation layer separates statistical answer quality from biological endpoint semantics.</text>

<text x="45" y="112" class="sh">A  Separation: the same perfect marginals support opposite hard-relation status</text>
<rect x="50" y="132" width="1100" height="318" rx="10" class="soft"/>
<rect x="405" y="154" width="390" height="72" rx="10" class="box"/>
<text x="600" y="180" class="sh" text-anchor="middle">Same exact role-specific answers</text>
<text x="600" y="207" class="n" text-anchor="middle">P(E=1)=0.5   ·   P(F=1)=0.5</text>
<line x1="520" y1="226" x2="315" y2="274" class="arrow"/>
<line x1="680" y1="226" x2="885" y2="274" class="arrow"/>
<text x="300" y="292" class="b" text-anchor="middle">World A: dependency compatible</text>
<text x="900" y="292" class="b" text-anchor="middle">World B: dependency violated</text>
<rect x="215" y="310" width="170" height="72" rx="7" class="box"/><text x="300" y="339" class="n" text-anchor="middle">v=0</text><text x="300" y="365" class="s" text-anchor="middle">P(E=1,F=0)=0</text>
<rect x="815" y="310" width="170" height="72" rx="7" class="box"/><text x="900" y="339" class="n" text-anchor="middle">v=0.5</text><text x="900" y="365" class="s" text-anchor="middle">P(E=1,F=0)=0.5</text>
<text x="600" y="408" class="b" text-anchor="middle">Classical Fréchet–Hoeffding bounds: max(0,pE−pF) ≤ v ≤ min(pE,1−pF)</text>
<text x="600" y="432" class="xs" text-anchor="middle">Established probability theory used as a separation argument, not claimed as a new theorem.</text>

<text x="45" y="500" class="sh">B  Biological authorization: define the dependency at the event where biology makes a prediction</text>
<rect x="50" y="520" width="1100" height="185" rx="10" class="soft"/>
<rect x="84" y="562" width="250" height="88" rx="7" class="dashbox"/><text x="209" y="588" class="b" text-anchor="middle">Rejected shortcut</text><text x="209" y="614" class="s" text-anchor="middle">raw occurrence / suitability</text><text x="209" y="634" class="s" text-anchor="middle">surfaces forced to match</text>
<line x1="334" y1="606" x2="430" y2="606" class="dash"/>
<rect x="440" y="562" width="148" height="88" rx="7" class="box"/><text x="514" y="594" class="sh" text-anchor="middle">E(k)</text><text x="514" y="620" class="s" text-anchor="middle">dependent event</text><text x="514" y="640" class="xs" text-anchor="middle">at opportunity k</text>
<line x1="588" y1="606" x2="676" y2="606" class="arrow"/>
<rect x="686" y="562" width="160" height="88" rx="7" class="box"/><text x="766" y="594" class="sh" text-anchor="middle">F(k)</text><text x="766" y="620" class="s" text-anchor="middle">required function</text><text x="766" y="640" class="xs" text-anchor="middle">at the same key</text>
<rect x="892" y="552" width="225" height="108" rx="7" class="box"/><text x="1004" y="580" class="b" text-anchor="middle">Hard contradiction</text><text x="1004" y="606" class="s" text-anchor="middle">E(k)=true</text><text x="1004" y="628" class="s" text-anchor="middle">AND authorized F(k)=false</text><text x="1004" y="649" class="xs" text-anchor="middle">otherwise unresolved / noninformative</text>
<text x="600" y="686" class="xs" text-anchor="middle">Different roles may legitimately use different estimators, predictors, accessible areas and raw scales upstream.</text>

<text x="45" y="756" class="sh">C  The required function is not automatically one named provider</text>
<rect x="50" y="776" width="1100" height="135" rx="10" class="soft"/>
<rect x="83" y="808" width="310" height="70" rx="7" class="box"/><text x="238" y="834" class="b" text-anchor="middle">Route 1: externally complete provider set</text><text x="238" y="858" class="s" text-anchor="middle">F(k)=OR over all admissible providers</text>
<rect x="445" y="808" width="310" height="70" rx="7" class="box"/><text x="600" y="834" class="b" text-anchor="middle">Route 2: direct aggregate function</text><text x="600" y="858" class="s" text-anchor="middle">effective pollination / usable resource / prey</text>
<rect x="807" y="808" width="310" height="70" rx="7" class="box"/><text x="962" y="834" class="b" text-anchor="middle">Incomplete provider universe</text><text x="962" y="858" class="sh" text-anchor="middle">absence → unresolved</text>
<text x="600" y="938" class="s" text-anchor="middle">Joint models can estimate coupling; the relation-endpoint contract supplies the biological relation, common key and contradiction rule.</text>
</svg>'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = {
        "figure1_relation_endpoint_contract_v0_2.svg": figure1(),
        "figure3_relation_layer_and_event_function_v0_2.svg": figure3(),
    }
    for name, text in outputs.items():
        path = OUT / name
        path.write_text(text, encoding="utf-8")
        print(path)


if __name__ == "__main__":
    main()
