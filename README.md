# ExecuTorch: minimal App Inventor extension

A small Android-only base repo for loading your own `.pte` model from an App Inventor project asset and running `forward`. Three blocks, four events, no camera, microphone, sensor or model-specific code.

<img width="912" height="679" alt="image" src="https://github.com/user-attachments/assets/d857c0d2-1b33-4d9c-b351-fa92cea3ea10" />


## Try it

1. Import `examples/ExecuTorchIris.aia` using **Projects > Import project (.aia) from my computer**. It includes the trained classifier, extension and working blocks.
2. Build an APK for a 64-bit Android device (Android 8 or later). Prefer a compiled APK for the first test; 32-bit Companion processes cannot load this runtime.
3. Tap **Try setosa**, then **Classify flower**. Repeat for versicolor and virginica. Edit the four measurements (in cm) to try your own inputs.

The included Iris classifier accepts raw measurements in this order: sepal length, sepal width, petal length, petal width. Normalization is included in the model. Its three output probabilities are setosa, versicolor and virginica. This is a teaching demo for Iris measurements, not a general plant identifier.

The original `ExecuTorchSmoke.aia` add-one example remains available; the raw block example below refers to that diagnostic.

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

`UnloadModel()` releases native model memory and raises `ModelUnloaded`.

## Deliberately small model contract

- One float32 tensor input and one float32 tensor output, exposed by `forward`.
- Values are flattened in row-major order. Shape dimensions must be positive integers; their product must equal the value count. An empty shape represents a scalar with one value.
- The model is a self-contained `.pte` asset, with parameters embedded. External weight files are not supported.
- Export with ExecuTorch **1.5.1**, matching the pinned Android runtime. Custom operators and delegates absent from that runtime will fail.
- Preprocessing, label lookup, image decoding, audio and detection postprocessing belong in your own code.
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

Choose a new version if that tag already exists. The release includes ARM64 and multi-ABI `.aix` files, both sample `.aia` apps, the Iris model/contract, and SHA-256 checksums. **Actions > Build and release extension > Run workflow** runs the same checks without publishing a release. The workflow uses the checked-in model, so training and PyTorch are not required on the CI runner.

Requires Python 3, Git, JDK 17+ and an Android SDK with a platform and Build Tools/D8 installed. Set `JAVA_HOME` and `ANDROID_HOME`; on this Windows machine the script also detects Android Studio's bundled JDK and the default SDK location.

```powershell
git submodule update --init --depth 1
python scripts/build.py
python scripts/make_example.py
python scripts/make_iris_example.py
python scripts/verify.py
python scripts/verify_iris.py
```

The App Inventor API jars are pinned by the `lib/appinventor` submodule. Maven coordinates are pinned in `scripts/build.py`; downloaded files go in `.cache/`. No Gradle or Ant installation is required. `build.xml` is the original MIT template's legacy build, retained for provenance; use the Python build for this project.

To re-export the small model, use a separate Python environment with `executorch==1.5.1` and compatible PyTorch, then run `python scripts/export_smoke.py`. A generated model is already checked in; building the extension does not require PyTorch.

## Native packaging

The default phone AIX contains Java bytecode for compiled apps, DEX for Companion, and arm64-v8a libraries. Use `python scripts/build.py --abi all` to add x86_64 emulator libraries. Standard native metadata lets the APK builder include 64-bit libraries. A compressed native asset bundle supplies an explicit load path for extension class loaders. Only libc++ is also packaged as a standard native library to declare the supported APK ABIs. The phone archive is around 6.6 MB. The loader extracts only the current ABI into app-private storage. Native dependencies and licensing are listed in `THIRD_PARTY_NOTICES.md`.

A device must run a **64-bit app process**, not just have a 64-bit CPU. Restart Companion after rebuilding a native extension. iOS and 32-bit Android are unsupported. Coexistence with another extension using a different ExecuTorch/fbjni/NativeLoader version has not been tested.

## Upload troubleshooting

If MIT App Inventor reports "Upload Error", try the smaller `out/ExecuTorch-ARM64.aix` phone build. The earlier packages were around 19 MB (multi-ABI) and 9.9 MB (ARM64); the current ARM64 archive is around 6.6 MB. The generic uploader error does not prove a size limit was the cause; server/session/network errors can produce it too. If it persists, capture the upload request status from the browser Network panel. The smaller build and archive checks pass locally. A 3 KB diagnostic extension imported successfully on MIT ai2a, while testing the main package is still in progress.

## Verification status

Java compilation, annotation generation, DEX compilation, input tests and AIX archive checks pass locally. The `.pte` exported successfully. App Inventor import, its APK build, actual Android model execution and Companion loading have **not** been tested: no device is attached. This is a starter prototype, not a verified public release. The local Windows Python native ExecuTorch runtime also failed to load its DLL with the installed PyTorch; do not treat successful export as a runtime inference test.

The fuller reference implementation remains in `../appinventor-executorch/`. Both projects use the same component/package name, so use one at a time in an App Inventor project. This repo has not been published or submitted upstream.

Built from [MIT's extension template](https://github.com/mit-cml/extension-template) and [ExecuTorch's Android API](https://docs.pytorch.org/executorch/stable/using-executorch-android.html).

## Architecture diagram

Open [docs/architecture.drawio](docs/architecture.drawio) in https://app.diagrams.net using **File > Open From > Device**. All nodes and connectors are editable.
