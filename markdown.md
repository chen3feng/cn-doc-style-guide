# Markdown 风格指导

Markdown 之所以出色，主要是因为它能够编写纯文本并获得结果是出色的格式化输出。
为了使后面的作者保持清晰状态，您的 Markdown 应该尽可能地简单以及与整个语料库可能一致。

我们寻求三个目标的平衡：

1. *源文本可读且可移植。*
2. *Markdown 文件可随时间跨团队维护。*
3. *语法简单易记。*

## 文档布局

通常，大多数文档都受益于以下布局的一些变化：

```markdown
# 文档标题

简介。

[TOC]

## 主题

内容。

## 参见

* https://link-to-more-info
```

1.  `#文档标题`：第一个标题应该是个一级标题，并且理想情况下应与文件名相同或几乎相同。第一个一级标题用作页面`<title>`。

1.  `作者`：*可选*。如果您想声明该文档的所有权，或者如果您对此引以为豪，请在标题下添加自己。然而，修订历史通常就足够了。

1.  `简短介绍。` 用 1-3 个句子提供有关该主题的高级概述话题。想象自己是一个完全的新手，他进入了您的“扩展福报”文档，并且需要了解您视为理所当然的最基本假设。
    “什么是福报？我为什么要扩展它？”

1.  `[TOC]`：如果您使用支持目录的代码托管服务，例如 Gitiles，在简短的介绍之后加上`[TOC]`。参见
    [`[TOC]`文档](https://gerrit.googlesource.com/gitiles/+/master/Documentation/markdown.md#Table-of-contents)。

1.  `## Topic`：其余标题应从 2 级开始。

1.  `## 参见`：将其他链接放在底部，以方便想要了解更多或没有找到需要的信息的用户。

## 字符行限制

尽可能遵守项目的字符行限制。除了长网址和表格可能导致破例外。（标题也不能换行，但我们鼓励保持简短）。其余情况，就换行：

```markdown
无人爱苦，亦无人寻之欲之，乃因其苦。事实中有痛苦可以带来巨大的，以一小例子为例，
有没有人剧烈运动，可以为他带来好处？

*   邪恶克制的足球。在几乎不能说话迫害。我们觉得是很明智，即使这样，也不得不
    保密。参见[福报文档]（https://gerrit.googlesource.com/gitiles/+/master/Documentation/markdown.md）。
```

通常，在长链接之前插入换行符可以保持可读性，同时最大程度地减少溢出：

```markdown
无人爱苦，亦无人寻之欲之，乃因其苦。 参见
[福报文档](https://gerrit.googlesource.com/gitiles/+/master/Documentation/markdown.md)
以了解详情。
```

## 行尾空白

不要使用行尾的空格，而应该使用行尾的反斜杠。

[CommonMark规范](http://spec.commonmark.org/0.20/#hard-line-breaks)要求在行尾的两个空格应插入一个`<br />`标签。
但是，很多目录中有对行尾随空白预提交检查，并且有许多 IDE 无论如何都会清理它。

最佳做法是完全避免使用`<br />`。Markdown 只需使用换行符即可为您创建段落标签：请习惯这种用法。

## 标题

### ATX 风格的标题

```markdown
## 标题 2
```

带`=`或`-`下划线的标题可能很难维护，并且不符合其余的标题语法。 用户会问：`---`是指 H1 还是 H2？

```markdown
标题 - 你记得住这是哪一级吗？**不要这样**
---------
```

### 标题加空格

最好在 `#` 后加上空格，并在前后加上换行符：

```markdown
……前面的文字

# 标题 1

后面的文字……
```

缺少空格会使得源代码阅读起来有点困难：

```markdown
……前面的文字

# 标题 1
后面的文字…… **不要这样**
```

## 列表

### 对长列表使用“懒人编号”

Markdown 足够聪明，可以让生成的 HTML 正确地呈现您的编号列表。对于可能会更改的较长列表，尤其是较长的嵌套列表，请使用“懒人”编号：

```markdown
1.  福。
1.  报。
    1.  福福。
    1.  报报。
1.  爆炸
```

但是，如果列表很小，并且您不怎么去改它，则最好使用完整编号的列表，因为在源代码中更好阅读：

```markdown
1.  福。
2.  报。
3.  福报。
```

### 嵌套列表加空格

当列表嵌套时，对有编号和无编号列表使用 4 个空格缩进：

```markdown
1.  编号列表后空 2 格。
    换行的话缩进 4 格。
2.  又是空 2 格。

*   无编号列表后空 3 格。
    换行的话缩进 4 格。
    1.  编号列表后空 2 格。
        嵌套列表中换行的话缩进 8 格。
    2.  看起来很漂亮，是不是？
*   无编号列表后空 3 格。
```

下面的写法能用，但很混乱：

```markdown
* 一个空格
换行没有缩进。
     1. 不规则的嵌套…… **不要这样。**
```

即使没有嵌套，也可以用 4 个空格缩进，使得对于换行的文字保持一致的布局：

```markdown
*   福，
    换行。

1.  2 个空格
    以及缩进 4 个空格。
2.  又是 2 空格。
```

但是，当列表很小而且没有嵌套且只有一行时，两种列表都只需要空一格就够用了：

```markdown
* 福
* 报
* 爆炸。

1. 福。
2. 报。
```

## 代码

### 内联代码

&#96;反引号&#96; 表示`内联代码`，会将所有括起来的内容原样展示。用于短代码引用和字段名称：

```markdown
您将要运行 `really_cool_script.sh arg`。

请注意该表中的 `福报不断` 字段。
```

当需要在抽象意义上指代某些文件类型，而不是某个具体的文件时，请使用内联代码：

```markdown
请确保更新你的 `README.md`！
```

反引号是“转义” Markdown 元字符最常规的方法。在大多数情况下，需要转义，代码字体才有意义无论如何。

### 代码块

对于超过一行的代码引用，使用代码块：

<pre>
```python
def Foo(self, bar):
  """福报函数"""
  self.bar = bar
```
</pre>

#### 声明语言

最好明确声明代码所用的语言，使得无论是语法高亮或着后续的修改者都无需猜测。

#### 缩进的代码块有时会更整洁

四个空格缩进也被解释为代码块。可以看起来更干净，更容易在源代码中阅读，但是无法指定语言。我们在编写许多简短代码片段时鼓励使用它们：

```markdown
你需要运行：

    bazel run :thing -- --foo

然后：

    bazel run :another_thing -- --bar

接着：

    bazel run :yet_again -- --baz
```

#### 换行转义

读者希望大多数命令行片段都能直接复制粘贴到终端。因此最好对换行进行转义。可以用一个行尾的反斜杠：

<pre>
```shell
bazel run :target -- --flag --foo=longlonglonglonglongvalue \
--bar=anotherlonglonglonglonglonglonglonglonglonglongvalue
```
</pre>

#### 列表中的嵌套代码块

如果你需要在列表中放代码块，请确保将其正确缩进以免破坏列表：

```markdown
*   列表项。

    ```c++
    int foo;
    ```

*   下一项。
```

你还可以用 4 个空格来创建一个嵌套的代码块。只需要在列表缩进中再额外缩进 4 个空格即可：

```markdown
*   列表项。

        int foo;

*   下一项。
```

## 链接

长链接使 Markdown 源代码难以阅读并且破坏 80 个字符的换行规则。**请尽可能缩短链接**。

### 使用内容丰富的 Markdown 链接标题

就像在 HTML 一样，Markdown 链接语法也允许你设置链接标题。请用好它。

把链接标记为“链接”或“此处”。否则当读者快速扫视文档时，提供不了任何实际信息，并且也是对空间的浪费：

```markdown
关于更多信息，请参见语法指导：[链接](syntax_guide.md)。
或者，查看风格指导[这里](style_guide.md)。
**不要这样。**
```

正确的做法是，自然地写出一句话，把带有链接的最恰当短语包含在里面：

```markdown
关于更多信息，请参见[语法指导](syntax_guide.md)。
或者，查看[风格指导](style_guide.md)。
```

## 图像

尽量少用图像，并且尽量用简单的截屏。本指南的设计理念是，纯文本可以让用户更快地投入到工作交流中，减少读者分心和作者拖沓。
但是，有时图像对显示您的意图也很有帮助。

参见[图像语法](https://gerrit.googlesource.com/gitiles/+/master/Documentation/markdown.md#Images).

## 优先用列表而不是表格

任何 Markdown 中的表格都应该很小。复杂的大表格在源代码中很难阅读，最重要的是，**以后修改的痛苦**。

```markdown
水果 | 属性 | 备注
---- | ---- | --- | ---
苹果 | [多汁](https://example.com/SomeReallyReallyReallyReallyReallyReallyReallyReallyLongQuery), 结实, 甘甜 | 苹果让你远离医生。
香蕉 | [方便](https://example.com/SomeDifferentReallyReallyReallyReallyReallyReallyReallyReallyLongQuery), 软糯, 甘甜 | 与普遍的看法相反，大多数猿类更喜欢芒果。

**不要这样**
```

[列表](#列表)和副标题通常就足以展示相同的信息，尽管不太紧凑，却更易于编辑：

```markdown
## 水果

### 苹果

* [多汁](https://SomeReallyReallyReallyReallyReallyReallyReallyReallyReallyReallyReallyReallyReallyReallyReallyReallyLongURL)
* 结实
* 甘甜

苹果让你远离医生。

### 香蕉

* [方便](https://example.com/SomeDifferentReallyReallyReallyReallyReallyReallyReallyReallyLongQuery)
* 软糯
* 甘甜

与普遍的看法相反，大多数猿类更喜欢芒果。
```

但是，有些时候小的表格却更合适：

```markdown
 名次| 是谁 | 原因
---- | ---- | ---
季军 | 孙悟空   | 一个跟头十万八千里
亚军 | 曹操     | 说曹操，曹操到
冠军 | 香港记者 | 比其他的西方记者跑得还快
```

## 优先使用 Markdown 语法而不是 HTML

请尽可能使用标准的 Markdown 语法，并避免 HTML。如果你觉得似乎无法达到所需的目的，请重新考虑是否真的需要。除了[大表](#优先用列表而不是表格)外，Markdown 已经能满足几乎所有需求。

每多一点 HTML 或 Javascript，就会少一点可读性和可移植性。
反过来，这也限制了与其他一些有用工具的整合，比如可以将源代码显示为纯文本或将其渲染的工具。参见[哲学](philosophy.md)。

Gitiles 不支持渲染 HTML。
