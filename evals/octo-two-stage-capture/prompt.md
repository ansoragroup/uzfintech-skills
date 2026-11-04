---
name: octo-two-stage-capture
max_turns: 12
timeout_seconds: 300
tags: [octo, lifecycle]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
We are moving checkout to Octo. Our items are made to order, so we want to block the money
on the card when the customer pays and charge it only after the workshop confirms the
order, usually one or two days later. Which calls do we make, and in what order? Keep it
short.
