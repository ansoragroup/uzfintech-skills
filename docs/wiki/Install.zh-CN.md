# 安装

[English](Install.md) · [Русский](Install.ru.md) · [Oʻzbekcha](Install.uz.md) · **简体中文**

技能就是包含 `SKILL.md` 的普通文件夹。任何支持 [Agent Skills](https://agentskills.io) 的智能体都能加载它们。对于其他智能体，可以在 `AGENTS.md` 中指向它们。

## `skills` CLI（任意智能体）

```sh
npx skills add ansoragroup/uzfintech-skills
```

[`skills`](https://github.com/vercel-labs/skills) CLI 会询问要安装到哪些智能体，以及是安装到当前项目还是全局安装。常用选项：

| 选项 | 作用 |
|---|---|
| `-g` | 全局安装，而不是装进当前项目 |
| `-a claude-code,codex` | 只为这些智能体安装 |
| `-s payme,click` | 只安装这些服务商 |
| `-l` | 列出仓库中的技能，但不安装 |
| `-y` | 对所有提示都回答 yes（CI、脚本） |

之后可以用：`npx skills update`、`npx skills list`、`npx skills remove payme`。

## Claude Code 插件

```
/plugin marketplace add ansoragroup/uzfintech-skills
/plugin install uzfintech@uzfintech-skills
```

插件会给技能加上命名空间，例如 `uzfintech:payme`、`uzfintech:click` 等。用 `/plugin marketplace update uzfintech-skills` 更新。

## 手动复制

```sh
git clone https://github.com/ansoragroup/uzfintech-skills
cp -R uzfintech-skills/skills/* ~/.claude/skills/    # Claude Code, every project
cp -R uzfintech-skills/skills/* ~/.codex/skills/     # Codex
```

如果只用于单个项目，复制到 `<project>/.claude/skills/`。请复制整个文件夹：`SKILL.md` 旁边的 `scripts/` 和 `references/` 也是技能的一部分。

## 锁定版本

从某个 tag 安装，就能一直使用同一版接口契约笔记，直到你决定更新：

```sh
git submodule add https://github.com/ansoragroup/uzfintech-skills vendor/uzfintech-skills
git -C vendor/uzfintech-skills checkout v0.2.0
```

[CHANGELOG.md](https://github.com/ansoragroup/uzfintech-skills/blob/main/CHANGELOG.md) 列出了每个版本的改动。

## 不支持技能的智能体

把本仓库纳入你的项目（vendor，用上面的 submodule 即可），然后在项目的 `AGENTS.md` 中加入以下内容：

```md
## Payment provider contracts
For Uzbek payment provider work (Uzum Bank, Alif, Click, Paynet, Payme, Multicard), read
`vendor/uzfintech-skills/skills/<provider>/SKILL.md` first and follow its pointers. Run its
`scripts/sign.py` and `scripts/validate.py` instead of computing signatures by hand, and
review changes against the matching `checklists/*.md`.
```

## 环境要求

- 运行工具需要 `PATH` 中有 `python3` 3.9 或更高版本。工具只使用标准库。
- 如果希望智能体自己运行工具，需要允许它执行 shell 命令。在 Claude Code 中，允许 `Bash(python3:*)`，或在第一次调用时批准。

## 故障排查

| 现象 | 解决方法 |
|---|---|
| 智能体凭记忆回答，没有打开技能 | 在请求中写明服务商和产品（“Payme Merchant API”“Click SHOP API”）。技能的 description 正是按这些名称匹配的。 |
| `python3: command not found` | 安装 Python 3.9+，或用你现有的解释器调用工具。 |
| `sign.py: set CLICK_SECRET_KEY ...` | 导出 `sign.py --list` 给出的变量，例如 `CLICK_SECRET_KEY`。工具从不通过参数接收密钥。 |
| 插件已安装，但找不到技能 | 运行 `/plugin`，确认 `uzfintech` 已启用，然后开启新会话。 |
