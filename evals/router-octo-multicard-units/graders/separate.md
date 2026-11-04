---
type: llm
weight: 2
---
The answer says the helper must not be reused for Octo: Multicard `amount` is an integer in
tiyin (4 900 000), while Octo `total_sum` is a decimal in major units of the currency
(49000, for example `49000.0`), so passing the tiyin value would charge a hundred times the
price. Each value is taken from that provider's own skill, and no unit rule is carried from
one provider to the other (`uzfintech.units-differ-per-provider`). Extra correct detail
does not fail the answer.
