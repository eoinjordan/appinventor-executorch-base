# Block reference

Every block the ExecuTorch component adds to App Inventor (extension version 4). The pictures and tables are generated from the built extension by `python scripts/make_block_reference.py`; edit the Java source or that script, not this page.

Run a custom ExecuTorch 1.5.1 PTE model. One float32 tensor input and output. Android 8+, 64-bit process.

Drag **ExecuTorch** from the Extension drawer onto the screen; it appears as a non-visible component. In the Blocks editor, click `ExecuTorch1` to find the blocks below. The purple blocks are calls you make; the gold blocks are events that run when the extension has something to report.

## Calls

### LoadModel

![call ExecuTorch1.LoadModel](images/blocks/call-LoadModel.png)

Load a .pte project asset. Replaces the previous model only after loading succeeds. Export with ExecuTorch 1.5.1.

| Parameter | Type | Meaning |
| --- | --- | --- |
| `assetName` | text | Exact filename of the `.pte` in the project Media, for example `fruit_classifier.pte`. |

Call once, usually in `Screen.Initialize`. Wait for `ModelLoaded` before running anything. If loading fails you get `ErrorOccurred` with operation `LoadModel`, and the previous model, if any, stays loaded.

### RunImage

![call ExecuTorch1.RunImage](images/blocks/call-RunImage.png)

Run a project image asset or image-picker path. Stretch-resize to size x size and pass RGB float32 NCHW values in [0,1]. Use a model exported for this exact input contract, such as the bundled fruit model. Returns InferenceCompleted.

| Parameter | Type | Meaning |
| --- | --- | --- |
| `imagePath` | text | A Media asset name (`apple.jpg`), an ImagePicker `Selection`, or the `image` path from `Camera.AfterPicture`. |
| `size` | number | Side length in pixels. The photo is stretched to `size × size`; the fruit model uses 32. |

For image models that take RGB float32 NCHW input in `[0, 1]`. Any further normalization must be inside the model. Finishes with `InferenceCompleted` or `ErrorOccurred`.

### RunModel

![call ExecuTorch1.RunModel](images/blocks/call-RunModel.png)

Run forward with a flat float32 values list and an integer shape list. Returns one float32 tensor; wait for InferenceCompleted before submitting another frame.

| Parameter | Type | Meaning |
| --- | --- | --- |
| `values` | list | Flat list of numbers in row-major order. For a `[1, 4]` tensor, four numbers. |
| `shape` | list | List of positive whole numbers whose product equals the length of `values`. An empty list means a single scalar. |

For any model that takes one float32 tensor. Finishes with `InferenceCompleted` or `ErrorOccurred`. Wait for the result before sending the next call; the queue holds four.

### UnloadModel

![call ExecuTorch1.UnloadModel](images/blocks/call-UnloadModel.png)

Release the current model's native memory.

No parameters.

Frees the native memory. Raises `ModelUnloaded`. Call `LoadModel` again before the next inference.

## Events

### ModelLoaded

![when ExecuTorch1.ModelLoaded](images/blocks/event-ModelLoaded.png)

The model's forward method is ready.

| Parameter | Type | Meaning |
| --- | --- | --- |
| `assetName` | text | The filename that was loaded. The fruit app shows it on screen. |

Use the parameter blocks by name (`message`, not `get message`) inside the event.

Enable your inference buttons here.

### InferenceCompleted

![when ExecuTorch1.InferenceCompleted](images/blocks/event-InferenceCompleted.png)

Flat float32 output values, output shape, and inference duration in milliseconds.

| Parameter | Type | Meaning |
| --- | --- | --- |
| `values` | list | Flat list of float32 outputs. For the fruit model: three scores in apple, banana, orange order (list positions 1, 2, 3). |
| `shape` | list | Shape of the output tensor, for example `[1, 3]`. |
| `elapsedMs` | number | Inference time in milliseconds, measured on the phone. |

Use the parameter blocks by name (`message`, not `get message`) inside the event.

Read scores with the `select list item` block. Scores are probabilities only if the model ends in softmax, as the fruit model does.

### ErrorOccurred

![when ExecuTorch1.ErrorOccurred](images/blocks/event-ErrorOccurred.png)

A load, input, inference, or native-library error.

| Parameter | Type | Meaning |
| --- | --- | --- |
| `operation` | text | Which block failed: `LoadModel`, `RunImage`, `RunModel` or `UnloadModel`. |
| `message` | text | The original error text from the extension or the native runtime. Include it when reporting a problem. |

Use the parameter blocks by name (`message`, not `get message`) inside the event.

Show `message` to the user. The fruit app treats a `LoadModel` error specially: it disables the photo controls and offers a retry.

### ModelUnloaded

![when ExecuTorch1.ModelUnloaded](images/blocks/event-ModelUnloaded.png)

The current model has been released.

No parameters.

The model has been released; inference calls will fail until you load one.

## How the fruit app wires them together

```text
when Screen1.Initialize
    call ExecuTorch1.LoadModel  assetName: "fruit_classifier.pte"

when ExecuTorch1.ModelLoaded (assetName)
    enable the sample and photo buttons; show assetName on screen

when AppleButton.Click
    call ExecuTorch1.RunImage  imagePath: "apple.jpg"  size: 32

when ExecuTorch1.InferenceCompleted (values, shape, elapsedMs)
    compare select list item values 1, 2 and 3; show the largest label and elapsedMs

when ExecuTorch1.ErrorOccurred (operation, message)
    if operation = "LoadModel": disable the buttons, show message, show Retry
    else: show operation and message
```

Open `examples/ExecuTorchFruit.aia` in App Inventor and switch to **Blocks** to see the real thing. The [learning guide](learning-guide.md) walks through one prediction and the [developer guide](developer-guide.md) has the model contract these blocks expect.
