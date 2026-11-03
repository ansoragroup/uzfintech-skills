---
type: regex
pattern: '(?i)refund|return(s|ed)? (the )?(money|funds)'
match: contains
weight: 3
---
Warns that answering anything but `success: true` cancels the payment and refunds the payer.
