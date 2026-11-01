# Learning guide

Start with the [main README](../README.md) to get the app running. This page explains
what the app is doing and suggests experiments.

## What you are learning

**Image classification** assigns a label to a whole image. This app chooses among three
labels; it does not locate multiple objects or draw boxes around them.

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

The classifier is trained with scikit-learn, represented as a PyTorch model, then
exported to an ExecuTorch `.pte` file. App Inventor supplies the screen, camera, photo
picker and event blocks. Choosing a photo does not add it to the training dataset or
change the model.

## Follow one prediction through the blocks

1. **Screen.Initialize** calls `LoadModel("fruit_classifier.pte")`.
2. **ModelLoaded** enables the sample and photo controls and shows the model name under
   **What is running on this phone**.
3. Selecting a photo calls `RunImage(imagePath, 32)`. The extension resizes it to 32 by
   32 pixels and converts its red, green and blue channels into numbers.
4. **InferenceCompleted** returns three scores, in **apple, banana, orange** order, and
   the elapsed time. The app displays the highest-scoring label.
5. **ErrorOccurred** supplies the operation and message if a step fails.

Loading and inference finish asynchronously: use their completion events before
starting the next step.

## Experiments to try

- **Establish a baseline:** run each supplied photo and record its label and three scores.
- **Change one thing:** photograph the same fruit on a white surface, then change only the lighting, angle or background. Which scores change?
- **Try something unfamiliar:** show a pear or an empty table. The model still chooses one of its three classes. A high score does not guarantee a correct answer.
- **Check local inference:** after the model loads, enable airplane mode and classify a bundled sample again. Only the **Learn more** links need a connection.
- **Think about better data:** what additional varieties, lighting and backgrounds would you collect? Keep separate test photos that were not used to train the model.

The dataset contains isolated fruit on simple backgrounds and limited varieties. The
model has no "unknown" class. Host evaluation matched all 120 test photos, which are
separate from the 360 training photos, but those test photos look like the training
photos. Everyday photos, other varieties and unrelated objects are outside what it has
seen. See [dataset attribution and limitations](../models/FRUIT_DATASET.md).

## Learn more

- **New to App Inventor:** [MIT's beginner tutorials](https://appinventor.mit.edu/explore/ai2/tutorials) introduce screens, components and blocks. This is the app's **App Inventor tutorials** link.
- **Classification with blocks:** [Introduction to Machine Learning: Image Classification](https://appinventor.mit.edu/explore/resources/ai/image-classification-look-extension) provides beginner activities and teaching materials. It uses MIT's Look extension, so its blocks differ from this project.
- **Collect examples and train:** [Personal Image Classifier: Part 1](https://appinventor.mit.edu/explore/resources/ai/personal-image-classifier-part1) introduces training and testing. Its model format is not a drop-in `.pte` for this extension.
- **ML with Python:** [PyTorch: Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html) walks through data, models and training. This is the app's **Learn about AI** link.
- **Deploy on a phone:** [ExecuTorch documentation](https://docs.pytorch.org/executorch/stable/index.html) explains the runtime and model deployment. This is the app's **PyTorch / ExecuTorch** link. Use the pinned **1.5.1** export/runtime version for this extension.

## Next step

- [Train and export the model](training-and-export.md): commands, recorded output, dataset and hyperparameters.
- [Developer guide](developer-guide.md): the model contract, using your own model, building and releasing the extension.
