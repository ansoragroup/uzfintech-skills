---
type: llm
weight: 3
---
The answer advises against calling Tasnif from checkout and says to resolve codes ahead of
time (when a product is created or imported, in a background job) and read them from the
shop's own catalogue at checkout. It says a barcode hit is shown to a person to confirm
before it is stored, and that no hit does not mean the product has no code (fall back to a
text search). It decides "not found" from the reply body (`success: false`, empty
`content`), not from the HTTP status. It mentions throttling and caching, and that these
are the site's own undocumented endpoints with no published terms or SLA. It stores codes
as strings. It does not invent an authenticated or official Tasnif API, and gives no advice
on which code or VAT rate applies.
