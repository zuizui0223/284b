# Product-B v7.1 one-shot terminalization rule

This rule was frozen while the first JOS001 occurrence execution was still in progress. It does not change the scientific sampling thresholds, candidate set, country filter, witnesses, taxonomy, or control pool.

## Scope

This rule applies only after a v7.1 engineering one-shot occurrence workflow has crossed the occurrence-access boundary.

## Terminalization

1. **Completed audit artifact**
   - If the one-shot script writes an audit with `status = completed`, use its frozen `terminal_state` exactly as emitted.
   - Do not reinterpret or rerun it.

2. **Infrastructure/transport terminal after occurrence opening**
   - If occurrence access has begun but the workflow terminates before a completed audit is produced because of workflow timeout, network error, GBIF transport error, pagination ceiling, or similar execution failure, classify the engineering endpoint as `engineering_execution_unresolved`.
   - This state is neither a sampling pass nor a sampling failure.
   - It is not evidence for or against the directed dependency invariant.
   - Do not rerun the same engineering pair to obtain a cleaner or more favorable endpoint.

3. **Failure before occurrence opening**
   - Pure implementation/test failures before occurrence access may be repaired without consuming the one-shot scientific execution, provided no external occurrence response was opened.

## Downstream firewall

`engineering_execution_unresolved` cannot authorize model fitting, invariant evaluation, negative-control outcome evaluation, or process-knockout evaluation. JOS001 remains engineering-only and cannot be promoted to confirmatory evidence under any outcome.
