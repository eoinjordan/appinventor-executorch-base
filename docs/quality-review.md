# Quality review — 1 November 2026

Scope: extension runtime and tensor conversion, native library packaging/loading,
Python build and export scripts, three sample generators and their verification,
GitHub Actions release workflow, and beginner documentation/attribution.

## Findings addressed

| Finding | Change | Evidence |
| --- | --- | --- |
| Numeric conversion round-tripped `Number` through text and rejected valid `Float.MAX_VALUE` | Use `Number.doubleValue()`; reject null/text entries with clear validation errors | Expanded `TensorDataTest` covers float boundaries, invalid entries, RGB channel/alpha handling, shape validation and boxed output values |
| Native loading had no executable host regression tests | Extract dependency preflight/order into `NativeLibraries`, used by the Android loader | `NativeLibrariesTest` exercises missing/empty dependencies, absolute-path ordering, propagated linker failure and retry using temporary files and an injected loader |
| Rebuilding reused class and DEX directories, allowing removed outputs to persist | Clean generated directories before compilation, with workspace bounds checks | Python tests verify stale outputs are removed and parent/outside paths are rejected |
| Automatic SDK selection sorted directory names lexically | Select the latest stable numeric version, ignoring preview/non-directory entries | Tests include Android 9 vs 35, Build Tools 9 vs 10 vs 36, preview versions and absent versions |
| Sample extension versions were duplicated as literals | Read the packaged descriptor version during generation | All three sample archives must match their bundled descriptor and the current extension |
| Iris re-enabled classification after a load failure | Enable retrying classification only for non-loading errors | Iris archive verification checks the load-error condition |
| Notices still implied there were no pretrained examples | Clarify fruit and Iris model/dataset attribution | Review of notices and bundled attribution files |
| Text reads depended on the host code page | Read JSON and attribution sources explicitly as UTF-8 | Sample regeneration and fixture/archive checks on Windows; CI uses Linux |

The runtime descriptor is version 4. Sample projects are regenerated against it.
The public block API and pinned ExecuTorch runtime version remain unchanged.

## Verification

Build and regenerate samples, then run `scripts/verify.py`,
`scripts/verify_iris.py` and `scripts/verify_fruit.py`. The first command runs
both Java test programs and four Python unittest cases before checking archives.
CI runs these checks on the ARM64 build and package/unit checks on the multi-ABI build.
Workflow lint and `git diff --check` are additional local checks.

The optional training/export walkthrough was also executed on the host. Fresh
training reproduced the shipped weights/biases within `1e-6` and reached 100% on
the selected 120-image test subset. Export produced a 39,464-byte PTE whose hash
matches its generated contract. Both GIFs were decoded and visually reviewed;
their source transcripts are included in `docs/tutorials/`. This does not add an
Android runtime verification claim.

Native dependency tests use a fake loader: they verify the production preflight and
call ordering, not Android's dynamic linker. Saved model prediction checks also do
not execute a PTE through the Android runtime.

## Remaining verification

- Build and install the generated APK on a 64-bit Android device and confirm model
  startup, all three sample predictions, inference errors and retry.
- Test camera/gallery permissions, orientation changes, background/foreground and
  closing the app while inference is active.
- Run the multi-ABI build on an x86_64 Android emulator.
- Test coexistence with other native extensions and any intended Companion version.

There was no ADB device attached during this review. These remain unverified;
host tests and a successful CI build do not replace them.
