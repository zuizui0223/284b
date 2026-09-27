# PINK structural receipt v0.1

The current PINK DwC-A was audited without reading `individualCount`.

## Structure

- source SHA-256: `7f5fc2523ab226f22cfd8adf199e3964dd474284f0a23dd2c40733106522a735`
- core events: **100**
- site-years: **74**
- site-years with >=2 events: **26**
- site-years with >=3 events: **0**

The occurrence table contains explicit life-stage labels across the full dataset:
- Adult 978
- egg 87
- larvae 590
- juvenile 53
- Subadult 13
- unknown 252

However, the current public archive contains **no behavior/calling labels at all**.

For prospectively selected *Hyla arborea*, there are only **6 occurrence rows**, all `larvae`, all present. There is no explicit adult-call record for the focal species.

## Decision

PINK fails the frozen structural requirement that adult breeding/calling activity be explicitly recoverable.

This is not repaired by:
- relabelling generic `Adult` occurrence as calling/breeding activity;
- changing focal species because another species has more rows;
- treating absence of a call record as zero calling effort.

Therefore PINK is closed as the primary breeding-to-offspring dataset.

The predeclared fallback advances to **Mohonk Preserve**, with the ecological scope limited to transitions that its public data directly encode.

No stage association or abundance outcome was opened.
