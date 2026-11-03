# Uzum Ratekeeper (partner FX rates)

Hand-written notes. Generated tables: [`endpoints.md`](endpoints.md); schemas:
[`schemas/ops/`](schemas/ops/).

- Source: https://developer.uzumbank.uz/redocusaurus/ru_ratekeeper.yaml (en labels: `en_ratekeeper.yaml`)
- Fetched: 2026-11-03
- Small FastAPI service. **No `servers` block**: the host comes from onboarding.

## Auth

Header `X-API-Key: <RATEKEEPER_API_KEY>`. Your `partnerId` (uuid) goes in the body.

## Operations

| Method | Path | Request | `result` |
|---|---|---|---|
| POST | `/api/v1/partner/convert` | `partnerId`, `amount` (int, minor units), `currencyFrom`, `currencyTo` (`USD` / `RUB` / `EUR` / `UZS`), `direction` `TO_UZ` / `FROM_UZ`, `ips?` | `currencyFrom`, `currencyTo`, `rate` (**string** decimal), `amountFrom`, `amountTo` |
| POST | `/api/v1/partner/limits` | `amount`, `currencyTo` `USD` / `EUR`, `rateType` | `amountFrom`, `amountTo`, `currencyTo` |

Envelope `{code, message, result}`; `result` may be `null` on failure. 422 is FastAPI
validation (`detail[]`).

## Codes

The `code` enum is `0, 1000, 2000, 3000, 3001, 3002, 3003, 3004, 5000, 5001`. Only `0`
(success) has a published meaning; treat anything else as failure and log `message`.

## Gotchas

- Parse `rate` as a decimal string, never as a float.
- `direction` selects the request variant (`ConvertToUzCommand` / `ConvertFromUzCommand`).
