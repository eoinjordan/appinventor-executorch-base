package org.community.executorch;

import android.os.Build;
import android.os.Process;
import com.facebook.soloader.nativeloader.NativeLoader;
import com.facebook.soloader.nativeloader.NativeLoaderDelegate;
import com.google.appinventor.components.runtime.Component;
import com.google.appinventor.components.runtime.Form;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/** Provides an explicit native library path for APK and Companion extension class loaders. */
final class NativeRuntime {
  private static boolean ready;

  static synchronized void prepare(Form form, Component component) throws IOException {
    if (ready) return;
    if (!Process.is64Bit()) {
      throw new IOException("ExecuTorch requires a 64-bit app process. Build a 64-bit APK; a 32-bit Companion is unsupported.");
    }
    String selected = null;
    for (String abi : Build.SUPPORTED_ABIS) {
      if (abi.equals("arm64-v8a") || abi.equals("x86_64")) {
        selected = abi;
        break;
      }
    }
    if (selected == null) throw new IOException("Unsupported Android ABI");
    final File folder = new File(form.getFilesDir(), "executorch-1.5.1/" + selected);
    if (!folder.isDirectory() && !folder.mkdirs()) {
      throw new IOException("Cannot create native directory");
    }

    // Re-copy at process initialization so an interrupted previous copy is never reused.
    try (ZipInputStream zip = new ZipInputStream(
        form.openAssetForExtension(component, "native-runtime.zip"))) {
      ZipEntry entry;
      byte[] buffer = new byte[65536];
      while ((entry = zip.getNextEntry()) != null) {
        if (!entry.getName().startsWith(selected + "/")) continue;
        String name = entry.getName().substring(selected.length() + 1);
        if (!name.matches("lib[A-Za-z0-9_+.-]+\\.so")) {
          throw new IOException("Invalid native asset name");
        }
        File target = new File(folder, name);
        if (target.exists() && !target.delete()) throw new IOException("Cannot replace native library");
        try (OutputStream out = new FileOutputStream(target)) {
          int count;
          while ((count = zip.read(buffer)) != -1) out.write(buffer, 0, count);
        }
        if (!target.setReadOnly()) throw new IOException("Cannot protect native library");
      }
    }

    for (String name : new String[] {"libc++_shared.so", "libfbjni.so", "libexecutorch.so"}) {
      File library = new File(folder, name);
      if (!library.isFile() || library.length() == 0) {
        throw new IOException("Missing native asset for " + selected + ": " + name);
      }
    }

    NativeLoader.initIfUninitialized(new NativeLoaderDelegate() {
      @Override public boolean loadLibrary(String name, int flags) {
        System.load(new File(folder, System.mapLibraryName(name)).getAbsolutePath());
        return true;
      }
      @Override public String getLibraryPath(String name) {
        return new File(folder, System.mapLibraryName(name)).getAbsolutePath();
      }
      @Override public int getSoSourcesVersion() { return 1; }
    });
    System.load(new File(folder, "libc++_shared.so").getAbsolutePath());
    // ExecuTorch has a DT_NEEDED dependency on fbjni. Android's linker does not
    // search this asset extraction directory for transitive dependencies.
    // Preload fbjni by absolute path into this class loader's namespace first.
    System.load(new File(folder, "libfbjni.so").getAbsolutePath());
    ready = true;
  }
}
