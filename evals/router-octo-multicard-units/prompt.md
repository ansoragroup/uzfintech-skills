---
name: router-octo-multicard-units
max_turns: 12
timeout_seconds: 300
tags: [octo, multicard, router]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
Our shop already takes payments with Multicard invoices: a `toMinor(amountUzs)` helper fills
`amount` in create-invoice. We are adding the Octo payment page as a second option and plan
to reuse the same helper for `total_sum` in prepare_payment. An order is 49 000 UZS. What
exactly goes in Multicard's `amount` and in Octo's `total_sum`? Keep it short.
