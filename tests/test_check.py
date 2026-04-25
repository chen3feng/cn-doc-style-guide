"""Tests for ``cndocstyle.check``."""

from __future__ import annotations

import os

from cndocstyle import check


def _names(issues):
    """Extract the rule-name column from ``scan_file`` output."""
    return sorted({rule for _, _, rule, _ in issues})


def _write(tmp_path, text, name="doc.md"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return str(p)


# -- scan_line ---------------------------------------------------------------


def test_scan_line_detects_han_ascii():
    hits = list(check.scan_line("版本v1.0"))
    rules = {name for name, _, _ in hits}
    assert "han+ascii" in rules


def test_scan_line_detects_ascii_han():
    hits = list(check.scan_line("v1 版本".replace(" ", "")))  # "v1版本"
    rules = {name for name, _, _ in hits}
    assert "ascii+han" in rules


def test_scan_line_detects_half_width_punct():
    hits = list(check.scan_line("你好,世界"))
    assert any(r == "han," for r, _, _ in hits)

    hits = list(check.scan_line("提示:这里"))
    assert any(r == "han:" for r, _, _ in hits)

    hits = list(check.scan_line("甲;乙"))
    assert any(r == "han;" for r, _, _ in hits)

    hits = list(check.scan_line("真的?是"))
    assert any(r == "han?" for r, _, _ in hits)

    hits = list(check.scan_line("不!要"))
    assert any(r == "han!" for r, _, _ in hits)


def test_scan_line_colon_before_double_slash_is_ignored():
    # "中文http://foo" contains `文h` which is still han+ascii, but NOT han:.
    hits = list(check.scan_line("见http://example.com"))
    assert not any(r == "han:" for r, _, _ in hits)


def test_scan_line_detects_parens():
    hits = list(check.scan_line("注释(说明)结束"))
    assert any(r == "han()" for r, _, _ in hits)


def test_scan_line_detects_multi_space():
    hits = list(check.scan_line("你  好"))
    assert any(r == "multi-space" for r, _, _ in hits)


def test_scan_line_detects_ascii_quote():
    hits = list(check.scan_line('他说"你好"结束'))
    assert any(r == "ascii-quote" for r, _, _ in hits)


def test_scan_line_inline_code_is_ignored():
    # Half-width comma is inside backticks, must not fire.
    hits = list(check.scan_line("使用 `a,b` 参数"))
    assert not any(r == "han," for r, _, _ in hits)


def test_scan_line_link_url_is_ignored():
    # Half-width punctuation inside the URL of a Markdown link must not fire.
    hits = list(check.scan_line("见[文档](http://example.com/a,b)结束"))
    # No han-punct or han+ascii inside the url because URL gets blanked.
    rules = {r for r, _, _ in hits}
    assert "han," not in rules
    assert "han:" not in rules


def test_scan_line_clean_input_has_no_hits():
    assert list(check.scan_line("你好，世界。")) == []
    assert list(check.scan_line("版本 v1.0 发布")) == []


# -- scan_file ---------------------------------------------------------------


def test_scan_file_skips_fenced_code_blocks(tmp_path):
    md = "# 标题\n\n```\n代码,里,的,逗号,不算\n```\n\n正文,这里算\n"
    path = _write(tmp_path, md)
    issues = check.scan_file(path)
    # Only the last line should have produced a han, hit.
    lines = {ln for ln, _, _, _ in issues}
    assert 7 in lines
    assert 4 not in lines  # inside the fenced block


def test_scan_file_handles_tilde_fences(tmp_path):
    md = "~~~\n里面,有,半角逗号\n~~~\n外面,也有\n"
    path = _write(tmp_path, md)
    issues = check.scan_file(path)
    lines = {ln for ln, _, _, _ in issues}
    assert 4 in lines
    assert 2 not in lines


def test_scan_file_clean_document(tmp_path):
    md = "# 标题\n\n这是一段干净的中文，没有问题。\n"
    path = _write(tmp_path, md)
    assert check.scan_file(path) == []


# -- CLI ---------------------------------------------------------------------


def test_main_returns_zero_on_clean_file(tmp_path, capsys):
    path = _write(tmp_path, "# 标题\n\n正文没问题。\n")
    rc = check.main([path])
    assert rc == 0


def test_main_returns_nonzero_on_dirty_file(tmp_path, capsys):
    path = _write(tmp_path, "标题:错误\n")
    rc = check.main([path])
    assert rc == 1
    out = capsys.readouterr().out
    assert "han:" in out


def test_main_exclude_flag_silences_rule(tmp_path, capsys):
    # Only violation is multi-space; excluding it must yield rc=0.
    path = _write(tmp_path, "你  好\n")
    rc = check.main([path, "--exclude", "multi-space"])
    assert rc == 0


def test_main_walks_directory(tmp_path, capsys):
    sub = tmp_path / "sub"
    sub.mkdir()
    _write(sub, "标题:错误\n", name="a.md")
    _write(sub, "# ok\n\n正文。\n", name="b.md")
    # A non-markdown file should be ignored.
    (sub / "readme.txt").write_text("不算,的\n", encoding="utf-8")

    rc = check.main([str(tmp_path)])
    assert rc == 1
    out = capsys.readouterr().out
    assert os.path.join("sub", "a.md") in out
    assert "readme.txt" not in out
