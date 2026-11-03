# Checklist: Click fiscalization (ofd_data)

Contracts: [`../references/common/README.md`](../references/common/README.md) and
[`../references/fiscalization/README.md`](../references/fiscalization/README.md). Mark each
item pass / fail / n.a. and cite the file and line that proves it.

## Choice
- [ ] Each payment uses either `submit_items` (Click fiscalizes) or `submit_qrcode` (your own
  receipt), never both.
- [ ] Fiscalization runs only after the payment succeeded.

## submit_items
- [ ] Item keys are PascalCase and the top-level keys snake_case; no serializer renames them.
- [ ] Required item fields are present: `Name`, `SPIC`, `PackageCode`, `Price`, `Amount`,
  `VAT`, `VATPercent`, `CommissionInfo`.
- [ ] `Price` is the line total and `GoodPrice` the unit price, both integer tiyin.
- [ ] `CommissionInfo` carries exactly one of `TIN` (9) or `PINFL` (14), confirmed with Click.
- [ ] `received_ecash + received_cash + received_card` equals the payment total in tiyin.
- [ ] Field lengths hold: `Name` 63, `Barcode` 13, `SPIC` 17, `PackageCode` 20, `Labels` 300.

## Results
- [ ] `error_code` is checked; failures are logged and retried later.
- [ ] Before a retry, `GET payment/ofd_data/:service_id/:payment_id` confirms no receipt exists.
- [ ] `paymentId` / `qrCodeURL` are read as camelCase.
