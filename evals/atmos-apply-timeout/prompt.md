---
name: atmos-apply-timeout
max_turns: 12
timeout_seconds: 300
tags: [atmos, lifecycle]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
Our Atmos card payments sometimes hang on `pay/apply` after the payer types the SMS code,
and our HTTP client gives up after 30 seconds. Right now we just show an error. I want to
wrap that call in a retry with exponential backoff, up to three attempts with the same
body. What backoff values would you pick? Keep it short.
