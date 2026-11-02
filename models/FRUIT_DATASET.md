# Fruit example attribution and scope

Dataset: Fruit Recognition dataset. Israr Hussain, Qianhua He, Zhuliang Chen and Wei Xie,
South China University of Technology, 2018. https://doi.org/10.5281/zenodo.1310165 .
License: CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ .

This example uses the Apple, Banana and Orange classes. `scripts/make_fruit_subset.py`
selects 400 photos per class from the Zenodo archive with a fixed seed: 300 for training
and 100 for testing, 1,200 in all. The archive MD5, the original path of every photo and
the content hash of every stored copy are recorded in `fruit_dataset_manifest.json`. No
photo appears in both splits.

Transformations: RGB conversion and a resize so the longer side is at most 128 pixels
when the subset is stored; a bilinear stretch resize to 32 by 32, division by 255 and
scaling to [-1, 1] when the model is trained and run. Trained normalization and
classifier parameters are embedded in `fruit_classifier.pte`. The three bundled sample
photos are copies from the Test split, renamed apple.jpg, banana.jpg and orange.jpg.

The photos, derived model and parameters are distributed with attribution to the authors
above under CC BY 4.0. The surrounding extension and application source code is
Apache-2.0. No endorsement by the dataset authors is implied.

This is a small three-class teaching classifier. The dataset shows one kind of fruit at a
time, often several pieces, on a metal tray under varied lab lighting, with several
apple varieties. Everyday
photographs, other varieties, cluttered backgrounds and unrelated objects are not
validated. It may confidently label an unrelated object as one of its three classes. No
general-purpose fruit-recognition accuracy is claimed.
