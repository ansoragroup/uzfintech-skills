# Checklist: Payme fiscalization

Contract: [`../references/fiscalization/README.md`](../references/fiscalization/README.md).
Also run [`common.md`](common.md).

## Items (`detail`)
- [ ] `detail` is sent in one place that fits the flow: the `CheckPerformTransaction` result, `receipts.create`, or the POST form (base64).
- [ ] `receipt_type` is `0`; `items` is never empty.
- [ ] Each item has `title`, unit `price` (tiyin), `count`, `code` (17-digit IKPU from tasnif.soliq.uz), `package_code` and `vat_percent`.
- [ ] `discount` is the line total, not per unit; `units` is sent only when known.
- [ ] `sum(price x count - discount) + shipping.price` equals the payment `amount`.
- [ ] IKPU and package codes come from the product catalogue, not hard-coded per order.

## `SetFiscalData` (Payme calls you)
- [ ] Answers `{success: true}` and stores `receipt_id`, `fiscal_sign`, `terminal_id`, `qr_code_url` and `date` (`YYYYMMDDhhmmss`).
- [ ] `type: CANCEL` is stored as a separate fiscal receipt and does not overwrite `PERFORM`.
- [ ] `receipt_id` is accepted as a string or a number.
- [ ] Errors use `-32001` (receipt not found), `-32700`, `-32602` with a plain-string `message`.

## `receipts.set_fiscal_data` (you call Payme)
- [ ] Sent from the back end with `id:key`; `receipt_id` is an integer and `qr_code_url` is present.
