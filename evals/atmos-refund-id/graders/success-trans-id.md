---
type: regex
pattern: 'success_trans_id'
match: contains
weight: 3
---
Says `pay/reverse` takes the `success_trans_id` of the paid transaction, not the draft
`transaction_id` from `pay/create`.
