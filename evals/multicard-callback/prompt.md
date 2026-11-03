---
name: multicard-callback
max_turns: 12
timeout_seconds: 300
tags: [multicard]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
Multicard calls our success callback after an invoice is paid. How do we verify it, and what
exactly must we answer? What happens if we answer something else?
