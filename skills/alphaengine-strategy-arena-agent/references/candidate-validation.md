# Candidate Validation

Use these rules for every simulation candidate and final export, regardless of runtime. No Python installation is required. Use the host's existing JSON tools, JavaScript runtime, PowerShell or other available execution tools. The optional Python helper implements these same metadata checks; do not install a language runtime merely to use this skill.

## Before Simulation

1. Cache the successful public router market catalog and `/strategies/{strategyId}/parameters` responses for the strategies being tested. Require the intended market ID to map uniquely to its market key; also check chain/address against any BFF catalog used for analysis. Send the chosen `hourly` or `daily` timeframe explicitly.
2. For each component, construct a new `strategyParams` object containing **every key** in its public parameter schema. Use an explicit supplied value when present; otherwise use the schema's `defaultValue` when present. Check property presence, not truthiness: `0` is a valid value. If neither exists, stop that candidate. Never obtain a default by guessing from another strategy or copying an unrelated example.
3. Reject unknown parameter keys, duplicate/invalid schema keys, and error responses used as schemas. Validate values against the current public types (`integer`, `number`, `string`), rejecting booleans as numbers and rejecting `NaN`/`Infinity`. Do not coerce strings into numbers or round values silently. Integer-valued JSON numbers must remain exact in the chosen runtime.
4. Apply the schema's actual `constraints.min`, `constraints.max` and `constraints.enum` fields. Check boundary values too. Do not look for `minimum`/`maximum` instead. If the schema has unsupported types/constraints, fail explicitly rather than silently skipping validation. Public metadata does not replace the producer's cross-parameter or private codec validation.
5. Require positive integer component weights totalling `10000`, a positive finite decimal-string capital, valid market identity, and explicit timeframe. Preserve ordered components and all tested request settings. Reject non-finite numbers in retained settings too.
6. Save this **complete request** before simulation. Use it for deduplication and the API call. Canonicalize object-key order for request hashes while preserving array order, ignoring only correlation/ephemeral fields as described in API workflow. Explicit defaults and equivalent default-expanded drafts must not become distinct trials.

An unavailable tool/runtime is a local capability limit, not permission to weaken these checks. Explain the specific blocker if no existing tool can validate and serialize the candidate reliably; do not claim an unverified export is ready.

## After Evaluation

- Bind the complete saved input to its simulation and evaluation responses, output identity, capital, snapshot hash, resolved execution/scoring profiles, score source and eligibility. Keep changed datasets/profiles separate.
- Export `marketKey`, `timeframe` and the exact ordered `components` from the saved winning request. Every public parameter remains explicit. Compare the export against that request; do not normalize, add defaults, round values, reorder components or retune settings after quoting its score.
- If a saved tested request is incomplete, or current metadata would change it, prepare a complete candidate and simulate it within budget before presenting a score for the new object. Retain the schema snapshot used for the trial.
- Retain capital and other API-only reproduction settings in the report; do not pretend they are supported dashboard JSON fields. If a component uses settings the dashboard cannot represent, report the incompatibility instead of silently dropping them.
- State exactly what was checked: public parameter metadata and simulation acceptance when verified. These checks do not prove private submission acceptance or its final score. Include the mandatory final note from `SKILL.md`.

## Optional Python Helper

When Python 3 is already available, `scripts/prepare_candidate.py` provides offline `prepare` and `export` commands with no packages, network access or credentials. See [the CLI example](api-workflow.md#prepare-and-export-candidates). Agents using another runtime follow the same rules above; the Python implementation does not prescribe a search algorithm.
