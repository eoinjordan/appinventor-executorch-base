# Beginner fruit classification
Status: complete; local tests and GitHub CI passed; Android testing unverified
## Goal
Make fruit photos the default beginner classification example.
## Through-line
Image asset/picker -> RGB tensor helper -> checked-in PTE -> named fruit prediction.
## Constraints
Keep custom numeric inference; bundle a small model and real licensed sample photos.
## Non-goals
General object detection, arbitrary backgrounds, runtime training.
## Blocks
| Step | Verify |
| --- | --- |
| Pin and sample Fruits-360 official Training/Test splits; train/export | export_fruit.py; verify_fruit.py |
| Add minimal RGB image input adapter | JVM pixel-layout tests; Java/D8 build |
| Build complete AIA with sample/photo controls | archive, component-name and API signature checks |
| Update default docs and tag release assets | actionlint; manual GitHub workflow |
## Done when
Model/app checked in, host tests and CI pass; Android limitations remain explicit.
## Open questions
Native inference/camera validation needs an Android device.
## Risks
Dataset-specific model; plain backgrounds and limited fruit varieties.
## Status log
2026-11-01: flow-local unavailable; drafted locally from user request.

CI: https://github.com/eoinjordan/appinventor-executorch-base/actions/runs/41346319011 (success).
