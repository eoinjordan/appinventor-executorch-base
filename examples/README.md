# Example projects

Three ready-to-import App Inventor projects. Each one already contains the
extension and its model, so you can import, build an APK and test without any
other downloads. All three need a 64-bit Android phone; see
[What you need](../README.md#what-you-need) in the main README.

| Project | What it shows | Model | Start here if… |
| --- | --- | --- | --- |
| [`ExecuTorchFruit.aia`](ExecuTorchFruit.aia) | Image classification from the camera or gallery | `fruit_classifier.pte`, 3 classes, about 39 KB | You are new to this. This is the main example. |
| [`ExecuTorchIris.aia`](ExecuTorchIris.aia) | Classification from four typed-in numbers | `iris_classifier.pte`, 3 classes, about 2 KB | You want to see a numeric (non-image) model. |
| [`ExecuTorchSmoke.aia`](ExecuTorchSmoke.aia) | The smallest possible round trip through the extension | `add_one.pte`, adds 1 to each input | You are debugging the extension itself. |

Import any of them with **Projects → Import project (.aia) from my computer**.

## Fruit photo classifier

The step-by-step walkthrough, block explanations and troubleshooting live in the
[main README](../README.md#try-the-example-app). In short: import, build an APK,
wait for **Ready**, then tap **Apple**, **Banana** or **Orange** under **Sample
photos**. Each sample should produce its own label. Then try **Choose photo** or
**Take photo** with one centred fruit on a plain white background.

The sample buttons classify photos that ship with the app; they do not train the
model. The model has no "unknown" class, so it may confidently name a fruit when
shown something else. The [learning guide](../docs/learning-guide.md) explains why
and suggests experiments.

The **What is running on this phone** card shows the loaded model file, the
ExecuTorch runtime version and the model's limits. The **Learn more** buttons
(**App Inventor tutorials**, **Learn about AI**, **PyTorch / ExecuTorch** and
**This project's guide**) open in your browser and need an internet connection.
Classification itself runs on the phone.

### What the app does under the hood

On startup the app calls `LoadModel("fruit_classifier.pte")`. The photo controls
stay disabled until `ModelLoaded` fires. If loading fails, the app shows the
original error and offers **Retry loading fruit model**; if retrying does not help,
that first error message is the one to report.

When you pick a photo the app calls `RunImage(path, 32)`. The extension stretches
the image to 32 × 32, converts it to an RGB float32 tensor of shape `[1, 3, 32, 32]`
with values in `[0, 1]`, and runs the model. Any further normalization is baked into
the model. `InferenceCompleted` returns three probabilities in **apple, banana,
orange** order.

### For maintainers

- Regenerate the project: `python scripts/make_fruit_example.py`
- Check it: `python scripts/verify_fruit.py`
- Retrain and re-export: see the [training and export guide](../docs/training-and-export.md).
  Needs PyTorch, ExecuTorch 1.5.1, scikit-learn, NumPy and Pillow.

The repository ships the pretrained [`fruit_classifier.pte`](../models/fruit_classifier.pte)
and the full [480-photo dataset subset](../models/fruit_dataset.zip). GitHub Actions
verifies their hashes and publishes them with the generated app. On the host, the
model classified all 120 held-out test photos correctly; that says nothing yet about
native Android execution or photos from a phone camera, which still need device testing.

Dataset, model and photo attribution: [models/FRUIT_DATASET.md](../models/FRUIT_DATASET.md).

## Iris measurements classifier

A numeric example: the classic Iris dataset, where four flower measurements predict
one of three species. There is no camera involved, so it is a good way to see
`RunModel` with a plain list of numbers.

Build and install the APK, then tap **Try setosa**, **Try versicolor** or
**Try virginica** followed by **Classify flower**. The prediction should match the
preset. You can also edit the four measurements yourself (sepal length, sepal width,
petal length and petal width, all in centimetres). The app shows three probability
scores and the inference time.

### For maintainers

- Regenerate the project: `python scripts/make_iris_example.py`
- Check it: `python scripts/verify_iris.py`
- Retrain and re-export: `python scripts/export_iris.py` in an environment with
  ExecuTorch 1.5.1, PyTorch, scikit-learn and NumPy. Export was last tested with
  PyTorch 2.8.0 and scikit-learn 1.8.0.

`models/iris_contract.json` records the input shape `[1, 4]`, output shape `[1, 3]`,
feature order, presets, labels and the PTE hash. Normalization is inside the model.
`iris_parameters.json` holds the trained weights and `iris_test_fixtures.json` the
disjoint train/test indices and held-out predictions. The classifier scored 100% on
its fixed 30-sample held-out split; as with the fruit model, native Android
execution has not yet been verified on a device.

Dataset attribution: Fisher, R. (1936). Iris. UCI Machine Learning Repository,
<https://doi.org/10.24432/C56C76>, CC BY 4.0. Training uses scikit-learn's copy.
See [models/DATASETS.md](../models/DATASETS.md).

## Add-one smoke test

The smallest useful check that the extension works at all. `add_one.pte` adds 1 to
every element of its input. The app loads the model, runs `RunModel` with values
`[1, 2, 3, 4]` and shape `[1, 4]`, and should display `[2, 3, 4, 5]`.

Use this when you are changing the extension's Java or native packaging and want to
rule out the model as a cause. The [developer guide](../docs/developer-guide.md#using-your-own-model)
shows the same blocks in text form.

### For maintainers

- Regenerate the project: `python scripts/make_example.py`
- Regenerate the model: `python scripts/export_smoke.py` (needs ExecuTorch 1.5.1)
- Check it: `python scripts/verify.py`
