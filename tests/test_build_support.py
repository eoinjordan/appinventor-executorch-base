from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_support import latest_version_directory, reset_output_directory


class BuildSupportTest(unittest.TestCase):
    def test_numeric_sdk_selection_excludes_previews_and_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ["9.0.0", "10.0.0", "36.0.0", "37.0.0-rc1", "unrelated"]:
                (root / name).mkdir()
            (root / "99.0.0").touch()
            self.assertEqual(latest_version_directory(root).name, "36.0.0")

    def test_platform_selection_and_no_supported_versions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(FileNotFoundError):
                latest_version_directory(root, "android-")
            for name in ["android-9", "android-35", "android-36-preview"]:
                (root / name).mkdir()
            self.assertEqual(latest_version_directory(root, "android-").name, "android-35")

    def test_clean_rebuild_removes_deleted_classes_and_old_dex(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ["classes", "dex"]:
                output = root / name
                output.mkdir()
                (output / "stale-output").write_text("old build")
                self.assertEqual(reset_output_directory(output, root), output.resolve())
                self.assertEqual(list(output.iterdir()), [])

    def test_clean_rejects_workspace_root_and_outside_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "build"
            root.mkdir()
            for target in [root, root.parent, root / ".." / "unrelated"]:
                with self.assertRaises(ValueError):
                    reset_output_directory(target, root)
            self.assertTrue(root.is_dir())


if __name__ == "__main__":
    unittest.main()
