# Relation-layer separation argument v0.1

## Purpose

This note addresses the strongest remaining novelty objection to the pre-field Method paper:

> If each ecological answer is already statistically adequate, is the proposed relation-endpoint layer merely good practice rather than a distinct inferential object?

The answer is no in a precise but deliberately modest sense. **Even perfect marginal answers do not, in general, identify a directional biological relation between them.** The probability argument is classical Fréchet-Hoeffding coupling logic; the contribution here is to use it as a separation argument for ecological answer composition, not to claim new probability theory.

No focal Level-C values are used. Empirical ledger increment = 0.

## 1. Setup

Let `E(k)` be a dependent event and `F(k)` the required function at a common biological opportunity key `k`.

A hard directional endpoint is

`E(k) -> F(k)`.

Its violation probability over a declared key population is

`v = P(E=1, F=0)`.

Suppose, optimistically, that two role-specific models are individually perfect and provide the exact marginal probabilities

`p_E = P(E=1)`

and

`p_F = P(F=1)`.

The question is whether these exact marginal answers determine `v`.

## 2. Exact bounds

Let

`j = P(E=1,F=1)`.

For Bernoulli marginals the classical Fréchet-Hoeffding bounds give

`max(0, p_E + p_F - 1) <= j <= min(p_E,p_F)`.

Because

`v = p_E - j`,

we obtain the sharp interval

`max(0,p_E-p_F) <= v <= min(p_E,1-p_F)`.

This is not a new inequality. Its methodological consequence here is the point: **answer-level marginal correctness does not generally determine relation-level violation.**

## 3. Two-world counterexample

Take the exact same perfect marginal answers:

`p_E = p_F = 0.5`.

Then the sharp bound is

`0 <= v <= 0.5`.

Two joint worlds are both fully compatible with those same marginals.

### World A — dependency-compatible coupling

| | F=0 | F=1 |
|---|---:|---:|
| E=0 | 0.5 | 0 |
| E=1 | 0 | 0.5 |

Here `v=P(E=1,F=0)=0`, so `E -> F` holds almost surely.

### World B — dependency-violating coupling

| | F=0 | F=1 |
|---|---:|---:|
| E=0 | 0 | 0.5 |
| E=1 | 0.5 | 0 |

Here `v=0.5`; every positive `E` key violates the implication.

The two worlds have **identical marginal answers and opposite hard-relation status**.

Therefore no statistic that uses only the two marginal answers can distinguish them.

## 4. What this establishes

The result separates three inferential layers that can otherwise be conflated:

1. **answer adequacy** — is each role-specific target estimated defensibly?;
2. **joint/event alignment** — are the answers coupled on the biological key where the relation applies?;
3. **relation authorization** — is the proposed relation itself externally justified and is the state needed to contradict it identifiable?

Improving layer 1 cannot, by itself, supply layers 2 or 3.

This remains true even if detection is perfect and the marginal estimators have zero error. The problem is not only observation-process uncertainty; it is missing joint relation structure.

## 5. Relation to JSDMs

Joint species distribution models explicitly distinguish marginal and joint prediction. A JSDM can therefore address part of layer 2 by modelling a joint distribution or co-occurrence structure.

The relation-endpoint method is still not a substitute for a JSDM, and the separation argument is not a claim that JSDMs cannot model dependence. The remaining distinction is biological: a statistical joint distribution does not, on its own, determine whether the authorized endpoint should be co-occurrence, directional functional dependency, stage transition, reproductive opportunity or another biological relation.

Accordingly:

- marginal SDMs cannot identify the hard relation in the counterexample;
- a suitable JSDM may estimate the joint coupling;
- external biology plus the relation-endpoint contract still determines **which joint event and which directional claim are scientifically licensed**.

## 6. Relation to co-occurrence / interaction inference

The same separation explains why co-occurrence is not automatically a biotic interaction or a mandatory dependency. Co-occurrence structure can be informative, but a hard ecological implication requires a frozen biological event and function, not only statistical association.

The Method paper should therefore avoid claiming that statistical joint modelling is insufficient in general. Its narrower claim is that **statistical adequacy does not itself choose the biological relation endpoint**.

## 7. Strongest defensible novelty sentence after this argument

> Existing methods can make individual ecological answers accurate and can model their joint distribution; the relation-endpoint contract addresses the logically separate step of specifying which biological relation those answers are authorized to test, at which biological key, and under what observation state that relation may be opened or contradicted.

This is stronger than saying only that non-detection is not absence, while remaining compatible with occupancy models, JSDMs, data-fusion methods and LIES.

## 8. Manuscript implication

This counterexample is valuable because it directly answers the "framework / good-practice only" objection. It shows that the relation layer cannot be eliminated merely by making upstream models better.

However, the Fréchet-Hoeffding result itself is classical and must not be sold as mathematical novelty. The candidate manuscript use is a short formal paragraph or inset in the relation-endpoint architecture, with the full derivation in Supplement or repository documentation.

No focal Level-C values are opened. No empirical conclusion is added.
