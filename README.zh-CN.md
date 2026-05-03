# PDF to Anki Cards

[English](README.en.md) | [简体中文](README.zh-CN.md)

将 PDF、词汇表、课堂讲义、教材页面、公式资料和图文学习材料转换成经过校验的 Anki `.apkg` 牌组包。

这个仓库包含一个可复用的 AI Agent Skill，以及一组确定性脚本。它来自一次真实的 PDF 转 Anki 工作流：要让 Anki 顺利导入，必须认真处理 note model、卡片模板、媒体映射，以及 protobuf 格式的 `meta` 文件。

## 仓库简介

**PDF to Anki Cards** 是一个面向 Claude Code / Codex 的 Skill，也是一个 Python 工具集，用于把 PDF 学习资料转换成可直接导入 Anki 的牌组。它将 Agent 辅助制卡和确定性的 `.apkg` 构建/校验脚本结合起来，让生成的卡片能够可靠保留模板、媒体、音频和 Anki 包元数据。

本项目是一个完全的 vibe coding 项目：初始工作流、实现代码、文档和仓库包装都通过人类主导的 AI 编程会话完成。

## 功能特性

- 从 PDF 中提取文本和词汇表。
- 从结构化卡片 JSON 构建 Anki `.apkg` 文件。
- 可以复用已有 `.apkg` 的样式、模板和字段结构。
- 保留 Anki 的音频/图片媒体映射。
- 在导入前校验包完整性。
- 支持多种卡片模式：词汇、问答、填空式、术语、公式和图像卡。
- 包含兼容 Claude Code / Codex 的 `SKILL.md`。

## 仓库结构

```text
.
├── SKILL.md                         # Agent skill 指令
├── package.json                     # npm/npx 安装元数据
├── bin/
│   └── pdf-to-anki-cards.js         # npm 安装 CLI
├── scripts/
│   ├── inspect_apkg.py              # 检查参考 Anki 包
│   ├── extract_pdf_content.py       # 从 PDF 提取文本和词表
│   ├── build_apkg.py                # 从结构化 JSON 构建 .apkg
│   ├── generate_audio.py            # 可选音频元数据/生成工具
│   └── validate_apkg.py             # 校验最终 .apkg 文件
├── references/
│   ├── anki-apkg-format.md          # APKG 格式实现说明
│   ├── card-design-rules.md         # 高质量卡片设计规则
│   └── content-modes.md             # 支持的内容模式
├── docs/
│   ├── INSTALL.md                   # 作为 Claude Code/Codex skill 安装
│   ├── INSTALL.zh-CN.md             # 中文安装教程
│   └── USAGE.md                     # 命令示例
└── examples/
    └── cards.sample.json            # 最小卡片 JSON 示例
```

## 快速开始

使用 npm/npx 安装为 Agent Skill：

```bash
npx github:ess434879-dotcom/pdf-to-anki-cards install --target claude
```

或从 GitHub 全局安装：

```bash
npm install -g github:ess434879-dotcom/pdf-to-anki-cards
pdf-to-anki-cards install --target claude
```

Claude Code、Codex、Git 和 npm 安装方式详见 [docs/INSTALL.zh-CN.md](docs/INSTALL.zh-CN.md)。

创建一个最小示例牌组：

```bash
python3 scripts/build_apkg.py \
  --cards examples/cards.sample.json \
  --out example.apkg \
  --deck-name "Example PDF Cards"

python3 scripts/validate_apkg.py example.apkg
```

检查已有 Anki 包：

```bash
python3 scripts/inspect_apkg.py path/to/reference.apkg --out inspect.json
```

提取 PDF 内容：

```bash
python3 scripts/extract_pdf_content.py path/to/source.pdf --out extracted.json
```

`extract_pdf_content.py` 需要 PyMuPDF：

```bash
python3 -m pip install -r requirements.txt
```

## 卡片 JSON 格式

构建脚本接受一个卡片列表，或一个包含 `cards` 列表的对象。

```json
[
  {
    "type": "qa",
    "front": "What is active recall?",
    "back": "A study method where you retrieve the answer from memory before checking it.",
    "source_page": 1,
    "tags": ["study", "memory"]
  }
]
```

词汇卡示例：

```json
{
  "type": "vocab",
  "word": "aggressive",
  "definition": "adj. 好斗的，有侵略性的；进取的",
  "phonetic": "/əˈɡresɪv/",
  "audio": "[sound:aggressive.mp3]",
  "source_page": 1,
  "tags": ["cet6", "vocab"]
}
```

## 参考牌组

如果提供参考 `.apkg`，`build_apkg.py` 会复用它的 note model、模板、CSS 和 `meta` 字节：

```bash
python3 scripts/build_apkg.py \
  --cards cards.json \
  --reference reference.apkg \
  --out generated.apkg \
  --deck-name "Generated Deck"
```

这适用于你希望新牌组继承已有牌组外观和交互风格的场景。

## 为什么必须校验

Anki 包看起来是 zip 文件，但不能随便打包。常见错误会导致导入失败或媒体丢失：

- `meta` 文件格式错误
- `[sound:...]` 引用没有出现在 `media` 映射中
- `media` 中的数字 key 没有对应 zip 文件
- note/card 数量不匹配

生成后请始终运行：

```bash
python3 scripts/validate_apkg.py generated.apkg
```

## 作为 Agent Skill 使用

将本仓库安装为 Claude Code 或 Codex skill 后，可以这样要求：

```text
Use pdf-to-anki-cards to convert this PDF into an Anki deck.
```

安装方式见 [docs/INSTALL.zh-CN.md](docs/INSTALL.zh-CN.md)。

## 当前状态

这是一个早期但可用的实用工具集。APKG 构建和校验路径是确定性的，已经在小型示例牌组和真实词汇 PDF 工作流中测试过。PDF 到高质量问答/填空卡的内容生成，仍然需要调用方 Agent 进行理解和整理。

## 许可证

MIT License。详见 [LICENSE](LICENSE)。
