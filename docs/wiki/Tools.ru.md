# Инструменты

[English](Tools.md) · **Русский** · [Oʻzbekcha](Tools.uz.md) · [简体中文](Tools.zh-CN.md)

В каждом скилле есть два скрипта в `skills/<provider>/scripts/`. Им нужен `python3` 3.9+ и
больше ничего. Модель, которая считает MD5 или base64-заголовок в уме, ошибается достаточно
часто, чтобы это стало проблемой. Скрипты считают правильно каждый раз и показывают, как
получили результат.

| Скрипт | Отвечает на вопрос | Вывод |
|---|---|---|
| `sign.py` | «Правильная ли подпись или заголовок авторизации? Какой должна быть?» | точная подписываемая строка со скрытым секретом, значение, `MATCH` / `MISMATCH` |
| `validate.py` | «Соответствует ли тело контракту?» | `OK` или `INVALID` с JSON-путями |

Оба завершаются с кодом `0` при успехе, `1` при несовпадении или невалидном теле и `2` при
ошибке использования.

## sign.py

```
sign.py --list                          schemes, the fields they need, the secret variable
sign.py SCHEME [PAYLOAD] [-f k=v ...]   compute; verifies too when PAYLOAD carries the sign
sign.py SCHEME ... --expect VALUE       verify a received signature or header
sign.py --selftest                      check the implementation against fixed vectors
```

`PAYLOAD` — это файл или `-` для stdin, в JSON или form-urlencoded. `alif.webhook`
подписывает сырые байты тела. `-f key=value` добавляет или переопределяет поле. Копия внутри
скилла показывает только схемы своего провайдера.

### Схемы

| Схема | Что считает | Переменная секрета |
|---|---|---|
| `alif.webhook` | заголовок `Signature` = base64(HMAC-SHA256(secret, raw body)) | `ALIF_WEBHOOK_SECRET` |
| `click.prepare` | `sign_string` для SHOP API Prepare (MD5) | `CLICK_SECRET_KEY` |
| `click.complete` | `sign_string` для SHOP API Complete (MD5) | `CLICK_SECRET_KEY` |
| `click.advanced` | `sign_string` для Advanced / Split Shop, значения `params` в порядке тела | `CLICK_SECRET_KEY` |
| `click.auth` | заголовок `Auth` Merchant API: `merchant_user_id:sha1(ts+secret):ts`, секунды | `CLICK_SECRET_KEY` |
| `multicard.callback` | `sign` в success callback = md5(store_id invoice_id amount secret) | `MULTICARD_SECRET` |
| `multicard.webhook` | `sign` в вебхуке статуса; пробует формы MD5 и SHA1 и говорит, какая совпала | `MULTICARD_SECRET` |
| `payme.basic` | Merchant API `Authorization: Basic base64(login:KEY)` | `PAYME_KEY` |
| `payme.xauth` | Subscribe API `X-Auth`: `CASHBOX_ID` или `CASHBOX_ID:KEY` с `--backend` | `PAYME_KEY` |
| `payme.checkout` | GET-ссылка на оплату = хост + base64(`m=..;ac.<field>=..;a=..;l=..`) | нет |
| `paynet.basic` | `Authorization: Basic base64(service_id:secret_key)` | `PAYNET_SECRET_KEY` |
| `uzum.fastpay` | `Authorization` для FastPay / Dynamic QR: `user:sha1(ts+secret):ts`, миллисекунды | `UZUM_SECRET_KEY` |
| `uzum.basic` | вебхуки Merchant API, CrossBorder, PaymentHub: Basic `login:password` | `UZUM_PASSWORD` |

### Секреты

Секрет берётся только из переменной окружения из таблицы (или той, что вы укажете через
`--secret-env`), и никогда из аргумента, поэтому он не попадает в историю shell и логи
агента. В выводе он печатается как `<SECRET>`. Значения, где секрет виден открытым текстом,
например Basic-заголовок, печатаются только с `--reveal`.

### Примеры

Найти, почему Click отклоняет запрос Prepare:

```console
$ CLICK_SECRET_KEY=test-secret python3 skills/click/scripts/sign.py click.prepare body.txt \
    --expect d7696dbc2b950daf03e1191fbea5fbb3
input   12345100<SECRET>100011000.002026-11-03 10:00:00
value   24d6c366acd79c05457ddf0547d6d65c
MISMATCH, received d7696dbc2b950daf03e1191fbea5fbb3
```

Click подписал `amount=1000.00` в том виде, в каком отправил. Обработчик собрал его заново
как `1000.0`. Подписывайте сырые значения в том виде, в каком они пришли.

Собрать ссылку на оплату Payme:

```console
$ python3 skills/payme/scripts/sign.py payme.checkout \
    -f m=5e730e8e0b852a417aa49ceb -f ac.order_id=10001 -f a=500000 -f l=uz
input   m=5e730e8e0b852a417aa49ceb;ac.order_id=10001;a=500000;l=uz
value   https://checkout.paycom.uz/bT01ZTczMGU4ZTBiODUyYTQxN2FhNDljZWI7YWMub3JkZXJfaWQ9MTAwMDE7YT01MDAwMDA7bD11eg==
```

`a` в tiyin: `500000` — это 5 000 сумов.

Собрать заголовок `Auth` для Click Merchant API:

```console
$ CLICK_SECRET_KEY=... python3 skills/click/scripts/sign.py click.auth \
    -f merchant_user_id=1 -f timestamp=1762160400
input   sha1(1762160400<SECRET>)
value   1:0df3d3bac209c59a2feefb9ad688c7e003f411c3:1762160400
```

Без `timestamp` берётся текущее время.

Проверить вебхук статуса Multicard, если не знаете, какую формулу использует магазин:

```console
$ MULTICARD_SECRET=... python3 skills/multicard/scripts/sign.py multicard.webhook \
    -f uuid=u-1 -f amount=500000 -f invoice_id=10001
30501c3fbfec8d8fa0a9451049a92fda  md5(u-1500000<SECRET>)
33faffb79880f2af5ca164b7ce5e890aa87a29a2  sha1(u-110001500000<SECRET>)
```

## validate.py

```
validate.py --list [TEXT]                 list schemas: name, method, endpoint
validate.py SCHEMA PAYLOAD [--part PART]  validate PAYLOAD (file, '-' = stdin)
```

`SCHEMA` — имя схемы (`CreateTransaction`), `product/name`, если имя есть в двух продуктах
(`merchant/CreateTransaction`), или путь к файлу.

| Опция | Для чего |
|---|---|
| `--part params` / `result` | методы JSON-RPC: параметры запроса (по умолчанию) или ваш result |
| `--part body` / `query` / `path` | REST-схемы, написанные вручную |
| `--part request` / `response` с `--status 400` | схемы, сгенерированные из OpenAPI (`schemas/ops/*.json`) |

Что он делает за вас:

- Разворачивает конверт JSON-RPC, с `"jsonrpc"` или без, и конверт `{success, data}`.
  Конверт ошибки, переданный как result, считается ошибкой, а не валидным ответом.
- Принимает тело form-urlencoded (`a=1&b=2`) и читает числовые строки как числа там, где
  схема этого требует, потому что любое значение формы приходит строкой.
- Плейсхолдеры вроде `"<CARD_TOKEN>"` совпадают с чем угодно и считаются в выводе.

```console
$ python3 skills/payme/scripts/validate.py CreateTransaction body.json
INVALID references/merchant/schemas/CreateTransaction.json (params): 1 problem(s)
  $.amount: expected integer, got string

$ python3 skills/uzum/scripts/validate.py --list crossborder/confirm
crossborder/confirmcredit                    POST /cbt/v1/transfer/confirm_credit Confirm Transfer to Uzbekistan
crossborder/confirmdebit                     POST /cbt/v1/transfer/confirm_debit Confirm Transfer from Uzbekistan
crossborder/confirmpayment                   POST /cbt/v1/payment/confirm_payment Confirm a Cross-border Payment
```

## В вашем CI

Скрипты детерминированные, поэтому их можно гонять по фикстурам в вашем репозитории:

```sh
for f in tests/fixtures/payme/create-*.json; do
  python3 vendor/uzfintech-skills/skills/payme/scripts/validate.py CreateTransaction "$f" || exit 1
done
```

## Для мейнтейнеров

Исходники обоих скриптов лежат в `scripts/shared/`. `scripts/lint --fix` копирует их в
каждый скилл, а `scripts/lint --only tools` падает, если копия разошлась с исходником, если
не проходит `sign.py --selftest` или если `validate.py` падает на какой-либо схеме. Вместе с
каждой новой схемой добавляйте тестовый вектор в `sign.py`.
