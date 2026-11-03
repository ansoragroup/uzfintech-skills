# Checklist: Multicard Invoice

Contract: [`../references/invoice/README.md`](../references/invoice/README.md). Also run
[`common.md`](common.md).

## Create
- [ ] `POST /payment/invoice` sends `store_id`, tiyin `amount`, `invoice_id`, `callback_url` and a non-empty `ofd`.
- [ ] `ttl` is in seconds; `lang` is `ru`, `uz` or `en`; `sms` (if used) is `998XXXXXXXXX`.
- [ ] Both the invoice `uuid` and, once known, the payment `uuid` are stored with the order.
- [ ] The payer is sent to `checkout_url`; QR codes use `short_link` in production and `checkout_url` in the sandbox.

## Result
- [ ] The order is fulfilled only after a verified success callback or a `GET /payment/invoice/{uuid}` with `payment.status` = `success`.
- [ ] `return_url` and `return_error_url` only show a page; they never mark the order paid.
- [ ] `ERROR_TRANS_NOT_READY` (expired invoice) leads to a new invoice, not a retry of the old one.
- [ ] Unpaid invoices that are no longer needed are deleted with `DELETE /payment/invoice/{uuid}`; a `400` on a paid invoice is handled.

## Scanpay
- [ ] `PUT /payment/{uuid}/scanpay` uses the invoice `uuid` and the scanned `code`.
- [ ] A wrong QR (`400`) shows the message to the cashier; a timeout, `ERROR_DEBIT_UNKNOWN` or HTTP 500 leads to polling, not a second scan.
