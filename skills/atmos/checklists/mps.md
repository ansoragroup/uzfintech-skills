# Checklist: Atmos Visa / Mastercard (MPS / IPS)

Contract: [`../references/mps/README.md`](../references/mps/README.md). Also run
[`common.md`](common.md).

## Auth and transport
- [ ] Every `/mps`, `/checkout` and `/mps-extend/<partner>` call sends `Authorization: Bearer <token>` and `apikey: <API_KEY>`; the `apikey` comes from secrets.
- [ ] The `<partner>` path segment comes from configuration, as Atmos assigned it.
- [ ] Answers are read on `status.code` (`0` success, negative codes) and the transaction `status`.

## Card data and binding
- [ ] `pan` and `cvc2` (`card/bind`, `transaction/create`) are sent only from PCI DSS certified systems; otherwise the invoice page or bind-by-owner is used.
- [ ] The `expiry` format was confirmed with Atmos (`MMYY` label vs `YYMM` samples) and tested.
- [ ] `client_ip_addr` is the payer's IP, not the server's.
- [ ] The payer is sent to `redirect_uri` for 3DS; nothing is fulfilled before `apply`.
- [ ] The bind-by-owner callback checks `api_key` in constant time, stores `card_id` for the right customer and answers `{"status": 1, "message": "Успешно"}`.
- [ ] A card is used for `create/template` only when `GET /mps/pay/card/{id}` shows `verified_state` `VERIFIED`.

## Payments
- [ ] `ext_id` is a fresh UUID per transaction, stored before the call; `-10` leads to `get/ext_id`.
- [ ] The order is fulfilled only on `status` `4`; `0`-`3`, `8` and `9` are re-queried.
- [ ] A lost `apply` answer leads to `GET /mps/pay/transaction/get/{id}` or `get/ext_id`, never to a second `apply`.
- [ ] Invoices are polled with `invoice/get` until `final` is `true`; `success` decides; `payment_id` or `token` is sent, never both.
- [ ] `ofd_items` (pre-create, hold) or `items` (invoice) carry the fiscal lines.

## Holds and refunds
- [ ] Hold, `apply`, `cancel` and `return` take the hold `transaction_id`; `return` is used only for a captured hold.
- [ ] Refunds for non-hold MPS payments were agreed with Atmos; nothing assumes a refund call.
