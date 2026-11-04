---
type: llm
weight: 3
---
The code verifies `signature` as sha256 over the lower-case hex sha256 of `token:merchant_id`,
joined with `:` to `transaction_id:bill_id:status`, and rejects the request before any state
change when it does not match. It points out that the Bitrix module skips this check instead
of copying that behaviour.
