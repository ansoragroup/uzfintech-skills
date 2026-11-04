---
name: fiscal-payme-basket-code
max_turns: 12
timeout_seconds: 300
tags: [fiscal, payme, router]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
Payme rejects the basket of our online shop. In `detail.items` we send each product like
this, with the IKPU taken from our products table:

```json
{"title": "Mouse pad", "price": 5000000, "count": 1, "code": 6401004002000000, "vat_percent": 12}
```

What is wrong with this item and how do we fix it?
