# RMNP confirmatory model contract v0.12

The candidate-search phase is closed. The confirmatory primary taxon is *Pseudacris maculata*.

## Ecological question

> Within wetlands where chorus frogs are detected, does environmental filtering act more strongly on reproductive stages than on adult stages?

The paper is therefore about **life-stage filtering hidden inside species-level occupancy**, not about another overall occupancy trend.

## States

For each repeated-survey site-year:

- adult evidence = any `A` stage token;
- reproductive evidence = any `E` or `L` stage token.

A zero is explicitly **no observed stage evidence**, not proven stage absence.

Only site-years with at least two survey dates and at least one species detection are included.

## Primary test

Create two rows per eligible site-year: Adult and Reproductive.

Primary GEE:

`evidence ~ stage + fish + stage×fish + centered year + max survey effort + number of visits + depth class`

clustered by site.

The prespecified primary estimand is **stage×fish**. The directional hypothesis is negative: fish presence should depress reproductive-stage evidence more strongly than adult-stage evidence.

## Secondary long-term test

`evidence ~ stage + year + stage×year + effort + visits + depth`

The stage×year coefficient asks whether reproductive-stage evidence changes through time at a different rate from adult-stage evidence.

## Guardrails

This is stage-resolved occurrence evidence. It is not:
- true reproductive failure;
- recruitment into the adult population;
- causal evidence that fish management would restore reproduction;
- an extinction early-warning result.

Wood Frog is validation only if its prespecified sample-size gate passes.
