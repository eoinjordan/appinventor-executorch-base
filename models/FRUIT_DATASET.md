# Fruit example attribution and scope

Dataset: Mihai Oltean, Fruits-360 dataset, 2017–. Source: https://github.com/fruits-360/fruits-360-100x100 . License: CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/ . Copyright (c) 2017– Mihai Oltean.

This example uses Apple Red 1, Banana 1 and Orange 1. The exact source revision, selected original Training/Test paths, download URLs and content hashes are recorded in fruit_dataset_manifest.json. Training uses 120 photos per class; evaluation uses 40 photos per class from the official Test folders. No photos are moved from Test into Training.

Training transformations: RGB conversion, bilinear stretch resize to 32x32, division by 255 and scaling to [-1,1]. Trained normalization and classifier parameters are embedded in fruit_classifier.pte. The three bundled JPG sample photos are unmodified copies from the Test subset, renamed apple.jpg, banana.jpg and orange.jpg.

The model, derived parameters, dataset manifest and example photographs are distributed under CC BY-SA 4.0. The surrounding extension/application source code retains its Apache-2.0 license. No endorsement by the dataset creator is implied.

This is a small three-class teaching classifier, validated on a subset of this dataset. The dataset uses isolated fruit on white backgrounds and limited varieties. Everyday photographs, new varieties, different lighting/backgrounds and unrelated objects are not validated. It may confidently label an unrelated object as one of its three classes. No general-purpose fruit-recognition accuracy is claimed.
