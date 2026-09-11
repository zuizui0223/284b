# Product-B Level C v6: raw calibration reconstruction audit

## Question
Can the candidate-specific calibration required by v5 be reconstructed from already-existing supplementary or repository data, without opening focal cross-role outcomes?

## Frozen scope
The candidate set remains exactly `CREMV3-007` and `BELV3-012`. No new candidate search, replacement, prior-system rescue, threshold relaxation, Level-A q95 import, or focal outcome opening is authorized.

## Cremastra
The 2026 sensor-camera study provides strong positive evidence and useful operational metadata: cameras were deployed before anthesis through flower senescence; failures and out-of-frame periods are described; supplementary material includes camera-operation and storage/battery-change information; scheduled-camera trials exist. However, the study itself states that quantitative validation against continuous recording is still required to establish detection completeness. The scheduled-camera comparison does not supply a same-inflorescence, full-window gold-standard stream from which candidate-specific sensitivity/FNR for effective visits can be estimated. Therefore existing supplementary/raw material cannot reconstruct the v5 calibration.

Required new measurement: overlap sensor cameras with continuous or prospectively scheduled reference observation on the same inflorescences and windows, label effective pollination events independently of fruit outcome, and explicitly separate camera failure/out-of-frame periods from confirmed no-event periods.

## Belonocnema
The Dryad archive clearly separates `Budbreak in Nature` from `Emergence in Nature` and also contains common-garden budbreak, laboratory emergence, and longevity files. This is enough for the v3 three-channel architecture, but not for v5 detection calibration. The repository inventory does not identify repeated within-tree budbreak rescoring or cross-observer reference observations that would estimate false-negative detection of the usable-resource state. Therefore existing files cannot reconstruct the required absence calibration.

Required new measurement: repeated within-tree resource observations over the full relevant window, independent or cross-observer scoring against a prespecified usable-resource threshold, with missing-record and confirmed-absence states kept distinct.

## Result
`0/2` candidates pass raw/supplementary calibration reconstruction. Both remain nonbiological `calibration_stream_absent` states. This is not evidence that pollination or budbreak resource was absent.

No hard endpoint, soft cross-check, process knockout, or focal cross-role statistic is opened. Empirical ledger increment remains zero and the global 284b empirical ledger remains 1.
