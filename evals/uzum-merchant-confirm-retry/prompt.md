---
name: uzum-merchant-confirm-retry
max_turns: 12
timeout_seconds: 300
tags: [uzum, merchant]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
We implement the Uzum Bank Merchant API webhooks. Our `/confirm` handler sometimes times out
after it already marked the order paid. What does Uzum do next, and what must `/status` and a
repeated `/confirm` return? Also, what type is `errorCode`?
