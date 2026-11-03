# Установка

[English](Install.md) · **Русский** · [Oʻzbekcha](Install.uz.md) · [简体中文](Install.zh-CN.md)

Скиллы — это обычные папки с `SKILL.md`. Их загружает любой агент с поддержкой
[Agent Skills](https://agentskills.io). Для остальных агентов укажите на них в `AGENTS.md`.

## CLI `skills` (любой агент)

```sh
npx skills add ansoragroup/uzfintech-skills
```

CLI [`skills`](https://github.com/vercel-labs/skills) спросит, в какие агенты ставить и
куда: в текущий проект или глобально. Полезные опции:

| Опция | Что делает |
|---|---|
| `-g` | ставит глобально, а не в текущий проект |
| `-a claude-code,codex` | ставит только для этих агентов |
| `-s payme,click` | ставит только этих провайдеров |
| `-l` | показывает скиллы в репозитории без установки |
| `-y` | отвечает «да» на все вопросы (CI, скрипты) |

Потом: `npx skills update`, `npx skills list`, `npx skills remove payme`.

## Плагин Claude Code

```
/plugin marketplace add ansoragroup/uzfintech-skills
/plugin install uzfintech@uzfintech-skills
```

В плагине скиллы получают пространство имён: `uzfintech:payme`, `uzfintech:click` и так
далее. Обновление: `/plugin marketplace update uzfintech-skills`.

## Ручное копирование

```sh
git clone https://github.com/ansoragroup/uzfintech-skills
cp -R uzfintech-skills/skills/* ~/.claude/skills/    # Claude Code, every project
cp -R uzfintech-skills/skills/* ~/.codex/skills/     # Codex
```

Для одного проекта копируйте в `<project>/.claude/skills/`. Копируйте папки целиком:
`scripts/` и `references/` рядом с `SKILL.md` — часть скилла.

## Зафиксировать версию

Ставьте из тега, чтобы заметки о контрактах не менялись, пока вы сами не решите обновиться:

```sh
git submodule add https://github.com/ansoragroup/uzfintech-skills vendor/uzfintech-skills
git -C vendor/uzfintech-skills checkout v0.2.0
```

Что изменилось в каждой версии, смотрите в
[CHANGELOG.md](https://github.com/ansoragroup/uzfintech-skills/blob/main/CHANGELOG.md).

## Агенты без поддержки скиллов

Подключите репозиторий (подойдёт сабмодуль выше) и добавьте в `AGENTS.md` проекта:

```md
## Payment provider contracts
For Uzbek payment provider work (Uzum Bank, Alif, Click, Paynet, Payme, Multicard), read
`vendor/uzfintech-skills/skills/<provider>/SKILL.md` first and follow its pointers. Run its
`scripts/sign.py` and `scripts/validate.py` instead of computing signatures by hand, and
review changes against the matching `checklists/*.md`.
```

## Требования

- `python3` 3.9 или новее в `PATH` для инструментов. Они используют только стандартную
  библиотеку.
- Разрешение агенту запускать shell-команды, если хотите, чтобы он сам запускал инструменты.
  В Claude Code разрешите `Bash(python3:*)` или одобрите первый вызов.

## Решение проблем

| Симптом | Что делать |
|---|---|
| Агент отвечает по памяти и не открывает скилл | Назовите провайдера и продукт в запросе («Payme Merchant API», «Click SHOP API»). Описание скилла срабатывает на эти названия. |
| `python3: command not found` | Установите Python 3.9+ или вызывайте инструменты тем интерпретатором, который есть. |
| `sign.py: set CLICK_SECRET_KEY ...` | Экспортируйте переменную, которую называет `sign.py --list`, например `CLICK_SECRET_KEY`. Инструмент никогда не принимает секрет аргументом. |
| Плагин установлен, а скиллов нет | Запустите `/plugin`, проверьте, что `uzfintech` включён, и начните новую сессию. |
