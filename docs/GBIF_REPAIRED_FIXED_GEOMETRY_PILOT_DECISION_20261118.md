# Fixed-geometry repaired-source pilot: completed decision (18 November 2026)

## Completed evidence

The predeclared *Artemisia tridentata* heldout engineering pilot completed successfully in Actions run 44000170830. All 48 source × M × procedure model fits were sealed, with zero unresolved fit cells, using the restored 10,215-object GBIF source, the original signed 12-block centers (SHA-256 b9a5db3a5e0324abfdd38626727c170911cfc8994321eb0d24e6d995cd088a15), and the identical original 2,000-row comparison frames at M = 150, 300, 500 km. Original and repaired within-source predictions were compared on exactly matching comparison row IDs.

The median normalized prediction total-variation distance was **0.012490942512058359** for PRESERVED_SPECIMEN (24/24 comparable) and **0.018778625727311756** for HUMAN_OBSERVATION (24/24 comparable). These are medians over correlated procedure × M cells of a single taxon, not independent replicate effect estimates. The larger observation-mode median is descriptive and does not establish a statistically meaningful difference between source modes. Both modes showed nonzero source-version sensitivity.

The *Abies grandis* original reference geometry reconstruction also succeeded in Actions run 44000689837. Both historical specieskeys (2685361 and 8KCY), the 7,244-cell original pooled geometry and 12-block center hash **9eb19bf125fdd06c5e2b9ef901c869c23db6cd9aa88feb1305dffed79ff37f7e** were exactly reproduced. No reference model refitting or q95 recalibration was done by that job.

## Gate to full repaired-source robustness

The pilot establishes technical feasibility for one heldout refit and one reference geometry reconstruction; it does **not** establish all-59 portability. The next scale-out must be guarded by:

1. For each of the 47 fixed reference taxa and 12 heldout taxa, verify signed original qualification and fitted-model ZIPs, original specieskey set and 9,705-object source provenance.
2. Reconstruct each original 12-block center array and require byte-level signed center-hash equality before any repaired fit. Include multi-key species such as *Abies grandis*.
3. Use original 2,000-row M frames for both source modes, original 19 CHELSA predictors, original eight procedures, three M values and adequacy gates. No posthoc taxon, method, M or cell substitution.
4. Seal all 59 repaired source-specific model fits and inventories, and check per-taxon source-thinned counts against the already qualified restored-source receipts. Preserve unresolved fits rather than imputing predictions.
5. Only after all 47 reference taxa are sealed, recompute the 24 procedure × M reference q95 ceilings with nearest-rank and at least 30 qualified taxa per cell. Fail closed on underpowered reference cells.
6. Only then open the 12 original heldout taxa once under repaired-source ceilings; report taxon-level outcomes and all 288 cell states, and distinguish source-completeness sensitivity from a new prospective biological replication.

Do not recycle the historical q95 for the repaired source or claim that the original 0/12 result is robust to the October source restoration until this entire test completes. Do not open NEON field plant labels without an independently qualified leakage-safe source/plot gate.

## Provenance and interpretation

- Refit run: https://github.com/zuizui0223/284b/actions/runs/44000170830
- Reference geometry run: https://github.com/zuizui0223/284b/actions/runs/44000689837
- Pilot receipts: results/gbif_repaired_Artemisia_fixedcenters_fit_contract_v1.json, results/gbif_repaired_Artemisia_single_source_drift_v1.json, results/gbif_original_reference_Abies_grandis_centers_v1.json
- Original endpoint: 12 independent heldout taxa, 283/288 evaluable diagnostics, 0/12 taxa above historical frozen envelope.
- New independent biological conclusion count: **0**. Submission status: **HOLD**.
