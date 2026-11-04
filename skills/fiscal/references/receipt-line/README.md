# One receipt line: package code, unit, price, VAT, benefit, marking, principal

Hand-written notes. A fiscal receipt line carries more than the MXIK code
([`../mxik/`](../mxik/README.md)). This page explains each extra value in provider-neutral
terms and points to the field that carries it; the full per-provider table is in
[`../providers/`](../providers/README.md).

- Source: the Tasnif replies in [`../sandbox/`](../sandbox/README.md); the tax committee's
  digital-marking page https://gov.uz/ru/soliq/activity_page/raqamli-markirovka; the
  provider references linked in each row
- Fetched: 2026-11-04

## Package code and unit

The package code says **in what package or unit the quantity on the line is counted** for
that MXIK. It is not your SKU, barcode or warehouse unit.

- Each MXIK has its own package list on its Tasnif card (`packages[]` in the by-mxik reply).
  In the sample, code `04016001002000000` lists `1342705` (`шт.`, the plain unit,
  `isUnitPackage` `"1"`) and `1659249` (`пакет` holding 1 `шт.`, `parentCode` `1342705`).
- Pick the package that matches how the line counts: if the line sells 3 pieces, use the
  piece package with quantity 3 (derived from the package fields; confirm with the
  accountant when a product is sold in several packings).
- A package code is only valid together with its own MXIK. Copying one product's package code
  to another product is a common cause of rejected items (Uzum Fiscalization answers 400
  `code` `1` for an invalid SPIC or package; Uzum Checkout answers `3055`).
- Providers declare it as a **string** (Payme `package_code`, Click `PackageCode` max 20,
  Uzum `package_code` / `packageCode`, Multicard `package_code`, Octo `package_code`, Atmos
  `details` key `package_code`); Tasnif returns it as a number. Convert once, store text.
- It is required wherever it is documented, including for services (Payme says so
  explicitly). Alif documents no package-code field; Paynet publishes no receipt fields.
  Warning [`fiscal.package-code-required`](../lifecycle/README.md#warn-without-being-asked).
- A separate **unit code** exists at two providers: Payme `units` (optional number) and
  Click `Units` (optional). The references do not say where the numbers come from; the
  Tasnif reply carries `unitCode` / `unitName` per code (`null` in the sample) and `unitId`
  per package. Leave the unit field out unless the provider tells you its value.

## Quantity and price

Providers disagree about whether `price` is per unit or per line, and about the money unit.
This is the most common silent mismatch when one catalogue feeds several providers.
Warning [`fiscal.price-semantics-differ`](../lifecycle/README.md#warn-without-being-asked).

| Provider | Quantity | Price | Line total | Discount | Money unit |
|---|---|---|---|---|---|
| Payme `detail.items[]` | `count` | `price` per unit | not sent | `discount`, line total | tiyin |
| Click `submit_items` | `Amount` | `GoodPrice` per unit | `Price` | `Discount`, `Other` | tiyin |
| Uzum Fiscalization | `count` (fractional allowed) | `price` per unit, before discount | not sent | `discount`, `voucher`, line totals | tiyin |
| Uzum Checkout cart | `quantity` | `unitPrice` | `total` | `receiptParams.discount` | tiyin |
| Alif `receipt.items[]` | `amount` | `price` per unit | not sent | `discount`, line total | tiyin |
| Multicard `ofd[]` | `qty` (integer) | `price` per unit | `total` = `qty x price` before discounts | not in the item | tiyin |
| Octo `basket[]` | `count` | `price` per unit | not sent | not in the item | major units (`1000.0` UZS) |
| Atmos `ofd_items[]` | `details` key `quantity` | not sent | `amount`, line amount | not in the item | tiyin |

Each provider also checks the lines against the payment amount in its own way; see the
provider's fiscal page before you build the sum.

## VAT

Every provider that documents receipt lines has a VAT value per line, but the meaning
differs:

| Provider | Field | Meaning |
|---|---|---|
| Payme | `vat_percent` (required) | VAT percent for the line |
| Click | `VATPercent` (required) and `VAT` (required) | percent, and the VAT **amount** of the line in tiyin |
| Uzum Fiscalization / Checkout | `vat_percent` / `vatPercent` | integer percent |
| Alif | `vat_percent` | percent; the provider computes VAT after the discount |
| Multicard | `vat` | integer percent |
| Octo | `nds` (required) | `1` VAT included, `0` no VAT; the rate itself is registered with the product |
| Atmos | none documented | ask Atmos |
| Paynet | none published | ask Paynet |

- Which rate applies to a product, and whether the seller is a VAT payer at all, is a tax
  question for the seller's accountant. This skill does not give tax advice and does not
  list rates; take the number from the seller's tax settings, per product.
- Click is the only provider here that wants the VAT **amount**; compute it from the line
  total and the rate the seller gave you, and round as the seller's accountant says.

## Benefits (`lgota`)

The Tasnif reply carries `lgotaId` and `lgotaName` per code: a tax benefit linked to the
code (`null` in the sample). No provider reference in this repository documents a field
for a benefit on the receipt line. If a product has a benefit, ask the provider how to
send it before going live; until then do not invent a field.

## Marking codes (Asl Belgisi)

Some goods carry a digital marking code (Data Matrix) issued through the national
information system Asl Belgisi (https://aslbelgisi.uz/). The tax committee's marking page
lists these product groups with their start dates (fetched 2026-11-04; check the page for
newer groups):

| Product group | Marking since |
|---|---|
| Tobacco products | 2021-01-01 |
| Alcohol products | 2021-01-01 |
| Beer products | 2021-04-01 |
| Household appliances | 2022-04-15 |
| Medicines and medical devices | 2022-09-01 |
| Water and soft drinks | 2024-03-01 |

When a marked product is sold, the receipt line carries the scanned code of **each unit**.
Where providers put it:

| Provider | Field | Notes |
|---|---|---|
| Click | `Labels` | string array, up to 300, "marking codes for labelled goods" |
| Uzum Fiscalization | `labels` | array; mandatory for marked goods since 2024-03-01; not in the OpenAPI schema |
| Uzum Checkout | `receiptParams.labels[]` | `3055` names a wrong marking code |
| Alif | `marking_code` | 32 characters, the first 16 digits; required for some IKPU codes |
| Multicard | `mark` | array, one code per unit; required for marked goods |
| Atmos | `details` key `mark_code` | one value per line (shape for several units not described) |
| Payme | none documented | ask Payme before selling marked goods |
| Octo | none documented | ask Octo |
| Paynet | none published | ask Paynet |

- A line with quantity 3 of a marked product needs 3 codes where the field is an array
  (Click, Uzum, Multicard; derived from "one per unit"). Split lines per unit if the
  provider takes only one code per line (derived).
- Never invent or reuse marking codes; they come from scanning the unit that is sold.
- Warning [`fiscal.marked-goods-need-codes`](../lifecycle/README.md#warn-without-being-asked).

## Principal TIN / PINFL (agent and marketplace sales)

When the seller sells on behalf of someone else, several providers take the principal's
tax number on the line: Click `CommissionInfo` (`TIN` 9 or `PINFL` 14, required on every
item), Uzum `commission_info` / Checkout `TIN` or `PINFL`, Alif `tin` (9) xor `pin` (14),
Multicard `tin`, Octo `inn` (legal entity) or `pinfl` (individual entrepreneur, from
01.08.2025), Atmos PINFL items `tin`. Send exactly one of the two where the provider says
"or". Whose number goes there for your contract is a question for the provider.
