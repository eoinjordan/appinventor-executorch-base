"""Small, host-testable helpers for selecting SDKs and cleaning build outputs."""
from pathlib import Path
import re
import shutil


def latest_version_directory(root: Path, prefix: str = "") -> Path:
    """Choose the newest installed stable numeric version, excluding previews."""
    candidates = []
    for path in root.iterdir():
        match = re.fullmatch(re.escape(prefix) + r"(\d+(?:\.\d+)*)", path.name)
        if path.is_dir() and match:
            candidates.append((tuple(map(int, match[1].split("."))), path))
    if not candidates:
        raise FileNotFoundError(f"No stable SDK versions found in {root}")
    return max(candidates)[1]


def reset_output_directory(path: Path, workspace: Path) -> Path:
    """Remove stale generated files, refusing targets outside the build workspace."""
    path = path.resolve()
    workspace = workspace.resolve()
    if path == workspace or not path.is_relative_to(workspace):
        raise ValueError(f"Output must be inside the build workspace: {path}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path
