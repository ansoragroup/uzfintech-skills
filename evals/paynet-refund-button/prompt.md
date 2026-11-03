---
name: paynet-refund-button
max_turns: 12
timeout_seconds: 300
tags: [paynet, lifecycle]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
Add a "Refund" button to our admin order page for orders paid by card through Paynet
acquiring. Support should be able to use it on any paid order. Which call does it make,
and what should the button handle? Keep it short.
