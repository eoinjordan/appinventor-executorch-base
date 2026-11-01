# Example project

`ExecuTorchFruit.aia` is the fruit photo classifier described in the
[main README](../README.md). It contains the extension, the trained
`fruit_classifier.pte`, three test photos, the dataset attribution and all the blocks.
Import it with **Projects > Import project (.aia) from my computer**, build an APK and
install it on a 64-bit Android phone.

## What the app does

On startup the app calls `LoadModel("fruit_classifier.pte")`. The photo controls stay
disabled until `ModelLoaded`. If loading fails, the app shows the original error and
offers **Retry loading fruit model**.

When you pick a photo the app calls `RunImage(path, 32)`. The extension stretches the
image to 32 by 32 pixels, converts it to RGB float32 values in `[0, 1]` with shape
`[1, 3, 32, 32]` and runs the model. The remaining normalization is inside the model.
`InferenceCompleted` returns three probabilities in **apple, banana, orange** order and
the app displays the highest-scoring label, the three scores and the inference time.

Each block and its parameters are shown in the [block reference](../docs/blocks.md).
The **Learn more** buttons open MIT's App Inventor tutorials, PyTorch's beginner course,
the ExecuTorch documentation and this project's guide in the browser.

## Regenerating the project

The project is generated, not hand-edited. After changing `scripts/make_fruit_example.py`
or anything in `models/`, run:

```powershell
python scripts/make_fruit_example.py
python scripts/verify_fruit.py
```

The generator reads the extension from `out/org.community.executorch.aix`, so build the
extension first (see the [developer guide](../docs/developer-guide.md#build)). To retrain
or re-export the model, follow [training and export](../docs/training-and-export.md).

Dataset, model and photo attribution: [models/FRUIT_DATASET.md](../models/FRUIT_DATASET.md).
