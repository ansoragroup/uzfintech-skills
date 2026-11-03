# Checklist: Uzum PaymentHub (BaaS JSON-RPC)

Contract: [`../references/paymenthub/README.md`](../references/paymenthub/README.md),
[`methods.md`](../references/paymenthub/methods.md), [`errors.md`](../references/paymenthub/errors.md).

## Transport
- [ ] Host from config (production not published); Basic auth from secrets.
- [ ] JSON-RPC 2.0 envelope with a unique `id` per call.
- [ ] Response parsed per method wrapper (`result.receipt` vs bare `result` for `receipt.account.*` and requisite create / confirm).
- [ ] Negative error codes on the wire (`-31602`), not the unsigned values printed on vendor pages.

## Money movement
- [ ] `ext_id` unique per receipt, persisted before `create`; `-31613` -> look up with `receipt.check.extId`.
- [ ] Amounts integer tiyin; MFO and account numbers kept as strings.
- [ ] Only `state 4` is treated as success; `50` / `51` final failures; everything else polled.
- [ ] `30`, `57`, timeouts, lost responses and `-31615` -> poll `receipt.check.id`; never recreate or blindly re-confirm.
- [ ] Decline reason (`result.error`) logged for diagnostics only; logic uses `state`.
- [ ] Account to card: `sender.id` = `"<login>:<sender_id>"`; document block sent above the 50 BRV threshold.
- [ ] Requisite transfers allow up to two business days before declaring them stuck.

## Cards
- [ ] `cards.add` OTP valid 2 minutes; resend via `{id, sms.hash}`; OTP errors `-31617`, `-31618`, `-31622` handled.
- [ ] Card `state` checked (`0` usable; negative values explained to the user).
- [ ] PAN never stored after tokenization.

## Reconciliation
- [ ] Daily `receipt.compare.payment` + `receipt.compare.check` (poll while `-31615`) or `receipt.registry` (page size <= 100).
- [ ] `bank`, `supplier` and `error` arrays reconciled and alerted.
