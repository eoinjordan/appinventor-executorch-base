# Learning guide: what the fruit app is doing

Once you have the app running (see the [main README](../README.md)), use this guide
to understand what happens between tapping a photo and seeing a label, and to try
some experiments that show what the model can and cannot do.

## The idea in one paragraph

**Image classification** means giving a whole image one label from a fixed list.
This app's list has three entries: apple, banana and orange. The model does not find
where the fruit is, count fruits, or draw boxes; it only answers "which of my three
labels fits this picture best?" Everything it knows was learned from example photos
before the app was built. Choosing a photo in the app does not teach it anything new.

## Words you will meet

| Term | What it means here |
| --- | --- |
| Dataset | The labelled fruit photos used to train and test the model |
| Training | Adjusting the model's numbers so it predicts the training photos well. Done once, on a computer, before the app exists |
| Model | The saved calculation that turns image numbers into three scores |
| Inference | Running that calculation on a new photo. This is what the phone does |
| Class / label | One of the possible answers: apple, banana or orange |
| Tensor | A grid of numbers. A photo becomes a tensor of red, green and blue values |
| Score | One number per class. The app shows the label with the highest score |
| PyTorch | The Python library used to describe and export the model |
| ExecuTorch | The runtime that executes the exported model on the phone |

In this project the classifier is trained with scikit-learn, rebuilt as a PyTorch
model, then exported to an ExecuTorch `.pte` file. App Inventor provides the screen,
camera, photo picker and the blocks that tie it together.

## Follow one prediction through the blocks

1. When the screen opens, **Screen.Initialize** calls `LoadModel("fruit_classifier.pte")`.
   Loading happens in the background.
2. When the model is ready, **ModelLoaded** fires and the app enables the sample and
   photo buttons. Until then they stay greyed out.
3. When you choose a photo, the app calls `RunImage(imagePath, 32)`. The extension
   shrinks the photo to 32 × 32 pixels and turns its red, green and blue values into
   a tensor of numbers between 0 and 1.
4. The model runs and **InferenceCompleted** fires with three scores, in
   **apple, banana, orange** order, plus the time it took. The app picks the
   highest score and shows its label.
5. If anything fails along the way, **ErrorOccurred** fires with the name of the step
   and the original error message, and the app displays both.

Loading and inference are asynchronous: the app waits for the completion event
rather than assuming the work is done.

## Experiments to try

- **Record a baseline.** Run each of the three sample photos and note the label and
  all three scores. You now know what "working" looks like.
- **Change one thing at a time.** Photograph the same fruit on a white surface, then
  change only the lighting, then only the angle, then only the background. Which
  changes move the scores most?
- **Show it something it has never seen.** Try a pear, a tomato or an empty table.
  The model still has to choose apple, banana or orange, and it may do so with a
  high score. This is the most important lesson: a confident answer is not
  necessarily a correct one.
- **Prove it runs on the phone.** After the model loads, turn on airplane mode and
  classify a sample again. Only the learning links need the internet.
- **Think like a data collector.** If you wanted this model to work on your kitchen
  table, what photos would you need to add? More varieties? Different lighting?
  Other objects labelled as "not a fruit"? Remember to keep some test photos aside
  that the model never trains on.

## Why it gets things wrong

The training photos show single, isolated fruits of one variety each on a plain
white background, and there is no "none of these" class. On the computer, the model
labelled all 120 held-out test photos correctly, but those test photos look just like
the training ones. Real phone photos, other varieties, clutter and unrelated objects
are outside what it has seen. The
[dataset attribution and scope notes](../models/FRUIT_DATASET.md) spell out these
limits.

## Learn more

- **New to App Inventor?** [MIT's beginner tutorials](https://appinventor.mit.edu/explore/ai2/tutorials)
  introduce screens, components and blocks.
- **Classification with blocks:** MIT's
  [Introduction to Machine Learning: Image Classification](https://appinventor.mit.edu/explore/resources/ai/image-classification-look-extension)
  has beginner activities and teaching materials. It uses MIT's Look extension, so
  its blocks differ from this project's.
- **Collect your own examples:** MIT's
  [Personal Image Classifier, Part 1](https://appinventor.mit.edu/explore/resources/ai/personal-image-classifier-part1)
  introduces training and testing with your own photos. Its model format is not a
  drop-in `.pte` for this extension.
- **Machine learning in Python:** [PyTorch: Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)
  walks through data, models and training. This is the app's **Learn about AI** link.
- **Running models on phones:** the [ExecuTorch documentation](https://docs.pytorch.org/executorch/stable/index.html)
  explains the runtime. This is the app's **PyTorch / ExecuTorch** link. This
  extension uses version **1.5.1**.

## Next steps

- [Train and export the model yourself](training-and-export.md): the exact commands,
  recorded output, dataset counts and what each setting means.
- [Developer guide](developer-guide.md): the model contract, using your own model,
  building and releasing the extension.
