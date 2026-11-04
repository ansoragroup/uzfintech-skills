---
type: regex
pattern: '/prepare_payment'
match: contains
weight: 2
---
Re-reads the status with a call to `/prepare_payment` (the three-field status form) before
marking the order paid.
