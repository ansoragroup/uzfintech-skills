---
name: alif-webhook-go
max_turns: 12
timeout_seconds: 300
tags: [alif, code]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
Write a Go HTTP handler that verifies an Alif (alifpay) payment webhook and then reads the
payment status. Keep the secret in an environment variable, and put the complete handler in
your reply.
