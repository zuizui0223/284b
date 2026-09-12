# Relation-layer reference handoff v0.1

Use this only if the relation-layer separation argument is promoted into an invited full manuscript. It does not alter the current empirical claim boundary.

## Core references

1. **Nelsen RB. 2006. _An Introduction to Copulas_, 2nd ed. Springer Series in Statistics. Springer, New York. DOI: 10.1007/0-387-28678-0.**  
   Use as a standard reference for classical Fréchet-Hoeffding / copula bounds. Do not imply the bounds are new to this paper.

2. **Wilkinson DP, Golding N, Guillera-Arroita G, Tingley R, McCarthy MA. 2021. Defining and evaluating predictions of joint species distribution models. _Methods in Ecology and Evolution_ 12:394–404. DOI: 10.1111/2041-210X.13518.**  
   Use to acknowledge explicitly that JSDM literature already distinguishes marginal from joint prediction.

3. **Galiana N, Arnoldi J-F, Mestre F, Rozenfeld A, Araújo MB. 2024. Power laws in species' biotic interaction networks can be inferred from co-occurrence data. _Nature Ecology & Evolution_ 8:209–217. DOI: 10.1038/s41559-023-02254-y.**  
   Use to position co-occurrence as informative but not identical to pairwise interaction semantics.

## Suggested manuscript-facing use

A concise architecture paragraph can say:

> Even exact role-specific marginals need not identify a directional endpoint. For `v=P(E=1,F=0)`, classical Fréchet-Hoeffding bounds give `max(0,p_E-p_F) <= v <= min(p_E,1-p_F)`; at `p_E=p_F=0.5`, the same marginals admit both `v=0` and `v=0.5` (Nelsen 2006). JSDMs can estimate joint rather than marginal predictions (Wilkinson et al. 2021), but statistical joint structure still does not by itself determine whether the licensed ecological endpoint is co-occurrence, interaction or a directional functional dependency (cf. Galiana et al. 2024).

Then return immediately to the five-part relation-endpoint contract. Do not expand this into a claim of new coupling theory.

## Claim boundary

- nonempirical method support only;
- no focal Level-C values;
- no new empirical conclusion;
- empirical ledger increment = 0.
