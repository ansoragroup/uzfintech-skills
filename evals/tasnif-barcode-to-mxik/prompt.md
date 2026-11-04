---
name: tasnif-barcode-to-mxik
max_turns: 12
timeout_seconds: 300
tags: [tasnif, fiscal]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---
Our online shop has about 3000 products, each with an EAN-13 barcode, and most of them have
no IKPU yet. I want checkout to send the barcode to tasnif.soliq.uz, get the IKPU and the
package code back, and put them on the fiscal receipt. Which request do I call, and what do I
need to watch out for?
