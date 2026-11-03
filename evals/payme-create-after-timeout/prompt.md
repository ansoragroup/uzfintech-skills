---
name: payme-create-after-timeout
max_turns: 12
timeout_seconds: 300
tags: [payme, merchant]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
Payme just sent `CreateTransaction` for a transaction id we first saw 13 hours ago; it is
still in state 1 in our database. What exactly do we answer, and what should we have done
with that transaction earlier? Keep it short.
