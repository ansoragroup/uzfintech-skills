---
name: oson-notify-handler
max_turns: 12
timeout_seconds: 300
tags: [oson, lifecycle]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
We take payments through Oson (invoice/create, the payer pays on their page). Write a small
PHP endpoint for the notification Oson posts to us after payment, modelled on their 1C-Bitrix
module: when the status says the order is paid, call `markPaid($transactionId)`. Just the
code and one or two lines of notes.
