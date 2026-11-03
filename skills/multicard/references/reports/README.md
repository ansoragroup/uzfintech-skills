# Multicard Reports (application, store, recipient requisites, payment and payout registries)

Hand-written notes. Transport, auth and errors: [`../common/README.md`](../common/README.md).
Schemas: [`schemas/`](schemas/). Examples: [`examples/`](examples/).

- Source: https://docs.multicard.uz/19729326e0, https://docs.multicard.uz/41406205e0,
  https://docs.multicard.uz/19729327e0, https://docs.multicard.uz/19729328e0,
  https://docs.multicard.uz/19729329e0, model page https://docs.multicard.uz/9655483d0
  (store) (Russian pages)
- Fetched: 2026-11-03
- Use: wallet balance before payouts, cashbox fiscal settings, split recipients, daily
  reconciliation.

## Methods

| Method | Endpoint | Params (`*` required) | Result (`data`) |
|---|---|---|---|
| get-application | `GET /payment/application` | none | `application_id`, `wallet_sum`, `wallet_overdraft`, `otp_required`, `otp_length`, `allow_bank_transaction`, `official_name`, ... |
| get-store | `GET /payment/store/{uuid}` | path store `uuid` | store: `id`, `uuid`, `title`, `tax_registration`, `tax_mxik`, `tax_package_code`, `tax_commission_recipient_tin`, `merchant`, ... |
| get-merchant-account | `GET /payment/merchant-account/{recipient}` | path requisites uuid | `tin`, `official_name`, `mfo`, `account_no`, `vat_payer`, `active`, ... |
| get-payment-history | `GET /payment/store/{store_id}/history` | query `offset*`, `limit*`, `only_status`, `start_date*`, `end_date*` | `pagination{total, offset, limit}`, `stat[]`, `list[]` |
| get-payout-history | `GET /payment/store/{store_id}/credit-history` | query `offset*`, `limit*`, `only_status*`, `start_date*`, `end_date*` | same shape |

`start_date` and `end_date` are `Y-m-d H:i:s` in GMT+5. `only_status` filters on one status
(for example `success`); it is **required** on the payout registry and optional on the
payment registry.

## Store fiscal settings

| Field | Meaning |
|---|---|
| `tax_registration` | `0` fiscalization off, `1` on, `2` fiscalize only the commission charged on top (`up`), `3` only the commission paid by the merchant (`down`) |
| `tax_mxik` | default IKPU for the cashbox, or `null` |
| `tax_package_code` | default package code for that IKPU, or `null` |
| `tax_commission_recipient_tin` | commissioner TIN used for fiscal receipts; `null` means the merchant's TIN |

Read the store once per cashbox and decide whether you or Multicard fiscalizes
([`../common/README.md`](../common/README.md#fiscal-items-ofd)).

## Wallet

- `wallet_sum` is the partner deposit in tiyin; `wallet_overdraft` is how far it may go
  below zero (field meaning derived from the names; the docs do not describe them).
- Check the balance before a payout; payouts are paid from this wallet.
- `split` parts of type `wallet` top it up.

## Errors

| Case | Answer |
|---|---|
| registry: missing or invalid parameter | `400 ERROR_FIELDS` |
| registry: `store_id` that is not yours | `403 ERROR_ACCESS_DENIED` |

## Gotchas

- Registries are paged with `offset` and `limit`; loop until `offset + limit >= total`
  (derived).
- `stat[]` carries totals per status and payment system for the selected range (derived
  from its fields); compare it with your own totals during reconciliation.
- `store_id` in the registry path is your cashbox id; get-store takes the store **uuid**.
- `active` on merchant-account is shown as `1` or `true` in different places; accept both.

## Examples

[`examples/`](examples/): get-application response, payment-history query and response.
