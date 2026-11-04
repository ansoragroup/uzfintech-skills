# Atmos Visa / Mastercard acquiring (MPS / IPS: invoice page, card binding with 3DS, recurring, hold)

Hand-written notes. Token call and the `apikey` header: [`../common/README.md`](../common/README.md#auth).
Schemas: [`schemas/`](schemas/) (shared models: [`mps-status.json`](schemas/mps-status.json),
[`mps-card.json`](schemas/mps-card.json), [`mps-transaction.json`](schemas/mps-transaction.json)).
Examples: [`examples/`](examples/). The docs call this module both MPS and IPS.

- Source: https://docs.atmos.uz/en/#visa-mastercard-acquiring, https://docs.atmos.uz/en/#card-binding-ips,
  https://docs.atmos.uz/en/#card-linking-by-the-owner, https://docs.atmos.uz/en/#payments-ips,
  https://docs.atmos.uz/en/#create-an-invoice-ips, https://docs.atmos.uz/en/#get-invoice-status-mps,
  https://docs.atmos.uz/en/#transaction-creation-ips,
  https://docs.atmos.uz/en/#creating-a-recurring-payment-ips,
  https://docs.atmos.uz/en/#retrieving-transaction-details-ips, https://docs.atmos.uz/en/#holding-ips,
  https://docs.atmos.uz/en/#system-errors-ips, https://docs.atmos.uz/en/#error-codes,
  https://docs.atmos.uz/en/#transaction-status-status
- Fetched: 2026-11-04
- Needs: a Bearer token, the `apikey` issued when Visa / Mastercard is connected, your
  `store_id`, and a billing URL for the bind-by-owner callback. Raw card data (`pan`, `cvc2`)
  only with a PCI DSS certificate; everyone else uses the invoice page or bind-by-owner.

Base URLs: `https://apigw.atmos.uz/mps`, `https://apigw.atmos.uz/checkout`, and
`https://apigw.atmos.uz/mps-extend/<partner>` for holds (`<partner>` is a path segment
Atmos assigns to you; the docs show one partner's value, do not copy it). Amounts are
tiyin. Send `Authorization: Bearer <token>` and `apikey: <API_KEY>` on every call
(derived: the samples show `apikey` only on some calls).

## Choose a flow

| Need | Flow | Card data on your side |
|---|---|---|
| One-off payment, no PCI DSS | invoice page: `checkout/invoice/create` → `url` → poll `checkout/invoice/get` | no |
| Save a card, no PCI DSS | bind by owner: `checkout/card-bind/create` → `url` → callback with `card_id` | no |
| Save a card, PCI DSS | `mps/pay/card/bind` → 3DS `redirect_uri` → `verified_state` | yes |
| Charge a saved card with the payer present | `pre-create` → `create/bind` → 3DS → `apply` | no |
| Charge a saved card without the payer (recurring) | `transaction/create/template` (card must be 3DS-verified) | no |
| Card data payment, PCI DSS | `pre-create` → `transaction/create` → 3DS → `apply` | yes |
| Reserve, then capture | [holding](#holding) on `/mps-extend/<partner>` | no |

## Flow (saved card, payer present)

```
POST /mps/pay/transaction/pre-create {amount, ext_id, store_id, account, invoice_id, ofd_items}
   └─> payload.id                                   (draft, nothing debited)
POST /mps/pay/transaction/create/bind {transaction_id: payload.id, card_id, amount, client_ip_addr}
   └─> payload.redirect_uri  -> send the payer through 3DS
POST /mps/pay/transaction/apply {transaction_id}
   └─> payload.status 4 SUCCESS, rrn, ofd_redirect_uri
lost answer / status 0-3?  GET /mps/pay/transaction/get/{id}  or  POST /mps/pay/get/ext_id {ext_id}
```

## Methods

| Method | Endpoint | Params (`*` required) | Result |
|---|---|---|---|
| mps-invoice-create | `POST /checkout/invoice/create` | `request_id*`, `account*`, `amount*`, `success_url*`, `items*[] {items_id, name, amount, quantity, details[] {name, values}}`, `expiration_time` (minutes) or `expiration_date` | `payment_id`, `token`, `url` |
| mps-invoice-get | `POST /checkout/invoice/get` | `payment_id` **or** `token` (never both) | `state`, `success`, `final`, `amount`, `payment_items[]` |
| mps-card-bind-link | `POST /checkout/card-bind/create` | `request_id*`, `store_id*`, `account*`, `success_url*` | `payment_id`, `token`, `url` |
| mps-card-bind | `POST /mps/pay/card/bind` | `store_id*`, `pan*`, `expiry*`, `card_name*`, `cvc2*`, `client_ip_addr*`, `ext_id*` | `payload.redirect_uri`, `payload.card` |
| mps-get-card | `GET /mps/pay/card/{id}` | path `id*` | `card {verified_state, status_3ds, card_type, masked_pan}` |
| mps-unbind-card | `POST /mps/pay/card/unbind` | `card_id*`, `store_id*` | `status` |
| mps-pre-create | `POST /mps/pay/transaction/pre-create` | `amount*`, `ext_id*`, `store_id*`, `account*`, `invoice_id*`, `ofd_items*` | `payload.id` |
| mps-create-bind | `POST /mps/pay/transaction/create/bind` | `transaction_id*`, `card_id*`, `amount*`, `client_ip_addr*` | `payload.redirect_uri` |
| mps-create | `POST /mps/pay/transaction/create` | `transaction_id*`, `pan*`, `expiry*`, `amount*`, `card_name*`, `cvc2*`, `ext_id*` (UUID) | `payload.redirect_uri` |
| mps-apply | `POST /mps/pay/transaction/apply` | `transaction_id*` | transaction (`status`, `rrn`, `card`) |
| mps-create-template | `POST /mps/pay/transaction/create/template` | `card_id*`, `amount*`, `ext_id*` (UUID) | transaction |
| mps-get-transaction | `GET /mps/pay/transaction/get/{id}` | path `id*` | transaction |
| mps-get-by-ext-id | `POST /mps/pay/get/ext_id` | `ext_id*` | transaction |

## Card linking by the owner

1. `POST /checkout/card-bind/create` returns a `url`. Send the cardholder there.
2. The cardholder types the card on the Atmos page and confirms with an SMS code.
3. Atmos POSTs `{"api_key": "<API_KEY>", "card_id": 1}` to your billing system. Check that
   `api_key` equals the key Atmos issued (constant-time compare), store `card_id` against the
   customer who opened that link (match it by your `account` / `request_id`; how the callback
   identifies the link is not documented, ask Atmos).
4. Answer `{"status": 1, "message": "Успешно"}`. The docs do not say what happens on any other
   answer.
5. Read `GET /mps/pay/card/{card_id}` and keep the card for recurring use only when
   `verified_state` is `VERIFIED`.

## Holding

| Method | Endpoint | Params (`*` required) | Result |
|---|---|---|---|
| mps-hold | `POST /mps-extend/<partner>/hold` | `ext_id*`, `amount*`, `account*`, `invoice_id*`, `card_id*`, `ofd_items*[] {items_id, ofd_code, name, amount, quantity}`; the sample also sends `store_id` and `client_ip_addr` | `payload.id`, `payload.status` |
| mps-hold-apply | `POST /mps-extend/<partner>/apply` | `transaction_id*` | `payload.status` 4 |
| mps-hold-cancel | `POST /mps-extend/<partner>/cancel` | `transaction_id*` | `status` |
| mps-hold-return | `POST /mps-extend/<partner>/return` | `transaction_id*` | `payload.status` 7 (refund of a captured hold) |

No hold lifetime and no partial capture are documented here; ask Atmos.

## Errors

`status.code` `0` is success. Two tables exist; the card-linking one is the longer:

| Code | Name | What to do |
|---|---|---|
| `-1`, `-2`, `-100` | system, undefined, processing error | read the transaction before any retry |
| `-10` | transaction already exists | your `ext_id` was used: read it with `get/ext_id` |
| `-11` | transaction in an invalid / uncertain state | read the transaction; do not repeat the call |
| `-12` | transaction not found | check the id |
| `-13` | commission calculation error | ask Atmos |
| `-15` | cannot cancel, try later | retry the cancel later |
| `-20`, `-21` | terminal not found / misconfigured | ask Atmos |
| `-200`, `-202`, `-204` | card not found, not valid, binding not active | bind the card again |
| `-201` | card not verified (3DS expected or failed) | send the payer through 3DS; no recurring charge |
| `-203` | declined by the payment system | show to the payer |
| `-300` | insufficient funds | show to the payer |
| `-350` | store not found | check `store_id` |
| `-400` | API key not found | check the `apikey` header |

Transaction `status`: `0` NEW, `1` OPEN, `2` PENDING_OPEN, `3` PENDING_CONFIRM (not final:
query again later), `4` SUCCESS, `5` FAILED, `6` CANCELLED, `7` REVERTED (final), `8`
PENDING_CANCELLED, `9` PENDING_REVERTED. 3DS / card `verified_state`: `OPEN`, `PENDING`,
`VERIFIED`, `FAILED`. `card_type`: `VISA`, `MASTERCARD`.

## Gotchas

- Fulfil only on `status` `4`. The table marks `8` and `9` as final although their names say
  pending; keep querying them until `6` or `7` (derived).
- `create`, `create/bind` and `card/bind` answer with a `redirect_uri` to the bank 3DS page.
  Money is not taken until 3DS and `apply` succeed.
- `create/template` (recurring) works only for a card whose 3DS passed; check
  `GET /mps/pay/card/{id}` first. Expect `-201` otherwise.
- `ext_id` must be unique per transaction (a client UUID); reuse gives `-10`. On a timeout
  read by `ext_id`, never send a new create with a new `ext_id` blindly.
- `expiry` is labelled `MMYY` but every sample value reads as `YYMM`. Test with a real
  card in the sandbox before you go live, and ask Atmos.
- `client_ip_addr` is the **payer's** IP, not your server's.
- `invoice/get`: trust `final` and `success`; `state` values other than `SUCCESS` are not
  listed. No callback is documented for invoice payments, so poll until `final` is `true`
  (derived).
- `expiration_time` on invoices is in minutes.
- Only a hold has a documented refund (`return`). There is no documented cancel or refund for
  a normal MPS payment; ask Atmos before you promise refunds to buyers.
- The bind-by-owner callback reaches the same billing system as the payments callback but
  has a different body (`api_key`, `card_id`) and expects the message `Успешно`.
- Fiscal data: `ofd_items` on `pre-create` and hold, `items` on invoices. The receipt link
  comes back as `ofd_redirect_uri` (`ofd_commission_uri` for the fee).

## Examples

[`examples/`](examples/): every method above has a request and a response, except
mps-get-card and mps-get-transaction (GET, response only).
