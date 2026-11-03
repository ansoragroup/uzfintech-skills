# Checklist: Alif Checkout (invoice + hosted page)

Contract: [`../references/checkout/README.md`](../references/checkout/README.md). Also run
[`common.md`](common.md).

- [ ] `/invoice` items: `price` is the **unit** price in tiyin, `amount` is the quantity, and `discount` is the line total.
- [ ] Invoice total `sum(price x amount - discount)` is checked to be within 50,000..20,000,000,000 tiyin before the call.
- [ ] `webhook_url`, `redirect_url` and `cancel_url` are `https://` and come from config.
- [ ] With `receipt: true`, every item has `spic`; `marking_code` is present for marked goods; `tin` xor `pin` is set for commission lines.
- [ ] `payouts` sum to no more than the total.
- [ ] The invoice `id` from the response is persisted with the order, and the buyer is redirected to `https://checkout.alifpay.uz/?invoice=<id>`.
- [ ] Invoice ids are not validated as full UUIDs.
- [ ] Webhook: `Signature` is verified, HTTP 200 is returned, then `getInvoice` is called before fulfilment.
- [ ] Only `payment.status == "SUCCEEDED"` counts as paid; a missing `payment` means unpaid.
- [ ] The `redirect_url` landing page does not mark the order paid; it reads the state.
- [ ] `refundInvoice` is treated as a full refund, and receipt links are read from both `receipts` and `payment.receipt.results`.
- [ ] `addInvoiceReceiptURL` is called only after payment, with an absolute `ofd.soliq.uz` URL.
- [ ] `sendInvoice` handles `1109` (send limit).
- [ ] `hold.enabled` / `chargeInvoiceHold` is used only for instalment invoices, and a stale held invoice is charged or followed up.
