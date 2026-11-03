# Checklist: Uzum CrossBorder, Remit Core and Ratekeeper

Contracts: [`../references/crossborder/README.md`](../references/crossborder/README.md),
[`../references/remitcore/README.md`](../references/remitcore/README.md),
[`../references/ratekeeper/README.md`](../references/ratekeeper/README.md).

## CrossBorder
- [ ] Hosts from config (production over IPSec; test host differs between spec and docs).
- [ ] Basic auth from secrets.
- [ ] Optional fields omitted, never sent as `""` or `null` (`10002`).
- [ ] Amounts integer minor units; currencies from the allowed list.
- [ ] `externalTransferId` / `externalPaymentId` unique and persisted before the call (`10211` / `20201`).
- [ ] `PHONE` identification always sends `bankLabel` from `receiver_banks`.
- [ ] Confirm within 20 minutes of the check (`10221` / `20204`), and only when `APPROVED`.
- [ ] `PENDING` polled via `/transfer/status` (no callback).
- [ ] `cancel_debit` used only to undo a successful debit whose onward credit failed.
- [ ] Errors read from the `error` block on both HTTP 200 and non-200.

## Remit Core
- [ ] `X-Api-Key` on every call; unknown response fields ignored.
- [ ] `register` -> `process`; `2000` treated as async (callback or `get_status`), never re-registered.
- [ ] `2002` treated as in progress.
- [ ] `target` / `source` use `paymentInstrumentType`; countries ISO alpha-3.
- [ ] DEBIT `2001` -> OTP `confirm` (or 3DS outside Remit Core); `resend_otp`; `cancel` only for DEBIT.
- [ ] Callback endpoint returns 2xx and is idempotent on `transferId`.
- [ ] Limit errors (`3003`, `3004`, `3012`, `3013`, `3014`) surfaced to the user, not retried.

## Ratekeeper
- [ ] `rate` parsed as a decimal string.
- [ ] Any non-zero `code` treated as failure and logged with `message`.
