---
name: multicard-callback-stock
max_turns: 12
timeout_seconds: 300
tags: [multicard, lifecycle]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
This is our Multicard `callback_url` handler in Express. The signature check already
passes. Is the rest fine? Keep it short.

```js
app.post('/multicard/callback', async (req, res) => {
  const order = await Orders.findById(req.body.invoice_id);
  if (!order) return res.status(404).json({ success: false, message: 'order not found' });
  const reserved = await Stock.reserve(order.items);
  if (!reserved) return res.status(409).json({ success: false, message: 'out of stock' });
  await order.markPaid(req.body.uuid);
  res.json({ success: true });
});
```
