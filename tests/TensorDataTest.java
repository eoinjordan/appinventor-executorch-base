import java.util.Arrays;
import org.community.executorch.TensorData;

public final class TensorDataTest {
  private static void check(boolean value) { if (!value) throw new AssertionError(); }
  private static void badShape(Object[] shape, int count) {
    try { TensorData.shape(shape, count); throw new AssertionError("Invalid shape accepted"); }
    catch (IllegalArgumentException | ArithmeticException expected) {}
  }
  private static void badValue(Object value) {
    try { TensorData.values(new Object[]{value}); throw new AssertionError("Invalid float accepted"); }
    catch (IllegalArgumentException expected) {}
  }
  public static void main(String[] args) {
    check(Arrays.equals(TensorData.rgb(new int[]{0xffff0000,0xff00ff00}), new float[]{1,0,0,1,0,0}));
    check(Arrays.equals(TensorData.rgb(new int[]{0xffffffff,0xff000000}), new float[]{1,0,1,0,1,0}));
    check(Arrays.equals(TensorData.values(new Object[]{1, "2.5", -3}), new float[]{1, 2.5f, -3}));
    check(Arrays.equals(TensorData.shape(new Object[]{1, 4}, 4), new long[]{1, 4}));
    check(TensorData.shape(new Object[]{}, 1).length == 0); // Scalar tensor.
    check(Arrays.equals(TensorData.shape(new Object[]{"2", "3"}, 6), new long[]{2, 3}));
    check(Arrays.equals(TensorData.rgb(new int[]{0x001122ff}), new float[]{17/255f,34/255f,1})); // Ignore alpha.
    check(TensorData.rgb(new int[]{}).length == 0);
    check(TensorData.values(new Object[]{}).length == 0);
    check(Arrays.equals(TensorData.values(new Object[]{Float.MAX_VALUE}), new float[]{Float.MAX_VALUE}));
    badShape(new Object[]{}, 0);
    badShape(new Object[]{-1}, 1);
    badShape(new Object[]{Double.POSITIVE_INFINITY}, 1);
    badShape(new Object[]{(double) Integer.MAX_VALUE + 1}, 1);
    badShape(new Object[]{null}, 1);
    badShape(new Object[]{"not a number"}, 1);
    badShape(new Object[]{0}, 0);
    badShape(new Object[]{1.5}, 1);
    badShape(new Object[]{2, 3}, 5);
    badShape(new Object[]{Double.NaN}, 1);
    badShape(new Object[]{Integer.MAX_VALUE,Integer.MAX_VALUE,3}, 1);
    for (double value : new double[]{Double.NaN, Double.POSITIVE_INFINITY, Double.MAX_VALUE}) {
      badValue(value);
    }
    badValue(null);
    badValue("");
    badValue("apple");
    badValue(Double.NEGATIVE_INFINITY);
    check(Arrays.equals(TensorData.box(new float[]{1,2.5f}), new Object[]{1.0,2.5}));
    check(Arrays.equals(TensorData.box(new long[]{Long.MAX_VALUE}), new Object[]{Long.MAX_VALUE}));
    System.out.println("PASS: float32 conversion, shape products, scalar shape, invalid values and overflow");
  }
}
