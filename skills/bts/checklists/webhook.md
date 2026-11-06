# Checklist: BTS webhook

Contract: [`../references/webhook/README.md`](../references/webhook/README.md). Mark each
item pass / fail / n.a. and cite the file and line that proves it.

## Authenticity

- [ ] The token is read from the `itx-apiKey` header, Bearer, the form field `itx-apiKey` or the form field `token`, in that order (`bts.webhook-token-check`)
- [ ] The token is compared in constant time; the previous token is accepted during rotation
- [ ] A mismatch answers `401` and changes nothing

## Parsing

- [ ] The form-data field that holds JSON is found and parsed (`bts.webhook-form-json`)
- [ ] Strings are trimmed
- [ ] The status comes from `status.code`, never `status.id * 100` (`bts.status-code-not-id`)
- [ ] Unparseable input answers `400`

## Idempotency

- [ ] Duplicates are dropped on `orderId:code:date`
- [ ] A repeat answers `200` without changing anything
- [ ] Unknown codes are stored and logged, not rejected (`bts.undocumented-codes`)
