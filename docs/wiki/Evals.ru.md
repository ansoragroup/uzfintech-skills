# Evals

[English](Evals.md) · **Русский** · [Oʻzbekcha](Evals.uz.md) · [简体中文](Evals.zh-CN.md)

Скиллы проверяются по поведению. Каждый кейс в
[`evals/`](https://github.com/ansoragroup/uzfintech-skills/tree/main/evals) — это запрос,
который разработчик отправил бы на самом деле, плюс грейдеры, которые проверяют главное в
ответе: загружен нужный скилл, назван точный код ошибки, запущен инструмент, тестовая карта
не выдумана.

## Запуск

Нужен [Claude Code](https://claude.com/claude-code) с `claude plugin eval`.

```sh
claude plugin eval . --runs 3                              # every case, three runs each
claude plugin eval . --tag payme                           # one provider
claude plugin eval . --case click-sign-mismatch --allow-tools Bash
claude plugin eval . --ablation with-without               # also run without the skills
```

- `--allow-tools Bash` разрешает агенту запускать `sign.py`. Кейсам с тегом `tools` это
  нужно.
- `--ablation with-without` прогоняет каждый кейс со скиллами и без них. Разница — это то,
  что дают скиллы. Грейдеры `skill` учитываются только в прогоне «with».
- Один прогон всего набора стоит около $2. Ограничить расходы можно через `--max-cost-usd`.

В CI задача `evals` в `.github/workflows/ci.yml` запускается по требованию (workflow
dispatch с `evals: true`), если задан секрет `ANTHROPIC_API_KEY`:

```sh
claude plugin eval . --runs 3 --allow-tools Bash --trust-plugin --no-publish \
  --threshold 0.8 --max-cost-usd 20 --json results.json
```

## Формат кейса

```
evals/<case>/prompt.md       frontmatter: name, tags, runs, max_turns, allowed_tools
evals/<case>/graders/*.md    one grader per file
```

| Грейдер | Что проверяет | Для чего |
|---|---|---|
| `regex` | шаблон в финальном ответе (`flags: i`, `match: contains`) | точные коды, имена полей, числа |
| `tool_used` | что инструмент вызван, с `input_match` по его входу | загружен нужный скилл, запущен `sign.py` |
| `llm` | судья читает ответ по записанным критериям | то, что шаблоном не выразить, например «не выдумывает номер карты» |

Кейс может задавать только переменные окружения `EVAL_*`. Данные песочницы пишите прямо в
промпт.

## Как написать хороший кейс

1. Спрашивайте так, как спрашивает разработчик. Не называйте ловушку, которую проверяете.
2. Предпочитайте `regex`. Пишите критерии `llm` так, чтобы правильный ответ с лишними
   подробностями проходил, а неправильный — нет.
3. Один грейдер — одно поведение; давайте больший вес самому важному.
4. Прогоните новый кейс три раза. Правильный ответ должен проходить каждый раз.

Текущие кейсы и что проверяет каждый, перечислены в
[`evals/README.md`](https://github.com/ansoragroup/uzfintech-skills/blob/main/evals/README.md).
