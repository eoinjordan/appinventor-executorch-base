package org.community.executorch;

import java.io.File;
import java.io.IOException;

/** Native dependency preflight and ordering, independent of Android for host tests. */
final class NativeLibraries {
  interface Loader {
    void load(String absolutePath);
  }

  private NativeLibraries() {}

  static void loadDependencies(File folder, Loader loader) throws IOException {
    // Check the entire set before loading any part of it into the process.
    for (String name : new String[] {"libc++_shared.so", "libfbjni.so", "libexecutorch.so"}) {
      File library = new File(folder, name);
      if (!library.isFile() || library.length() == 0) {
        throw new IOException("Missing native asset: " + library.getAbsolutePath());
      }
    }
    // Module's static initializer loads ExecuTorch through NativeLoader later.
    // Preload its dependencies in the same class loader's namespace first.
    loader.load(new File(folder, "libc++_shared.so").getAbsolutePath());
    loader.load(new File(folder, "libfbjni.so").getAbsolutePath());
  }
}
