# Learn image classification with App Inventor and ExecuTorch


Build an Android app that predicts whether a photo shows an **apple, banana or orange**. This community extension connects MIT App Inventor blocks to ExecuTorch, which runs a trained model on the phone.

This is a local AI machine learning model. It uses your phone's processor to run a PyTorch ExecuTorch model. Your photos are processed on your phone. To learn more about AI or PyTorch, use the links in the app or the [learning resources below](#learn-more).

Start with the ready-made fruit app. You do not need Python, Java or previous machine learning experience to try it: the extension, model, photos and blocks are included. This is a learning prototype; successful Android inference still needs device verification.

## What to download

You need an App Inventor account, a computer with a browser and a 64-bit Android phone running Android 8 or later.

| File | What it is | When you need it |
| --- | --- | --- |
| [ExecuTorchFruit.aia](examples/ExecuTorchFruit.aia) | Editable App Inventor project with the extension and model | Start here; download the raw file from GitHub |
| `.apk` | Installable Android app | Build from the project to test on your phone |
| `.aix` | Extension that adds ExecuTorch blocks | For a different project; not needed separately for the sample |
| `.pte` | Exported model that ExecuTorch runs | Already included as `fruit_classifier.pte` |

The screenshots below show earlier versions; the current project includes a revised layout and learning links.

<img width="912" height="679" alt="image" src="https://github.com/user-attachments/assets/d857c0d2-1b33-4d9c-b351-fa92cea3ea10" />


## Try your first prediction

1. Open [MIT App Inventor](https://ai2.appinventor.mit.edu/) and sign in.
2. Import `examples/ExecuTorchFruit.aia` using **Projects > Import project (.aia) from my computer**. Give it a new project name if you imported an older version.
3. Explore **Designer** to see the screen, then **Blocks** to see how it works.
4. Choose **Build > Android App (.apk)**. Transfer the APK to your phone, install it and open it. Use a compiled APK for this first test; a 32-bit Companion process cannot load the runtime.
5. Wait for **Ready**, then tap **Apple**, **Banana** or **Orange** under **Sample photos**. The prediction should match the selected photo. These buttons classify supplied examples; they do not train the model.
6. Try **Choose photo** or **Take photo**. Use one centred fruit on a plain white background. Allow camera/photo access when Android asks.
7. Open **Learn about AI** or **PyTorch / ExecuTorch** at the bottom of the screen for tutorials. These pages need internet access; the bundled model performs classification locally.

The app loads its pretrained `fruit_classifier.pte` automatically. If loading fails, photo controls stay disabled and the original error appears with **Retry loading fruit model**. You do not need to supply or train a model. If retry fails, report that loading error; a later "Load a model first" message alone does not identify the cause.

<img width="1343" height="760" alt="image" src="https://github.com/user-attachments/assets/d6d73135-a291-4c3a-8921-c5b6e3b78ee0" />


The checked-in `.pte` is about 39 KB. No Python installation, training or model download is needed to try the app. See [the beginner app guide](examples/README.md) and [dataset attribution](models/FRUIT_DATASET.md).

## What you are learning

**Image classification** assigns a label to a whole image. This app chooses among three labels; it does not locate multiple objects or draw boxes around them.

| Term | Meaning in this example |
| --- | --- |
| Dataset | Labelled fruit photos used for training and testing |
| Training | Learning model parameters from examples; already done before this app runs |
| Model | The saved calculation that turns image numbers into scores |
| Inference | Running that calculation on a new photo |
| Class / label | One possible answer: apple, banana or orange |
| Tensor | A structured collection of numbers, such as image colour values |
| Score | A value for each class; the app displays the highest-scoring label |
| PyTorch | Tools used to represent and export the model in this project |
| ExecuTorch | The runtime that executes the exported model on the phone |

The teaching classifier is trained with scikit-learn, represented as a PyTorch model, then exported to an ExecuTorch `.pte` file. App Inventor supplies the screen, camera, photo picker and event blocks. Choosing a photo does not add it to the training dataset or change the model.

## Follow one prediction through the blocks

1. **Screen.Initialize** calls `LoadModel("fruit_classifier.pte")`.
2. **ModelLoaded** enables the sample and photo controls.
3. Selecting a photo calls `RunImage(imagePath, 32)`. The extension resizes it to 32 by 32 pixels and converts its red, green and blue channels into numbers.
4. **InferenceCompleted** returns three scores, in **apple, banana, orange** order, and the elapsed time. The app displays the highest-scoring label.
5. **ErrorOccurred** supplies the operation and message if a step fails.

Loading and inference finish asynchronously: use their completion events before starting the next step.

## Experiments to try

- **Establish a baseline:** run each supplied photo and record its label and three scores.
- **Change one thing:** photograph the same fruit on a white surface, then change only the lighting, angle or background. Which scores change?
- **Try something unfamiliar:** show a pear or an empty table. The model still chooses one of its three classes. A high score does not guarantee a correct answer.
- **Check local inference:** after the model loads, enable airplane mode and classify a bundled sample again. Documentation links need a connection.
- **Think about better data:** what additional varieties, lighting and backgrounds would you collect? Keep separate test photos that were not used to train the model.

The dataset contains isolated fruit on simple backgrounds and limited varieties. The model has no "unknown" class. Host evaluation matched all 120 selected test photos, separate from the 360 training photos; this does not establish accuracy on your phone camera or arbitrary objects. See [dataset attribution and limitations](models/FRUIT_DATASET.md).

## Learn more

- **New to App Inventor:** [MIT's beginner tutorials](https://appinventor.mit.edu/explore/ai2/tutorials) introduce screens, components and blocks.
- **Classification with blocks:** [Introduction to Machine Learning: Image Classification](https://appinventor.mit.edu/explore/resources/ai/image-classification-look-extension) provides beginner activities and teaching materials. It uses MIT's Look extension, so its blocks differ from this project.
- **Collect examples and train:** [Personal Image Classifier: Part 1](https://appinventor.mit.edu/explore/resources/ai/personal-image-classifier-part1) introduces training and testing. Its model format is not a drop-in `.pte` for this extension.
- **ML with Python:** [PyTorch: Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html) walks through data, models and training. This is the app's **Learn about AI** link.
- **Deploy on a phone:** [ExecuTorch documentation](https://docs.pytorch.org/executorch/stable/index.html) explains the runtime and model deployment. This is the app's **PyTorch / ExecuTorch** link. Use the pinned **1.5.1** export/runtime version for this extension.

## Next step: use your own model

The sections below cover extending and building the extension. You can use the fruit app without completing them.

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
python -m pip install numpy Pillow
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

If App Inventor reports **Upload Error**, use the ARM64 phone build (around 6.2 MB) rather than the larger multi-ABI build. Select an `.aia` through the project importer or an `.aix` through the extension importer. If it persists, record the full error; an upload failure alone does not establish the cause.

If an older project fails with **AttachNativeLibs: Unknown native lib type**, import the rebuilt sample; it removes the native declaration that triggers the server error. If **join** reports `*nothing*`, replace the older sample project: event arguments must use their actual names, such as `message`, not `get message`.

For **UnsatisfiedLinkError: libfbjni.so not found**, including a `clns` namespace error, use extension version **3** or newer and rebuild the APK. Its loader explicitly loads `libc++_shared.so` and then `libfbjni.so` by absolute path before ExecuTorch, because Android does not search the extraction directory for transitive dependencies. The updated sample projects already include this loader. Fully close an older app or Companion process before testing a new native extension.

## Verification status

Local checks pass for Java/DEX compilation, numeric inputs, native assets, project archives, prediction fixtures and fruit event argument bindings. The fruit project has been opened in App Inventor; reported APK packaging and event binding failures led to fixes. Successful APK compilation, native Android inference, camera/picker behaviour and the revised layout still need device verification. The local Windows Python native ExecuTorch runtime failed to load its DLL with the installed PyTorch; successful export is not a native runtime test.

This is a community starter project, not an official MIT App Inventor or PyTorch extension. The fuller reference implementation is a separate `appinventor-executorch` repo. Both use the same component/package name, so use one at a time in an App Inventor project.

Built from [MIT's extension template](https://github.com/mit-cml/extension-template) and [ExecuTorch's Android API](https://docs.pytorch.org/executorch/stable/using-executorch-android.html).

## Architecture diagram

Open [docs/architecture.drawio](docs/architecture.drawio) in https://app.diagrams.net using **File > Open From > Device**. All nodes and connectors are editable.

## Fruit model reproducibility

The repo includes the pretrained [fruit_classifier.pte](models/fruit_classifier.pte) and the full [480-image dataset subset](models/fruit_dataset.zip): 360 training photos and 120 test photos, with attribution and a manifest inside the ZIP. The app bundles three test photos so beginners can try it without downloading the dataset separately.

`models/fruit_contract.json` records labels, shapes, prediction fixtures and the model hash. `models/fruit_dataset_manifest.json` pins the Fruits-360 revision, original paths, URLs and all 480 content hashes. `models/fruit_parameters.json` contains the derived classifier parameters. CI verifies the model and dataset hashes, rebuilds the app, checks automatic loading/error handling, and includes the model, dataset ZIP and generated app in build artifacts and tagged releases. Pull requests run these checks too.

`python scripts/export_fruit.py` verifies and extracts the checked-in dataset to `.cache/fruits/`, trains the classifier and exports PyTorch -> ExecuTorch 1.5.1. It does not select new photos from upstream. Training needs PyTorch, ExecuTorch, scikit-learn, NumPy and Pillow; CI uses the pretrained model and does not retrain it. Normalization beyond RGB /255 is embedded in the model. Host evaluation reached 100% on this selected 120-image Test subset; that is not a claim of accuracy on arbitrary phone photos. Android inference and camera/picker behaviour require device validation.

The fruit model, derived parameters and sample photographs use CC BY-SA 4.0 with attribution to Mihai Oltean, Fruits-360. Extension/application code remains Apache-2.0; see [dataset attribution and scope](models/FRUIT_DATASET.md).
