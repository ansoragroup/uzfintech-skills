---
name: click-sign-mismatch
max_turns: 12
timeout_seconds: 300
tags: [click, shop-api, tools]
runs: 1
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---
Our Click SHOP API Prepare handler answers `-1 SIGN CHECK FAILED` for every request since we
switched to a JSON framework that parses `amount` as a float. Here is one request body:

    click_trans_id=12345&service_id=100&click_paydoc_id=1&merchant_trans_id=100001&amount=1000.00&action=0&error=0&error_note=Success&sign_time=2026-11-03 10:00:00&sign_string=bfcd1dc19ee36f8a7a1bad400fc52748

Our sandbox secret key is `test-secret`. Find the bug and show the correct way to build
`sign_string`.
