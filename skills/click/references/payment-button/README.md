# Click payment link, button, pay-by-card widget and mobile deeplink

Hand-written notes. There is no API body here; the [`examples/`](examples/) folder holds the
parameter sets as JSON, and [`schemas/`](schemas/) describes them. Credentials are in
[`../common/README.md`](../common/README.md).

- Source: https://docs.click.uz/en/click-button/, https://docs.click.uz/en/click-pay-by-card/,
  https://docs.click.uz/en/additional/mobile
- Fetched: 2026-11-03
- Direction: **the payer is sent to Click.** The payment itself reaches your billing
  through the SHOP API (Prepare / Complete), so the service needs
  [`../shop-api/`](../shop-api/README.md) as well. Only the SHOP API Complete, or a Merchant
  API status call, proves that the order was paid.

## Variants

| Variant | How | Result reaches you via |
|---|---|---|
| Link | `GET https://my.click.uz/services/pay?<params>` (a plain `<a href>`) | SHOP API Complete; the payer returns to `return_url` |
| Form | `<form action="https://my.click.uz/services/pay" method="get">` with hidden inputs | same |
| Pay-by-card button | `<script src="https://my.click.uz/pay/checkout.js" class="uzcard_payment_button" data-...>` inside your `<form method="post">` | your form is posted with an extra `status` field, plus SHOP API Complete |
| Pay-by-card from code | load `checkout.js`, call `createPaymentRequest(params, callback)` | `callback({status})` when the window closes, plus SHOP API Complete |
| Mobile deeplink | open `https://my.click.uz/services/pay/?<params>` with `ACTION_VIEW` (Android) or `UIApplication.open` (iOS) | the app closes (or opens `return_url`); ask your server for the status |

## Parameters

Link and form (query string / hidden inputs):

| Parameter | Required | Rule |
|---|---|---|
| `merchant_id` | yes | your merchant id |
| `service_id` | yes | your service id |
| `transaction_param` | yes | your order id; Click passes it to the SHOP API as `merchant_trans_id` |
| `amount` | yes | soums, formatted `N.NN` (e.g. `25000.00`) |
| `merchant_user_id` | no | your user id at Click |
| `return_url` | no | where the payer lands afterwards |
| `card_type` | no | `uzcard` or `humo`, to restrict the card type |

The deeplink needs only `service_id`, `merchant_id`, `amount` and `transaction_param`;
`return_url` is optional there too.

Pay-by-card widget: the same values as `data-service-id`, `data-merchant-id`,
`data-transaction-param`, `data-merchant-user-id`, `data-amount`, `data-card-type`, plus
`data-label` for the button text. `createPaymentRequest` takes them as an object with
snake_case keys (`service_id`, `merchant_id`, `amount`, `transaction_param`,
`merchant_user_id`, `card_type`).

`status` values returned by the widget:

| `status` | Meaning |
|---|---|
| < 0 | error |
| 0 | created |
| 1 | processing |
| 2 | paid |

## Mobile apps

- If the CLICK app is installed it opens the link; otherwise the browser does.
- After a payment the CLICK app closes itself. Refresh the order from your server when your
  app comes back to the foreground (`onStart` / `onRestart` on Android, the active-state
  callback on iOS), looking it up by `transaction_param`.
- With `return_url`, the app opens that URL (`ACTION_VIEW`) after success or error. Bind it
  to an Activity or a Universal Link / custom scheme.
- A native Android SDK exists: `github.com/click-llc/android-msdk`. Merchants that have
  their own billing still implement the SHOP API on the server.

## Gotchas

1. `return_url`, the posted `status` and the widget callback come from the payer's browser
   and can be forged or lost. Never mark an order paid on them. Wait for SHOP API Complete,
   or check with `payment/status_by_mti`.
2. `amount` must be `N.NN`. Format it with two decimals and a dot, without thousands
   separators.
3. The amount in the link is only what the payer sees. Your Prepare handler must still
   compare it with the order total, because anyone can edit a URL.
4. One `transaction_param` per order. If an order can be paid more than once (a top-up
   account), your Prepare logic decides whether to accept a repeat.
5. The vendor's form sample puts `uzcard/humo` into `card_type`. The valid values are
   `uzcard` or `humo`; leave the field out to allow both.
6. The widget script is loaded from `my.click.uz`. If you use a Content Security Policy,
   allow `https://my.click.uz` in `script-src`.

## Examples

- [`payment-link.request.json`](examples/payment-link.request.json): the link parameters.
  The resulting URL is
  `https://my.click.uz/services/pay?service_id=100&merchant_id=1&amount=25000.00&transaction_param=100001&return_url=https%3A%2F%2Fmerchant.example.com%2Forders%2F100001`.
- [`create-payment-request.request.json`](examples/create-payment-request.request.json): the
  object passed to `createPaymentRequest`.
