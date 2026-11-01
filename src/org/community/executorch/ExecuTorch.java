package org.community.executorch;

import android.app.Activity;
import android.graphics.Bitmap;
import com.google.appinventor.components.annotations.DesignerComponent;
import com.google.appinventor.components.annotations.SimpleEvent;
import com.google.appinventor.components.annotations.SimpleFunction;
import com.google.appinventor.components.annotations.SimpleObject;
import com.google.appinventor.components.common.ComponentCategory;
import com.google.appinventor.components.runtime.AndroidNonvisibleComponent;
import com.google.appinventor.components.runtime.ComponentContainer;
import com.google.appinventor.components.runtime.EventDispatcher;
import com.google.appinventor.components.runtime.OnDestroyListener;
import com.google.appinventor.components.runtime.util.YailList;
import com.google.appinventor.components.runtime.util.MediaUtil;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import org.pytorch.executorch.EValue;
import org.pytorch.executorch.Module;
import org.pytorch.executorch.Tensor;

/** Minimal custom-PTE component. All native model operations use one worker. */
@DesignerComponent(
    version = 2,
    description = "Run a custom ExecuTorch 1.5.1 PTE model. One float32 tensor input and output. Android 8+, 64-bit process.",
    category = ComponentCategory.EXTENSION,
    nonVisible = true,
    androidMinSdk = 26,
    iconName = "aiwebres/executorch.png")
@SimpleObject(external = true)
public final class ExecuTorch extends AndroidNonvisibleComponent implements OnDestroyListener {
  private final Activity activity;
  private final ThreadPoolExecutor worker = new ThreadPoolExecutor(
      1, 1, 0L, TimeUnit.MILLISECONDS, new ArrayBlockingQueue<Runnable>(4));
  private volatile boolean destroyed;
  // Accessed only on the worker thread.
  private Module model;

  private interface Task {
    void run() throws Exception;
  }

  public ExecuTorch(ComponentContainer container) {
    super(container.$form());
    activity = container.$context();
    form.registerForOnDestroy(this);
  }

  private void submit(final String operation, final Task task) {
    if (destroyed) return;
    try {
      worker.execute(new Runnable() {
        @Override public void run() {
          try {
            task.run();
          } catch (Exception e) {
            error(operation, e);
          } catch (LinkageError e) {
            // Unsupported ABI or missing native dependency becomes a block event.
            error(operation, e);
          }
        }
      });
    } catch (RejectedExecutionException e) {
      error(operation, new IllegalStateException("Busy: wait for the previous result"));
    }
  }

  private void event(final String name, final Object... args) {
    activity.runOnUiThread(new Runnable() {
      @Override public void run() {
        if (!destroyed) EventDispatcher.dispatchEvent(ExecuTorch.this, name, args);
      }
    });
  }

  private void error(String operation, Throwable e) {
    event("ErrorOccurred", operation, e.getClass().getSimpleName() + ": " + e.getMessage());
  }

  @SimpleFunction(description = "Load a .pte project asset. Replaces the previous model only after loading succeeds. Export with ExecuTorch 1.5.1.")
  public void LoadModel(final String assetName) {
    submit("LoadModel", new Task() {
      @Override public void run() throws Exception {
        if (!assetName.endsWith(".pte")) {
          throw new IllegalArgumentException("Provide the name of a .pte project asset");
        }
        NativeRuntime.prepare(form, ExecuTorch.this);
        File file = File.createTempFile("executorch-", ".pte", activity.getCacheDir());
        Module next = null;
        try {
          try (InputStream in = form.openAsset(assetName);
               OutputStream out = new FileOutputStream(file)) {
            byte[] buffer = new byte[65536];
            int count;
            while ((count = in.read(buffer)) != -1) out.write(buffer, 0, count);
          }
          // FILE mode owns a buffer; the temporary asset copy can be deleted.
          next = Module.load(file.getAbsolutePath(), Module.LOAD_MODE_FILE);
          next.loadMethod("forward");
          Module previous = model;
          model = next;
          next = null;
          if (previous != null) previous.destroy();
          event("ModelLoaded", assetName);
        } finally {
          if (next != null) next.destroy();
          file.delete();
        }
      }
    });
  }

  @SimpleFunction(description = "Run forward with a flat float32 values list and an integer shape list. Returns one float32 tensor; wait for InferenceCompleted before submitting another frame.")
  public void RunModel(final YailList values, final YailList shape) {
    submit("RunModel", new Task() {
      @Override public void run() {
        if (model == null) throw new IllegalStateException("Load a model first");
        float[] input = TensorData.values(values.toArray());
        long[] dimensions = TensorData.shape(shape.toArray(), input.length);
        runTensor(input, dimensions);
      }
    });
  }

  @SimpleFunction(description = "Run a project image asset or image-picker path. Stretch-resize to size x size and pass RGB float32 NCHW values in [0,1]. Use a model exported for this exact input contract, such as the bundled fruit model. Returns InferenceCompleted.")
  public void RunImage(final String imagePath, final int size) {
    submit("RunImage", new Task() {
      @Override public void run() throws Exception {
        if (model == null) throw new IllegalStateException("Load a model first");
        if (size < 1 || size > 512) {
          throw new IllegalArgumentException("Image size must be between 1 and 512");
        }
        Bitmap source = MediaUtil.getBitmapDrawable(form, imagePath).getBitmap();
        Bitmap resized = Bitmap.createScaledBitmap(source, size, size, true);
        try {
          int[] pixels = new int[size * size];
          resized.getPixels(pixels, 0, size, 0, 0, size, size);
          runTensor(TensorData.rgb(pixels), new long[] {1, 3, size, size});
        } finally {
          // MediaUtil may cache the source bitmap; only release our resized copy.
          if (resized != source) resized.recycle();
        }
      }
    });
  }

  private void runTensor(float[] input, long[] dimensions) {
    long start = System.nanoTime();
    EValue[] outputs = model.forward(EValue.from(Tensor.fromBlob(input, dimensions)));
    if (outputs.length != 1 || !outputs[0].isTensor()) {
      throw new IllegalArgumentException("This base supports exactly one tensor output");
    }
    Tensor output = outputs[0].toTensor();
    event("InferenceCompleted",
        YailList.makeList(TensorData.box(output.getDataAsFloatArray())),
        YailList.makeList(TensorData.box(output.shape())),
        (System.nanoTime() - start) / 1e6);
  }

  @SimpleFunction(description = "Release the current model's native memory.")
  public void UnloadModel() {
    submit("UnloadModel", new Task() {
      @Override public void run() {
        releaseModel();
        event("ModelUnloaded");
      }
    });
  }

  private void releaseModel() {
    if (model != null) {
      model.destroy();
      model = null;
    }
  }

  @Override public void onDestroy() {
    destroyed = true;
    worker.getQueue().clear();
    // Cleanup follows any running inference, never racing native execution.
    worker.execute(new Runnable() {
      @Override public void run() { releaseModel(); }
    });
    worker.shutdown();
  }

  @SimpleEvent(description = "The model's forward method is ready.")
  public void ModelLoaded(String assetName) { event("ModelLoaded", assetName); }

  @SimpleEvent(description = "The current model has been released.")
  public void ModelUnloaded() { event("ModelUnloaded"); }

  @SimpleEvent(description = "Flat float32 output values, output shape, and inference duration in milliseconds.")
  public void InferenceCompleted(YailList values, YailList shape, double elapsedMs) {
    event("InferenceCompleted", values, shape, elapsedMs);
  }

  @SimpleEvent(description = "A load, input, inference, or native-library error.")
  public void ErrorOccurred(String operation, String message) {
    event("ErrorOccurred", operation, message);
  }
}
