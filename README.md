# ExecuTorch for MIT App Inventor

[![Build and release extension](https://github.com/eoinjordan/appinventor-executorch-extension/actions/workflows/release-extension.yml/badge.svg)](https://github.com/eoinjordan/appinventor-executorch-extension/actions/workflows/release-extension.yml)
[![Latest release](https://img.shields.io/github/v/release/eoinjordan/appinventor-executorch-extension?label=release&color=246747)](https://github.com/eoinjordan/appinventor-executorch-extension/releases/latest)
[![ExecuTorch 1.5.1](https://img.shields.io/badge/ExecuTorch-1.5.1-7c5cbf)](https://docs.pytorch.org/executorch/stable/index.html)
[![Android 8+ 64-bit](https://img.shields.io/badge/Android-8%2B%2064--bit-586a62)](#what-you-need)
[![License: Apache-2.0](https://img.shields.io/badge/code-Apache--2.0-blue)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-blue)](models/FRUIT_DATASET.md)

**Downloads** (latest release):
[![Download the app (.apk)](https://img.shields.io/badge/app-ExecuTorchFruit.apk-246747)](https://github.com/eoinjordan/appinventor-executorch-extension/releases/latest/download/ExecuTorchFruit.apk)
[![Download the project (.aia)](https://img.shields.io/badge/project-ExecuTorchFruit.aia-246747)](https://github.com/eoinjordan/appinventor-executorch-extension/releases/latest/download/ExecuTorchFruit.aia)
[![Download the extension for phones (.aix)](https://img.shields.io/badge/extension-ExecuTorch--ARM64.aix-7c5cbf)](https://github.com/eoinjordan/appinventor-executorch-extension/releases/latest/download/ExecuTorch-ARM64.aix)
[![Download the extension for emulators (.aix)](https://img.shields.io/badge/extension-ExecuTorch--multi--ABI.aix-7c5cbf)](https://github.com/eoinjordan/appinventor-executorch-extension/releases/latest/download/ExecuTorch-multi-ABI.aix)
[![Download the model (.pte)](https://img.shields.io/badge/model-fruit__classifier.pte-b6872c)](https://github.com/eoinjordan/appinventor-executorch-extension/releases/latest/download/fruit_classifier.pte)
[![Download the dataset subset (.zip)](https://img.shields.io/badge/dataset-fruit__dataset.zip-b6872c)](https://github.com/eoinjordan/appinventor-executorch-extension/releases/latest/download/fruit_dataset.zip)

A community Android extension for running a local machine learning model from
App Inventor blocks. The example app classifies a photo as **apple, banana or orange**.
It uses your phone's processor to run a PyTorch ExecuTorch model; classification
does not send the photo to a server.

<img width="270" height="600" alt="ExecuTorch Fruit Classification App Demo" src="https://github.com/user-attachments/assets/3570e2de-3861-469a-b173-69e5a24d080a" />

You can try the supplied pretrained model without installing Python or training
anything. The extension, model, photos and blocks are all included in one project file.

## Where to go next

| If you want to | Read |
| --- | --- |
| Try the fruit app on your phone | This page |
| Understand what the app is doing | [Learning guide](docs/learning-guide.md) |
| Train the fruit model yourself or replace it with your own | [Training and export](docs/training-and-export.md) |
| See every block and its parameters | [Block reference](docs/blocks.md) |
| Add the extension to your own App Inventor project | [Use your own model](#next-step-use-your-own-model) below |
| Build, test, release or change the extension | [Developer guide](docs/developer-guide.md) |

## What to download

You need an App Inventor account, a computer with a browser and a 64-bit Android
phone running Android 8 or later.

| File | What it is | When you need it |
| --- | --- | --- |
| [ExecuTorchFruit.apk](https://github.com/eoinjordan/appinventor-executorch-extension/raw/main/assets/ExecuTorchFruit.apk) | The built app, ready to install (about 13 MB) | Quickest way to try it on a phone; no App Inventor account needed |
| [ExecuTorchFruit.aia](examples/ExecuTorchFruit.aia) | Editable App Inventor project with the extension and model | Start here to see and change the blocks; download the raw file from GitHub |
| [ExecuTorch-ARM64.aix](https://github.com/eoinjordan/appinventor-executorch-extension/releases/latest/download/ExecuTorch-ARM64.aix) | Extension that adds ExecuTorch blocks | For your own project; not needed separately for the sample |
| [ExecuTorch-multi-ABI.aix](https://github.com/eoinjordan/appinventor-executorch-extension/releases/latest/download/ExecuTorch-multi-ABI.aix) | Larger extension that also supports x86_64 emulators | Only for an emulator |
| `.pte` | Exported model that ExecuTorch runs | Already included as `fruit_classifier.pte` (about 39 KB) |

A release contains the code at its tag, so it can be older than the example in this repository.

<!-- blocks:start -->
## Blocks

The calls you make from your own blocks. Each one finishes with an event; the full list, the events, a diagram of how they run and which blocks each use case needs are in the [block reference](docs/blocks.md).

![The ExecuTorch blocks the fruit app uses](docs/images/blocks/fruit-app-blocks.png)


### LoadModel

![call ExecuTorch1.LoadModel](docs/images/blocks/call-LoadModel.png)

Load a .pte project asset. Replaces the previous model only after loading succeeds. Export with ExecuTorch 1.5.1.

| Parameter | Type | Meaning |
| --- | --- | --- |
| `assetName` | text | Exact filename of the `.pte` in the project Media, for example `fruit_classifier.pte`. |

Call once, usually in `Screen.Initialize`. Wait for `ModelLoaded` before running anything. If loading fails you get `ErrorOccurred` with operation `LoadModel`, and the previous model, if any, stays loaded.

### RunImage

![call ExecuTorch1.RunImage](docs/images/blocks/call-RunImage.png)

Run a project image asset or image-picker path. Stretch-resize to size x size and pass RGB float32 NCHW values in [0,1]. Use a model exported for this exact input contract, such as the bundled fruit model. Returns InferenceCompleted.

| Parameter | Type | Meaning |
| --- | --- | --- |
| `imagePath` | text | A Media asset name (`apple.jpg`), an ImagePicker `Selection`, or the `image` path from `Camera.AfterPicture`. |
| `size` | number | Side length in pixels. The photo is stretched to `size × size`; the fruit model uses 32. |

For image models that take RGB float32 NCHW input in `[0, 1]`. Any further normalization must be inside the model. Finishes with `InferenceCompleted` or `ErrorOccurred`.

### RunModel

![call ExecuTorch1.RunModel](docs/images/blocks/call-RunModel.png)

Run forward with a flat float32 values list and an integer shape list. Returns one float32 tensor; wait for InferenceCompleted before submitting another frame.

| Parameter | Type | Meaning |
| --- | --- | --- |
| `values` | list | Flat list of numbers in row-major order. For a `[1, 4]` tensor, four numbers. |
| `shape` | list | List of positive whole numbers whose product equals the length of `values`. An empty list means a single scalar. |

For any model that takes one float32 tensor. Finishes with `InferenceCompleted` or `ErrorOccurred`. Wait for the result before sending the next call; the queue holds four.

### UnloadModel

![call ExecuTorch1.UnloadModel](docs/images/blocks/call-UnloadModel.png)

Release the current model's native memory.

No parameters.

Frees the native memory. Raises `ModelUnloaded`. Call `LoadModel` again before the next inference.

Events: `ModelLoaded(assetName)`, `InferenceCompleted(values, shape, elapsedMs)`, `ErrorOccurred(operation, message)` and `ModelUnloaded()`. See the [block reference](docs/blocks.md#events) for their parameters.
<!-- blocks:end -->

## Try your first prediction

To skip App Inventor for now, install [ExecuTorchFruit.apk](https://github.com/eoinjordan/appinventor-executorch-extension/raw/main/assets/ExecuTorchFruit.apk)
on your phone (allow installs from your browser or file manager when Android asks) and
go to step 5. To see how it is built:

1. Open [MIT App Inventor](https://ai2.appinventor.mit.edu/) and sign in.
2. Import `examples/ExecuTorchFruit.aia` using **Projects > Import project (.aia) from my computer**. Give it a new project name if you imported an older version.
3. Explore **Designer** to see the screen, then **Blocks** to see how it works.
4. Choose **Build > Android App (.apk)**. Download the APK or scan the QR code on your phone, install it and open it. Use a compiled APK; a 32-bit Companion process cannot load the runtime.

   ![Build > Android App shows a download button and a QR code for the APK](docs/images/screenshots/build-apk-dialog.png)

5. Wait for the result card to say **Ready**. The app loads `fruit_classifier.pte` automatically.
6. Under **Step 1**, tap **Apple**, **Banana** or **Orange**. The prediction should match the selected photo. These buttons classify supplied examples; they do not train the model.
7. Under **Step 2**, try **Choose photo** or **Take photo**. Start with a few fruit of one kind on a plain tray or table. Allow camera/photo access when Android asks.
8. Turn on airplane mode and tap a sample again. Classification still works because the model runs on the phone.

The result card shows the label, the three class scores and the time inference took on
the phone. **What is running on this phone** shows the loaded model file, the ExecuTorch
runtime version and what the model can and cannot see. **Learn more** opens MIT's App
Inventor tutorials, PyTorch's beginner course, the ExecuTorch documentation and this
project's guide; those pages need internet access.

If loading fails, the photo controls stay disabled and the original error appears with
**Retry loading fruit model**. If retry fails, report that loading error.

## The dataset

![Actual Fruit Recognition training photos: apples, bananas and oranges on a tray under lab lighting](docs/images/fruit-dataset.png)

| Label | Training photos | Separate test photos |
| --- | ---: | ---: |
| Apple | 300 | 100 |
| Banana | 300 | 100 |
| Orange | 300 | 100 |
| **Total** | **900** | **300** |

Examples from our subset of the Fruit Recognition dataset: one kind of fruit at a time,
often several pieces, on a metal tray under varied lab lighting, with several apple
varieties. The grid shows training photos; testing uses separate photos. Photos: Hussain,
He, Chen and Xie, South China University of Technology, CC BY 4.0. Resized and labelled;
[attribution](models/FRUIT_DATASET.md) and [source records](docs/images/fruit-dataset-sources.json).

The model gets 89% of the 300 test photos right. That is a fair score for a small linear
model on photos with real lighting variation, and the mistakes are part of what the app
teaches: tap a sample, then try photos that are nothing like the training set.

**Image classification** assigns a label to a whole image. This app chooses among three
labels; it does not locate multiple objects or draw boxes around them. The model has no
"unknown" class, so a pear or an empty table still gets one of the three labels. The
[learning guide](docs/learning-guide.md) explains the terms and has experiments to try.

## How the blocks work

![The ExecuTorch blocks the fruit app uses: LoadModel, ModelLoaded, RunImage, InferenceCompleted and ErrorOccurred](docs/images/blocks/fruit-app-blocks.png)

The purple blocks are calls you make; the gold blocks are events the extension raises.
The [block reference](docs/blocks.md) has a picture of every block, a table of its
parameters, a diagram of how the blocks run and which ones each use case needs.

![The fruit project in the Blocks editor](docs/images/screenshots/blocks-editor.png)

| Block or event | What it does |
| --- | --- |
| `Screen.Initialize` | Calls `LoadModel("fruit_classifier.pte")` |
| `ModelLoaded(assetName)` | Enables the sample and photo controls and fills in the model name |
| `RunImage(imagePath, 32)` | Resizes the photo to 32 by 32 pixels, converts it to numbers and runs the model |
| `InferenceCompleted(values, shape, elapsedMs)` | Returns three scores; the app displays the highest-scoring label |
| `ErrorOccurred(operation, message)` | Supplies the operation and the original error if a step fails |

Scores arrive in **apple, banana, orange** order, which is positions **1, 2, 3** in an
App Inventor list. That order belongs to this model; your own model defines its own.
Loading and inference finish asynchronously: use their completion events before
starting the next step. Two procedures keep the handlers short: `SetControls(enabled)`
turns the five buttons on or off and `Classify(imagePath)` shows the photo and calls
`RunImage`.

| Use case | ExecuTorch blocks you need |
| --- | --- |
| Image model with bundled photos (this app) | `LoadModel`, `ModelLoaded`, `RunImage`, `InferenceCompleted`, `ErrorOccurred` |
| Photos from the gallery or camera | the same, calling `RunImage` from `ImagePicker.AfterPicking` or `Camera.AfterPicture` |
| Numeric model (sensor readings, typed values) | `LoadModel`, `ModelLoaded`, `RunModel`, `InferenceCompleted`, `ErrorOccurred` |
| Switching models or freeing memory | add `UnloadModel` and `ModelUnloaded` |

## Next step: use your own model

The [training and export guide](docs/training-and-export.md) has copyable PowerShell
and terminal commands, recorded command output, and an explanation of each
hyperparameter. These steps are optional; the supplied app already includes its model.
Once you have a new `fruit_classifier.pte`, replace the one in the project's **Media**,
rebuild the APK and test all three samples. Keep size 32 and the same label order.

To add the extension to a different project:

1. Import `ExecuTorch-ARM64.aix` through **Extensions > Import extension**. It appears
   under **Extension** in the palette.

   ![The ExecuTorch extension listed in the Designer palette](docs/images/screenshots/extension-drawer.png)

2. Drag **ExecuTorch** onto the screen. It is a non-visible component.
3. Upload your `.pte` to **Media**.
4. Call `LoadModel` with the exact asset filename. Enable your inference button only after `ModelLoaded`.
5. For an image model that matches the contract, call `RunImage(imagePath, size)`. For any
   other model, call `RunModel(values, shape)` with a flat list and matching dimensions.
6. Handle `InferenceCompleted` and `ErrorOccurred`.

Your model must be exported with ExecuTorch **1.5.1** and take one float32 tensor in and
one float32 tensor out. The full contract is in the
[developer guide](docs/developer-guide.md#deliberately-small-model-contract) and each
block's parameters are in the [block reference](docs/blocks.md).

## If it does not run

| Symptom | What to check |
| --- | --- |
| **Upload Error** | Import an `.aia` through the project importer and an `.aix` through the extension importer. On a phone use the ARM64 extension |
| **Model unavailable** | Read the original loading message, then tap **Retry loading fruit model** |
| **Load a model first** | Use the current sample and wait for `ModelLoaded` |
| `libfbjni.so` or linker namespace error | Use extension version 3 or newer, rebuild the APK and fully close the previous app before retesting |
| `join` receives `*nothing*` | Replace the older sample project; event variables must be named `message`, not `get message` |
| Unexpected prediction | Test a bundled photo first, then check lighting, background, fruit variety and, for your own model, the class order |

When reporting a problem, include the complete error, the Android version, the sample or
extension version, and whether you used an APK or the Companion.

## Learn more

- **New to App Inventor:** [MIT's beginner tutorials](https://appinventor.mit.edu/explore/ai2/tutorials) introduce screens, components and blocks.
- **Classification with blocks:** [Introduction to Machine Learning: Image Classification](https://appinventor.mit.edu/explore/resources/ai/image-classification-look-extension) provides beginner activities and teaching materials. It uses MIT's Look extension, so its blocks differ from this project.
- **ML with Python:** [PyTorch: Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html) walks through data, models and training.
- **Deploy on a phone:** [ExecuTorch documentation](https://docs.pytorch.org/executorch/stable/index.html) explains the runtime and model deployment. This extension uses **1.5.1**.
- [Earlier screenshots](docs/screenshots.md) of the project.

## For supporters

The [developer guide](docs/developer-guide.md) covers the source files, the build and
release process, native packaging, the model contract and the checks CI runs.

Code is Apache-2.0; see [LICENSE](LICENSE). The fruit photos, dataset subset and the
model trained from them are CC BY 4.0 with attribution to Hussain, He, Chen and Xie
(Fruit Recognition dataset, https://doi.org/10.5281/zenodo.1310165).
Keep those notices when sharing a modified app. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [models/FRUIT_DATASET.md](models/FRUIT_DATASET.md).

Built from [MIT's extension template](https://github.com/mit-cml/extension-template) and
[ExecuTorch's Android API](https://docs.pytorch.org/executorch/stable/using-executorch-android.html).
