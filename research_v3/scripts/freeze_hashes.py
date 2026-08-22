"""Create or verify a SHA-256 manifest for the research-v3 audit bundle."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


MANIFEST_NAME = "ARTIFACT_HASHES.sha256"
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".ruff_cache"}
EXCLUDED_FILES = {MANIFEST_NAME, "pytest.xml"}


def digest(path: Path) -> str:
    """Return a SHA-256 digest for one file."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def manifest_lines(root: Path) -> list[str]:
    """Produce deterministic manifest lines, excluding the self-referential manifest."""
    files = sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file()
            and path.name not in EXCLUDED_FILES
            and path.suffix not in {".pyc", ".pyo"}
            and not EXCLUDED_PARTS.intersection(path.relative_to(root).parts)
        ),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    return [f"{digest(path)}  {path.relative_to(root).as_posix()}" for path in files]


def main() -> int:
    """Write or verify the current research-v3 bundle manifest."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("research_v3"))
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = root / MANIFEST_NAME
    content = "\n".join(manifest_lines(root)) + "\n"
    if args.verify:
        if not manifest.is_file() or manifest.read_text(encoding="utf-8") != content:
            raise SystemExit("Research-v3 artifact manifest verification failed")
        print(f"Verified {len(content.splitlines())} research-v3 artifacts")
        return 0
    manifest.write_text(content, encoding="utf-8")
    print(f"Wrote {len(content.splitlines())} research-v3 artifact hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
