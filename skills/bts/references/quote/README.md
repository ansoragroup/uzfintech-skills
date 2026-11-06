# BTS quote (`order-calculate/index`): delivery price

Hand-written notes. Transport, auth and errors: [`../common/README.md`](../common/README.md).
City codes: [`../directory/README.md`](../directory/README.md). Schemas: [`schemas/`](schemas/).
Examples: [`examples/`](examples/).

- Source: https://docs.bts.uz/page/order-calculator
- Fetched: 2026-11-06

## Fields

| Field | Required | Notes |
|---|---|---|
| `senderCityCode` | yes | string city code, e.g. `"1001"` |
| `receiverCityCode` | yes | string city code, e.g. `"7001"` |
| `pickup_type` | yes | `courier`, `branch` or `self` |
| `dropoff_type` | yes | `courier`, `branch` or `self` |
| `is_multiple_cost` | no | `1` returns all four pairs |
| `weight` | yes | kilograms, float (`bts.weight-in-kg`) |
| `volume` | no | `{x, y, z}` in centimetres |

The reply `data` has `branch_to_branch`, `branch_to_courier`, `courier_to_branch` and
`courier_to_courier`, each `{available, price, reason}`. Show only pairs with
`available: true`; `reason` explains the others.

## Rules

- Door delivery is `courier`, a pickup point is `branch`.
- Weight: grams / 1000, rounded to one decimal, at least `0.1`.
- Quote at checkout and store the price with the order; the price on `order/add` may still
  differ, so read `cost` from its reply.
- A bad city code answers `422` `error.validation`.
- Prices come from this call only. Never hard-code or estimate tariffs.
