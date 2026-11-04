# Checklist: Oson go-live

Contracts: [`../references/lifecycle/README.md`](../references/lifecycle/README.md),
[`../references/sandbox/README.md`](../references/sandbox/README.md). Mark each item
pass / fail / n.a. and cite the evidence.

## Confirm with Oson in writing
- [ ] The current API description: required fields, limits and error codes (`oson.unverified-contract`).
- [ ] Which host serves your merchant id (`oson.host-from-config`).
- [ ] The `lifetime` unit and maximum, and the `amount` format (`oson.lifetime-unit`, `oson.amount-major-units`).
- [ ] The expected answer to the notification, retries and source IPs.
- [ ] How refunds work and who issues fiscal receipts (`oson.no-refund-api`).

## Environment
- [ ] `merchant_id` and `token` for production are in the secret store, not in code or images.
- [ ] The notify URL is set in the business cabinet and reachable over HTTPS from the internet.
- [ ] There is no test mode, so a staff account makes one small real payment end to end before launch and the refund path for it is agreed with Oson (`oson.no-test-mode`).

## Monitoring
- [ ] Alerts fire on signature mismatches, unknown `transaction_id` values and invoices stuck in `REGISTRED` or `ON_PROGRESS` past their lifetime.
- [ ] Logs keep `transaction_id`, `bill_id`, `status`, `error_code` and `message`, never the token.
