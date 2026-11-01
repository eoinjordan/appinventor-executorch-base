import java.util.Arrays;
import org.community.executorch.TensorData;

public final class TensorDataTest {
  private static void check(boolean value) { if (!value) throw new AssertionError(); }
  private static void badShape(Object[] shape, int count) {
    try { TensorData.shape(shape, count); throw new AssertionError("Invalid shape accepted"); }
    catch (IllegalArgumentException | ArithmeticException expected) {}
  }
  public static void main(String[] args) {
    check(Arrays.equals(TensorData.rgb(new int[]{0xffff0000,0xff00ff00}), new float[]{1,0,0,1,0,0}));
    check(Arrays.equals(TensorData.rgb(new int[]{0xffffffff,0xff000000}), new float[]{1,0,1,0,1,0}));
    check(Arrays.equals(TensorData.values(new Object[]{1, "2.5", -3}), new float[]{1, 2.5f, -3}));
    check(Arrays.equals(TensorData.shape(new Object[]{1, 4}, 4), new long[]{1, 4}));
    check(TensorData.shape(new Object[]{}, 1).length == 0); // Scalar tensor.
    badShape(new Object[]{0}, 0);
    badShape(new Object[]{1.5}, 1);
    badShape(new Object[]{2, 3}, 5);
    badShape(new Object[]{Double.NaN}, 1);
    badShape(new Object[]{Integer.MAX_VALUE,Integer.MAX_VALUE,3}, 1);
    for (double value : new double[]{Double.NaN, Double.POSITIVE_INFINITY, Double.MAX_VALUE}) {
      try { TensorData.values(new Object[]{value}); throw new AssertionError("Invalid float accepted"); }
      catch (IllegalArgumentException expected) {}
    }
    check(TensorData.box(new float[]{1,2}).length == 2);
    System.out.println("PASS: float32 conversion, shape products, scalar shape, invalid values and overflow");
  }
}
