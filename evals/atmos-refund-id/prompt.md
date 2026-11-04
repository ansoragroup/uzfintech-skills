---
name: atmos-refund-id
max_turns: 12
timeout_seconds: 300
tags: [atmos, lifecycle]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
We take Uzcard and Humo cards through Atmos. On checkout we call `pay/create` and keep the
`transaction_id` it returns on the order; the payer then finishes with the SMS code. Support
now wants a "Refund" button for paid orders. Is this handler fine? Keep it short.

```python
def refund(order):
    r = atmos.post("/merchant/pay/reverse", json={
        "transaction_id": order.atmos_transaction_id,
        "reason": "Refund requested by support",
    })
    return r.json()["result"]["code"] == "OK"
```
