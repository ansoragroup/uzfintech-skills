# Checklist: Octo payment via the partner's site (card form on your page)

Contract: [`../references/partner-page/README.md`](../references/partner-page/README.md). Also run
[`common.md`](common.md) and [`payment-page.md`](payment-page.md) (creation, capture, status).

## Scope
- [ ] The shop holds a PCI DSS certificate; without one the Octo page or a token is used instead.
- [ ] `pan`, `exp` and `cvc2` are never logged or stored and are masked in error reports.

## Pay
- [ ] `POST /pay/{octo_payment_UUID}` sends `pan`, `exp` (YYMM), `method` (`bank_card`, `uzcard`, `humo`), `cvc2` and `cardHolderName`, or `card_token` and `method`.
- [ ] `email` is sent on `pay` whenever `prepare_payment` carried `user_data`.
- [ ] The integer `data.id` is stored as `paymentId` next to `octo_payment_UUID`.
- [ ] Visa / Mastercard payments show `redirectUrl` to the payer and wait for the notification; the presence of `redirectUrl` is never read as success.

## OTP (Uzcard / Humo)
- [ ] `verificationInfo` provides `verifyId`, the masked phone and `secondsLeft`; `secondsLeft: 0` is treated as expired.
- [ ] `check_sms_key` sends `smsKey`, `paymentId` (integer) and `verifyId`.
- [ ] The page shows the attempts left and starts a new payment after three wrong codes (`octo.otp-three-tries`).
- [ ] Resends go through `check_pan` with the new `verifyId`; `error: 17` stops resending and offers a new payment.
- [ ] After `check_sms_key` returns `succeeded`, the order still waits for the notification or a status check.
