# Octo test mode and sample data

Hand-written notes with exactly what Octo publishes for testing. Octo has **no separate
sandbox host**: a test payment is a normal call to `https://secure.octo.uz` with
`test: true`. Transport, auth and errors: [`../common/README.md`](../common/README.md).

- Sources: https://help.octo.uz/get-started.html (cabinet),
  https://help.octo.uz/payment-via-web/methods/prepare-payment.html (`test` flag), and the
  method pages named in "Vendor sample values" (Russian pages)
- Fetched: 2026-11-04

## Environments

| What | Test | Production |
|---|---|---|
| API base URL | `https://secure.octo.uz` | `https://secure.octo.uz` |
| Switch | `"test": true` in `prepare_payment` | `test` absent or `false` |
| Credentials | the shop's own `octo_shop_id` / `octo_secret` | the same pair |
| Echo | `isTest` / `test` in the transaction object | `false` |

- `test` is optional; **when it is missing, Octo creates a real payment**. Warning
  [`octo.test-flag-real-money`](../lifecycle/README.md).
- The vendor's own test-mode sample, copied exactly:

```json
{
  "auto_capture": true,
  "test": true,
  "init_time": "2024-05-02 09:17:00"
}
```

## Test credentials (how to get them)

1. Register a merchant account at `https://merchant.octo.uz/register` and activate it by
   following the cabinet instructions (get-started page).
2. Take `octo_shop_id` and `octo_secret` from the cabinet. The docs do not describe a
   separate test shop; ask Octo whether your shop can run `test: true` payments before it
   is fully activated (derived).
3. Ask Octo's technical team for the `unique_key` that signs notifications
   (notifications page); it is not shown in the docs and is not `octo_secret`.
4. Tokenization, two-stage payments, the partner-site flow (PCI DSS) and fiscal items are
   switched on and registered by Octo per shop; request them before you test (derived
   from the per-feature notes).

## Not published

- No sandbox or test host. The sample replies show `dev-pay.octo.uz` and
  `pay-dev.octo.uz` page links, but no page documents them as a test environment.
- No test card numbers with expected outcomes, no decline-simulation cards and no
  3-D Secure test codes.
- No test OTP for Uzcard or Humo; with `test: true` the docs do not say whether an SMS is
  sent or which code is accepted.
- No test `unique_key`, no published credentials and no Postman collection.
- No test PINFL, INN or fiscal object; fiscal items must be registered through the bank
  manager even for testing (derived).
- Whether `test: true` works for `bind_card`, `refund` and `fiscal-data` is not stated.

## Test scenarios (derived)

The docs list no scenarios. These runs use only the `test` flag and your own shop:

| Goal | Steps | Expected |
|---|---|---|
| one-stage page | `prepare_payment` with `test: true`, `auto_capture: true`; open `octo_pay_url` | notification `succeeded`; status check returns `succeeded` |
| two-stage hold | `prepare_payment` with `test: true`, `auto_capture: false`; pay; `set_accept` `capture` with a smaller `final_amount` | status `waiting_for_capture`, then `succeeded`; `refunded_sum` shows the released rest |
| hold release | as above, then `set_accept` `cancel` | status `canceled` |
| lost reply | drop the connection after `prepare_payment` | the three-field status call with the same `shop_transaction_id` returns the existing payment |
| wrong secret | any call with a wrong `octo_secret` | `error: 2`, `"Wrong secret"` (`fiscal-data`: `error: 1`) |
| notification check | verify `signature` with `scripts/sign.py octo.notify` and your `unique_key` | `MATCH`; a tampered `status` gives `MISMATCH` |
| refund limits | refund below 1 USD equivalent | `error: 22`, `"Wrong amount to refund."` |
| missing flag | your config test: the environment flag is unset | your code refuses to start or sends `test: true` explicitly; never a silent real payment |

Your `notify_url` and `bind_notify_url` must be reachable from the internet (derived).

## Vendor sample values

Copied exactly from the request and response samples on the Octo pages (paths below are
under `https://help.octo.uz/`). Use them in mocks, fixtures and parsers that replay Octo's
shapes. They are illustrative: none is documented as a working credential, card or test
object, and real-looking personal names and e-mail addresses in the samples are left out.

| Call | Values | Page |
|---|---|---|
| prepare_payment / check status | `octo_shop_id` `123`, `octo_secret` `"537da54b-835a-4968-9864-c2ae02c5902e"`, `shop_transaction_id` `"0000_0000_0000_0000_0010"`, `init_time` `"2024-05-02 09:17:00"`, `total_sum` `1000.0`, `currency` `"UZS"`, `description` `"TEST_PAYMENT"`; status reply `shop_transaction_id` `"c9211e0f-c6ba-4d97-b8be-fb230ef3985b"`, `octo_payment_UUID` `"e3f40dc3-4955-412a-853a-2ddd28d3201f"` | `payment-via-web/methods/prepare-payment.html`, `check-status.html` |
| basket item | `position_desc` `"Solyonaya ili solonovataya ryba"`, `count` `1`, `price` `100.0`, `spic` `"00305001001000000"`, `inn` `"123456"` or `pinfl` `"123451246"`, `package_code` `"1425207"`, `nds` `1` | `fiscal-data.html` |
| unregistered basket | `error` `403`, message names merchant ID `242` and the basket values above | `fiscal-data.html` |
| cancel a hold | `octo_secret` `"6665a780-6715-45ab-83e2-74f012867a26"`, `accept_status` `"cancel"`, `final_amount` `700.00` | `cancel.html` |
| set_accept reply | `octo_pay_url` `"https://dev-pay.octo.uz/pay/6b6b4477-ab8b-49dc-97eb-638b15b9b3e9?language=uz"` | `payment-via-web/methods/set-accept.html` |
| refund reply | `octo_payment_UUID` `"6b6b4477-ab8b-49dc-97eb-638b15b9b3e9"`, `refund_id` `"9ddd6a6c-e8c7-4859-9943-70c5bf7b4405"`, `refund_time` `"2024-12-18 16:59:39"`, `status` `"succeeded"`; `amount` `1000.00` | `refunds.html` |
| pay with card (partner site) | `pan` `"8600313260861293"`, `exp` `"2602"`, `method` `"uzcard"`, `cvc2` `""`, `cardHolderName` `"CardHolder Name"`; reply `uuid` `"04b7f6dd-4693-4afa-96e9-f42790413de7"`, `redirectUrl` `"https://pay2.octo.uz/uzcard/sms/04b7f6dd-4693-4afa-96e9-f42790413de7"`, `expireTime` `1732701267781` | `payment-confirm-pay.html` |
| verificationInfo | `verifyId` `819`, `phone` `"+998** *****33"`, `secondsLeft` `221` (or `0` when expired) | `payment-via-partner-web/methods/verification-info.html` |
| check_sms_key | `smsKey` `"317168"`, `paymentId` `822`; reply `id` `5520`, `processorKey` `"010967385013"`, `merchantId` `242`, `createTime` `1732700367802`, `peyedTime` `1732700437809`, `processingReference` `"1732700437604_5520"`, `bankCode` `"RB"`, `redirectUrl` `"https://dev-pay.octo.uz/status/04b7f6dd-4693-4afa-96e9-f42790413de7"` | `payment-via-partner-web/methods/check-sms-key.html` |
| check_pan (OTP resend) | `pan` `"1234123412341234"`, `expDate` `"2601"`; reply `verifyId` `856`, `phone` `"+998** *****33"` | `otp-resend.html` |
| bind_card | `pan` `"9860240101226506"`, `exp` `"2805"`, `phone` `"998901234567"`, `cardHolderName` `"Card Holder Name"`, `cvc2` `""`, `method` `"humo"`, `return_url` / `notify_url` / `bind_notify_url` `"https://notify-url.uz"`; reply `shop_transaction_id` `"123431321323334132333"`, `octo_payment_UUID` `"06000144-db56-47b6-9eba-021ad4ff246b"`, `octo_pay_url` `"https://pay-dev.octo.uz/uzcard/sms/06000144-db56-47b6-9eba-021ad4ff246b"` | `tokenization.html` |
| bind_card/check_sms_key | `smsKey` `"61135"`; `verifyId` `819` from `verificationInfo` | `tokenization.html` |
| bind callback (you receive) | `shop_transaction_id` `"d87f4hd8d76f4h58d"`, `pan` `"4276380012341025"`, `exp` `"2006"`, `card_token` `"sdf9g87sd6f9g876sdf9g876sdf98g"`; error answer `"Invalid shop_transaction_id"` | `tokenization.html` |
| block_card_token | `octo_shop_id` `242`, `octo_secret` `"1d45df74-bb95-47cf-a616-8d6dcee2e10d"`, `card_token` `"sdf9g87sd6f9g876sdf9g876sdf98g"` | `tokenization.html` |
| fiscal-data | `octo_shop_id` `10000`, `octo_secret` `"2d45df74-bb95-47cf-a616-8d6dcee2e10d"`, `payment_uuid` `"1145df74-bb95-47cf-a616-8d6dcee2e222"`; reply `phone` `"998781290011"`, `terminalID` `"EZ000000000102"`, `receiptId` `2121`, `dateTime` `"20220929013159"`, `fiscalSign` `"420808230750"` | `fiscal-data.html` |
| Postman variables in samples | `{{merchant_id}}`, `{{merchant_secret}}`, `{{$randomUUID}}`, `{{octo_payment_UUID}}`, `{{payment_id}}`, `{{bind_octo_payment_UUID}}`, `{{bind_verifyId}}` | several |

Sample-specific caveats:

- The OTPs `317168` and `61135` are format samples, not documented test codes.
- `8600313260861293` and `9860240101226506` look like real card numbers and the docs do
  not call them test cards. Use them only in offline fixtures and parsers; never pay with
  or bind them, on any host. `4276380012341025` carries a 2020 expiry (`2006`) and is
  stale. `1234123412341234` is a format filler.
- The basket sample has `price` `100.0` x `count` `1` against `total_sum` `1000.0`; do not
  copy that mismatch.
- The secrets in the samples differ per page and none is documented as working.
- `https://notify-url.uz` is a sample address; point callbacks at your own host.
