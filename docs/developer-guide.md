# Developer guide

For supporters: people who build, test, release or change the extension. To try the
app, start with the [main README](../README.md). To train the fruit model, see
[training and export](training-and-export.md).

Run the commands below from the repository root. Examples use PowerShell; the Python
scripts run the same way in a macOS or Linux terminal.

## How the extension is put together

One App Inventor component wraps the ExecuTorch Android runtime:

- `LoadModel(assetName)` and `UnloadModel()` manage one model at a time.
- `RunModel(values, shape)` runs any model that takes one float32 tensor.
- `RunImage(imagePath, size)` decodes an image, resizes it and runs an image model.
- `ModelLoaded`, `ModelUnloaded`, `InferenceCompleted` and `ErrorOccurred` report back.

Work runs on a single background thread with a queue of four pending calls; events
return on the UI thread. Wait for `InferenceCompleted` before sending the next frame.
If the queue is full the call is rejected with an `ErrorOccurred` whose message starts
with `Busy`. Model cleanup runs after any active inference.

In scope: custom `.pte` inference for single-tensor models, the image helper that
matches the fruit model, reproducible builds and releases, and one worked example that
beginners can import. Out of scope: training on the phone, models with several inputs
or outputs, detection or audio post-processing, delegates or custom operators that are
not in the pinned runtime, 32-bit Android and iOS.

A fuller reference implementation lives in a separate `appinventor-executorch` repo.
Both use the same component and package name, so use one at a time in an App Inventor
project.

### Diagrams

Open [architecture.drawio](architecture.drawio) or
[blocks-workflow.drawio](blocks-workflow.drawio) in <https://app.diagrams.net> using
**File > Open From > Device**. All nodes and connectors are editable. The workflow file
and its renders in `docs/images/blocks/` are written by `scripts/make_workflow_diagrams.py`;
edit the script when you want the pictures in the docs to change too.

## Architecture and files to extend

<img width="912" height="679" alt="The fruit project open in the App Inventor Designer" src="https://github.com/user-attachments/assets/d857c0d2-1b33-4d9c-b351-fa92cea3ea10" />

| Path | Purpose |
| --- | --- |
| `src/org/community/executorch/ExecuTorch.java` | Blocks, events, model lifecycle and inference |
| `src/org/community/executorch/TensorData.java` | Input validation and list conversion |
| `src/org/community/executorch/NativeRuntime.java` | ABI selection, native asset extraction and JNI loading |
| `src/org/community/executorch/NativeLibraries.java` | Testable native dependency checks and load order |
| `tests/` | Java unit tests for `TensorData` and `NativeLibraries`; Python tests for the build helpers |
| `scripts/build.py`, `scripts/build_support.py` | Download pinned runtime dependencies, compile and package the AIX |
| `scripts/make_fruit_example.py` | Generate `examples/ExecuTorchFruit.aia` |
| `scripts/make_block_reference.py` | Draw the block pictures and write `docs/blocks.md` and the README Blocks section from the built AIX |
| `scripts/make_workflow_diagrams.py` | Write `docs/blocks-workflow.drawio` and its PNG/SVG renders from one list of boxes and arrows |
| `scripts/verify.py`, `scripts/verify_fruit.py` | Host checks for the extension and the fruit project |
| `scripts/make_fruit_subset.py` | Pick the pinned photo subset from the Zenodo archive (maintainers, once) |
| `scripts/train_fruit.py`, `scripts/export_fruit.py` | Train the fruit classifier and export it to PTE |
| `scripts/make_dataset_preview.py`, `scripts/make_training_gifs.py` | Regenerate the dataset contact sheet and the training/export GIFs |
| `models/` | The `.pte`, contract, parameters, dataset subset, manifest and attribution |
| `examples/` | The generated project and its [README](../examples/README.md) |
| `lib/appinventor` | Git submodule pinning the App Inventor API jars |
| `.github/workflows/release-extension.yml` | CI: build, verify and publish releases |
| `build.xml`, `update-deps.sh`, `upgrade-appinventor.sh` | From MIT's extension template; retained for provenance, not used by this build |

For a model that matches the supported contract, start by changing the app's assets and
blocks. If you need to extend Java preprocessing, `RunImage` prepares image values and
`TensorData` converts numeric lists; `runTensor` contains the shared `Tensor.fromBlob`,
forward call and output conversion. Add a unit test next to the existing ones in `tests/`.

## Build

Requires Python 3, Git, JDK 17+ and an Android SDK with a platform and Build Tools/D8
installed. Set `JAVA_HOME` and `ANDROID_HOME`; on Windows the script also detects
Android Studio's bundled JDK and the default SDK location. No Gradle or Ant is required.

```powershell
git submodule update --init --depth 1
python scripts/build.py                # phone build, arm64-v8a
python scripts/build.py --abi all      # adds x86_64 for emulators
python scripts/make_fruit_example.py
python scripts/make_block_reference.py # needs ImageMagick for PNGs; writes SVG without it
python scripts/make_workflow_diagrams.py
```

After changing a block, parameter or description in `ExecuTorch.java`, rebuild and run
`make_block_reference.py` so [docs/blocks.md](blocks.md) and its pictures match. The
script stops if a new parameter has no plain-language description in its `PARAMETERS`
table.

Outputs go to `out/`: `ExecuTorch-ARM64.aix` (around 6.2 MB) and, with `--abi all`,
`ExecuTorch-multi-ABI.aix` (around 10.9 MB). The App Inventor API jars are pinned by the
`lib/appinventor` submodule. Maven coordinates are pinned in `scripts/build.py`;
downloaded files go in `.cache/`. Building the extension does not require PyTorch; the
model is checked in.

## Checks

```powershell
python -m pip install numpy Pillow
python scripts/verify.py
python scripts/verify_fruit.py
```

`verify.py` runs the Java unit tests for tensor conversion and native dependency
loading, the Python tests for SDK selection and clean build outputs, and package checks
on the AIX and the sample project's extension version. `verify_fruit.py` checks the
saved predictions, the model and dataset hashes, the disjoint train/test split,
attribution, the assets inside the `.aia` and the block wiring.

GitHub Actions runs the same checks on every pull request and on manual runs
(**Actions > Build and release extension > Run workflow**), for both the phone and
emulator builds. The fruit app has also been built in App Inventor and tested on an
Android phone.

## Release

Pushing a `v*` tag builds and publishes a GitHub release:

```powershell
git push origin main
git tag v0.1.0
git push origin v0.1.0
```

Choose a new version if that tag already exists. The release includes the ARM64 and
multi-ABI `.aix` files, `ExecuTorchFruit.aia`, `ExecuTorchFruit.apk`, the fruit model,
contract, dataset ZIP and manifest, the attribution text and SHA-256 checksums. The
workflow uses the checked-in model, so the CI runner does not need PyTorch.

Before tagging:

1. If the extension changed, bump `version` in `ExecuTorch.java`, rebuild, regenerate
   the sample project and run the checks, so the released `.aia` references the new
   extension version.
2. If the sample project changed, import the current `.aia` into App Inventor, choose
   **Build > Android App (.apk)** and commit the download as `assets/ExecuTorchFruit.apk`.
   CI copies that file into the release; it does not build APKs itself.

## Native packaging

The default phone AIX contains Java bytecode for compiled apps, DEX for Companion, and
arm64-v8a libraries. `--abi all` adds x86_64 emulator libraries. Native libraries are
stored only in a compressed asset bundle and loaded explicitly from app-private storage.
Native metadata is empty to avoid MIT's `AttachNativeLibs` extension check failing with
`Unknown native lib type`.

The loader loads `libc++_shared.so`, then `libfbjni.so` by absolute path, and then
ExecuTorch, because Android does not search the extraction directory for transitive
dependencies.

A device must run a **64-bit app process**, not just have a 64-bit CPU. Another
extension that introduces only 32-bit native libraries may prevent this loader from
running. Restart Companion after rebuilding a native extension. iOS and 32-bit Android
are unsupported. Coexistence with another extension using a different
ExecuTorch/fbjni/NativeLoader version has not been tested. The extension requests no
permissions; camera and storage permissions belong to the app's own components.

Native dependencies and licensing are listed in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Deliberately small model contract

- One float32 tensor input and one float32 tensor output, exposed by `forward`.
- Values are flattened in row-major order. Shape dimensions must be positive integers; their product must equal the value count. An empty shape represents a scalar with one value.
- The model is a self-contained `.pte` asset, with parameters embedded. External weight files are not supported.
- Export with ExecuTorch **1.5.1**, matching the pinned Android runtime. Custom operators and delegates absent from that runtime will fail.
- `RunImage` handles image decoding, stretch resize and RGB /255 conversion to float32 NCHW values in `[0, 1]`. Label lookup, further preprocessing, audio and detection postprocessing belong in your app or model.

## Use your own model

Import `out/ExecuTorch-ARM64.aix` through **Extensions > Import extension**, drag
ExecuTorch onto the screen, upload your `.pte` to Media, and wire the blocks. The
[block reference](blocks.md) shows each block and its parameters. The fruit app uses
this pattern:

```text
when Screen1.Initialize:
    call ExecuTorch1.LoadModel("fruit_classifier.pte")

when ExecuTorch1.ModelLoaded(assetName):
    enable the sample and photo buttons

when AppleButton.Click:
    call ExecuTorch1.RunImage("apple.jpg", 32)

when ExecuTorch1.InferenceCompleted(values, shape, elapsedMs):
    pick the largest of values[1], values[2], values[3] and show its label

when ExecuTorch1.ErrorOccurred(operation, message):
    show operation and message
```

For a numeric model, call `RunModel(values, shape)` with a flat list and matching
dimensions instead of `RunImage`. `UnloadModel()` releases native model memory and
raises `ModelUnloaded`.

## Fruit model reproducibility

The repo includes the pretrained [fruit_classifier.pte](../models/fruit_classifier.pte)
and the full [1,200-photo dataset subset](../models/fruit_dataset.zip): 900 training
photos and 300 test photos, with attribution and a manifest inside the ZIP. The app
bundles three test photos so beginners can try it without downloading the dataset.

| File | Contents |
| --- | --- |
| `models/fruit_contract.json` | Labels, shapes, preprocessing, prediction fixtures and the model hash |
| `models/fruit_dataset_manifest.json` | Zenodo DOI and archive MD5, each photo's original path, label, split and content hash |
| `models/fruit_parameters.json` | Trained classifier weights and biases |
| `models/FRUIT_DATASET.md` | Attribution, transformations and scope |

`scripts/make_fruit_subset.py` selects the subset from the extracted Zenodo archive
(8.5 GB, run once by a maintainer; the result is checked in). `scripts/train_fruit.py`
verifies and extracts the checked-in dataset to `.cache/fruits/` and trains the classifier. `scripts/export_fruit.py` converts the trained parameters to
PyTorch and exports them to ExecuTorch 1.5.1. Neither script selects new photos from
upstream. Training needs PyTorch, ExecuTorch, scikit-learn, NumPy and Pillow; CI uses the
pretrained model and does not retrain it. Normalization beyond RGB /255 is embedded in
the model.

The fruit model, derived parameters and sample photographs use CC BY 4.0 with
attribution to Hussain, He, Chen and Xie (Fruit Recognition dataset). Extension and
application code remains Apache-2.0;
see [dataset attribution and scope](../models/FRUIT_DATASET.md).

## Upload troubleshooting

If App Inventor reports **Upload Error**, use the ARM64 phone build (around 6.2 MB)
rather than the larger multi-ABI build. Select an `.aia` through the project importer
or an `.aix` through the extension importer. If it persists, record the full error.

If an older project fails with **AttachNativeLibs: Unknown native lib type**, import
the rebuilt sample; it removes the native declaration that triggers the server error.
If **join** reports `*nothing*`, replace the older sample project: event arguments must
use their actual names, such as `message`, not `get message`.

For **UnsatisfiedLinkError: libfbjni.so not found**, including a `clns` namespace
error, use extension version **3** or newer and rebuild the APK. Fully close an older
app or Companion process before testing a new native extension.

If the model loads but inference fails, check the contract: one float32 input, export
version 1.5.1, no unsupported operators or delegates. The `ErrorOccurred` message
includes the native runtime's text.

Built from [MIT's extension template](https://github.com/mit-cml/extension-template)
and [ExecuTorch's Android API](https://docs.pytorch.org/executorch/stable/using-executorch-android.html).
