package org.community.executorch;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/** Exercises the production dependency loader without loading Android binaries on the host. */
public final class NativeLibrariesTest {
  private static void check(boolean value) {
    if (!value) throw new AssertionError();
  }

  public static void main(String[] args) throws Exception {
    File folder = Files.createTempDirectory("native-libraries-test-").toFile();
    String[] names = {"libc++_shared.so", "libfbjni.so", "libexecutorch.so"};
    try {
      for (String name : names) Files.write(new File(folder, name).toPath(), new byte[] {1});
      List<String> loaded = new ArrayList<>();
      NativeLibraries.loadDependencies(folder, loaded::add);
      check(loaded.equals(Arrays.asList(new File(folder, names[0]).getAbsolutePath(),
          new File(folder, names[1]).getAbsolutePath())));

      for (String missing : names) {
        File file = new File(folder, missing);
        check(file.delete());
        loaded.clear();
        try {
          NativeLibraries.loadDependencies(folder, loaded::add);
          throw new AssertionError("Missing dependency accepted: " + missing);
        } catch (IOException expected) {
          check(expected.getMessage().contains(missing));
          check(loaded.isEmpty()); // Never partially initialize an incomplete bundle.
        }
        Files.write(file.toPath(), new byte[0]);
        try {
          NativeLibraries.loadDependencies(folder, loaded::add);
          throw new AssertionError("Empty dependency accepted");
        } catch (IOException expected) {
          check(loaded.isEmpty());
        }
        Files.write(file.toPath(), new byte[] {1});
      }

      loaded.clear();
      UnsatisfiedLinkError failure = new UnsatisfiedLinkError("simulated linker error");
      try {
        NativeLibraries.loadDependencies(folder, path -> { loaded.add(path); throw failure; });
        throw new AssertionError("Linker failure swallowed");
      } catch (UnsatisfiedLinkError expected) {
        check(expected == failure);
        check(loaded.size() == 1); // Do not load fbjni if libc++ fails.
      }
      loaded.clear();
      NativeLibraries.loadDependencies(folder, loaded::add); // A failed attempt remains retryable.
      check(loaded.size() == 2);
    } finally {
      for (String name : names) Files.deleteIfExists(new File(folder, name).toPath());
      Files.delete(folder.toPath());
    }
    System.out.println("PASS: native dependency order, complete bundle preflight, linker errors and retry");
  }
}
