# Third-party notices

Fruit example: Mihai Oltean, Fruits-360 dataset, 2017–. Source https://github.com/fruits-360/fruits-360-100x100 , CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). The model, learned parameters and bundled sample JPGs are distributed under CC BY-SA 4.0; see models/FRUIT_DATASET.md for transformations, pinned sources and scope. Extension/application source retains Apache-2.0.

Original component, helper, build scripts and example code: Copyright 2026 Eoin. Licensed under Apache-2.0; see LICENSE.

This repository is based on MIT CML's extension-template, retaining its Git history, template build files, dependency submodule and bundled build tools. MIT App Inventor's Java APIs and annotations are compile-time dependencies, not merged into the extension runtime. See https://github.com/mit-cml/appinventor-sources and the individual headers/licenses for the template and build tools.

Runtime dependencies packaged in the AIX:

| Dependency | Version | License |
| --- | --- | --- |
| org.pytorch:executorch-android | 1.5.1 | BSD-3-Clause; see licenses/ExecuTorch-LICENSE.txt |
| com.facebook.fbjni:fbjni | 0.7.0 | Apache-2.0; see licenses/fbjni-LICENSE.txt |
| com.facebook.soloader:nativeloader | 0.10.5 | Apache-2.0; see licenses/SoLoader-LICENSE.txt |
| org.jetbrains.kotlin:kotlin-stdlib | 1.9.23 | Apache-2.0; see licenses/Kotlin-LICENSE.txt |
| Android NDK libc++_shared | Supplied by fbjni 0.7.0 | LLVM/Apache-2.0 with LLVM exceptions; see licenses/LLVM-LICENSE.txt |

ExecuTorch and its distributed native binary also contain third-party code; consult its upstream third-party sources and notices at https://github.com/pytorch/executorch/tree/v1.5.1/third-party before redistribution. The fruit classifier is trained by this project using Fruits-360; its pretrained parameters follow the attribution above. The optional Iris example uses the UCI Iris dataset under CC BY 4.0; see examples/README.md and the app's IRIS_ATTRIBUTION.txt. models/add_one.pte is generated from the add-one module in scripts/export_smoke.py and follows this project's license.

Palette logo: unmodified ExecuTorch logo from https://github.com/pytorch/executorch/blob/v1.5.1/docs/source/_static/img/et-logo.png . ExecuTorch/PyTorch marks belong to their owners; this is a community extension, not an official MIT/PyTorch product.
