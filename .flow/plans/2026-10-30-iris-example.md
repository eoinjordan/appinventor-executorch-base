# Beginner Iris example
Status: implementing (user requested implementation)
## Goal
Include a useful trained PTE and self-contained beginner App Inventor project.
## Through-line
Four flower measurements -> existing generic tensor block -> species probabilities.
## Constraints
Keep the base extension API unchanged; no new phone permissions.
## Non-goals
Camera/image adapters; changes to the full reference repo.
## Blocks
| Step | Verify |
| --- | --- |
| Train/export Iris model and save held-out fixtures | python scripts/verify_iris.py |
| Generate AIA with presets, inputs, labels and events | python scripts/make_iris_example.py; archive/XML checks |
| Document beginner steps and attribution | inspect README and bundled contract |
## Done when
Model and example committed; host tests pass; Android limitations explicit.
## Open questions
Device validation requires a connected 64-bit Android device.
## Risks
Native ExecuTorch Python DLL currently incompatible with installed host PyTorch.
## Status log
2026-10-30: flow-local unavailable; drafted locally; continuing authorized work.
