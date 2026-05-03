# 安装教程

本仓库既可以作为普通脚本工具使用，也可以安装成 Claude Code / Codex 的 Agent Skill。

## 使用 npm / npx 从 GitHub 安装

可以。这个 skill 支持 npm 工具链安装，而且不需要先发布到 npm registry；npm 可以直接从 GitHub 仓库安装。

安装到 Claude Code：

```bash
npx github:ess434879-dotcom/pdf-to-anki-cards install --target claude
```

安装到 Codex：

```bash
npx github:ess434879-dotcom/pdf-to-anki-cards install --target codex
```

同时安装到 Claude Code 和 Codex：

```bash
npx github:ess434879-dotcom/pdf-to-anki-cards install --target all
```

如果本地已经存在旧版本，可以加 `--force` 覆盖：

```bash
npx github:ess434879-dotcom/pdf-to-anki-cards install --target claude --force
```

也可以先从 GitHub 全局安装 CLI：

```bash
npm install -g github:ess434879-dotcom/pdf-to-anki-cards
pdf-to-anki-cards install --target claude
```

安装到自定义 skills 目录：

```bash
pdf-to-anki-cards install --dir /path/to/skills --force
```

## Claude Code 手动安装

安装为个人 Claude Code skill：

```bash
mkdir -p ~/.claude/skills
cp -R pdf-to-anki-cards ~/.claude/skills/pdf-to-anki-cards
```

如果 Claude Code 已经在运行，重启 Claude Code 或开启新会话。然后可以调用：

```text
/pdf-to-anki-cards
```

也可以自然语言调用：

```text
Use pdf-to-anki-cards to convert this PDF into an Anki deck.
```

## Codex 手动安装

安装为个人 Codex skill：

```bash
mkdir -p ~/.codex/skills
cp -R pdf-to-anki-cards ~/.codex/skills/pdf-to-anki-cards
```

重启 Codex 或开启新会话，让 skill 列表刷新。

## Python 依赖

大多数 APKG 脚本只使用 Python 标准库。PDF 提取需要 PyMuPDF：

```bash
python3 -m pip install -r requirements.txt
```

## 可选音频后端

这个 skill 不会把音频生成写死到某一个操作系统。

- `none`：不生成音频。
- `reuse`：复用参考 `.apkg` 中已有媒体。
- `anki-tts`：使用 Anki 原生 TTS 语法。
- `macos-say`：使用 macOS `say` 生成 `.aiff` 文件。
- `windows-sapi`：计划中的 Windows 后端。
- `linux-tts`：计划中的 Linux 后端。
- `online-tts`：计划中的在线 TTS 后端，应要求明确的网络/API 授权。
