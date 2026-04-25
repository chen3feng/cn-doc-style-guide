# 工具

本仓库附带一组用于检查和自动修复中文 Markdown 文档排版的 Python 小工具，实现了《[Markdown 规范](markdown.md)》和《[最佳实践](best_practices.md)》中的一部分机械可检查的规则。

工具仅依赖 Python 3 标准库，无需安装。源码位于 `src/cndocstyle/`，作为 Python 包使用（`python3 -m cndocstyle.xxx`）。

## `cndocstyle.check` — 格式检查

扫描指定路径下的所有 `.md` 文件，报告不符合规范的位置。

```bash
python3 -m cndocstyle.check path/to/docs
python3 -m cndocstyle.check README.md foo.md bar/
python3 -m cndocstyle.check path/to/docs --exclude multi-space
```

检测项包括：

| 规则名 | 含义 |
| ---- | ---- |
| `han+ascii` | 汉字紧邻 ASCII 字母/数字，中间缺少半角空格 |
| `ascii+han` | ASCII 字母/数字紧邻汉字，中间缺少半角空格 |
| `han,` `han:` `han;` `han?` `han!` | 汉字后使用了半角标点（应为全角） |
| `han()` | 汉字与半角括号相邻 |
| `multi-space` | 汉字之间出现两个及以上空格 |
| `ascii-quote` | 汉字与半角 `"` 相邻 |

围栏代码块（```` ``` ```` / `~~~`）、行内代码（`` `...` ``）以及 Markdown 链接的 URL 部分会在扫描前被忽略，以减少误报。

> 注：行内代码两侧的正常空格会被当作 `multi-space` 误报，这是已知限制，可用 `--exclude multi-space` 过滤。

退出码：发现任何问题时返回非零，可直接用在 CI 中。

## `cndocstyle.formatter` — 自动修复

在「安全变换」的前提下，自动修复 `cndocstyle.check` 能发现的大部分问题：

- 在汉字与 ASCII 字母/数字之间补一个半角空格。
- 将汉字后紧跟的半角 `, : ; ? !` 替换为对应的全角标点（`://` 这种 URL 片段会保留）。
- 将与汉字相邻的半角 `(` `)` 替换为全角 `（` `）`。
- 合并汉字之间的多余空格。

**默认是干跑（dry run）**，只打印会改哪些文件；加 `--apply` 才真正写回：

```bash
# 看一眼哪些文件会被修改
python3 -m cndocstyle.formatter path/to/docs

# 确认没问题后再落盘
python3 -m cndocstyle.formatter --apply path/to/docs
```

为避免误伤，以下情况**不会**自动处理，请手动检查：

- 半角双引号 `"..."` → 弯引号 `“…”`。因为 `"` 经常出现在代码片段、URL 或英文原文中，自动转换风险太大。
- 半角句号 `.`。文件名、版本号、域名等会被破坏。
- C++ 的 `+` 与汉字相邻时不加空格（例如 `C++目标` 不会被改成 `C++ 目标`）。

## `cndocstyle.preview` — 预览 diff

不写回、仅输出 `cndocstyle.formatter` 将会产生的 unified diff，方便审阅：

```bash
python3 -m cndocstyle.preview path/to/doc.md
```

## 推荐流程

1. 先跑 `cndocstyle.check` 看看问题规模。
2. 针对个别文件用 `cndocstyle.preview` 核对自动修复是否符合预期。
3. 执行 `cndocstyle.formatter --apply` 批量修复。
4. 再跑一次 `cndocstyle.check`，人工处理剩余（引号、句号、专有名词大小写等工具不处理的项）。

> 在仓库根目录下执行 `python3 -m cndocstyle.xxx` 即可；若要在其他目录使用，可把本仓库的 `src/` 加入 `PYTHONPATH`，或将来通过 `pip install` 发布后直接 `import cndocstyle`。

## 开发与测试

这组工具只依赖 Python 3 标准库，使用时无需安装任何依赖。但如果要修改工具本身，建议安装 [`ruff`](https://docs.astral.sh/ruff/) 和 `pytest`：

```bash
python3 -m pip install ruff pytest
```

所有配置都在仓库根目录的 `pyproject.toml` 中：

```bash
# 静态检查（与 CI 使用同一套规则）
ruff check .

# 代码风格检查（与 CI 使用同一套规则）
ruff format --check .

# 如需自动修复风格，去掉 --check 即可
ruff format .

# 跑单元测试
pytest
```

GitHub Actions 工作流 `.github/workflows/ci.yml` 会在 push 和 pull request 时自动跑 `ruff check`、`ruff format --check` 和 `pytest`，覆盖 Python 3.9/3.10/3.11/3.12。
