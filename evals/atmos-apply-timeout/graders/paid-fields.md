---
type: regex
pattern: 'success_trans_id|confirmed'
match: contains
weight: 2
---
Decides "paid" on `confirmed` and `success_trans_id`, not on the result code alone.
