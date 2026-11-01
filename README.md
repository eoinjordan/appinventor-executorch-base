# ExecuTorch: minimal App Inventor extension


A small Android-only base repo for loading your own `.pte` model from an App Inventor project asset and running `forward`. Four blocks and four events: generic numeric inference plus a small RGB image input helper. Camera and photo-picker UI are provided by the sample app using App Inventor built-in components.

<img width="912" height="679" alt="image" src="https://github.com/user-attachments/assets/d857c0d2-1b33-4d9c-b351-fa92cea3ea10" />


## Try it

1. Import `examples/ExecuTorchFruit.aia` using **Projects > Import project (.aia) from my computer**. It includes the extension, trained fruit model, three sample photos and all blocks.
2. Build an APK for a 64-bit Android phone (Android 8+). A 32-bit Companion process cannot load the native runtime.
3. Tap **Try apple**, **Try banana** or **Try orange**. The prediction should match the selected sample.
4. Try **Choose a fruit photo** or **Take a fruit photo**. Use one centred fruit on a plain white background. The model knows only these three fruit classes and has not been validated for general photographs or unrelated objects.

<img width="1343" height="760" alt="image" src="https://github.com/user-attachments/assets/d6d73135-a291-4c3a-8921-c5b6e3b78ee0" />


The checked-in `.pte` is about 39 KB. No Python installation, training or model download is needed to try the app. See [the beginner app guide](examples/README.md) and [dataset attribution](models/FRUIT_DATASET.md).

For your own image model, call `LoadModel(assetName)` followed by `RunImage(imagePath, size)` and handle `InferenceCompleted(values, shape, elapsedMs)`. The image helper passes RGB NCHW float32 values in [0,1], stretched to a square; any additional normalization must be inside your model. It does not assume fruit labels or any other model-specific class list.

The Iris measurements app and add-one smoke app remain available as optional numeric-tensor examples. The raw block example below uses the add-one diagnostic.

Or import `out/ExecuTorch-ARM64.aix` through **Extensions > Import extension**, drag ExecuTorch onto the screen, upload your `.pte` to Media, and wire these blocks:

```text
when Button.Click:
    call ExecuTorch.LoadModel("add_one.pte")

when ExecuTorch.ModelLoaded(assetName):
    call ExecuTorch.RunModel(values=[1,2,3,4], shape=[1,4])

when ExecuTorch.InferenceCompleted(values, shape, elapsedMs):
    set Label.Text to values

when ExecuTorch.ErrorOccurred(operation, message):
    set Label.Text to message
```

`UnloadModel()` releases native model memory and raises `ModelUnloaded`. `RunImage` is optional; `RunModel` continues to accept custom numeric tensors.

## Deliberately small model contract

- One float32 tensor input and one float32 tensor output, exposed by `forward`.
- Values are flattened in row-major order. Shape dimensions must be positive integers; their product must equal the value count. An empty shape represents a scalar with one value.
- The model is a self-contained `.pte` asset, with parameters embedded. External weight files are not supported.
- Export with ExecuTorch **1.5.1**, matching the pinned Android runtime. Custom operators and delegates absent from that runtime will fail.
- `RunImage` handles image decoding, stretch resize and RGB /255 conversion. Label lookup, further preprocessing, audio and detection postprocessing belong in your app/model.
- Work runs on a single background thread; events return on the UI thread. Wait for completion before sending another frame. Model cleanup runs after any active inference.
- No permissions are requested by this extension.

## Files to extend

| File | Purpose |
| --- | --- |
| `src/org/community/executorch/ExecuTorch.java` | Blocks, events, model lifecycle and inference |
| `src/org/community/executorch/TensorData.java` | Input validation and list conversion |
| `src/org/community/executorch/NativeRuntime.java` | ABI selection, native asset extraction and JNI loading |
| `scripts/build.py` | Download pinned runtime dependencies, compile and package AIX |
| `scripts/export_smoke.py` | Recreate the deterministic add-one model |
| `scripts/make_example.py` | Recreate the smoke-test App Inventor project |
| `scripts/verify.py` | Host tests and archive checks |

The first useful edit is inside `RunModel`: add your preprocessing immediately before `Tensor.fromBlob`, and your postprocessing after `getDataAsFloatArray`.

## Build

GitHub Actions builds and publishes release downloads when a `v*` tag is pushed:

```powershell
git push origin main
git tag v0.1.0
git push origin v0.1.0
```

Choose a new version if that tag already exists. The release includes ARM64 and multi-ABI `.aix` files, the fruit and smoke `.aia` apps, the fruit model/contract and dataset attribution, and SHA-256 checksums. **Actions > Build and release extension > Run workflow** runs the same checks without publishing a release. The workflow uses the checked-in model, so training and PyTorch are not required on the CI runner.

Requires Python 3, Git, JDK 17+ and an Android SDK with a platform and Build Tools/D8 installed. Set `JAVA_HOME` and `ANDROID_HOME`; on this Windows machine the script also detects Android Studio's bundled JDK and the default SDK location.

```powershell
git submodule update --init --depth 1
python scripts/build.py
python scripts/make_example.py
python scripts/make_iris_example.py
python scripts/make_fruit_example.py
python scripts/verify.py
python scripts/verify_iris.py
python scripts/verify_fruit.py
```

The App Inventor API jars are pinned by the `lib/appinventor` submodule. Maven coordinates are pinned in `scripts/build.py`; downloaded files go in `.cache/`. No Gradle or Ant installation is required. `build.xml` is the original MIT template's legacy build, retained for provenance; use the Python build for this project.

To re-export the small model, use a separate Python environment with `executorch==1.5.1` and compatible PyTorch, then run `python scripts/export_smoke.py`. A generated model is already checked in; building the extension does not require PyTorch.

## Native packaging

The default phone AIX contains Java bytecode for compiled apps, DEX for Companion, and arm64-v8a libraries. Use `python scripts/build.py --abi all` to add x86_64 emulator libraries. Native libraries are stored only in a compressed asset bundle and loaded explicitly from app-private storage. Native metadata is empty to avoid MIT's `AttachNativeLibs` extension check failing with `Unknown native lib type`. The phone archive is around 6.2 MB. A 64-bit Android process is required; another extension that introduces only 32-bit native libraries may prevent this loader from running. Native dependencies and licensing are listed in `THIRD_PARTY_NOTICES.md`.

A device must run a **64-bit app process**, not just have a 64-bit CPU. Restart Companion after rebuilding a native extension. iOS and 32-bit Android are unsupported. Coexistence with another extension using a different ExecuTorch/fbjni/NativeLoader version has not been tested.

## Upload troubleshooting

If MIT App Inventor reports "Upload Error", try the smaller `out/ExecuTorch-ARM64.aix` phone build. The earlier packages were around 19 MB (multi-ABI) and 9.9 MB (ARM64); the current ARM64 archive is around 6.6 MB. The generic uploader error does not prove a size limit was the cause; server/session/network errors can produce it too. If it persists, capture the upload request status from the browser Network panel. The smaller build and archive checks pass locally. A 3 KB diagnostic extension imported successfully on MIT ai2a, while testing the main package is still in progress.

## Verification status

Java compilation, annotation generation, DEX compilation, input tests and AIX archive checks pass locally. The `.pte` exported successfully. App Inventor import, its APK build, actual Android model execution and Companion loading have **not** been tested: no device is attached. This is a starter prototype, not a verified public release. The local Windows Python native ExecuTorch runtime also failed to load its DLL with the installed PyTorch; do not treat successful export as a runtime inference test.

The fuller reference implementation remains in `../appinventor-executorch/`. Both projects use the same component/package name, so use one at a time in an App Inventor project. This repo has not been published or submitted upstream.

Built from [MIT's extension template](https://github.com/mit-cml/extension-template) and [ExecuTorch's Android API](https://docs.pytorch.org/executorch/stable/using-executorch-android.html).

## Architecture diagram

Open [docs/architecture.drawio](docs/architecture.drawio) in https://app.diagrams.net using **File > Open From > Device**. All nodes and connectors are editable.

## Fruit model reproducibility

`models/fruit_contract.json` records labels, input/output shapes, probability fixtures and model hash. `models/fruit_dataset_manifest.json` pins the Fruits-360 revision and all 480 original image URLs/hashes. `models/fruit_parameters.json` contains the derived classifier parameters. Only three JPG photos are bundled in the app; the full training subset stays in `.cache/fruits/`.

`python scripts/export_fruit.py` downloads 120 Training images and 40 Test images per class from the pinned source, trains the classifier and exports PyTorch -> ExecuTorch 1.5.1. Training needs PyTorch, ExecuTorch, scikit-learn, NumPy and Pillow. Normalization beyond RGB /255 is embedded in the model. Host evaluation reached 100% on this selected 120-image official Test subset; that is not a claim of accuracy on arbitrary phone photos. Android resize/numerical behaviour and camera/picker permission flows require on-device validation.

The fruit model, derived parameters and sample photographs use CC BY-SA 4.0 with attribution to Mihai Oltean, Fruits-360. Extension/application code remains Apache-2.0; see [dataset attribution and scope](models/FRUIT_DATASET.md).
