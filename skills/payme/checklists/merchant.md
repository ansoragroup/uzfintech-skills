# Checklist: Payme Merchant API

Contract: [`../references/merchant/README.md`](../references/merchant/README.md). Also run
[`common.md`](common.md).

## CheckPerformTransaction
- [ ] Validates `account` (answers `-31050..-31099` with `data` = the field name) and `amount` (`-31001`).
- [ ] Creates nothing; returns `allow: true`, plus `detail` when fiscal items are needed.
- [ ] Answers `-32400` when a system that Create or Perform depends on is down.

## CreateTransaction
- [ ] Re-validates `account` and `amount`; persists the transaction keyed by the Payme `id` with its `time`.
- [ ] A repeat with a known `id` in state `1` returns the stored `create_time`, `transaction` and `state` unchanged.
- [ ] A known `id` older than 43 200 000 ms is cancelled (`-1`, reason `4`) and answers `-31008`.
- [ ] A new `id` for a one-time account that already has a state `1` transaction answers `-31008`.
- [ ] The order is reserved ("waiting for payment") and cannot be edited while the transaction is open.
- [ ] `transaction` is returned as a string; `receivers` only for split payments.

## PerformTransaction
- [ ] Unknown `id` answers `-31003`; a cancelled or timed-out transaction answers `-31008`.
- [ ] Marks the order paid and fulfils it exactly once; a repeat returns the stored `perform_time` and `state: 2`.

## CancelTransaction
- [ ] State `1` -> `-1`, state `2` -> `-2`; `reason` is stored; a repeat returns the stored `cancel_time` and `state`.
- [ ] A performed transaction that can no longer be reversed answers `-31007`; unknown `id` answers `-31003`.
- [ ] A cancel after perform triggers the refund or reversal in your billing.

## CheckTransaction and GetStatement
- [ ] `CheckTransaction` returns stored times (`0` when not happened), `state` and `reason` (`null` unless cancelled).
- [ ] `GetStatement` is implemented, filters `from <= time <= to` on the Payme `time`, sorts ascending, and omits failed creates.

## Other methods
- [ ] `SetFiscalData` is handled or answered with a defined error (see [`fiscalization.md`](fiscalization.md)).
- [ ] Unknown methods, including an unimplemented `ChangePassword`, answer `-32601` with the name in `data`.
