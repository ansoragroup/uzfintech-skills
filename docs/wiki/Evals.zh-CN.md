# 评测

[English](Evals.md) · [Русский](Evals.ru.md) · [Oʻzbekcha](Evals.uz.md) · **简体中文**

这些技能按行为来测试。[`evals/`](https://github.com/ansoragroup/uzfintech-skills/tree/main/evals) 中的每个用例都是开发者真实会发出的请求，并配有评分器（grader），检查回答中真正重要的东西：是否加载了正确的技能、错误码是否准确、是否运行了工具、有没有编造测试卡。

## 运行

你需要支持 `claude plugin eval` 的 [Claude Code](https://claude.com/claude-code)。

```sh
claude plugin eval . --runs 3                              # every case, three runs each
claude plugin eval . --tag payme                           # one provider
claude plugin eval . --case click-sign-mismatch --allow-tools Bash
claude plugin eval . --ablation with-without               # also run without the skills
```

- `--allow-tools Bash` 允许智能体运行 `sign.py`。`tools` 类用例需要它。
- `--ablation with-without` 会让每个用例在有技能和无技能两种情况下各跑一遍。两者的差异就是技能带来的提升。`skill` 评分器只在“with”组中计分。
- 完整跑一遍整个套件大约花费 $2。可以用 `--max-cost-usd` 设置上限。

在 CI 中，`.github/workflows/ci.yml` 里的 `evals` 任务按需运行（通过 workflow dispatch 并传入 `evals: true`），前提是已设置 `ANTHROPIC_API_KEY` secret：

```sh
claude plugin eval . --runs 3 --allow-tools Bash --trust-plugin --no-publish \
  --threshold 0.8 --max-cost-usd 20 --json results.json
```

## 用例格式

```
evals/<case>/prompt.md       frontmatter: name, tags, runs, max_turns, allowed_tools
evals/<case>/graders/*.md    one grader per file
```

| 评分器 | 检查内容 | 适用于 |
|---|---|---|
| `regex` | 最终回答中的某个模式（`flags: i`、`match: contains`） | 准确的错误码、字段名、数字 |
| `tool_used` | 某个工具被调用过，并用 `input_match` 匹配其输入 | 加载了正确的技能、运行了 `sign.py` |
| `llm` | 由评审模型对照书面标准阅读回答 | 模式无法表达的内容，例如“没有编造卡号” |

用例只能设置 `EVAL_*` 环境变量。沙箱值直接写进提示词里。

## 怎样写好一个用例

1. 像开发者那样提问。不要点明你要测试的陷阱。
2. 优先使用 `regex`。编写 `llm` 标准时，要让带有额外细节的正确回答仍能通过，而错误的回答会失败。
3. 每个评分器只检查一种行为，并给最重要的几项更高的权重。
4. 新用例要运行三次。对正确的回答，它必须每次都判为通过。

当前的用例及各自检查的内容列在 [`evals/README.md`](https://github.com/ansoragroup/uzfintech-skills/blob/main/evals/README.md) 中。
