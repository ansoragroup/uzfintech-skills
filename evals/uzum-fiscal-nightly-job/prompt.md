---
name: uzum-fiscal-nightly-job
max_turns: 12
timeout_seconds: 300
tags: [uzum, fiscalization, lifecycle]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
We take payments through the Uzum Merchant API (webhooks). Sketch a nightly job, run at
03:00 Tashkent time, that sends Uzum Fiscalization receipts for all of yesterday's
confirmed payments. Pseudocode is fine.
