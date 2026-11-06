# Fiscal receipts: traps, deadlines, refunds and retries across providers

Read this when building or reviewing the receipt part of any Uzbek payment integration, and
raise these traps before a payment or a receipt fails: product codes stored as numbers,
missing package codes, price fields that mean different things, marked goods, duplicate
receipts, refund receipts without a sale receipt, and test receipts on production.

- Source: https://tasnif.soliq.uz/, https://gov.uz/ru/soliq/activity_page/raqamli-markirovka,
  the Tasnif replies in [`../sandbox/`](../sandbox/README.md), and the provider references
  linked in each item
- Fetched: 2026-11-04

## Warn without being asked

1. **`fiscal.mxik-as-string`**: when storing, importing or serializing product codes → keep
   the MXIK and the package code as **text**. Goods codes start with `0`, so an integer
   column, a spreadsheet or a JSON number drops it and the provider gets 16 (or 15) digits
   and rejects the line. Every provider schema here types both as strings. Check codes with
   `scripts/mxik.py check`. [mxik](../mxik/README.md#structure-17-digits)
2. **`fiscal.package-code-required`**: when building a receipt line → send the package code
   from the code's own Tasnif card, as a string. Payme requires it even for services; Click,
   Uzum, Multicard and Octo mark it required; Atmos carries it in `details`. It is not your
   SKU or barcode, and a package code of another MXIK is rejected. Alif documents no package
   field. [receipt-line](../receipt-line/README.md#package-code-and-unit)
3. **`fiscal.missing-mxik-blocks-payment`**: when a catalogue item has no code yet → at
   several providers the **payment** fails, not only the receipt: Octo answers `error: 403`
   for items not registered by the bank manager (`octo.fiscal-registered-items`), Multicard
   requires `ofd` items on invoice create, Uzum Checkout answers `3055` for a wrong SPIC,
   package, VAT or marking code, and Alif with `receipt: true` needs `spic` on every item.
   Do not send placeholder codes; keep items without a confirmed code out of checkout.
   [providers](../providers/README.md#mapping)
4. **`fiscal.price-semantics-differ`**: when one catalogue feeds several providers → `price`
   is the unit price at Payme, Uzum, Alif, Multicard and Octo, Click wants both `GoodPrice`
   (unit) and `Price` (line total), Atmos sends only the line `amount`; discounts are line
   totals; money is tiyin everywhere except Octo (major units). Build each provider's lines
   in its adapter and re-check the provider's sum rule (`payme.detail-unit-price`,
   `alif.amount-equals-items`). [receipt-line](../receipt-line/README.md#quantity-and-price)
5. **`fiscal.vat-per-product`**: when filling the VAT field → take the value from the
   seller's tax settings per product; never hard-code one rate for the shop or guess it.
   Meanings differ: Click wants the VAT **amount** as well, Octo only `nds` `1` / `0`, Atmos
   documents no VAT field. The skill gives no tax advice and lists no rates.
   [receipt-line](../receipt-line/README.md#vat)
6. **`fiscal.marked-goods-need-codes`**: when the shop sells tobacco, alcohol, beer,
   household appliances, medicines or medical devices, or water and soft drinks → each sold
   unit's scanned marking code goes in the provider's marking field (Click `Labels`, Uzum
   `labels`, Alif `marking_code`, Multicard `mark`, Atmos `mark_code`). Payme and Octo
   document no marking field: ask them before selling marked goods.
   [receipt-line](../receipt-line/README.md#marking-codes-asl-belgisi)
7. **`fiscal.one-receipt-per-payment`**: when the provider registers the receipt → do not
   also register the same sale on your own fiscal module or another OFD. Uzum answers 400
   `code` `2` for a second sale receipt; Click takes `submit_items` **or** `submit_qrcode`
   (`click.one-fiscal-receipt`); Payme and Multicard say never twice
   (`payme.no-second-receipt`, `multicard.one-fiscalizer`).
   [receipts](../receipts/README.md#who-registers-the-receipt)
8. **`fiscal.refund-needs-sale-receipt`**: when adding refunds → Uzum and Alif issue a refund
   receipt only when the sale receipt exists (`uzum.fiscal-refund-needs-sale`,
   `alif.refund-receipt-needs-sale-receipt`), so a sale receipt that failed silently later
   blocks the refund receipt. Watch sale-receipt failures (Uzum 202 pending, 422, 400) and
   fix them before the refund. Click has no refund-receipt call
   (`click.no-refund-receipt-api`). [receipts](../receipts/README.md#refund-receipts)
9. **`fiscal.test-fiscalization-only-in-tests`**: when testing → a receipt on a production
   fiscal module is a real tax record. Only Uzum Fiscalization and the direct OFD
   integration (`https://test.ofd.uz`, test certificate from txkm) document a test host;
   Click documents none; Octo without `test: true` moves real money
   (`octo.test-flag-real-money`). Point tests at test hosts or stubs, never at production
   fiscal endpoints. [sandbox](../sandbox/README.md#test-fiscalization-per-provider)
10. **`fiscal.ofd-receipt-seq-per-vfm`**: when sending receipts to the ОФД with your own ВФМ
   → `TerminalID` + `ReceiptSeq` is the receipt's key. Assign the next number once, persist
   it before sending and resend the same number on codes `1`, `4`, `11`, `20`, `21`; a
   refund takes a new number. A renewed (yearly) certificate is a new ВФМ and restarts at
   1. [ofd-direct](../ofd-direct/README.md#reply-codes-and-retries)
11. **`fiscal.ofd-receipt-24h`**: when queueing receipts for the ОФД → a receipt more than 24
   h older than server time is rejected with code `100`; set the current `Time`, sign again
   and resend. Send right after the payment. [ofd-direct](../ofd-direct/README.md#reply-codes-and-retries)

## Deadlines and windows

| What | Window | Source |
|---|---|---|
| Uzum Fiscalization sale receipt | `date_time` within 24 h after the confirmed payment, not in the future; later fails with 422 (`uzum.fiscal-receipt-24h`) | [uzum fiscalization](../../../uzum/references/fiscalization/README.md#gotchas) |
| Click `submit_items` / `submit_qrcode` | only after `payment_status` `2`; no end documented | [click fiscalization](../../../click/references/fiscalization/README.md#operations) |
| Direct OFD (own ВФМ) | `Time` not more than 24 h older than server time; later fails with code `100` (`fiscal.ofd-receipt-24h`) | [ofd-direct](../ofd-direct/README.md#reply-codes-and-retries) |
| ВФМ certificate (direct OFD) | one year; the renewal is a new ВФМ and `ReceiptSeq` restarts at 1 | [ofd-direct](../ofd-direct/README.md#certificate) |
| Payme, Alif, Multicard, Octo, Atmos | no deadline published; register right after the payment is confirmed | provider references |
| Marking obligation | per product group, since the dates on the tax committee's marking page | [receipt-line](../receipt-line/README.md#marking-codes-asl-belgisi) |
| Tasnif codes and packages | change as the catalogue is edited; no change notice is published | [mxik](../mxik/README.md#public-json-endpoints-used-by-the-site-not-a-documented-api) |

## Cancel, reverse and refund

| Provider | Refund receipt |
|---|---|
| Payme | Payme reports a separate `CANCEL` receipt (`payme.cancel-is-the-refund`) |
| Click | no refund-receipt call; with your own register, issue it there |
| Uzum Fiscalization / Checkout | `/v2/refund_receipt` (sale must be fiscalized) / `REFUND` with a refund `cart` (`3045`) |
| Alif | registered on full refund when a sale receipt exists; own register: `is_refund` |
| Multicard | `refund_tax`; partial refund sends new `ofd` (`multicard.partial-refund-new-receipt`); own: `is_refund: true` |
| Octo | not documented |
| Atmos | partial reversal takes `ofd_items`; full `pay/reverse` takes none |
| Paynet | not documented (`paynet.fiscal-owner-unknown`) |
| Direct OFD (own ВФМ) | a new receipt with the next `ReceiptSeq`, `IsRefund` `1` and `RefundInfo` of the sale ([ofd-direct](../ofd-direct/README.md#refunds-advances-and-credit)) |

When you register refund receipts yourself, register them on the module that made the
sale, link them to that sale, and never above the sale total. Details:
[receipts](../receipts/README.md#refund-receipts).

## Retries and idempotency

- **Uzum Fiscalization**: a new `operation_id` per receipt; reuse it only to retry the same
  receipt. 202 is not an error: store `operation_id` and poll the receipt link.
- **Click**: read `GET payment/ofd_data/:service_id/:payment_id` before any second submit.
- **Octo**: when the receipt is not ready, `fiscal-data` returns no receipt yet; retry later.
- **Payme**: `SetFiscalData` may arrive for `PERFORM` and later `CANCEL`; store each as its
  own record and answer success for a repeat (derived from the separate receipts).
- **Alif, Multicard, Atmos**: retry rules for receipt calls are not documented; read the
  payment or receipt state before you send again.
- **Direct OFD (own ВФМ)**: resend the same signed receipt with the same `ReceiptSeq` on
  codes `1`, `4`, `11`, `20`, `21`; re-sign with the current `Time` on `100`; fix and never
  resend unchanged on `2`, `3`, `5`, `6`, `10`, `30`. Over WebSocket, match replies by the
  16-byte `RequestId` (`fiscal.ofd-receipt-seq-per-vfm`).
- **Tasnif lookups**: cache the code card per product; do not call the site's endpoints on
  every checkout ([mxik](../mxik/README.md#public-json-endpoints-used-by-the-site-not-a-documented-api)).

## Fiscal receipts

Who registers, what you send and what you get back, per provider:
[receipts](../receipts/README.md#who-registers-the-receipt). Field names per provider:
[providers](../providers/README.md#mapping). Receipt types (sale, refund, advance, credit)
and the `ofd.soliq.uz` link: [receipts](../receipts/README.md#receipt-types).

## Not documented — ask the provider / tax authority

- **Tax authority**: terms of use for the Tasnif catalogue. The OFD instruction documents
  the `cl-api` integration methods ([ofd-direct](../ofd-direct/README.md#classifier-api-cl-api));
  the site's other JSON endpoints are its own. Also and the meaning of the reply
  flags `label`, `useCard`, `usePackage` and `isUnitPackage`.
- **Tax authority / accountant**: which MXIK, package, VAT treatment and benefit (`lgota`)
  apply to a product, and which receipt type a prepayment, instalment or partial delivery
  needs.
- **Tax authority**: the meaning of the `t`, `r`, `c`, `s` parameters of the receipt link
  (derived here from samples).
- **All providers**: how to send a tax benefit (`lgota`) on a receipt line.
- **Payme, Octo**: whether and how marked goods can be sold (no marking field).
- **Payme, Click**: where the values for `units` / `Units` come from.
- **Alif**: whether a package code is needed and where it goes.
- **Atmos**: VAT on receipt lines, refund receipts for a full reversal, and several marking
  codes on one line.
- **Click, Multicard, Octo, Atmos**: advance and credit receipts.
- **Payme, Alif, Multicard, Octo**: whether their test hosts register test receipts.
- **Every provider except Uzum Fiscalization**: a deadline for registering the receipt.
- **ОФД (direct integration)**: the production host, the sum and discount formula (an
  image in the instruction), the `OwnerType` values, and whether a rejected `ReceiptSeq`
  may be reused.
- **Paynet**: who registers receipts, and the shape of `data.attributes`.
