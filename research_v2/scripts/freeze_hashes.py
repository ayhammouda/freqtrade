"""Generate or verify the local research-v2 SHA-256 manifest."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def freeze_files(repository: Path, output: Path) -> list[Path]:
    research_root = repository / "research_v2"
    files = [
        path
        for path in research_root.rglob("*")
        if path.is_file()
        and path.resolve() != output.resolve()
        and not EXCLUDED_PARTS.intersection(path.parts)
    ]
    agents = repository / "AGENTS.md"
    if agents.is_file():
        files.append(agents)
    return sorted(files, key=lambda path: path.relative_to(repository).as_posix())


def manifest_lines(repository: Path, output: Path) -> list[str]:
    return [
        f"{sha256_file(path)}  {path.relative_to(repository).as_posix()}"
        for path in freeze_files(repository, output)
    ]


def verify(repository: Path, output: Path) -> None:
    existing = output.read_text(encoding="utf-8").splitlines()
    current = manifest_lines(repository, output)
    if existing != current:
        existing_set = set(existing)
        current_set = set(current)
        missing = sorted(existing_set - current_set)
        added = sorted(current_set - existing_set)
        raise RuntimeError(
            f"Manifest mismatch; changed_or_missing={missing}; current_or_added={added}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    repository = args.repository.resolve()
    output = args.output.resolve()
    if args.verify:
        verify(repository, output)
        print(f"Verified {len(manifest_lines(repository, output))} manifest entries")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    lines = manifest_lines(repository, output)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines)} hashes to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
