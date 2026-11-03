# uzfintech-skills

[English](Home.md) · **Русский** · [Oʻzbekcha](Home.uz.md) · [简体中文](Home.zh-CN.md)

Скиллы для агентов по платёжным API Узбекистана: **Uzum Bank, Alif, Click, Paynet, Payme и
Multicard**. Агент с этими скиллами отвечает по точным заметкам о контракте, проверяет
подписи и payload двумя небольшими скриптами и предупреждает о сроках, реверсах и
фискальных чеках до того, как они превратятся в инциденты на проде.

## С чего начать

| Я хочу... | Страница |
|---|---|
| поставить скиллы в Claude Code, Codex, Cursor или другой агент | [Установка](Install.ru.md) |
| проверить подпись, заголовок авторизации или payload | [Инструменты](Tools.ru.md) |
| понять, как агенту работать со скиллами и как выглядит хороший ответ | [Гайд для агентов](Agent-guide.ru.md) |
| увидеть временные окна, правила отмены / возврата и чеков по каждому провайдеру | [Lifecycle](Lifecycle.ru.md) |
| измерить, становятся ли ответы лучше со скиллами | [Evals](Evals.ru.md) |
| исправить факт или добавить продукт или провайдера | [Как помочь](Contributing.ru.md) |
| быстро найти ответ | [FAQ](FAQ.ru.md) |

## Провайдеры

| Скилл | Провайдер | Что покрывает |
|---|---|---|
| [`uzum`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/uzum/SKILL.md) | Uzum Bank | Вебхуки Merchant API, Checkout, Fiscalization, FastPay, Dynamic QR, CrossBorder, Remit Core, Ratekeeper, Nasiya, PaymentHub |
| [`alif`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/alif/SKILL.md) | Alif (alifpay) | Checkout, Payments, Cards, Hold, Monitoring, Summary, карта перехода со старого API |
| [`click`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/click/SKILL.md) | Click | SHOP API, Advanced / Split Shop, Merchant API, токены карт, Fiscalization, CLICK Pass, платёжная кнопка, Telegram Payments |
| [`paynet`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/paynet/SKILL.md) | Paynet | Интернет-эквайринг для Humo и Uzcard |
| [`payme`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/payme/SKILL.md) | Payme (Paycom) | Merchant API, Subscribe API, Checkout, Fiscalization |
| [`multicard`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/multicard/SKILL.md) | Multicard | Инвойсы, привязка карт, платежи, возвраты, холды, выплаты, отчёты |

## Что внутри скилла

```
skills/<provider>/
  SKILL.md                 router: products, decision table, rules, gotchas, warnings
  references/<product>/    README.md notes, schemas/*.json, examples/*.json
  references/sandbox/      vendor test hosts, cards, OTP codes, scenarios, kept exactly
  references/lifecycle/    deadlines, cancel / reverse / refund, retries, fiscal receipts
  checklists/*.md          review items: pass, fail or n.a. with a file:line citation
  scripts/sign.py          signatures and auth headers
  scripts/validate.py      JSON Schema check of request and response bodies
```

Заметки написаны по публичной документации для разработчиков. У каждой справки указана
страница-источник и дата загрузки. Главным источником остаётся документация вендора.
