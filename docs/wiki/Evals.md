# Evals

**English** · [Русский](Evals.ru.md) · [Oʻzbekcha](Evals.uz.md) · [简体中文](Evals.zh-CN.md)

The skills are tested by behaviour. Each case in
[`evals/`](https://github.com/ansoragroup/uzfintech-skills/tree/main/evals) is a request a
developer would really send, plus graders that check what matters in the answer: the right
skill loaded, the exact error code, the tool run, no invented test card.

## Run

You need [Claude Code](https://claude.com/claude-code) with `claude plugin eval`.

```sh
claude plugin eval . --runs 3                              # every case, three runs each
claude plugin eval . --tag payme                           # one provider
claude plugin eval . --case click-sign-mismatch --allow-tools Bash
claude plugin eval . --ablation with-without               # also run without the skills
```

- `--allow-tools Bash` lets the agent run `sign.py`. The `tools` cases need it.
- `--ablation with-without` runs each case with and without the skills. The difference is
  what the skills add. The `skill` graders count only in the "with" arm.
- One run of the whole suite costs about $2. Use `--max-cost-usd` to cap it.

In CI, the `evals` job in `.github/workflows/ci.yml` runs on demand (workflow dispatch with
`evals: true`) when the `ANTHROPIC_API_KEY` secret is set:

```sh
claude plugin eval . --runs 3 --allow-tools Bash --trust-plugin --no-publish \
  --threshold 0.8 --max-cost-usd 20 --json results.json
```

## Case format

```
evals/<case>/prompt.md       frontmatter: name, tags, runs, max_turns, allowed_tools
evals/<case>/graders/*.md    one grader per file
```

| Grader | Checks | Use for |
|---|---|---|
| `regex` | a pattern in the final answer (`flags: i`, `match: contains`) | exact codes, field names, numbers |
| `tool_used` | that a tool was called, with `input_match` on its input | the right skill loaded, `sign.py` run |
| `llm` | a judge reads the answer against written criteria | what a pattern cannot express, such as "invents no card number" |

A case may set only `EVAL_*` environment variables. Put sandbox values in the prompt itself.

## Writing a good case

1. Ask the way a developer asks. Do not name the trap you are testing.
2. Prefer `regex`. Write `llm` criteria so that a correct answer with extra detail still
   passes and a wrong one fails.
3. Check one behaviour per grader and weight the ones that matter most.
4. Run a new case three times. It must pass a correct answer every time.

The current cases and what each checks are listed in
[`evals/README.md`](https://github.com/ansoragroup/uzfintech-skills/blob/main/evals/README.md).
