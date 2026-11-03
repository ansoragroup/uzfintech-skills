---
type: regex
pattern: 'errorCode[^\n]{0,60}string|string[^\n]{0,60}errorCode'
match: contains
weight: 2
---
Says `errorCode` is a string.
