---
type: llm
weight: 2
---
Passes when the answer says not to resend `pay/apply` after a timeout (it moves money and a
second call can debit twice or fail), and to read the transaction state instead. Fails when
the answer proposes backoff values for repeating `pay/apply` without that warning. Extra
detail, such as retrying the read itself with backoff, still passes.
