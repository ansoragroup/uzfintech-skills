# Choosing and combining providers: traps, deadlines, refunds and retries

Read this when choosing a provider, comparing providers, or putting several behind one
checkout. Raise these traps before shared code moves money: units, callback answers,
refund rules, hold windows, retries, test hosts and QR products all differ per provider, and
a rule copied from one provider breaks another. Each item points to the provider rules it
summarises; the provider's own lifecycle page is the contract.

- Source: the provider lifecycle pages linked in each item, the
  [features table](../providers/README.md#features) and the [cheatsheet](../cheatsheet/README.md)
- Fetched: 2026-11-04

## Warn without being asked

1. **`uzfintech.one-provider-at-a-time`**: when one question or one code path covers two or
   more providers → load each provider's skill and answer for each one separately. Field
   names, units, auth, retry and refund rules never carry over; the router tables only say
   whether a feature exists and where to read about it.
   [providers](../providers/README.md#features)
2. **`uzfintech.units-differ-per-provider`**: when one amount helper feeds several providers
   → Payme, Uzum, Alif, Multicard, Atmos and Paynet take integer tiyin; Click takes soum,
   with tiyin only in fiscal data (`click.soums-vs-tiyin`); Octo takes decimal major units;
   Oson takes soum (`oson.amount-major-units`); Kapitalbank states no unit
   (`kapitalbank.amount-units-unstated`). Convert inside each provider's adapter, never in
   shared code. [cheatsheet](../cheatsheet/README.md#units-auth-and-callbacks)
3. **`uzfintech.callback-answers-differ`**: when one endpoint or handler receives several
   providers' callbacks → the expected answer differs, and a wrong one costs money: Payme
   wants HTTP 200 even for errors (`payme.http-200-always`), the Uzum Merchant API wants
   HTTP 400 for a business error, Multicard refunds unless the success callback gets
   `{"success": true}` (`multicard.callback-reject-refunds`), Atmos does not debit without
   `{"status": 1}` (`atmos.callback-ack`), and Alif cancels and refunds after about an hour
   without a 200 (`alif.webhook-1h-auto-refund`). Give each provider its own route,
   signature check and answer. [cheatsheet](../cheatsheet/README.md#units-auth-and-callbacks)
4. **`uzfintech.http-200-is-not-success`**: when one HTTP client calls several providers →
   some return errors inside HTTP 200 (`alif.error-is-http-200`,
   `kapitalbank.error-in-http-200`), and Paynet's top-level `status` only says the call
   worked (`paynet.success-only-paid`). Check the body field each provider's skill names.
5. **`uzfintech.redirect-is-not-payment`**: when checkout sends the payer back to your site →
   the return proves nothing at any provider here. Mark paid only on the provider's
   confirmed callback or status read (`payme.return-url-not-proof`,
   `click.return-url-not-proof`, `oson.status-before-shipping`; Octo says the same of
   `return_url` in its [rules](../../../octo/SKILL.md#rules-that-apply-everywhere)).
6. **`uzfintech.read-state-before-resend`**: when a money call times out or answers an
   unknown state → read that payment's state at the same provider and never send the money
   call again (`multicard.never-resend-money-calls`, `atmos.apply-no-resend`,
   `paynet.unknown-state-poll`, `kapitalbank.poll-status-not-resend`). How you read it back
   and which ids you reuse differ per provider. [retries](#retries-and-idempotency)
7. **`uzfintech.refund-rules-differ`**: when one refund button serves several providers →
   Payme, Click and Paynet refund only the full amount, Alif too except instalments; Click
   only within the current reporting month (`click.reversal-month-window`), Paynet within 1
   month (`paynet.reverse-1-month`); Oson has no refund method (`oson.no-refund-api`); the
   Uzum Merchant API gives you no refund call (`uzum.merchant-no-refund-api`). Offer partial
   refunds per provider, never globally. [refunds](#cancel-reverse-and-refund)
8. **`uzfintech.hold-windows-differ`**: when one pre-auth flow serves several providers →
   expiry is set differently at each: Payme and Alif in days per card scheme, Multicard and
   Atmos in minutes you choose, Octo by shop setting with 30 minutes as the safe default;
   Uzum publishes none; Click, Paynet and Oson publish no hold at all. Capture before each
   provider's own window. [deadlines](#deadlines-and-windows)
9. **`uzfintech.test-money-differs`**: when testing → only Payme, Alif, Multicard, Uzum
   Checkout and Uzum Fiscalization publish test hosts. Octo tests on the production host
   with `test: true` and moves real money without it (`octo.test-flag-real-money`); Atmos
   publishes a test page and widget but no API test host; Click, Paynet, Oson and
   Kapitalbank publish none (`oson.no-test-mode`,
   `kapitalbank.host-and-sandbox-not-published`). Never label a production host as a
   sandbox in config. [cheatsheet](../cheatsheet/README.md#refunds-holds-receipts-and-test-hosts)
10. **`uzfintech.qr-products-differ`**: when the task says "QR payment" → ask which one: the
    payer's app QR scanned at the till (CLICK Pass, Uzum FastPay, Multicard scanpay), a QR
    the merchant shows (Uzum Dynamic QR, alif mobi QR, Payme `Paycom.QR`), the national
    UzQR, or Rahmat on restaurant pre-checks. UzQR and Rahmat have no public developer API
    in these sources; do not invent endpoints, and do not attribute Rahmat to any provider.
    [QR payments](../providers/README.md#qr-payments)

## Deadlines and windows

| What | Window | Source |
|---|---|---|
| Payme Merchant API transaction in state `1` | cancelled 12 h after the Payme `time` (`payme.create-timeout-12h`) | [payme](../../../payme/references/lifecycle/README.md#warn-without-being-asked) |
| Payme hold | Uzcard released after 30 days; Humo confirm or cancel within 30 days (`payme.hold-30-days`) | [payme](../../../payme/references/lifecycle/README.md#warn-without-being-asked) |
| Alif hold | Humo 10 days, Uzcard 30 days (`alif.hold-expiry-10-30-days`) | [alif](../../../alif/references/lifecycle/README.md#warn-without-being-asked) |
| Multicard hold | `expiry` 1..43200 minutes (`multicard.hold-expiry-minutes`) | [multicard](../../../multicard/references/lifecycle/README.md#warn-without-being-asked) |
| Atmos hold | `duration` in minutes; the longest is not published (`atmos.hold-expiry`) | [atmos](../../../atmos/references/lifecycle/README.md#warn-without-being-asked) |
| Octo two-stage hold | 30 minutes on the two-stage pages; longer only by shop setting (`octo.hold-auto-cancel`) | [octo](../../../octo/references/lifecycle/README.md#warn-without-being-asked) |
| Alif webhook delivery | retried about 1 h, then cancelled and refunded (`alif.webhook-1h-auto-refund`) | [alif](../../../alif/references/lifecycle/README.md#warn-without-being-asked) |
| CLICK Pass confirmation | 30 seconds (`click.pass-confirm-30s`) | [click](../../../click/references/lifecycle/README.md#warn-without-being-asked) |
| Click reversal | current reporting month; last month's only on the first day of the next (`click.reversal-month-window`) | [click](../../../click/references/lifecycle/README.md#warn-without-being-asked) |
| Paynet reverse | 1 month after the payment (`paynet.reverse-1-month`) | [paynet](../../../paynet/references/lifecycle/README.md#warn-without-being-asked) |
| Uzum Fiscalization sale receipt | within 24 h after the confirmed payment (`uzum.fiscal-receipt-24h`) | [uzum](../../../uzum/references/lifecycle/README.md#warn-without-being-asked) |
| Auth tokens | Atmos Bearer 3600 s by the text (`atmos.access-token-1h`); Multicard 24 h (`multicard.token-24h`) | [atmos](../../../atmos/references/lifecycle/README.md#warn-without-being-asked), [multicard](../../../multicard/references/lifecycle/README.md#warn-without-being-asked) |

Every other provider window lives on that provider's lifecycle page, under "Deadlines and
windows".

## Cancel, reverse and refund

| Provider | Rule | Source |
|---|---|---|
| Payme | `CancelTransaction` / `receipts.cancel` is the refund, full only (`payme.cancel-is-the-refund`) | [payme](../../../payme/references/lifecycle/README.md#cancel-reverse-and-refund) |
| Click | `payment/reversal`, full, current reporting month (`click.reversal-month-window`) | [click](../../../click/references/lifecycle/README.md#cancel-reverse-and-refund) |
| Uzum | Checkout: TWO_STEP reverse, ONE_STEP refund only (`uzum.checkout-stale-authorized`); Merchant API: Uzum calls your `/reverse` (`uzum.merchant-no-refund-api`) | [uzum](../../../uzum/references/lifecycle/README.md#cancel-reverse-and-refund) |
| Alif | full only; partial for instalments (`alif.refund-full-only`) | [alif](../../../alif/references/lifecycle/README.md#cancel-reverse-and-refund) |
| Paynet | `reverse`, full, within 1 month (`paynet.reverse-1-month`) | [paynet](../../../paynet/references/lifecycle/README.md#cancel-reverse-and-refund) |
| Multicard | full and partial, partial after Multicard enables it | [multicard](../../../multicard/references/lifecycle/README.md#cancel-reverse-and-refund) |
| Atmos | `pay/reverse` by `success_trans_id`; partial needs a confirm (`atmos.reverse-success-id`, `atmos.partial-reverse-confirm`) | [atmos](../../../atmos/references/lifecycle/README.md#cancel-reverse-and-refund) |
| Octo | cancel only holds; `/refund` for paid payments, with limits (`octo.cancel-only-holds`, `octo.refund-limits`) | [octo](../../../octo/references/lifecycle/README.md#cancel-reverse-and-refund) |
| Oson | no API method (`oson.no-refund-api`) | [oson](../../../oson/references/lifecycle/README.md#cancel-reverse-and-refund) |
| Kapitalbank | no recall method published for a sent payment order; ask the bank | [kapitalbank](../../../kapitalbank/references/lifecycle/README.md#cancel-reverse-and-refund) |

## Retries and idempotency

- **Your calls to a provider**: store your own id before the call, and after a timeout read
  the state back with the same provider's status call before any retry
  (`alif.persist-id-first`, `uzum.checkout-operation-id`,
  `multicard.never-resend-money-calls`, `atmos.apply-no-resend`,
  `paynet.unknown-state-poll`, `kapitalbank.poll-status-not-resend`).
- **Provider calls to you**: repeats of the same transaction must get the stored answer and
  never a second fulfilment (`payme.idempotent-replays`, `click.idempotent-retries`).
- **Mixed checkout**: keep one payment record per provider attempt, keyed by that provider's
  id. A payer who switches provider starts a new attempt; do not reuse ids across providers.
  This is derived from the per-provider rules above.

## Fiscal receipts

Who registers the receipt is in the last column of the
[features table](../providers/README.md#features); the fields per provider are in the
[fiscal skill](../../../fiscal/SKILL.md) and its
[providers table](../../../fiscal/references/providers/README.md#mapping). One payment gets one
sale receipt, never one from the provider and one from you (`fiscal.one-receipt-per-payment`).
Paynet does not say who registers receipts (`paynet.fiscal-owner-unknown`); Oson does not say
either, so register them yourself until it confirms; Kapitalbank moves bank transfers, not
card sales.

## Not documented — ask the provider

- **Paynet**: who registers fiscal receipts; any test host.
- **Oson**: a published API reference (its contract is rebuilt from plugins), a refund
  method, and the body its notification expects back.
- **Octo**: the answer body for `notify_url`, and your shop's hold window.
- **Kapitalbank**: the amount unit, the API host and a sandbox.
- **Atmos**: an API test host.
- **Click, Paynet, Oson**: holds or pre-authorisation.
- **Uzum**: the Checkout TWO_STEP hold expiry, and test data for the Merchant API.
- **UzQR**: a developer API; ask the merchant's bank or provider how it issues a code and
  reports its payments.
- **Rahmat**: a developer API and the company that runs it.
- **Every provider**: commercial terms. They differ per merchant contract; this plugin does
  not record or compare them.
