# Beginner fruit photo classifier

Import **ExecuTorchFruit.aia** through Projects > Import project (.aia) from my computer. The trained PTE, extension, sample photos and all blocks are included. Build an ARM64 Android APK for a phone test; no Python or training is required to try it.

Tap **Apple**, **Banana** or **Orange** under **Sample photos**. Each sample should produce the matching label. These buttons classify supplied photos; they do not train the model. Then try **Choose photo** or **Take photo**. Use one centred fruit on a plain white background. This three-class teaching model may guess a fruit label for unrelated objects; a high score does not guarantee a correct answer.

Use **Learn ML** or **ExecuTorch docs** to open the official tutorials in your browser. Documentation needs internet access; bundled model inference runs locally. The [beginner learning guide](../README.md#learn-more) also links to App Inventor classification lessons and includes experiments to try.

The app loads fruit_classifier.pte on startup, then calls RunImage(path,32). Image conversion produces RGB NCHW float32 [1,3,32,32] in [0,1]; the remaining normalization is inside the model. InferenceCompleted returns probabilities in apple, banana, orange order.

Host eager evaluation classified all 120 selected official Test photos correctly, separately from the 360 Training photos. This does not verify native Android execution or general phone-photo accuracy. Camera/picker permission flows still need device testing.

Generate with `python scripts/make_fruit_example.py`; verify with `python scripts/verify_fruit.py`. Retraining/export uses `scripts/export_fruit.py` with PyTorch, ExecuTorch 1.5.1, scikit-learn, NumPy and Pillow. Dataset, model and photo attribution/license details are in [models/FRUIT_DATASET.md](../models/FRUIT_DATASET.md).

## Optional Iris measurements app

Import **ExecuTorchIris.aia** using App Inventor's Projects > Import project (.aia) from my computer. The extension and 2.3 KB trained `.pte` are already inside it. Build an APK for a 64-bit Android phone; no Python installation or model download is needed on the phone.

Choose Try setosa, Try versicolor or Try virginica, then tap Classify flower. The prediction should match the selected preset. You can edit sepal length, sepal width, petal length and petal width, all in centimetres. Three probability scores and inference time appear below the prediction.

`models/iris_contract.json` documents input [1,4], output [1,3], feature order, presets, labels and PTE hash. Normalization is inside the model. `iris_parameters.json` contains the trained weights and `iris_test_fixtures.json` contains disjoint train/test indices and held-out predictions.

The classifier reached 100% eager accuracy on the fixed 30-sample held-out split. This does not prove native PTE predictions or general plant-identification accuracy. Android execution remains to be tested.

Recreate the project with `python scripts/make_iris_example.py` and check it with `python scripts/verify_iris.py`. To retrain/export, run `scripts/export_iris.py` in an environment with ExecuTorch 1.5.1, PyTorch, scikit-learn and NumPy. Export was tested with PyTorch 2.8.0 and scikit-learn 1.8.0; the local native ExecuTorch Python DLL remains incompatible, so the host tests check eager/exported graphs and saved fixtures.

Dataset attribution: Fisher, R. (1936). Iris. UCI Machine Learning Repository, https://doi.org/10.24432/C56C76 . CC BY 4.0: https://creativecommons.org/licenses/by/4.0/ . Training uses scikit-learn's copy. Measurements and labels were used to derive model parameters; three preset examples are included.

ExecuTorchSmoke.aia remains a smaller add-one diagnostic.
