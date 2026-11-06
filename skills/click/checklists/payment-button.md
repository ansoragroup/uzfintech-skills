# Checklist: Click payment link, button, widget and deeplink

Contracts: [`../references/payment-button/README.md`](../references/payment-button/README.md)
and [`../references/shop-api/README.md`](../references/shop-api/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Parameters
- [ ] `merchant_id`, `service_id`, `transaction_param` and `amount` are always sent.
- [ ] `amount` is formatted `N.NN` with a dot and no thousands separators.
- [ ] `transaction_param` is the order id that the SHOP API receives as `merchant_trans_id`.
- [ ] `card_type` is `uzcard`, `humo` or absent, never `uzcard/humo`.
- [ ] `return_url` is URL-encoded and points to a page that reads the status from your server.

## Trust
- [ ] The order is marked paid only by SHOP API Complete or a Merchant API status call.
- [ ] `return_url`, the posted `status` and the widget callback only refresh the UI.
- [ ] Prepare compares the amount with the order total, since the link can be edited.

## Widget and mobile
- [ ] `checkout.js` loads from `https://my.click.uz`, allowed by any Content Security Policy.
- [ ] The app refreshes the order from your server when it returns to the foreground.
- [ ] Deeplinks fall back to the browser when the CLICK app is missing.
- [ ] On a mobile website the payment link opens with a same-tab top-level navigation from
  the payer's tap, never `window.open`, an iframe or `fetch`.
- [ ] The return or pending page re-reads the status on `pageshow` (back/forward cache) and
  `visibilitychange`, and an older status reply cannot overwrite a newer one.
