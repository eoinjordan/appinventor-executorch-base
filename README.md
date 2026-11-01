# ExecuTorch for MIT App Inventor

A community extension that lets MIT App Inventor apps run a PyTorch model on the
phone with [ExecuTorch](https://docs.pytorch.org/executorch/stable/index.html).
The ready-made example app looks at a photo and says whether it shows an
**apple, banana or orange**. The model runs on the phone's own processor, so the
photo is never sent to a server.

<img width="270" height="600" alt="ExecuTorch fruit classification app running on an Android phone" src="https://github.com/user-attachments/assets/3570e2de-3861-469a-b173-69e5a24d080a" />

You can try the example without installing Python, training anything or writing
code: the project file already contains the extension, the trained model, sample
photos and all the blocks.

> **Project status.** This is a community learning project, not an official MIT
> App Inventor or PyTorch extension. The extension builds and passes its host-side
> checks, but inference on a real Android phone and the camera/gallery flows have
> not yet been verified on a device. If you test it on a phone, please
> [open an issue](https://github.com/eoinjordan/appinventor-executorch-extension/issues)
> with what you saw.

## Where to start

| I want to… | Go to |
| --- | --- |
| Try the fruit app on my phone | [Try the example app](#try-the-example-app) below |
| Understand what the app is doing | [Learning guide](docs/learning-guide.md): concepts, a walk through one prediction, experiments |
| Add ExecuTorch blocks to my own App Inventor project | [Use the extension in your own project](#use-the-extension-in-your-own-project) below |
| Train the fruit model myself, or swap in my own copy | [Training and export guide](docs/training-and-export.md) |
| Build, test, release or change the extension itself | [Developer guide](docs/developer-guide.md) |
| See the other sample projects (Iris, add-one smoke test) | [Example projects](examples/README.md) |

## What you need

- An [MIT App Inventor](https://ai2.appinventor.mit.edu/) account and a computer with a web browser.
- An Android phone running **Android 8 or later** that runs apps as **64-bit** processes.
  Most phones from the last few years do. 32-bit devices and iOS are not supported.
- A way to copy an APK to the phone (USB cable, cloud drive or email to yourself).

Use a **built APK** for your first test. The App Inventor Companion app runs as a
32-bit process on some devices and cannot load the ExecuTorch runtime.

### Downloads

| File | What it is | Do you need it? |
| --- | --- | --- |
| [`ExecuTorchFruit.aia`](examples/ExecuTorchFruit.aia) | The complete, editable example project | **Yes.** Everything else is already inside it. On GitHub, use **Download raw file**. |
| `ExecuTorch-ARM64.aix` | The extension on its own, for phones | Only for your own project. Get it from [Releases](https://github.com/eoinjordan/appinventor-executorch-extension/releases). |
| `ExecuTorch-multi-ABI.aix` | Larger extension that also supports x86_64 emulators | Only if you need an emulator. |
| `fruit_classifier.pte` | The trained model (about 39 KB) | Already inside the `.aia`. Also in [`models/`](models/). |

Quick glossary: an **.aia** is a project you open and edit in App Inventor; an
**.aix** adds new blocks to a project; an **.apk** is the app you install on the
phone; a **.pte** is the model file ExecuTorch runs.

Release downloads are built from the code at their tag, so a release can be a
little older than the example in this repository.

## Try the example app

1. Sign in to [MIT App Inventor](https://ai2.appinventor.mit.edu/).
2. Choose **Projects → Import project (.aia) from my computer** and pick
   `ExecuTorchFruit.aia`. If you imported an older version before, give this one a new name.
3. Look around. In **Designer** you will see the screen layout and a non-visible
   `ExecuTorch1` component. In **Blocks** you will see how the model is loaded and
   how a photo is classified.
4. Choose **Build → Android App (.apk)**, copy the APK to your phone and install it.
5. Open the app and wait for the status to read **Ready**. The bundled model loads automatically.
6. Under **Sample photos**, tap **Apple**, **Banana** and **Orange**. Each prediction
   should match the photo shown. These buttons only test the model; they do not train it.
7. Try **Choose photo** or **Take photo**, allowing access when Android asks. Start
   with a single, centred fruit on a plain white background.
8. Optional: turn on airplane mode and tap a sample again. Classification still
   works because it runs on the phone. Only the learning links need the internet.

For each prediction the app shows the chosen label, the three class scores and
how long inference took. A high score is not a guarantee: the model always picks
one of its three fruits, even for a photo of something else.

### The dataset behind the model

![Nine training photographs: three views each of an apple, a banana and an orange on white backgrounds](docs/images/fruit-dataset.png)

The model was trained on a small, pinned subset of the
[Fruits-360](https://github.com/fruits-360/fruits-360-100x100) dataset:
360 training photos and 120 separate test photos, with isolated fruit on white
backgrounds. The grid above shows nine real training photos; the app bundles
three test photos. Photos by Mihai Oltean, CC BY-SA 4.0. See the
[attribution and scope notes](models/FRUIT_DATASET.md) and the
[source records for these nine images](docs/images/fruit-dataset-sources.json).

This is **image classification**: one label for the whole photo. The app does
not find several fruits in one picture or draw boxes around them. Unusual
varieties, cluttered backgrounds or unrelated objects can produce confident but
wrong answers. The [learning guide](docs/learning-guide.md) has experiments that
show these limits.

## How the blocks work

| Block or event | What it does in the example |
| --- | --- |
| `Screen.Initialize` | Calls `LoadModel("fruit_classifier.pte")` |
| `ModelLoaded(assetName)` | Enables the photo buttons once the model is ready |
| `RunImage(imagePath, 32)` | Resizes the photo to 32 × 32, converts it to numbers and runs the model |
| `InferenceCompleted(values, shape, elapsedMs)` | Delivers three scores; the app shows the highest-scoring label |
| `ErrorOccurred(operation, message)` | Shows which step failed and the original error text |

The three scores arrive in **apple, banana, orange** order, which is positions
**1, 2, 3** in an App Inventor list. That order belongs to this particular model;
your own model defines its own.

The [learning guide](docs/learning-guide.md#follow-one-prediction-through-the-blocks)
follows a single prediction through these blocks step by step.

## Use the extension in your own project

1. Download `ExecuTorch-ARM64.aix` from [Releases](https://github.com/eoinjordan/appinventor-executorch-extension/releases)
   and import it with **Extensions → Import extension**.
2. Drag **ExecuTorch** onto the screen. It appears as a non-visible component.
3. Upload your `.pte` file to the project's **Media**.
4. Call `LoadModel` with the exact asset filename. Only enable your inference
   button after `ModelLoaded` fires.
5. For an image model that matches the contract, call `RunImage(imagePath, size)`.
   For any other model, call `RunModel(values, shape)` with a flat list of numbers
   and the matching dimensions.
6. Handle `InferenceCompleted` to show results and `ErrorOccurred` to show problems.

Your model must be exported with **ExecuTorch 1.5.1** and take one float32 tensor
in and give one float32 tensor out. The full
[model contract](docs/developer-guide.md#model-contract) is in the developer guide.

## Replace the fruit model with your own

The [training and export guide](docs/training-and-export.md) walks through
training the classifier on your computer and exporting it to a `.pte`, with the
exact commands, recorded terminal output and an explanation of every setting.

Once you have a new `fruit_classifier.pte`, replace the one in the example
project's **Media**, rebuild the APK and test all three samples again. Keep the
input size at 32 and the same label order. If you change the classes, input shape
or preprocessing, update the blocks and labels to match.

## If something goes wrong

| What you see | What to try |
| --- | --- |
| **Upload Error** when importing | Import an `.aia` through the *project* importer and an `.aix` through the *extension* importer. On a phone, use the smaller ARM64 extension. |
| **Model unavailable** on the status line | Read the original error shown below it, then tap **Retry loading fruit model**. The photo buttons stay disabled until loading succeeds. |
| **Load a model first** | Use the current example project and wait for `ModelLoaded`. Do not enable inference after a failed load. |
| `libfbjni.so` or linker namespace error | Use extension version 3 or newer, rebuild the APK and fully close the old app before testing again. |
| `join` shows `*nothing*` | You have an older example. Import the current `.aia`; event variables must be named plainly (`message`, not `get message`). |
| A prediction looks wrong | Test a bundled sample first. Then check lighting, background, fruit variety and, for your own model, the class order. |

When reporting a problem, please include the complete error text, your Android
version, which example or extension version you used, and whether it was an APK or
the Companion. More detail is in the developer guide's
[troubleshooting section](docs/developer-guide.md#troubleshooting).

## Learn more

- [MIT App Inventor beginner tutorials](https://appinventor.mit.edu/explore/ai2/tutorials)
- [MIT: Introduction to Machine Learning: Image Classification](https://appinventor.mit.edu/explore/resources/ai/image-classification-look-extension)
  (uses MIT's Look extension, so the blocks differ)
- [PyTorch: Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)
- [ExecuTorch documentation](https://docs.pytorch.org/executorch/stable/index.html)
- [Earlier screenshots of this project](docs/screenshots.md)

## License

The extension and example code are **Apache-2.0** ([LICENSE](LICENSE)). The fruit
photos, dataset subset and the model trained from them are **CC BY-SA 4.0** with
attribution to Mihai Oltean / Fruits-360. Keep those notices if you share a modified
app. Full details are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and
[models/FRUIT_DATASET.md](models/FRUIT_DATASET.md).

Source, releases and issues: [github.com/eoinjordan/appinventor-executorch-extension](https://github.com/eoinjordan/appinventor-executorch-extension).
