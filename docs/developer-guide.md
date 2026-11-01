# Developer guide

For people who want to build, test, release or change the extension, or run their
own model through it. If you only want to try the ready-made app, start with the
[main README](../README.md). For training the fruit model, see
[training and export](training-and-export.md).

All commands below run from the repository root. Examples use PowerShell syntax
where it matters; the Python scripts themselves are cross-platform.

## Overview

The extension wraps the ExecuTorch Android runtime as a single App Inventor
component with a small, deliberately narrow API:

- `LoadModel(assetName)` / `UnloadModel()` manage one model at a time.
- `RunModel(values, shape)` runs any model that takes one float32 tensor.
- `RunImage(imagePath, size)` is a convenience for image models: decode, resize, convert, run.
- `ModelLoaded`, `ModelUnloaded`, `InferenceCompleted` and `ErrorOccurred` report back.

The design in one line: **one serialized native runtime, model-specific logic kept
in the app or the model, events delivered on the UI thread.** Work runs on a single
background thread with a short queue (four pending calls). Wait for
`InferenceCompleted` before sending the next frame; if the queue is full, the call is
rejected with an `ErrorOccurred` whose message starts with `Busy`.

### Scope and non-goals

In scope: custom `.pte` inference for single-tensor models, an image helper that
matches the bundled fruit model, reproducible builds and releases, and worked
examples that beginners can import. Out of scope: training on the phone, models with
several inputs or outputs, detection or audio post-processing, delegates or custom
operators that are not in the pinned runtime, 32-bit Android and iOS.

### Related repository

A fuller reference prototype, `appinventor-executorch`, adds sensors, flashlight,
YOLO output decoding, wake-word and activity-recognition blocks. Both repositories
use the same component and package name (`org.community.executorch`), so only import
one of them into a given App Inventor project. This base repository is the one that
is published and documented for users.

### Architecture diagram

Open [architecture.drawio](architecture.drawio) in <https://app.diagrams.net> via
**File → Open From → Device**. All nodes and connectors are editable.

## Repository map

| Path | Purpose |
| --- | --- |
| `src/org/community/executorch/ExecuTorch.java` | The component: blocks, events, model lifecycle, inference |
| `src/org/community/executorch/TensorData.java` | Input validation and App Inventor list ↔ tensor conversion |
| `src/org/community/executorch/NativeRuntime.java` | ABI selection, native asset extraction and JNI loading |
| `src/org/community/executorch/NativeLibraries.java` | Host-testable native dependency checks and load order |
| `tests/` | Java unit tests (`TensorDataTest`, `NativeLibrariesTest`) and Python tests for the build helpers |
| `scripts/build.py`, `scripts/build_support.py` | Download pinned dependencies, compile, package the `.aix` |
| `scripts/make_example.py`, `make_iris_example.py`, `make_fruit_example.py` | Generate the three sample `.aia` projects |
| `scripts/verify.py`, `verify_iris.py`, `verify_fruit.py` | Host checks for the extension and each sample |
| `scripts/export_smoke.py`, `export_iris.py`, `train_fruit.py`, `export_fruit.py` | Create the models (need a PyTorch/ExecuTorch environment) |
| `scripts/make_dataset_preview.py`, `make_training_gifs.py` | Regenerate the dataset contact sheet and the training/export GIFs |
| `models/` | Checked-in `.pte` files, contracts, parameters, fixtures and dataset attribution |
| `examples/` | Generated sample projects and their [README](../examples/README.md) |
| `lib/appinventor` | Git submodule pinning the App Inventor API jars |
| `.github/workflows/release-extension.yml` | CI: build, verify and publish releases |
| `build.xml`, `update-deps.sh`, `upgrade-appinventor.sh` | Inherited from MIT's extension template; kept for provenance, not used by this project's build |

## Build locally

Requirements: Python 3, Git, JDK 17 or newer, and an Android SDK with a platform and
Build Tools (for D8) installed. Set `JAVA_HOME` and `ANDROID_HOME`. On Windows the
build script also detects Android Studio's bundled JDK and the default SDK location.
No Gradle or Ant is needed.

```powershell
git submodule update --init --depth 1
python scripts/build.py                # phone build: arm64-v8a
python scripts/build.py --abi all      # adds x86_64 for emulators
```

Outputs land in `out/`: `ExecuTorch-ARM64.aix` (about 6.2 MB) and, with `--abi all`,
`ExecuTorch-multi-ABI.aix` (about 10.9 MB). Maven dependencies are pinned in
`scripts/build.py` and cached in `.cache/`. Building the extension does **not**
require PyTorch; the models are checked in.

To regenerate the sample projects after a build:

```powershell
python scripts/make_example.py
python scripts/make_iris_example.py
python scripts/make_fruit_example.py
```

## Verify

```powershell
python -m pip install numpy Pillow
python scripts/verify.py
python scripts/verify_iris.py
python scripts/verify_fruit.py
```

`verify.py` runs the Java unit tests (tensor conversion, native dependency loading),
the Python tests for SDK selection and clean build outputs, and checks that every
sample project contains the current extension version. The two model scripts check
saved predictions against the fixtures, model and dataset hashes, train/test split
integrity and the wiring of the generated projects.

CI runs the same checks on every pull request and on manual runs
(**Actions → Build and release extension → Run workflow**), for both the phone and
emulator builds.

## Release

Pushing a `v*` tag builds and publishes a GitHub release:

```powershell
git push origin main
git tag v0.1.0
git push origin v0.1.0
```

Pick a new version if the tag already exists. A release contains the ARM64 and
multi-ABI `.aix` files, the fruit and smoke `.aia` projects, the fruit model with its
contract and dataset attribution, and SHA-256 checksums. The workflow uses the
checked-in model, so the CI runner never needs PyTorch.

Before tagging, bump `version` in `ExecuTorch.java`, regenerate the sample projects
and run the verification scripts, so that the release's `.aia` files reference the
new extension version.

## Native packaging

The phone `.aix` contains Java bytecode for compiled apps, DEX for the Companion, and
`arm64-v8a` native libraries. `--abi all` adds `x86_64`. The native libraries are
stored only in a compressed asset bundle and loaded explicitly from app-private
storage at runtime; the extension declares no native libraries in its metadata.
This sidesteps MIT's `AttachNativeLibs` check, which otherwise fails with
`Unknown native lib type`.

The loader loads `libc++_shared.so`, then `libfbjni.so` by absolute path, and only
then the ExecuTorch library. Android does not search the extraction directory for
transitive dependencies, so the order matters; getting it wrong produces the
`libfbjni.so not found` / `clns` namespace error described under Troubleshooting.

Constraints worth remembering:

- The app must run as a **64-bit process**, not merely on a 64-bit CPU. Another
  extension that ships only 32-bit native libraries can force a 32-bit process and
  break this loader.
- Restart the Companion after rebuilding a native extension, and fully close an
  older APK before installing a new one.
- Coexistence with another extension that bundles a different ExecuTorch, fbjni or
  SoLoader version has not been tested.
- The extension requests no Android permissions itself; camera and storage
  permissions belong to the app's own components.

Runtime dependencies and their licenses are listed in
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Model contract

The extension supports exactly this shape of model:

- One float32 tensor in, one float32 tensor out, exposed by `forward`.
- Values are passed as a flat list in row-major order plus a shape list of positive
  integers whose product equals the value count. An empty shape means a scalar.
- The model is a self-contained `.pte` asset with parameters embedded. External
  weight files are not supported.
- Exported with **ExecuTorch 1.5.1** to match the pinned Android runtime. Custom
  operators and delegates missing from that runtime will fail at load or run time.
- `RunImage` does image decoding, a stretch resize to `size × size`, and RGB
  conversion to float32 NCHW values in `[0, 1]`. Anything else (mean/std
  normalization, label lookup, detection or audio post-processing) belongs in the
  model or the app.

## Using your own model

Import `ExecuTorch-ARM64.aix` through **Extensions → Import extension**, drag the
component onto the screen, upload your `.pte` to **Media**, then wire the blocks.
The add-one smoke model makes the pattern easy to see:

```text
when Button.Click:
    call ExecuTorch.LoadModel("add_one.pte")

when ExecuTorch.ModelLoaded(assetName):
    call ExecuTorch.RunModel(values=[1,2,3,4], shape=[1,4])

when ExecuTorch.InferenceCompleted(values, shape, elapsedMs):
    set Label.Text to values          # shows [2, 3, 4, 5]

when ExecuTorch.ErrorOccurred(operation, message):
    set Label.Text to message
```

For an image model, replace `RunModel` with `RunImage(imagePath, size)` and make
sure your model expects the `[1, 3, size, size]` input described above. The fruit
app in `examples/` is a complete worked example. The Iris app shows a numeric model
with user-entered values.

`UnloadModel()` releases native memory and raises `ModelUnloaded`. Model cleanup
waits for any in-flight inference to finish.

### Extending the Java side

If your model fits the contract, change the app, not the extension. If you need new
preprocessing, the relevant pieces are `RunImage` (image → values), `TensorData`
(lists → tensors and back) and `runTensor`, which holds the shared
`Tensor.fromBlob`, forward call and output conversion. Add a unit test next to the
existing ones in `tests/`.

## Fruit model reproducibility

The repository includes the pretrained [`fruit_classifier.pte`](../models/fruit_classifier.pte)
and the complete [480-image dataset subset](../models/fruit_dataset.zip): 360 training
and 120 test photos, with attribution and a manifest inside the ZIP. The app itself
bundles only three test photos.

| File | Contents |
| --- | --- |
| `models/fruit_contract.json` | Labels, shapes, preprocessing, sample fixtures, model hash |
| `models/fruit_dataset_manifest.json` | Pinned Fruits-360 revision, original paths, URLs and all 480 content hashes |
| `models/fruit_parameters.json` | Trained classifier weights and biases |
| `models/FRUIT_DATASET.md` | Attribution, transformations and scope |

`scripts/train_fruit.py` verifies and extracts the dataset to `.cache/fruits/`, trains
the classifier and writes parameters. `scripts/export_fruit.py` turns those parameters
into a PyTorch module and exports it to ExecuTorch 1.5.1. Neither script selects new
photos from upstream. CI verifies the model and dataset hashes, rebuilds the app,
checks automatic loading and error handling, and ships the model, dataset ZIP and
generated app in build artifacts and releases, but it does not retrain.

Host evaluation reached 100% on the selected 120-image test subset. That is a
regression check for this teaching recipe, not a claim about accuracy on arbitrary
phone photos.

## Troubleshooting

**Upload Error in App Inventor.** Import `.aia` files through the project importer
and `.aix` files through the extension importer. On a phone, prefer the ARM64 build
(about 6.2 MB) over the multi-ABI build. If the error persists, capture the full
message; "Upload Error" alone does not identify the cause.

**AttachNativeLibs: Unknown native lib type.** You have an older project that still
declares native libraries. Import the rebuilt sample; current builds leave the native
metadata empty on purpose (see Native packaging).

**join reports `*nothing*`.** An older sample referenced event arguments as
`get message` instead of `message`. Import the current sample project.

**UnsatisfiedLinkError: libfbjni.so not found**, possibly with a `clns` namespace
message. Use extension version 3 or newer, which loads `libc++_shared.so` and
`libfbjni.so` explicitly before ExecuTorch. Rebuild the APK and fully close the old
app or Companion process before retesting.

**Model loads but inference fails.** Check the contract: one float32 input, export
version 1.5.1, no unsupported operators or delegates. The error message from
`ErrorOccurred` includes the native runtime's text.

## Known limitations and verification status

What has been checked on the host: Java and DEX compilation, numeric input
validation, native asset packaging, project archive structure, prediction fixtures
for all three models, and event argument bindings in the fruit project. The fruit
project has been opened in App Inventor; earlier APK packaging and event binding
failures were fixed as a result.

What has **not** yet been verified: successful APK compilation on the App Inventor
build server for the current version, native inference on a real Android device,
camera and photo picker permission flows, and the revised layout on a phone. The
local Windows Python ExecuTorch runtime fails to load its native DLL with the
installed PyTorch, so a successful export is not a native runtime test either.

This is a community starter project, not an official MIT App Inventor or PyTorch
extension. It is built from [MIT's extension template](https://github.com/mit-cml/extension-template)
and the [ExecuTorch Android API](https://docs.pytorch.org/executorch/stable/using-executorch-android.html).
