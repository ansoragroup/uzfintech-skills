# Checklist: BTS go-live

Contracts: [`../references/common/README.md`](../references/common/README.md),
[`../references/sandbox/README.md`](../references/sandbox/README.md),
[`../references/lifecycle/README.md`](../references/lifecycle/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Confirm with BTS in writing

- [ ] The production base URL and port
- [ ] The webhook retry policy and timeout
- [ ] The meaning of codes 900, 1000, 1300 and 1400
- [ ] Who issues the fiscal receipt for cash on delivery
- [ ] `package_id` and `post_type_id` for your account

## Environment

- [ ] The full simulator path (100 → 1200) passed on the test host, with the webhook registered as `environment: "test"` (`bts.test-env-webhook`)
- [ ] Production credentials and `webhook_token` are in the secret store, not in code
- [ ] The webhook is registered with `environment: "production"` and the production URL
- [ ] The sender fields are set before BTS is turned on at checkout

## Monitoring

- [ ] Alerts fire on repeated `401` logins and on 5xx bursts
- [ ] Orders flagged after a failed `order/add` are reviewed every day
- [ ] Unknown status codes are logged and reported
