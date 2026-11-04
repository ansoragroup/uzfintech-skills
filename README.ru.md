# uzfintech-skills

[English](README.md) · **Русский** · [Oʻzbekcha](README.uz.md) · [简体中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-10%20providers-0a7c66.svg)](#провайдеры)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-d97757.svg)](#установка)
[![Python 3.9+ stdlib](https://img.shields.io/badge/tools-python3%20stdlib-3776ab.svg)](#инструменты)

Скиллы для агентов по API узбекских платёжных провайдеров: **Uzum Bank, Alif, Click,
Paynet, Payme, Multicard, Atmos, Octo, Oson и Kapitalbank**, а также общий для всех них
скилл по фискальным чекам и скилл-роутер для выбора и сравнения провайдеров. Работают в
Claude Code, Codex, Cursor и любом другом агенте, который читает файлы `SKILL.md`.

Модели знают эти API лишь приблизительно. Путают tiyin и сумы, подписывают не ту строку,
придумывают коды ошибок и тестовые карты. Со скиллами агент отвечает по точным заметкам о
контракте и проверяет подписи и payload скриптами, а не угадывает. В каждом скилле есть:

- эндпоинты, заголовки авторизации, подписи, единицы сумм и машины состояний;
- урезанные JSON Schema, коды ошибок, правила идемпотентности и повторов;
- обезличенные примеры запросов и ответов;
- тестовые данные вендора без изменений: тестовые хосты, карты, OTP-коды, сценарии;
- чек-листы для ревью интеграции;
- `sign.py` и `validate.py`, два детерминированных инструмента без зависимостей.

## Провайдеры

| Скилл | Провайдер | Продукты |
|---|---|---|
| [`uzum`](skills/uzum/SKILL.md) | Uzum Bank | Merchant API (вебхуки), Checkout, Fiscalization, FastPay, Dynamic QR, CrossBorder, Remit Core, Ratekeeper, Nasiya, PaymentHub |
| [`alif`](skills/alif/SKILL.md) | Alif (alifpay) | Checkout, рассрочка Alif Nasiya, Payments, Cards, Hold, Monitoring, Summary, карта перехода со старого API |
| [`click`](skills/click/SKILL.md) | Click | SHOP API, Advanced / Split Shop, Merchant API, токены карт, Fiscalization, CLICK Pass, платёжная ссылка / кнопка / виджет, Telegram Payments |
| [`paynet`](skills/paynet/SKILL.md) | Paynet | Интернет-эквайринг (Humo / Uzcard): authorize, confirm, status, reverse |
| [`payme`](skills/payme/SKILL.md) | Payme (Paycom) | Merchant API, Subscribe API (карты, чеки, холды), Checkout (GET / POST / кнопка / QR), Fiscalization |
| [`multicard`](skills/multicard/SKILL.md) | Multicard | Инвойсы и scanpay, привязка карт, платежи (токен / карта / приложение / сплит), возвраты, холды, выплаты, отчёты |
| [`atmos`](skills/atmos/SKILL.md) | Atmos | Платежи (Uzcard / Humo: pay-create / pre-apply / apply, мультиплатежи, полный и частичный реверс, платёжная страница, HTML-виджет), привязка карт, холды, списание по ПИНФЛ, Visa / Mastercard (MPS / IPS), Callback API |
| [`octo`](skills/octo/SKILL.md) | Octo | Эквайринг Visa / Mastercard / UnionPay и Uzcard / Humo: платёжная страница (одностадийная / двухстадийная), своя форма карты (PCI DSS), токены карт, полный и частичный возврат, фискализация (basket, fiscal-data) |
| [`oson`](skills/oson/SKILL.md) | Oson | Invoice API (invoice/create с pay_url, invoice/status) и подписанное уведомление об оплате, восстановлено по открытым плагинам Oson для магазинов |
| [`kapitalbank`](skills/kapitalbank/SKILL.md) | Kapitalbank | Kapital API для юрлиц: APILogin, платёжные поручения SendPaymentIBK, CheckPayments2, выписки (GetDoc1C, GetMT940), проверка счёта и получателя, курсы валют, счета-фактуры; коды назначения платежа ЦБ для платёжных поручений в сумах в любом банке |
| [`fiscal`](skills/fiscal/SKILL.md) | Все провайдеры | Фискальные чеки: коды MXIK (ИКПУ) из Tasnif, коды упаковки, поля НДС и льгот, маркировка Asl Belgisi, типы чеков, кто регистрирует чек и в каком поле у каждого провайдера |
| [`uzfintech`](skills/uzfintech/SKILL.md) | Все провайдеры | Роутер: выбор провайдера под задачу, сравнение провайдеров, шпаргалка по всем провайдерам (единицы, авторизация, колбэки, возвраты, холды, фискализация, тестовые хосты), заметки по UzQR |

Если задача — выбрать или сравнить провайдеров, начните с `uzfintech`. Он указывает на
скилл провайдера, в котором лежит контракт.

## Установка

### Любой агент: CLI `skills`

```sh
npx skills add ansoragroup/uzfintech-skills
```

CLI [`skills`](https://github.com/vercel-labs/skills) спросит, в какие агенты ставить
(Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot и другие) и куда: глобально или в
один проект. Чтобы поставить одного провайдера, добавьте `--skill payme`.

### Claude Code: плагин

```
/plugin marketplace add ansoragroup/uzfintech-skills
/plugin install uzfintech@uzfintech-skills
```

Обновление: `/plugin marketplace update uzfintech-skills`. В плагине скиллы получают
пространство имён: `uzfintech:payme`, `uzfintech:click` и так далее.

### Ручное копирование

```sh
git clone https://github.com/ansoragroup/uzfintech-skills
cp -R uzfintech-skills/skills/* ~/.claude/skills/    # Claude Code, all projects
cp -R uzfintech-skills/skills/* ~/.codex/skills/     # Codex
```

Для одного проекта копируйте в `<project>/.claude/skills/`.

### Агенты без поддержки скиллов: AGENTS.md

Подключите репозиторий (например, git-сабмодулем в `vendor/uzfintech-skills`) и добавьте
в `AGENTS.md` своего проекта:

```md
## Payment provider contracts
For Uzbek payment provider work (Uzum Bank, Alif, Click, Paynet, Payme, Multicard, Atmos,
Octo, Oson, Kapitalbank), read `vendor/uzfintech-skills/skills/<provider>/SKILL.md` first and
follow its pointers. To choose or compare providers, start with
`vendor/uzfintech-skills/skills/uzfintech/SKILL.md`. Run its
`scripts/sign.py` and `scripts/validate.py` instead of computing signatures by hand, and
review changes against the matching `checklists/*.md`.
```

Обновление, фиксация версии и решение проблем описаны на
[вики-странице «Установка»](docs/wiki/Install.ru.md).

## Как это устроено

Каждый скилл разделён на роутер и исполнителей: маленький роутер решает, куда идти, а
работа идёт в узких местах, где есть только нужный контекст.

```
             your question
                   │
     ┌─────────────▼─────────────┐   ~140 lines, loaded when the description matches:
     │  skills/<provider>/       │   products, decision table, gotchas,
     │  SKILL.md   (router)      │   answering rules, tool commands
     └──────┬────────────┬───────┘
  slow path │            │ fast path
  (reading) │            │ (deterministic)
     ┌──────▼──────┐  ┌──▼───────────────────┐
     │ references/ │  │ scripts/sign.py      │  exact signed string, MATCH / MISMATCH
     │ checklists/ │  │ scripts/validate.py  │  OK / INVALID with JSON paths
     └─────────────┘  └──────────────────────┘
```

- **Один провайдер на скилл.** Задача с несколькими провайдерами загружает каждый скилл
  отдельно и сравнивает в конце. Правила единиц, авторизации или повторов никогда не
  переносятся с одного провайдера на другой. Роутер `uzfintech` помогает выбрать и
  сравнить, а затем передаёт работу скиллу провайдера. Коды для чеков, общие для всех
  провайдеров (MXIK, коды упаковки, маркировка), лежат в скилле `fiscal`.
- **Сначала быстрый путь.** Подписи, заголовки авторизации, ссылки на оплату и форму payload
  считает код, а не модель. Агент запускает инструмент и цитирует его вывод.
- **Inline и spill.** В `SKILL.md` лежит только то, что нужно в каждой задаче. Контракты,
  схемы, примеры, тестовые данные и чек-листы вынесены в файлы, которые агент читает по
  необходимости.
- **Стабильные ID.** Схемы подписи (`payme.basic`, `click.prepare`), имена схем
  (`uzum/webhook-confirm`) и коды ошибок одинаковы на всех языках и не переводятся.
- **Ответ под канал.** В чате агент сначала даёт вывод, примерно в 100 словах. В PR или
  ревью пишет Problem, Change, Validation. Отвечает на вашем языке, но имена API оставляет
  как есть.
- **Предупреждает без вопроса.** Платёжные баги прячутся во временных окнах и необратимых
  шагах. Когда задача создаёт, подтверждает, отменяет, возвращает, повторяет или
  фискализирует платёж, агент сам называет срок, можно ли откатить шаг и что будет с
  фискальным чеком. См. [Предупреждения о жизненном цикле](#предупреждения-о-жизненном-цикле).

## Предупреждения о жизненном цикле

В каждом скилле есть `references/lifecycle/README.md`: сроки и временные окна провайдера,
правила отмены / реверса / возврата, повторов и идемпотентности, время жизни холдов и OTP,
правила фискальных чеков. Самые дорогие из них вынесены в `SKILL.md` в блок «Warn without
being asked», у каждого стабильный ID. Например, `uzum.fiscal-receipt-24h`: в фискальном
чеке Uzum `date_time` должен быть в пределах 24 часов после платежа, поэтому чек на возврат
нельзя просто отправить через неделю.

Все они собраны в одну таблицу на [вики-странице Lifecycle](docs/wiki/Lifecycle.ru.md).

## Инструменты

В каждом скилле есть `scripts/sign.py` и `scripts/validate.py`. Им нужен только `python3`
(3.9+) и стандартная библиотека. Секреты берутся из переменных окружения и печатаются как
`<SECRET>`.

```console
$ python3 skills/click/scripts/sign.py --list
click.prepare       SHOP API Prepare sign_string = md5(...)
                    fields: click_trans_id service_id merchant_trans_id amount action sign_time; secret: CLICK_SECRET_KEY
click.complete      SHOP API Complete sign_string = md5(...)
                    fields: click_trans_id service_id merchant_trans_id merchant_prepare_id amount action sign_time; secret: CLICK_SECRET_KEY
click.advanced      Advanced / Split Shop sign_string = md5(..., params values in body order, ...)
                    fields: click_paydoc_id attempt_trans_id service_id params action sign_time; secret: CLICK_SECRET_KEY
click.auth          Merchant API Auth: merchant_user_id:sha1(ts+secret):ts, ts in seconds
                    fields: merchant_user_id [timestamp]; secret: CLICK_SECRET_KEY

$ CLICK_SECRET_KEY=test-secret python3 skills/click/scripts/sign.py click.prepare body.txt \
    --expect d7696dbc2b950daf03e1191fbea5fbb3
input   12345100<SECRET>100011000.002026-11-03 10:00:00
value   24d6c366acd79c05457ddf0547d6d65c
MISMATCH, received d7696dbc2b950daf03e1191fbea5fbb3
```

Строка `input` показывает баг. Click прислал `amount=1000.00` и подписал именно эту строку.
Наш обработчик распарсил сумму как число и собрал обратно `1000.0`, поэтому в `body.txt`
уже не то, что подписывал Click. Подписывайте сырые значения ровно в том виде, в каком они
пришли.

```console
$ python3 skills/payme/scripts/validate.py CreateTransaction body.json
INVALID references/merchant/schemas/CreateTransaction.json (params): 1 problem(s)
  $.amount: expected integer, got string
```

`validate.py` разворачивает конверты JSON-RPC и `{success, data}`, читает
form-urlencoded тела и пропускает значения `<PLACEHOLDER>`. Оба инструмента завершаются с
кодом `0` при успехе, `1` при несовпадении и `2` при ошибке использования, так что их можно
ставить в CI. Все схемы описаны на [вики-странице «Инструменты»](docs/wiki/Tools.ru.md).

У двух скиллов есть свой офлайн-инструмент: `skills/kapitalbank/scripts/purpose_codes.py`
ищет и проверяет коды назначения платежа ЦБ, а `skills/fiscal/scripts/mxik.py` проверяет
коды MXIK, с поиском в Tasnif по явному флагу.

## Попробуйте

- «Click говорит, что наш `sign_string` в Prepare неверный. Вот тело запроса.»
- «Реализуй Payme Merchant API `CreateTransaction` с ошибками `-31008` / `-31050`.»
- «Что присылает Uzum Merchant `/confirm` и что отвечать на повтор?»
- «Проверь подпись вебхука Alif на Go.»
- «Какие тестовые карты и OTP-коды в песочнице Uzum Checkout?»
- «Проверь нашу интеграцию Multicard по чек-листу.»
- «Какие провайдеры умеют холдировать средства и списывать позже? Сравни Atmos и Octo.»
- «В нашем платёжном поручении всё ещё код назначения 00545. Чем его заменить?»
- «Payme sandboxida qaysi test kartalardan foydalanish mumkin?»

## Качество

| Проверка | Команда | Что доказывает |
|---|---|---|
| Lint репозитория | `scripts/lint` | инструменты синхронизированы и прошли самотест, каждый пример валиден по своей схеме, frontmatter в рамках спецификации, нет битых ссылок, скан на обезличивание, переводы на месте, версии согласованы, каждый ID предупреждения определён на своей странице lifecycle |
| Самотест парсера | `scripts/sync --selftest` | встроенный YAML-парсер совпадает с PyYAML |
| Поведенческие evals | `claude plugin eval . --runs 3` | агент со скиллом грузит нужного провайдера, цитирует точные коды, запускает инструменты и не выдумывает тестовые данные и коммерческие условия |

20 eval-кейсов лежат в [`evals/`](evals/README.md). CI запускает lint на каждом PR.

## Актуальность

У каждой справки есть URL источника и дата загрузки. Раз в неделю
`.github/workflows/sync.yml` запускает `scripts/sync`, пересобирает файлы, сгенерированные
из OpenAPI, и открывает PR, если поменялась спецификация или страница документации у
вендора. Человек перечитывает отмеченные страницы перед мержем.

```sh
scripts/sync --check            # report only; exit 1 when upstream changed
scripts/sync                    # regenerate derived files, update sources.yaml
```

## Документация

Полные руководства — в [вики](docs/wiki/Home.ru.md):
[Установка](docs/wiki/Install.ru.md) · [Инструменты](docs/wiki/Tools.ru.md) ·
[Гайд для агентов](docs/wiki/Agent-guide.ru.md) · [Lifecycle](docs/wiki/Lifecycle.ru.md) ·
[Evals](docs/wiki/Evals.ru.md) · [Как помочь](docs/wiki/Contributing.ru.md) · [FAQ](docs/wiki/FAQ.ru.md)

## Как помочь проекту

Исправления, новые продукты и новые провайдеры приветствуются. Прочитайте
[CONTRIBUTING.md](CONTRIBUTING.md): там правила для контента (не копировать текст вендора
дословно, обезличенные примеры, тестовые данные без изменений, никаких коммерческих условий)
и проверки перед PR. Об уязвимостях сообщайте так, как описано в [SECURITY.md](SECURITY.md).

## Отказ от ответственности

Проект не связан ни с одним из описанных платёжных провайдеров. Заметки сделаны по
публичной документации для разработчиков, и главный источник — она. Поведение в продакшене
уточняйте у своего провайдера. Ставки комиссии и условия расчётов зависят от договора
каждого мерчанта, поэтому скиллы их не называют. Никогда не коммитьте настоящие ключи и
данные клиентов.

## Лицензия

[MIT](LICENSE)
