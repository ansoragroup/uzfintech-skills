---
type: regex
pattern: 'reason[^\n]{0,40}\b4\b|\b4\b[^\n]{0,40}reason'
match: contains
weight: 2
---
Cancels the stale transaction with reason 4.
