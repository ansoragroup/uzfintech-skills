---
name: octo-notify-handler
max_turns: 12
timeout_seconds: 300
tags: [octo, lifecycle]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
Write a small Express (Node.js) route for the `notify_url` we pass to Octo in
`prepare_payment`. When Octo says the payment went through, mark our order as paid with
`orders.markPaid(shopTransactionId)`. Just the code and one or two lines of notes.
