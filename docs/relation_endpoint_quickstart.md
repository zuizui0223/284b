# Relation-endpoint quickstart

This quickstart shows how to use the reference implementation as a layer **above** ecological estimators. It does not fit an SDM, occupancy model, JSDM, phenology model or classifier. Those upstream methods produce answers; the relation-endpoint contract determines what joint biological relation those answers are allowed to test.

Run:

`python scripts/relation_endpoint_quickstart.py`

The output is JSON and uses synthetic values only.

## 1. Freeze the biological relation

A contract must state the relation explicitly.

Soft same-target example:

`relation = "same-target cross-source soft coherence"`

Hard directional example:

`relation = "E(k) -> F(k)"`

`relation_level` names the endpoint class; `relation` states the actual biological/statistical relation being tested. The two are not interchangeable.

## 2. Freeze the common biological key

Examples:

- matched rows for same-target reconstruction;
- plant site × flowering window;
- host patch × developmental interval;
- breeding patch × reproductive season.

Role-specific answers may use different estimators, predictors or accessible areas upstream. The contract requires only that the adapters map them into a defensible common relation space.

## 3. Declare role-specific adapters and adequacy gates

The contract stores:

- left adapter;
- right adapter;
- left adequacy gate;
- right adequacy gate.

If either answer is inadequate, the relation state is `unresolved`. Inadequacy is not discordance and is not biological absence.

## 4. Freeze the contract before focal outcomes

A validated contract can be serialized to deterministic canonical JSON and fingerprinted with SHA-256.

Generic example:

`python scripts/freeze_relation_endpoint_contract.py config/relation_endpoint_contract_example.json`

To write a receipt:

`python scripts/freeze_relation_endpoint_contract.py config/relation_endpoint_contract_example.json --out contract_receipt.json`

The receipt contains:

- the exact validated contract;
- canonical JSON material;
- `fingerprint_sha256`;
- `outcome_data_read=false` for the freeze utility itself;
- empirical-ledger increment 0.

The fingerprint is the prospective identity of the relation endpoint. Changing the relation, key space, adapters, adequacy rules or opening rule changes the fingerprint. JSON key ordering does not.

This does **not** by itself prove that a researcher refrained from viewing outcomes; it provides an auditable object that can be timestamped, versioned and compared with the contract used at opening.

## 5. Choose the opening rule

### Soft endpoint

Use `opening_rule="calibrated_soft_ceiling"`.

After both answers pass adequacy, compare relation-specific discordance with a prospectively frozen ceiling.

Possible states:

- `consistent`;
- `attention_required`;
- `unresolved`.

`attention_required` is not automatically a biological falsification.

### Hard directional endpoint

Use `opening_rule="hard_implication"` for `E(k) -> F(k)`.

Possible states:

- `no_observed_violation`;
- `hard_violation_authorized`;
- `noninformative_for_implication`;
- `unresolved`.

A hard violation requires all of the following:

- event answer adequate;
- function answer adequate;
- `E(k)=true`;
- function state classified as absent;
- observation process qualified for negative inference;
- focal key valid for negative inference.

If any required negative-evidence condition fails, the result remains `unresolved`.

## 6. Primitive levels versus composition-only levels

The current reference engine directly evaluates only the primitive endpoint classes used in the paper:

- Level A — same-target calibrated soft coherence;
- Level B — relation-specific soft cross-role coherence;
- Level C — directional hard dependency.

Levels D and E are **composition-only** in the current implementation:

- Level D mutual dependency must be represented by separately frozen directional relations, for example `X -> Y` and `Y -> X`, each with its own event/key semantics and adequacy requirements;
- Level E life-stage coupling must first declare the biologically relevant transition relation and then use the appropriate supported soft or directional primitive.

The engine deliberately rejects `D_mutual_dependency` and `E_stage_coupling` as direct one-size-fits-all contracts. This prevents the implementation from implying that mutuality or stage coupling has one universal generic opening rule.

## 7. Why unqualified absence remains unresolved

The quickstart includes two otherwise identical hard-endpoint calls:

- `function_state="absent"` with `observation_process_qualified=False` → `unresolved`;
- the same negative state with qualified observation and a valid focal key → `hard_violation_authorized`.

This is the core guardrail. A zero or negative label is not sufficient by itself to create a biological contradiction.

## 8. Invalid-state ablation

The quickstart also evaluates the exact class-conditional ablation with

- `a1=P(valid | F=true)=0.70`;
- `a0=P(valid | F=false)=0.90`;
- `q=0.95`;
- `sp=0.99`.

The result shows:

- false-violation inflation from zero collapsing = `1-a1 = 0.30`;
- apparent sensitivity gain = `1-a0 = 0.10`.

These are properties of deleting the unresolved-state guard, not a comparison against modern detection-aware models.

## 9. Minimal interpretation

The method has three separate questions:

1. **Answer construction:** are the role-specific ecological answers defensible?
2. **Joint structure:** what relation or coupling exists among those answers?
3. **Biological authorization:** which declared biological endpoint is that joint structure allowed to support, and what evidence can open or contradict it?

Occupancy models, SDMs, JSDMs, data-fusion models, sensor classifiers and direct measurements can all contribute to questions 1–2. The relation-endpoint contract formalizes question 3.

## Claim boundary

This quickstart is synthetic method documentation only.

- no focal Level-C values are read;
- no biological dependency is confirmed or falsified;
- no empirical ledger increment occurs;
- empirical ledger remains 1 in the pre-field paper.
