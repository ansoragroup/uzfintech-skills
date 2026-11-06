# Checklist: BTS quote and order

Contract: [`../references/order/README.md`](../references/order/README.md),
[`../references/quote/README.md`](../references/quote/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Quote

- [ ] The weight is sent in kilograms, rounded to one decimal, at least 0.1 (`bts.weight-in-kg`)
- [ ] Only pairs with `available: true` are offered
- [ ] Prices come from the API, never from hard-coded tariffs

## Create

- [ ] `order/add` is never resent blindly after a timeout or 5xx (`bts.no-blind-retry-create`)
- [ ] Phones are sent as `+998` and nine digits (`bts.phone-format`)
- [ ] Each item has its own `goods` line with an MXIK code, amount and price (`bts.mxik-per-item`)
- [ ] `orderId`, `barcode` and `cost` from the reply are stored on the order
- [ ] The sticker is fetched after create, and a sticker failure does not fail the order (`bts.sticker-after-create`)

## Cancel and track

- [ ] Cancel is offered only while the code is 100 (`bts.cancel-only-new`)
- [ ] `400 error.already_cancelled` is treated as success
- [ ] Track uses `status.code` and handles `404`
