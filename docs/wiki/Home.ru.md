# uzfintech-skills

[English](Home.md) · **Русский** · [Oʻzbekcha](Home.uz.md) · [简体中文](Home.zh-CN.md)

Скиллы для агентов по платёжным API Узбекистана: **Uzum Bank, Alif, Click, Paynet, Payme,
Multicard, Atmos, Octo, Oson и Kapitalbank**, а также общий для всех них скилл по
фискальным чекам, скилл по каталогу Tasnif для поиска и перепроверки кодов MXIK и
скилл-роутер для выбора и сравнения провайдеров. Агент с этими скиллами отвечает по точным заметкам о контракте, проверяет
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
| [`alif`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/alif/SKILL.md) | Alif (alifpay) | Checkout, рассрочка Alif Nasiya, Payments, Cards, Hold, Monitoring, Summary, карта перехода со старого API |
| [`click`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/click/SKILL.md) | Click | SHOP API, Advanced / Split Shop, Merchant API, токены карт, Fiscalization, CLICK Pass, платёжная кнопка, Telegram Payments |
| [`paynet`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/paynet/SKILL.md) | Paynet | Интернет-эквайринг для Humo и Uzcard |
| [`payme`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/payme/SKILL.md) | Payme (Paycom) | Merchant API, Subscribe API, Checkout, Fiscalization |
| [`multicard`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/multicard/SKILL.md) | Multicard | Инвойсы, привязка карт, платежи, возвраты, холды, выплаты, отчёты |
| [`atmos`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/atmos/SKILL.md) | Atmos | Платежи и реверсы Uzcard / Humo, платёжная страница и виджет, привязка карт, холды, списание по ПИНФЛ, Visa / Mastercard (MPS / IPS), Callback API |
| [`octo`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/octo/SKILL.md) | Octo | Платёжная страница (одностадийная / двухстадийная), своя форма карты, токены карт, полный и частичный возврат, фискализация |
| [`oson`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/oson/SKILL.md) | Oson | Invoice API и подписанное уведомление об оплате, восстановлено по открытым плагинам Oson для магазинов |
| [`kapitalbank`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/kapitalbank/SKILL.md) | Kapitalbank | Kapital API для юрлиц (платёжные поручения, статус, выписки, проверка счёта, курсы валют, счета-фактуры), коды назначения платежа ЦБ |
| [`fiscal`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/fiscal/SKILL.md) | Все провайдеры | Коды MXIK (ИКПУ) и упаковки, поля НДС и льгот, маркировка, типы чеков, поля чека у каждого провайдера |
| [`tasnif`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/tasnif/SKILL.md) | Tasnif (каталог налогового комитета) | Поиск по каталогу MXIK (ИКПУ) на tasnif.soliq.uz: поиск по тексту и штрихкоду (GTIN), карточка кода с кодами упаковки, история для перепроверки, картинки, списки классов, проверка для кассы через `cl-api`, проверка плательщика НДС в txkm; недокументированные публичные эндпоинты, сохранённые ответы вместо тестового хоста |
| [`uzfintech`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/uzfintech/SKILL.md) | Все провайдеры | Роутер: выбор и сравнение провайдеров, шпаргалка по всем провайдерам (единицы, авторизация, колбэки, возвраты, холды, фискализация, тестовые хосты), заметки по UzQR |

Если задача — выбрать или сравнить провайдеров, начните с `uzfintech`.

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
страница-источник и дата загрузки. Главным источником остаётся документация вендора. Tasnif
не публикует справку по API, поэтому скилл `tasnif` описывает эндпоинты, которые вызывает
сам сайт tasnif.soliq.uz, такими, какими они были на дату загрузки.
