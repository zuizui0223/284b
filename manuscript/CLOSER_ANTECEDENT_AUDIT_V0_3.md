# Closer-antecedent novelty audit v0.3 — through September 2026

Purpose: re-run the strongest plausible novelty attacks against the reviewer-hardened relation-endpoint Method paper without moving the frozen biological claim boundary.

## Result

No searched antecedent was found that makes the same methodological object central: **authorization of a declared biological relation endpoint across independently generated ecological answers**. The closest literatures solve adjacent problems and should be acknowledged as components or contrasts rather than claimed as new.

This audit does **not** justify widening the novelty claim. It narrows the defensible distinction.

## 1. Observation-process typology and identifiability — closest conceptual antecedent

Chadwick et al. (2024), *LIES of omission: complex observation processes in ecology* (*Trends in Ecology & Evolution* 39:368–380; DOI 10.1016/j.tree.2023.10.009), organize observation-process problems around Latency, Identifiability, Effort and Scale.

**Overlap:** observation-process identifiability, non-transferability across observation regimes and the need to specify how biological states map to observations.

**Boundary:** LIES characterizes the observation process for inference about biological processes. It does not by itself specify which relation should be imposed between two independently generated ecological answers, the biological key/event space in which that relation is meaningful, or the endpoint state machine that authorizes a joint relation claim.

**Manuscript stance:** LIES is an input/component. Observation-process identifiability is not a novelty claim.

## 2. Species-distribution data fusion — closest multi-source statistical antecedent

Pacifici et al. (2017), *Integrating multiple data sources in species distribution modeling: a framework for data fusion* (*Ecology* 98:840–850; DOI 10.1002/ecy.1710), jointly model standardized and non-standardized data sources and show that integrating a second source can improve out-of-sample species-distribution prediction.

Gelfand & Schliep (2026), *Model-Based Spatial Data Fusion* (*Annual Review of Statistics and Its Application* 13:225–244; DOI 10.1146/annurev-statistics-042424-052920), review stochastic fusion of heterogeneous spatial/spatiotemporal sources to improve inference and prediction, including ecological applications and sources with differing support and scale.

**Overlap:** heterogeneous sources, different observation quality, differing spatial support, joint ecological inference and prediction.

**Boundary:** data fusion combines multiple sources as jointly informative about a common latent process/quantity. The relation-endpoint method deliberately permits role-specific answers to remain separate upstream and asks a different question downstream: **what biological relation may the resulting answers jointly test?** Same-target reproducibility, soft cross-role concordance and directional dependency therefore do not collapse to one data-fusion estimand.

**Manuscript stance:** do not claim that 284b invents multi-source integration. If data-fusion literature is added to the main manuscript, use it to sharpen the upstream-versus-downstream distinction, not as a straw-man comparison.

## 3. Modern non-detection modelling remains a component

Recent work continues to improve detection modelling for opportunistic/citizen-science records; for example, *Non-detection by citizen scientists modeled as a function of visit characteristics* (2026, *Ecological Modelling*, DOI 10.1016/j.ecolmodel.2026.111474) models non-detection probabilities from visit characteristics.

**Overlap:** distinguishing biological absence from observation failure/non-detection.

**Boundary:** a detection model may supply the observation-process qualification needed by one role-specific answer. It does not choose the biological relation between independent answers or define whether a hard relation applies to raw occurrence, a functional state, or a site × biological-window event key.

**Manuscript stance:** zero collapsing remains an ablation of the endpoint's unresolved-state guard, never a claimed competitor to detection-aware modelling.

## 4. Standardized observation infrastructures address comparability upstream

The eLTER Framework of Standard Observations (Zacharias et al. 2026, *Earth's Future*, DOI 10.1029/2025EF006743) standardizes integrated long-term environmental measurements across domains, methods and scales.

**Overlap:** explicit definition of variables, observation protocols, harmonization and cross-domain comparability.

**Boundary:** harmonized observation design improves the quality and comparability of inputs. Relation-endpoint authorization governs the downstream inferential contract among answers after appropriate role-specific construction/adaptation.

## 5. Field-data design guidance is complementary

Jones (2026), *A short guide for effective field data collection* (*Methods in Ecology and Evolution*, DOI 10.1111/2041-210X.70259), emphasizes defining variables, data structure, protocols, pilot testing and protocol adherence before collection.

**Overlap:** prospectively defined measurement and failure handling.

**Boundary:** field-protocol quality is a prerequisite for adequate answers; it does not specify the relation endpoint joining independently generated answers.

## 6. What remains genuinely specific after the 2026 audit

The defensible contribution is not any one ingredient. It is the **composition and authorization rule**:

1. freeze the biological relation;
2. freeze the biological key/event space where that relation applies;
3. define role-specific adapters into that space;
4. require each answer to pass its own adequacy gate;
5. authorize only endpoint states supported by relation-specific calibration/opening logic;
6. retain invalid, missing, failed or otherwise unqualified negatives as `unresolved`.

This object is executable in `scripts/relation_endpoint_contract.py` and is tested on both calibrated soft and hard directional endpoint classes.

## 7. Quantitative distinction after reviewer hardening

For hard `E(k) -> F(k)` endpoints, the method's ablation analysis is class-conditional:

- `a1=P(valid key | F=true)`;
- `a0=P(valid key | F=false)`;
- false-violation inflation from zero collapsing = `1-a1`;
- apparent true-violation sensitivity gain = `1-a0`.

The simpler `1-a` identity is only the equal-validity corollary. This avoids hiding state-dependent observation validity and avoids presenting the ablation as an alternative observation model.

## 8. Editorial implication

The strongest Ecology Letters Method pitch remains:

> Existing methods can estimate ecological states from imperfect observations and can fuse multiple sources into common latent inference. The relation-endpoint contract addresses the next inferential layer: when independently generated answers are allowed to compose into a particular biological relation, and when the state required to contradict that relation is sufficiently identified to open the endpoint.

No new focal Level-C data are needed to support that methodological claim.

## 9. Canonical-manuscript action from this audit

**No automatic manuscript rewrite is authorized by this literature search.** Manuscript v0.7 already concedes imperfect detection, LIES, model adequacy, external validation and preregistration. If a full Method submission is invited, a concise data-fusion citation can be added during final reference formatting to make the upstream-versus-downstream distinction explicit, provided this does not alter the frozen scientific endpoint or imply that data fusion is a deficient method.

Empirical ledger increment: **0**.
