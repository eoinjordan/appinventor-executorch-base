package org.community.executorch;

/** Tensor validation has no Android dependencies, so it can be tested on the host. */
public final class TensorData {
  private TensorData() {}

  public static float[] values(Object[] items) {
    float[] result = new float[items.length];
    for (int i = 0; i < items.length; i++) {
      double value = Double.parseDouble(items[i].toString());
      if (!Double.isFinite(value) || Math.abs(value) > Float.MAX_VALUE) {
        throw new IllegalArgumentException("Values must be finite float32 numbers");
      }
      result[i] = (float) value;
    }
    return result;
  }

  public static long[] shape(Object[] items, int valueCount) {
    long[] result = new long[items.length];
    long product = 1;
    for (int i = 0; i < items.length; i++) {
      double value = Double.parseDouble(items[i].toString());
      if (!Double.isFinite(value) || value < 1 || value != Math.rint(value)
          || value > Integer.MAX_VALUE) {
        throw new IllegalArgumentException("Shape dimensions must be positive integers");
      }
      result[i] = (long) value;
      product = Math.multiplyExact(product, result[i]);
    }
    if (product != valueCount) {
      throw new IllegalArgumentException("Shape product must equal the number of input values");
    }
    return result;
  }

  public static Object[] box(float[] values) {
    Object[] result = new Object[values.length];
    for (int i = 0; i < values.length; i++) result[i] = (double) values[i];
    return result;
  }

  public static Object[] box(long[] values) {
    Object[] result = new Object[values.length];
    for (int i = 0; i < values.length; i++) result[i] = values[i];
    return result;
  }
}
