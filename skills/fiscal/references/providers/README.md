# Fiscal fields per provider

Hand-written notes. One table to map a catalogue item to each provider's receipt line. Each
row links the provider's own reference page, which holds the full field list, the exact
vendor samples and that provider's warnings. Concepts: [`../mxik/`](../mxik/README.md),
[`../receipt-line/`](../receipt-line/README.md), [`../receipts/`](../receipts/README.md).

- Source: the provider references linked in each row (each lists its vendor URLs)
- Fetched: 2026-11-04

## Mapping

| Provider | Who registers | MXIK | Package code | VAT | Marking | Refund receipt | Deadline |
|---|---|---|---|---|---|---|---|
| [Payme](../../../payme/references/fiscalization/README.md#detail-object) | Payme from `detail`; or your module + `receipts.set_fiscal_data` | `items[].code` | `package_code` (required, also for services) | `vat_percent` (required) | none documented | `SetFiscalData` `CANCEL` (Payme) | none published |
| [Click](../../../click/references/fiscalization/README.md#submit-items-fields) | Click (`submit_items`) or you (`submit_qrcode`), one per payment | `SPIC` (max 17) | `PackageCode` (required, max 20) | `VATPercent` + `VAT` amount (required) | `Labels` (up to 300) | no API | after `payment_status` `2`; none published |
| [Uzum Fiscalization](../../../uzum/references/fiscalization/README.md#v2receipt-request) | you, through the Fiscalization API (`/v2/receipt`) | `spic` (required) | `package_code` (required) | `vat_percent` (required) | `labels` (marked goods) | `/v2/refund_receipt`, sale must be fiscalized | `date_time` within 24 h |
| [Uzum Checkout](../../../uzum/references/checkout/README.md) | Uzum if auto-fiscalization is on; else Uzum Fiscalization | `receiptParams.spic` | `receiptParams.packageCode` | `receiptParams.vatPercent` | `receiptParams.labels[]` | `REFUND` (needs refund `cart`, `3045`) | none published |
| [Alif](../../../alif/references/payments/README.md#payment-struct) | Alif when asked (`receipt: true` / `receipt{}`); or you + `registerReceipt` | `spic` | not documented | `vat_percent` | `marking_code` (some IKPU codes) | on full refund, only if a sale receipt exists | none published |
| [Multicard](../../../multicard/references/common/README.md#fiscal-items-ofd) | store `tax_registration`: `1` Multicard, `0` you | `mxik` (required) | `package_code` (required) | `vat` | `mark` (one per unit) | `refund_tax`; partial refund sends new `ofd` | none published |
| [Octo](../../../octo/references/fiscal/README.md#basket-item) | Octo from `basket`; items pre-registered by the bank manager | `spic` | `package_code` (required) | `nds` (`1` / `0`) | none documented | not documented | none published |
| [Paynet](../../../paynet/references/lifecycle/README.md#fiscal-receipts) | not documented | none published | none published | none published | none published | not documented | none published |
| [Atmos](../../../atmos/references/common/README.md#fiscal-items) | Atmos when lines are sent (derived from `ofd_url`) | `ofd_code`, and `details` key `mxik_code` | `details` key `package_code` | none documented | `details` key `mark_code` | partial reversal takes `ofd_items`; full not described | none published |

"Required" means the provider marks it required; an empty cell in the provider's own
reference means it says nothing. Every provider here types MXIK and package code as
strings.

## Provider warnings to raise with these fields

| Provider | Warnings |
|---|---|
| Payme | `payme.detail-unit-price`, `payme.no-second-receipt`, `payme.cancel-is-the-refund` |
| Click | `click.one-fiscal-receipt`, `click.no-refund-receipt-api` |
| Uzum | `uzum.fiscal-receipt-24h`, `uzum.fiscal-refund-needs-sale`, `uzum.checkout-fiscal-owner` |
| Alif | `alif.amount-equals-items`, `alif.refund-receipt-needs-sale-receipt` |
| Multicard | `multicard.one-fiscalizer`, `multicard.partial-refund-new-receipt` |
| Octo | `octo.fiscal-registered-items`, `octo.test-flag-real-money` |
| Paynet | `paynet.fiscal-owner-unknown` |
| Atmos | `atmos.fiscal-items` |

## One catalogue record, many providers

Keep the fiscal values per catalogue item once, as text, and map them per provider at the
edge. A shape that covers every row above (field names are yours to choose):

```text
mxik            "04016001002000000"   17 digits, string
package_code    "1342705"             from the code's Tasnif card, string
vat             <rate from the seller's tax settings>
marking         true / false          scanned codes are per sold unit, not per product
principal       TIN (9) or PINFL (14), only for agent sales
```

- Convert prices at the edge: tiyin for everyone except Octo (major units), and check whether
  the provider wants the unit price, the line total, or both
  ([`../receipt-line/`](../receipt-line/README.md#quantity-and-price)).
- Provider-specific extras stay in the provider adapter: Click `VAT` amount, Octo product
  registration, Multicard store defaults `tax_mxik` / `tax_package_code`, Atmos `details`
  key-value pairs.
