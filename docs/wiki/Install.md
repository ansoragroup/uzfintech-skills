# Install

**English** · [Русский](Install.ru.md) · [Oʻzbekcha](Install.uz.md) · [简体中文](Install.zh-CN.md)

The skills are plain folders with a `SKILL.md`. Any agent that supports
[Agent Skills](https://agentskills.io) can load them. For other agents, point `AGENTS.md`
at them.

## The `skills` CLI (any agent)

```sh
npx skills add ansoragroup/uzfintech-skills
```

The [`skills`](https://github.com/vercel-labs/skills) CLI asks which agents to install to and
whether to install for this project or globally. Useful options:

| Option | Effect |
|---|---|
| `-g` | install globally instead of into the current project |
| `-a claude-code,codex` | install only for these agents |
| `-s payme,click` | install only these providers |
| `-l` | list the skills in the repository without installing |
| `-y` | answer yes to every prompt (CI, scripts) |

Later: `npx skills update`, `npx skills list`, `npx skills remove payme`.

## Claude Code plugin

```
/plugin marketplace add ansoragroup/uzfintech-skills
/plugin install uzfintech@uzfintech-skills
```

The plugin namespaces the skills as `uzfintech:payme`, `uzfintech:click` and so on. Update
with `/plugin marketplace update uzfintech-skills`.

## Manual copy

```sh
git clone https://github.com/ansoragroup/uzfintech-skills
cp -R uzfintech-skills/skills/* ~/.claude/skills/    # Claude Code, every project
cp -R uzfintech-skills/skills/* ~/.codex/skills/     # Codex
```

For a single project, copy into `<project>/.claude/skills/`. Copy whole folders: the
`scripts/` and `references/` next to `SKILL.md` are part of the skill.

## Pin a version

Install from a tag to keep the same contract notes until you choose to update:

```sh
git submodule add https://github.com/ansoragroup/uzfintech-skills vendor/uzfintech-skills
git -C vendor/uzfintech-skills checkout v0.3.0
```

[CHANGELOG.md](https://github.com/ansoragroup/uzfintech-skills/blob/main/CHANGELOG.md) lists
what each version changed.

## Agents without skill support

Vendor the repository (the submodule above works) and add this to your project's
`AGENTS.md`:

```md
## Payment provider contracts
For Uzbek payment provider work (Uzum Bank, Alif, Click, Paynet, Payme, Multicard, Atmos,
Octo, Oson, Kapitalbank), read `vendor/uzfintech-skills/skills/<provider>/SKILL.md` first and
follow its pointers. To choose or compare providers, start with
`vendor/uzfintech-skills/skills/uzfintech/SKILL.md`. Run its
`scripts/sign.py` and `scripts/validate.py` instead of computing signatures by hand, and
review changes against the matching `checklists/*.md`.
```

## Requirements

- `python3` 3.9 or newer on `PATH` for the tools. They use only the standard library.
- Permission for the agent to run shell commands, if you want it to run the tools itself.
  In Claude Code, allow `Bash(python3:*)` or approve the first call.

## Troubleshooting

| Symptom | Fix |
|---|---|
| The agent answers from memory and does not open the skill | Name the provider and the product in the request ("Payme Merchant API", "Click SHOP API"). The skill description matches on these names. |
| `python3: command not found` | Install Python 3.9+ or call the tools with the interpreter you have. |
| `sign.py: set CLICK_SECRET_KEY ...` | Export the variable that `sign.py --list` names, for example `CLICK_SECRET_KEY`. The tool never takes a secret as an argument. |
| The plugin is installed but the skills are missing | Run `/plugin` and check that `uzfintech` is enabled, then start a new session. |
