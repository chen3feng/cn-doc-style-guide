"""Tests for ``cndocstyle.formatter``."""

from __future__ import annotations

from cndocstyle import formatter as fmt

# -- fix_line: spacing -------------------------------------------------------


def test_inserts_space_between_han_and_ascii():
    assert fmt.fix_line("版本v1.0发布") == "版本 v1.0 发布"


def test_inserts_space_between_ascii_and_han():
    assert fmt.fix_line("v1版本") == "v1 版本"


def test_collapses_multiple_spaces_between_han():
    assert fmt.fix_line("你  好") == "你 好"
    assert fmt.fix_line("你     好") == "你 好"


def test_single_space_between_han_is_left_alone():
    # One space between two Han characters is legal: "你 好" stays "你 好".
    assert fmt.fix_line("你 好") == "你 好"


# -- fix_line: punctuation ---------------------------------------------------


def test_converts_half_width_comma_after_han():
    assert fmt.fix_line("你好,世界") == "你好，世界"


def test_converts_half_width_colon_after_han():
    assert fmt.fix_line("提示:内容") == "提示：内容"


def test_preserves_colon_before_double_slash():
    # Scheme-like ``://`` must NOT become ``：//``.
    assert fmt.fix_line("见http://example.com") == "见 http://example.com"


def test_converts_semicolon_qmark_bang_after_han():
    assert fmt.fix_line("甲;乙") == "甲；乙"
    assert fmt.fix_line("真的?") == "真的？"
    assert fmt.fix_line("不!") == "不！"


def test_converts_ascii_parens_adjacent_to_han():
    assert fmt.fix_line("注释(说明)结束") == "注释（说明）结束"


def test_does_not_touch_standalone_english_punct():
    # Pure English context must be untouched.
    assert fmt.fix_line("hello, world.") == "hello, world."
    assert fmt.fix_line("foo (bar) baz") == "foo (bar) baz"


def test_does_not_touch_double_quote():
    # Intentional: " is NOT in [A-Za-z0-9] and has no dedicated rule, so the
    # formatter leaves Han-adjacent double quotes alone. ``check.py`` still
    # flags them (``ascii-quote``) but fixing is left to the author.
    assert fmt.fix_line('他说"hello"结束') == '他说"hello"结束'


# -- fix_line: protected spans ----------------------------------------------


def test_inline_code_is_protected():
    # Inside backticks, nothing must change - not even half-width punct.
    assert fmt.fix_line("使用 `a,b:c` 参数") == "使用 `a,b:c` 参数"


def test_link_url_is_protected_but_label_is_not():
    # The URL in parens must stay byte-for-byte; the label gets normalised.
    # Here the label "文档v2" needs a space; the URL has a comma that MUST stay.
    # The outer ``[`` / ``]`` are NOT in [A-Za-z0-9], so no space is inserted
    # between the link and the surrounding Han text - another deliberate
    # conservative choice; fix such cases by hand.
    result = fmt.fix_line("见[文档v2](http://example.com/a,b)结束")
    assert result == "见[文档 v2](http://example.com/a,b)结束"


def test_html_tag_contents_are_protected():
    # Attributes inside the tag (``x,y``) must not be touched.
    # ``<`` / ``>`` are not in [A-Za-z0-9] so no space is inserted around
    # the tag boundary - that is a deliberate conservative choice.
    result = fmt.fix_line('前<a href="x,y">文档v1</a>后')
    assert result == '前<a href="x,y">文档 v1</a>后'


# -- fix_text: fenced blocks --------------------------------------------------


def test_fix_text_skips_fenced_code_block():
    src = "正文v1\n```\n代码里v1不改\n```\n正文v2\n"
    expected = "正文 v1\n```\n代码里v1不改\n```\n正文 v2\n"
    assert fmt.fix_text(src) == expected


def test_fix_text_handles_tilde_fences():
    src = "~~~\n原样v1\n~~~\n外面v2\n"
    expected = "~~~\n原样v1\n~~~\n外面 v2\n"
    assert fmt.fix_text(src) == expected


def test_fix_text_is_idempotent():
    src = "版本 v1 发布，详见 `code`。\n"
    once = fmt.fix_text(src)
    twice = fmt.fix_text(once)
    assert once == src
    assert twice == once


def test_fix_text_preserves_trailing_newline():
    src = "版本v1\n"
    out = fmt.fix_text(src)
    assert out.endswith("\n")
    assert out == "版本 v1\n"


def test_fix_text_preserves_no_trailing_newline():
    src = "版本v1"
    assert fmt.fix_text(src) == "版本 v1"


# -- fix_file + CLI -----------------------------------------------------------


def test_fix_file_dry_run_does_not_modify(tmp_path):
    p = tmp_path / "a.md"
    p.write_text("版本v1\n", encoding="utf-8")
    changed = fmt.fix_file(str(p), apply=False)
    assert changed is True
    # Content unchanged on disk.
    assert p.read_text(encoding="utf-8") == "版本v1\n"


def test_fix_file_apply_writes_change(tmp_path):
    p = tmp_path / "a.md"
    p.write_text("版本v1\n", encoding="utf-8")
    changed = fmt.fix_file(str(p), apply=True)
    assert changed is True
    assert p.read_text(encoding="utf-8") == "版本 v1\n"


def test_fix_file_returns_false_when_clean(tmp_path):
    p = tmp_path / "a.md"
    p.write_text("版本 v1\n", encoding="utf-8")
    changed = fmt.fix_file(str(p), apply=True)
    assert changed is False


def test_main_dry_run_reports_would_change_files(tmp_path, capsys):
    p = tmp_path / "a.md"
    p.write_text("版本v1\n", encoding="utf-8")
    rc = fmt.main([str(p)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "DRY" in out
    # File was NOT modified.
    assert p.read_text(encoding="utf-8") == "版本v1\n"


def test_main_apply_modifies_files(tmp_path, capsys):
    p = tmp_path / "a.md"
    p.write_text("版本v1\n", encoding="utf-8")
    rc = fmt.main(["--apply", str(p)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "FIX" in out
    assert p.read_text(encoding="utf-8") == "版本 v1\n"


def test_main_walks_directory_recursively(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    a = sub / "a.md"
    b = sub / "b.md"
    a.write_text("版本v1\n", encoding="utf-8")
    b.write_text("已经 v2 了\n", encoding="utf-8")
    rc = fmt.main(["--apply", str(tmp_path)])
    assert rc == 0
    assert a.read_text(encoding="utf-8") == "版本 v1\n"
    # b was already clean.
    assert b.read_text(encoding="utf-8") == "已经 v2 了\n"
