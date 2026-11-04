# CBU payment purpose codes and "Детали платежа" (every Uzbek bank)

Hand-written notes on the Central Bank of Uzbekistan (CBU) directory 60 «Назначение
платежа» and the content rules for the "Детали платежа" (payment details) field. These
rules apply to **UZS payment orders in every bank in Uzbekistan**, not only Kapitalbank.
The data is in [`codes.json`](codes.json); the offline tool is `scripts/purpose_codes.py`.
In the Kapital API the code goes in `purp_code` and the text in `purpose` of
`SendPaymentIBK` ([kapital-api](../kapital-api/README.md#payment-order-fields-sendpaymentibk)).

- Source: the CBU comparison (transition) table, published as spreadsheets:
  https://static.buhgalter.uz/tsdocs/ru/sravniteln_tabl_ru.xlsx (Russian),
  https://static.buhgalter.uz/tsdocs/uz/sravniteln_tabl_uz.xlsx (Uzbek, Cyrillic);
  the field rules and dates:
  https://buxgalter.uz/publish/doc/text215319_kakie_kody_ispolzovat_pri_zapolnenii_platejnyh_porucheniy
  (Russian), https://buxgalter.uz/oz/publish/doc/text215399_bank_tulovlarining_kodlari2
  (Uzbek), and a bank's client notice of 21.05.2026:
  https://kdb.uz/ru/press-center/news/new-requirements-for-completing-the-payment-details-field-in-uzbek-soums-payment-orders;
  P2P transfers:
  https://kun.uz/en/news/2026/03/26/central-bank-backtracks-on-mandatory-p2p-transfer-descriptions-following-public-pressure
- Fetched: 2026-11-04
- Needs: nothing; the table and the tool work offline.

## Dates

| Date | What changes | Source |
|---|---|---|
| 06.05.2026 | the new codes come into force; the "Детали платежа" content rules become mandatory for UZS payment orders | the table header, the kdb.uz notice |
| 06.05.2026 – 25.05.2026 | transition: old and new codes are both accepted (derived from the two dates) | the kdb.uz notice |
| 26.05.2026 | old codes are no longer accepted; an order with one is refused or delayed | the table header, both articles, the kdb.uz notice |

Warning `kapitalbank.old-purpose-codes-rejected`. Saved payment templates and internet
banking presets made before May 2026 still carry old codes; check them.

## What "Детали платежа" must contain

The field holds four parts (same list in the Russian article and the kdb.uz notice):

1. the current goods or services code from the updated directory;
2. the contract number and date, **when there is a contract**;
3. the name of the goods, works or services;
4. the type of payment (for example prepayment or payment) and any other required details.

The order of the parts, separators and wording are **not prescribed**. The tool assembles
them as `<code> <goods>, по договору № <no> от <DD.MM.YYYY>, <payment type>[, <extra>]`;
that layout is our convention (derived), not a CBU rule. Warning
`kapitalbank.payment-details-content`.

Whether a bank wants the code repeated inside the text when it also has a separate code
field (Kapital `purp_code`) is not stated. The list above names the code as part of the
field, so the tool repeats it. Ask your bank if its validator rejects that.

## The table

- **115 new codes**, `00001` to `00117`; `00077` and `00115` do not exist.
- **Goods, `00001`–`00097`**: one code per chapter of the Harmonized System (HS / ТН ВЭД),
  in chapter order. `00001` is live animals (chapter 1) and `00076` aluminium (chapter 76).
  The table has no `00077` because HS chapter 77 is reserved.
- **`00098` ПРОЧИЕ ТОВАРЫ** (other goods).
- **Services, `00099`–`00117`**: from `00099` КОММУНАЛЬНЫЕ ПЛАТЕЖИ to `00117` household and
  personal repairs; `00111` is ПРОЧИЕ УСЛУГИ (other services).
- **69 old codes**, each mapped to one or more new codes. The table warns that goods under
  one old code may fall under several new codes. Nine do:

| Old code | Old name (RU, as published) | New codes (the table's note) |
|---|---|---|
| `00513` | Мясо, колбаса и мясные консервы | `00002`; `00016` (колбаса и мясные консервы) |
| `00512` | Кондитерские изделия | `00017` (изготовленные из сахара); `00019` (изготовленные из муки) |
| `00545` | Сантехнические товары | `00039` (изготовленные из пластмассы); `00068` (изготовленные из камня); `00069` (изготовленные из керамики); `00076` (изготовленные из аллюминия) |
| `00525` | Бумага и канцелярские товары | `00048`; `00083` (канцелярские товары изготовленные из металла); `00096` (ручки) |
| `00535` | Головные уборы | `00065`; `00066` |
| `00693` | Металл и изделия из металла | `00072`; `00073` |
| `00532` | Кабель, электропроводники | `00074`; `00076` |
| `00518` | Запасные части автомобилей и бытовой техники | `00085` (за исключением автомобильных частей); `00087` (запасные части, относящиеся к автомобилям) |
| `00668` | За выполненные работы и оказанные услуги | `00100`; `00111` |

For these, pick the new code by what the goods are made of or what they are, using the
note where the table gives one (for `00545`: "изготовленные из аллюминия" → `00076`).
Without a note, compare the new names (`old CODE` prints them). One new code can follow
from several old ones (`00076` from `00545` and `00532`). Warning
`kapitalbank.one-old-code-many-new`.

## Errata in the published sheets (kept as published)

- **Shifted row**: on the Uzbek sheet the row for `00076` / old `00545` is shifted one
  column left (the old code is missing and its name sits in the code column). `codes.json`
  realigns it from the Russian sheet.
- **Latin look-alike letters** inside Cyrillic names: Latin `E` in 12 Uzbek names (for
  example `00069` КEРАМИК, `00072` ҚОРА МEТАЛЛАР) and in the Russian name of `00106`
  ПРОФEССИОНАЛЬНЫЕ; Latin `A` in the Uzbek name of `00116` AТРОФ. `codes.json` keeps the
  text as published; the tool's search ignores the difference. Do not copy these names into
  a payment text: type the goods name yourself.
- **Old `00652`** carries an Uzbek name (Коммунал туловлар) on the Russian sheet too; it maps
  to `00099`.
- The column `PR_PLAT` is `2` on every filled row; its meaning is not given.

## What the table does not cover

- **Budget and treasury payments** (taxes, duties, payments to budget organizations) follow
  a separate instruction and their own treasury codes; the table holds commercial codes only
  (Uzbek article). In the Kapital API, check the payee first with `GetBudjetAcc` (budget
  account and INN) or `GetNalogAcc` (fixed treasury requisites). Warning
  `kapitalbank.check-budget-account-first`.
- **Salary, loans, deposits, own-account transfers**: not in this table. Ask your bank which
  code applies. The tool answers `not in the published table` for them.
- **P2P card transfers** in consumer apps: a separate topic. After public criticism the CBU
  said in March 2026 that a P2P transfer purpose was never mandatory; banks may show or omit
  the field (kun.uz). It does not change the rules for payment orders above.

## Tool: `scripts/purpose_codes.py`

Standard library only, offline. Exit `0` accepted or found, `1` rejected, not found or
invalid, `2` usage error. `--date YYYY-MM-DD` checks a code on a given day (default today).

```sh
python3 scripts/purpose_codes.py search алюмин
python3 scripts/purpose_codes.py old 00545
python3 scripts/purpose_codes.py check 00699
python3 scripts/purpose_codes.py details --code 00076 --goods "алюминиевые смесители" \
    --contract-no 100001 --contract-date 03.11.2026 --payment-type оплата
python3 scripts/purpose_codes.py account 20208000012345678001 --mfo 01042
python3 scripts/purpose_codes.py --selftest
```

Output on 2026-11-04:

```
$ purpose_codes.py search алюмин
00076  АЛЮМИНИЙ И ИЗДЕЛИЯ ИЗ НЕГО | АЛЮМИНИЙ ВА УНИНГ МАҲСУЛОТЛАРИ

$ purpose_codes.py old 00545
old 00545  Сантехнические товары | Сантехника товарлари
  -> 00039  ПЛАСТМАССЫ И ИЗДЕЛИЯ ИЗ НИХ | ПЛАСТМАССАЛАР ВА ПЛАСТМАССА МАҲСУЛОТЛАР   [note: изготовленные из пластмассы / пластмассадан ясалганлар]
  -> 00068  ИЗДЕЛИЯ ИЗ КАМНЯ, ГИПСА, ЦЕМЕНТА, АСБЕСТА, СЛЮДЫ ИЛИ АНАЛОГИЧНЫХ МАТЕРИАЛОВ | ТОШ, ГИПС, ЦЕМЕНТ, АСБЕСТ, МИКИКА ЁКИ ШУНГА ЎХШАШ МАТЕРИАЛЛАР   [note: изготовленные из камня / тошдан ясалганлар]
  -> 00069  КЕРАМИЧЕСКИЕ ИЗДЕЛИЯ | КEРАМИК МАҲСУЛОТЛАР   [note: изготовленные из керамики / керамикадан ясалганлар]
  -> 00076  АЛЮМИНИЙ И ИЗДЕЛИЯ ИЗ НЕГО | АЛЮМИНИЙ ВА УНИНГ МАҲСУЛОТЛАРИ   [note: изготовленные из аллюминия / алюмендан ясалганлар]
  several new codes: pick the one whose note or name fits the goods

$ purpose_codes.py check 00699                      # exit 1
NO old-rejected: REJECTED on 2026-11-04: old codes are refused from 2026-05-26
old 00699  Покупка минеральных удобрений | Минерал угитлар хариди учун
  -> 00031  УДОБРЕНИЯ | ЎҒИТЛАР

$ purpose_codes.py details --code 00076 ...
purp_code: 00076
text:      00076 алюминиевые смесители, по договору № 100001 от 03.11.2026, оплата
OK

$ purpose_codes.py account 20208000012345678001 --mfo 01042
OK (format only; the check key is not public)
```

`details` exits `1` with `INVALID` and a `PROBLEM` line when the code is old or unknown,
the goods or payment type is empty, or only one of the contract number and date is given.
`account` checks only the shape (20 digits, MFO 5 digits): the account check-key algorithm
is not public, so a well-formed account can still be wrong.
