---
type: regex
pattern: '(?i)sha-?1'
match: contains
weight: 2
---
Computes the signature as sha1 over `unique_key`, `octo_payment_UUID` and `status`.
