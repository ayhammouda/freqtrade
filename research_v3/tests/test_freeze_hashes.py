# ruff: noqa: S101

from pathlib import Path

from research_v3.scripts.freeze_hashes import manifest_lines


def test_manifest_excludes_runtime_derivatives(tmp_path: Path) -> None:
    (tmp_path / "engine" / "__pycache__").mkdir(parents=True)
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "engine" / "source.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "Z.txt").write_text("z\n", encoding="utf-8")
    (tmp_path / "a.txt").write_text("a\n", encoding="utf-8")
    (tmp_path / "engine" / "__pycache__" / "source.pyc").write_bytes(b"volatile")
    (tmp_path / "artifacts" / "pytest.xml").write_text("<testsuite />\n", encoding="utf-8")

    lines = manifest_lines(tmp_path)

    assert len(lines) == 3
    assert lines[0].endswith("  Z.txt")
    assert lines[1].endswith("  a.txt")
    assert lines[2].endswith("  engine/source.py")
