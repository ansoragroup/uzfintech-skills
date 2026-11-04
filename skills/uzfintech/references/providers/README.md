# Which provider for which task

Hand-written notes. One table of features, one row per provider, built from the "Which
product?" tables of the provider skills. It says **whether** a provider documents a
feature and **which product** carries it. It never says how: field names, bodies, units,
signatures and windows are in the provider's own skill, linked from the first column.

- Source: the provider `SKILL.md` files linked in each row and the references they cite
- Fetched: 2026-11-04

## Features

"not published" means the provider's public docs, as captured in its skill, do not
describe the feature. Ask the provider; do not assume it is missing or present.

| Provider | Card payments | Hosted checkout | Merchant callback API (they call you) | Card tokens / recurring | Holds / pre-auth | Refunds / partial | QR | Split | Installments | Payouts / B2B | Who fiscalizes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [payme](../../../payme/SKILL.md#which-product) | Subscribe `cards.*` from your form | Checkout GET link / POST form | Merchant API (JSON-RPC methods you implement) | Subscribe `save: true`, then `receipts.*` per charge | `hold: true` | `CancelTransaction` / `receipts.cancel`, full only | `Paycom.QR` on Checkout | `receivers` | not published | not published | Payme, from `detail` |
| [click](../../../click/SKILL.md#which-product) | pay-by-card widget; card tokens | payment link / button, widget | SHOP API Prepare / Complete; Advanced Shop | card tokens (subscriptions, one-click) | not published | `payment/reversal`, full only | CLICK Pass (payer's app QR) | Split Shop | not published | not published | Click (`submit_items`) or you (`submit_qrcode`) |
| [uzum](../../../uzum/SKILL.md#which-product) | Checkout | Checkout (`paymentRedirectUrl`) | Merchant API webhooks | Checkout card binding | Checkout TWO_STEP | Checkout full or partial; Merchant API: Uzum calls `/reverse` | FastPay (payer's QR), Dynamic QR (your QR) | not published | Nasiya | PaymentHub (cards, transfers); CrossBorder, Remit Core | Checkout auto-fiscalization, or you through Fiscalization |
| [alif](../../../alif/SKILL.md#which-product) | `pay` `CARD` + OTP | Checkout `invoice` | webhooks (`Signature`) | `getCardToken`, then `pay` `TOKEN` | `hold` | full; partial for instalments only | alif mobi QR | `payouts` / `skip_payouts` | Nasiya through Checkout | split payouts to merchants only | Alif when asked (`receipt: true`), or you + `registerReceipt` |
| [multicard](../../../multicard/SKILL.md#which-product) | token or PCI DSS card payments | invoice `checkout_url` | success callback + status webhook | bind link or PCI DSS form; recurring | create, confirm, charge | full and partial | scanpay (payer's app QR) | `split` | not published | payouts to cards (KYC) | store `tax_registration`: Multicard or you |
| [atmos](../../../atmos/SKILL.md#which-product) | Uzcard / Humo; Visa / Mastercard (MPS) | payment page, HTML widget | Callback API to your billing URL | card linking; MPS recurring templates | Holding; MPS hold | full and partial reversal | not published | multi-payments (the store's own accounts) | not published | not published | Atmos, from `ofd_items` |
| [octo](../../../octo/SKILL.md#which-product) | Visa / Mastercard / UnionPay / Uzcard / Humo | payment page `octo_pay_url` | `notify_url`; capture callback | `bind_card`, `card_token` | two-stage, `auto_capture: false` | full or partial, with limits | not published | not published | not published | not published | Octo, from registered `basket` items |
| [paynet](../../../paynet/SKILL.md#which-operation) | Humo / Uzcard + OTP, host to host | not published | none; poll `status` | not published | not published | `reverse`, full | not published | not published | not published | not published | not documented |
| [oson](../../../oson/SKILL.md#which-product) | on Oson's page | invoice `pay_url` | notify | not published | not published | no API method | not published | not published | not published | not published | not documented; register yourself |
| [kapitalbank](../../../kapitalbank/SKILL.md#which-product) | n.a. (not acquiring) | n.a. | none; poll CheckPayments2 | n.a. | n.a. | n.a. | n.a. | n.a. | n.a. | UZS payment orders, invoices to companies | n.a. (bank transfers) |

- Oson's contract is rebuilt from its shop plugins, not from a published reference
  ([oson](../../../oson/SKILL.md)). Say so when you use its row.
- Card schemes beyond Uzcard / Humo appear in Octo, Atmos (MPS), the Multicard card
  object (`ps`) and the Uzum Merchant API `paymentSource`. Paynet's public docs have no
  Visa / Mastercard. Check the provider skill before you promise a scheme.
- Fiscal fields per provider (MXIK, package code, VAT, marking, refund receipt) are mapped in
  the [fiscal providers table](../../../fiscal/references/providers/README.md#mapping).

## How to pick

1. List the features the merchant needs from the columns above.
2. Drop providers whose cell says "not published" for a must-have feature, or keep them
   and write the open question down for the provider.
3. For each remaining provider, load its skill and confirm the product on its "Which
   product?" table before you design anything.
4. Commercial terms decide the rest and differ per merchant contract. Do not quote, estimate
   or compare them.

## QR payments

Three different things are called "QR payment". Keep them apart.

**The payer shows a QR, the cashier scans it.** Documented for CLICK Pass
([click](../../../click/SKILL.md#which-product)), Uzum FastPay
([uzum](../../../uzum/SKILL.md#which-product)) and Multicard scanpay, which reads a code from
the payer's Payme, Click, Uzum, Anorbank or Xazna app
([multicard invoice](../../../multicard/references/invoice/README.md#scanpay-paymego-clickpass-and-similar);
also in Multicard's own docs index, https://docs.multicard.uz/llms.txt).

**The merchant shows a QR, the payer scans it.** Documented for Uzum Dynamic QR
([uzum](../../../uzum/SKILL.md#which-product)), alif mobi QR
([alif](../../../alif/SKILL.md#which-product)) and the Payme Checkout `Paycom.QR` widget
([payme checkout](../../../payme/references/checkout/README.md#button-and-qr-code)).

**UzQR, the national single QR.** UzQR (https://uzqr.uz/, a dashboard behind a login) is a
Central Bank project for one QR standard: a single merchant code that any bank or payment
app can pay. Facts, as reported by buxgalter.uz on 08.07.2026
(https://buxgalter.uz/publish/doc/text216075_kak_rabotat_v_sisteme_uzqr; Uzbek version
https://buxgalter.uz/uz/publish/doc/text216157_uzqr_tizimida_qanday_ishlash_kerak):

- Since 01.07.2026, legal entities in trade and services must accept payments by the single
  QR; not doing so breaks the trade rules (Presidential Decree UP-246 of 10.12.2025,
  point 3).
- The rules for payment services through the single QR are a Central Bank board resolution
  of 25.03.2026 No. 511, registered by the Ministry of Justice on 15.04.2026 No. 3817.
- No public developer API for UzQR was found. To connect, ask the merchant's bank or
  payment provider how it issues a UzQR code and reports its payments; do not invent
  endpoints.

**Rahmat (restaurant bills and tips).** Rahmat puts a QR on the printed pre-check, so the
guest pays the bill and tips the waiter from a payment app (Payme, Click, Uzumbank,
Multicard, Anorbank, Alif and others). It connects through POS apps, for example the Poster
marketplace listing (https://joinposter.com/en/applications/rahmat). No public developer API
was found, and no source names the company behind it: do not attribute Rahmat to any
provider in this plugin.
