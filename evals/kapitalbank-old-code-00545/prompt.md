---
name: kapitalbank-old-code-00545
max_turns: 12
timeout_seconds: 300
tags: [kapitalbank, purpose-codes]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
We pay a supplier through the Kapitalbank corporate API (SendPaymentIBK) for aluminium
bathroom mixers. Our ERP still fills `purp_code` with 00545. Which `purp_code` do we send
now, and what should the `purpose` text say? The contract is No. 100001 of 03.11.2026 and
this is the full payment.
