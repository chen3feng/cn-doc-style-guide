"""Tests for ``cndocstyle.preview``."""

from __future__ import annotations

from cndocstyle import preview


def test_preview_empty_for_clean_file(tmp_path):
    p = tmp_path / "clean.md"
    p.write_text("已经 v1 发布。\n", encoding="utf-8")
    assert preview.preview(str(p)) == ""


def test_preview_shows_unified_diff_for_dirty_file(tmp_path):
    p = tmp_path / "dirty.md"
    p.write_text("版本v1\n", encoding="utf-8")
    diff = preview.preview(str(p))
    assert diff != ""
    # Unified-diff header lines.
    assert "--- " in diff
    assert "+++ " in diff
    # Shows both the old and the new line.
    assert "-版本v1" in diff
    assert "+版本 v1" in diff


def test_preview_does_not_modify_file(tmp_path):
    p = tmp_path / "dirty.md"
    original = "版本v1\n"
    p.write_text(original, encoding="utf-8")
    preview.preview(str(p))
    assert p.read_text(encoding="utf-8") == original


def test_main_returns_zero_when_no_diff(tmp_path, capsys):
    p = tmp_path / "clean.md"
    p.write_text("已经 v1 发布。\n", encoding="utf-8")
    rc = preview.main([str(p)])
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_main_returns_one_when_there_is_a_diff(tmp_path, capsys):
    p = tmp_path / "dirty.md"
    p.write_text("版本v1\n", encoding="utf-8")
    rc = preview.main([str(p)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "-版本v1" in out
    assert "+版本 v1" in out


def test_main_with_no_args_prints_doc(capsys):
    rc = preview.main([])
    # Documented behaviour: no args -> usage + exit code 2.
    assert rc == 2
    out = capsys.readouterr().out
    assert out.strip() != ""
