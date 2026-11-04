---
type: llm
weight: 2
---
Only the status `PAID` calls `markPaid`; `ON_PROGRESS` and `REGISTRED` do not, and a repeated
`PAID` for an already-paid order does not pay it twice.
