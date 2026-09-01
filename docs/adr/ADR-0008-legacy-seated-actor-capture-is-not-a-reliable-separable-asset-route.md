# ADR-0008: Legacy seated actor capture is not a reliable separable-asset route

## Decision

Do not extend the current local legacy Sigrid actor-capture profile through unconstrained prompt variation. Treat it as a documented failure profile for seated actor-only assets and defer alpha/matte or two-role G07 compositing tests until a different control mechanism is selected.

## Evidence

The original capture found furniture leakage in both Sigrid samples. A narrow retry explicitly requested an invisible support and intensified furniture/prop negatives. Seed 5301 nevertheless embedded a black tabletop; seed 5302 embedded a handheld tray. Thus all four reviewed Sigrid capture attempts leak foreign content. The r2 run took 67.368 seconds of local generation with no external cost. The seed-5301 renderer completed but its record write failed due to `null` used in Python; the output, Comfy history timing, and harness failure are retained explicitly.

## Consequences

This does not change `baseline_legacy` or frozen benchmark semantics. The controlled-actor route should next compare a genuinely different local control mechanism (for example a geometry/stage-assisted fictional-design route) rather than hide the limitation through unbounded prompt tuning. Adult likeness remains local-sensitive and no commercial claim is implied.
