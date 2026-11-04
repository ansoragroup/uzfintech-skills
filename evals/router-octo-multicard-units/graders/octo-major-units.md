---
type: regex
pattern: 'total_sum[^\n\d]{0,40}49[ ,]?000(\.0+)?(?![\d])'
match: contains
weight: 3
---
Octo `total_sum` is 49000 in major units (for example `49000.0`), not the tiyin value.
