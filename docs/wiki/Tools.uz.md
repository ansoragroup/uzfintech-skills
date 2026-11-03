# Vositalar

[English](Tools.md) · [Русский](Tools.ru.md) · **Oʻzbekcha** · [简体中文](Tools.zh-CN.md)

Har bir skillning `skills/<provider>/scripts/` papkasida ikkita skript bor. Ularga `python3`
3.9+ versiyasidan boshqa hech narsa kerak emas. MD5 yoki base64 headerni xayolan hisoblaydigan model
shunchalik koʻp xato qiladiki, buni eʼtiborsiz qoldirib boʻlmaydi. Bu skriptlar esa har safar
toʻgʻri hisoblaydi va hisob-kitobni ochiq koʻrsatadi.

| Skript | Qaysi savolga javob beradi | Natija |
|---|---|---|
| `sign.py` | "Bu imzo yoki auth header toʻgʻrimi? Qanday boʻlishi kerak?" | maxfiy kaliti yashirilgan aniq imzolangan satr, qiymat, `MATCH` / `MISMATCH` |
| `validate.py` | "Bu soʻrov tanasi kontraktga mosmi?" | `OK` yoki JSON yoʻllari bilan `INVALID` |

Ikkalasi ham muvaffaqiyatda `0`, mos kelmaslik yoki notoʻgʻri soʻrov tanasida `1`, notoʻgʻri
ishlatilganda `2` kodi bilan chiqadi.

## sign.py

```
sign.py --list                          schemes, the fields they need, the secret variable
sign.py SCHEME [PAYLOAD] [-f k=v ...]   compute; verifies too when PAYLOAD carries the sign
sign.py SCHEME ... --expect VALUE       verify a received signature or header
sign.py --selftest                      check the implementation against fixed vectors
```

`PAYLOAD` — fayl yoki stdin uchun `-`, JSON yoki form-urlencoded formatda. `alif.webhook` esa
buning oʻrniga soʻrov tanasining xom baytlarini imzolaydi. `-f key=value` maydon qoʻshadi yoki
mavjud maydonni almashtiradi. Skill ichidagi nusxa faqat oʻsha provayderning sxemalarini
koʻrsatadi.

### Sxemalar

| Sxema | Nimani hisoblaydi | Maxfiy kalit oʻzgaruvchisi |
|---|---|---|
| `alif.webhook` | `Signature` headeri = base64(HMAC-SHA256(secret, raw body)) | `ALIF_WEBHOOK_SECRET` |
| `click.prepare` | SHOP API Prepare `sign_string` (MD5) | `CLICK_SECRET_KEY` |
| `click.complete` | SHOP API Complete `sign_string` (MD5) | `CLICK_SECRET_KEY` |
| `click.advanced` | Advanced / Split Shop `sign_string`, `params` qiymatlari soʻrov tanasidagi tartibda | `CLICK_SECRET_KEY` |
| `click.auth` | Merchant API `Auth` headeri: `merchant_user_id:sha1(ts+secret):ts`, soniyalarda | `CLICK_SECRET_KEY` |
| `multicard.callback` | success callbackidagi `sign` = md5(store_id invoice_id amount secret) | `MULTICARD_SECRET` |
| `multicard.webhook` | status webhookidagi `sign`; MD5 va SHA1 variantlarini sinab koʻradi va qaysi biri mos kelganini aytadi | `MULTICARD_SECRET` |
| `payme.basic` | Merchant API `Authorization: Basic base64(login:KEY)` | `PAYME_KEY` |
| `payme.xauth` | Subscribe API `X-Auth`: `CASHBOX_ID` yoki `--backend` bilan `CASHBOX_ID:KEY` | `PAYME_KEY` |
| `payme.checkout` | checkout GET havolasi = host + base64(`m=..;ac.<field>=..;a=..;l=..`) | yoʻq |
| `paynet.basic` | `Authorization: Basic base64(service_id:secret_key)` | `PAYNET_SECRET_KEY` |
| `uzum.fastpay` | FastPay / Dynamic QR `Authorization`: `user:sha1(ts+secret):ts`, millisekundlarda | `UZUM_SECRET_KEY` |
| `uzum.basic` | Merchant API webhooklari, CrossBorder, PaymentHub: Basic `login:password` | `UZUM_PASSWORD` |

### Maxfiy kalitlar

Maxfiy kalit faqat jadvaldagi muhit oʻzgaruvchisidan (yoki `--secret-env` bilan siz koʻrsatgan
oʻzgaruvchidan) olinadi, hech qachon argumentdan olinmaydi. Shuning uchun u shell tarixiga va
agent loglariga tushmaydi. Natijada u `<SECRET>` deb chiqadi. Ichida maxfiy kalit ochiq holda
turgan qiymatlar, masalan Basic header, faqat `--reveal` bilan chiqariladi.

### Misollar

Click Prepare soʻrovini nega rad etayotganini aniqlash:

```console
$ CLICK_SECRET_KEY=test-secret python3 skills/click/scripts/sign.py click.prepare body.txt \
    --expect d7696dbc2b950daf03e1191fbea5fbb3
input   12345100<SECRET>100011000.002026-11-03 10:00:00
value   24d6c366acd79c05457ddf0547d6d65c
MISMATCH, received d7696dbc2b950daf03e1191fbea5fbb3
```

Click `amount=1000.00` qiymatini qanday yuborgan boʻlsa, shunday imzolagan. Handler esa uni
`1000.0` qilib qayta yigʻgan. Qiymatlarni qanday kelgan boʻlsa, xuddi shunday xom holida
imzolang.

Payme checkout havolasini yasash:

```console
$ python3 skills/payme/scripts/sign.py payme.checkout \
    -f m=5e730e8e0b852a417aa49ceb -f ac.order_id=10001 -f a=500000 -f l=uz
input   m=5e730e8e0b852a417aa49ceb;ac.order_id=10001;a=500000;l=uz
value   https://checkout.paycom.uz/bT01ZTczMGU4ZTBiODUyYTQxN2FhNDljZWI7YWMub3JkZXJfaWQ9MTAwMDE7YT01MDAwMDA7bD11eg==
```

`a` tiyinda beriladi: `500000` — bu 5 000 soʻm.

Click Merchant API uchun `Auth` headerini yasash:

```console
$ CLICK_SECRET_KEY=... python3 skills/click/scripts/sign.py click.auth \
    -f merchant_user_id=1 -f timestamp=1762160400
input   sha1(1762160400<SECRET>)
value   1:0df3d3bac209c59a2feefb9ad688c7e003f411c3:1762160400
```

Joriy vaqt ishlatilishi uchun `timestamp` maydonini bermang.

Doʻkon qaysi formuladan foydalanishini aniq bilmasangiz, Multicard status webhookini tekshirish:

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

`SCHEMA` — sxema nomi (`CreateTransaction`), bir xil nom ikki mahsulotda uchrasa
`product/name` (`merchant/CreateTransaction`) yoki fayl yoʻli.

| Parametr | Qachon ishlatiladi |
|---|---|
| `--part params` / `result` | JSON-RPC metodlari: soʻrov parametrlari (standart) yoki siz qaytaradigan result |
| `--part body` / `query` / `path` | qoʻlda yozilgan REST sxemalari |
| `--part request` / `response`, `--status 400` bilan | OpenAPI asosida yaratilgan sxemalar (`schemas/ops/*.json`) |

Siz uchun nimalarni hal qiladi:

- JSON-RPC qobigʻi (`"jsonrpc"` maydoni bor yoki yoʻqligidan qatʼi nazar) va `{success, data}`
  qobigʻi ochiladi. Result sifatida berilgan xato qobigʻi valid deb emas, xato deb koʻrsatiladi.
- Form-urlencoded soʻrov tanasi (`a=1&b=2`) qabul qilinadi. Sxemada son kutilgan joyda raqamli
  satrlar son sifatida oʻqiladi, chunki form qiymatlari doim satr boʻlib keladi.
- `"<CARD_TOKEN>"` kabi placeholderlar har qanday qiymatga mos keladi, natijada esa ularning soni
  koʻrsatiladi.

```console
$ python3 skills/payme/scripts/validate.py CreateTransaction body.json
INVALID references/merchant/schemas/CreateTransaction.json (params): 1 problem(s)
  $.amount: expected integer, got string

$ python3 skills/uzum/scripts/validate.py --list crossborder/confirm
crossborder/confirmcredit                    POST /cbt/v1/transfer/confirm_credit Confirm Transfer to Uzbekistan
crossborder/confirmdebit                     POST /cbt/v1/transfer/confirm_debit Confirm Transfer from Uzbekistan
crossborder/confirmpayment                   POST /cbt/v1/payment/confirm_payment Confirm a Cross-border Payment
```

## CI jarayonida

Skriptlar deterministik, shuning uchun ularni oʻz repozitoriyangizdagi fixturelarda ham ishga
tushirsa boʻladi:

```sh
for f in tests/fixtures/payme/create-*.json; do
  python3 vendor/uzfintech-skills/skills/payme/scripts/validate.py CreateTransaction "$f" || exit 1
done
```

## Maintainerlar uchun

Ikkala skriptning manbasi — `scripts/shared/`. `scripts/lint --fix` uni har bir skillga
nusxalaydi. `scripts/lint --only tools` esa nusxalardan biri farq qilib qolsa,
`sign.py --selftest` muvaffaqiyatsiz tugasa yoki `validate.py` biror sxemada ishdan chiqsa,
xato beradi. Har bir yangi sxema bilan birga `sign.py` skriptiga test vektorini ham qoʻshing.
