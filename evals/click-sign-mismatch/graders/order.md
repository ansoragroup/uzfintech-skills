---
type: regex
pattern: 'service_id[^\n]{0,40}(secret|SECRET)[^\n]{0,40}merchant_trans_id'
match: contains
weight: 2
---
Puts the secret between `service_id` and `merchant_trans_id`.
