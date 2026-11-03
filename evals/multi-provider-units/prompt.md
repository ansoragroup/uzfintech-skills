---
name: multi-provider-units
max_turns: 12
timeout_seconds: 300
tags: [payme, click, router]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
We take payments through both Payme (Merchant API) and the Click SHOP API. A product costs
15 000 UZS. What exact `amount` value does each provider send us for it, and in what format?
