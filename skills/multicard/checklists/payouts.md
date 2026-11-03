# Checklist: Multicard Payouts and Reports

Contracts: [`../references/payouts/README.md`](../references/payouts/README.md),
[`../references/reports/README.md`](../references/reports/README.md). Also run
[`common.md`](common.md).

## Payouts
- [ ] The wallet balance (`GET /payment/application`, `wallet_sum`) is checked before a payout.
- [ ] `POST /payment/credit` sends `card` (`pan` or `token`, Uzcard or Humo), tiyin `amount`, `store_id` as a **string**, `invoice_id` and `device_details` (`ip`, `user_agent`).
- [ ] `confirmable` is sent explicitly; with `true`, the payout is finished with `PUT /payment/credit/{uuid} {otp}`.
- [ ] `kyc_data` with all seven fields is sent for amounts above 10 000 000 UZS (1 000 000 000 tiyin); the threshold is compared in one unit.
- [ ] `kyc_data` in the answer is parsed as a JSON string; it is kept out of logs.
- [ ] `ERROR_UNKNOWN` or a timeout leads to polling `GET /payment/credit/{uuid}`; a payout is never resent with the same body.
- [ ] `ERROR_CARD_NOT_FOUND` asks the user for another card.

## Reports
- [ ] Store fiscal settings (`GET /payment/store/{uuid}`, `tax_registration`, `tax_mxik`, `tax_package_code`) are read per cashbox and drive the `ofd` logic.
- [ ] Registries send `offset`, `limit`, `start_date` and `end_date` in GMT+5, plus `only_status` on the payout registry, and page until `total` is reached.
- [ ] Daily reconciliation compares the registry with your own records and flags differences.
- [ ] `403 ERROR_ACCESS_DENIED` (another store's registry) is treated as a configuration error.
