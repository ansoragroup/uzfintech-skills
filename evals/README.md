# Evals

Behaviour tests for the skills, in the format of `claude plugin eval`. Each case is a
real developer request. Graders check that the agent loads the right skill, quotes the
exact contract, runs the tools and refuses to invent what the vendor does not publish.

```
evals/<case>/prompt.md        frontmatter (name, tags, runs, allowed_tools) + the prompt
evals/<case>/graders/*.md     one grader per file: regex, llm or tool_used
```

## Run

```sh
claude plugin eval . --runs 3                         # all cases, with the skills loaded
claude plugin eval . --tag payme                      # one provider
claude plugin eval . --case 'click-*' --allow-tools Bash   # cases that run sign.py
claude plugin eval . --ablation with-without          # also run without the skills
```

`Bash` is off unless you pass `--allow-tools Bash`. Without it, the `tools` cases cannot
run `sign.py` and their `tool` grader fails. With `--ablation with-without`, the `skill`
graders count only in the "with" arm, and the gap between the arms shows what the skills
add.

In CI, write JSON and set a budget:

```sh
claude plugin eval . --runs 3 --allow-tools Bash --trust-plugin --no-publish \
  --threshold 0.8 --max-cost-usd 20 --json results.json
```

A full run of every case once costs about $2.

## Cases

| Case | Checks |
|---|---|
| `payme-create-after-timeout` | `-31008`, the 12 h timeout, cancel reason `4` |
| `click-sign-mismatch` | signs `amount` exactly as received, field order, runs `sign.py` |
| `uzum-merchant-confirm-retry` | idempotent `/confirm` retry, `errorCode` as a string |
| `alif-webhook-go` | HMAC-SHA256 over the raw body, base64, constant-time compare |
| `multicard-callback` | callback `sign`, `success: true`, refund handling |
| `paynet-no-sandbox` | says Paynet publishes no sandbox or test cards and does not invent any |
| `payme-sandbox-uzbek` | Uzbek prompt: vendor test card data, answer in Uzbek |
| `no-commercial-terms` | no commission or settlement numbers; points to the merchant agreement |
| `multi-provider-units` | tiyin for Payme and sum for Click in one task, each skill loaded separately |
| `multicard-callback-stock` | unprompted warning: a non-success callback answer refunds the payer |
| `uzum-fiscal-nightly-job` | unprompted warning: receipt `date_time` within 24 h, else 422 |
| `paynet-refund-button` | unprompted warning: `reverse` works only within 1 month |
| `atmos-apply-timeout` | unprompted warning: never resend `pay/apply` after a timeout; read the state with `pay/get` |
| `atmos-refund-id` | `pay/reverse` takes `success_trans_id` from the apply reply, not the create `transaction_id` |
| `octo-two-stage-capture` | `auto_capture: false`, `set_accept`, and the 30-minute hold window |
| `octo-notify-handler` | verifies the SHA1 `signature` with `unique_key`, re-checks via `/prepare_payment` |
| `oson-notify-handler` | double SHA-256 `signature`, `hash_equals`, fulfils only on `PAID` |
| `kapitalbank-no-sandbox-host` | says no sandbox host is published and does not invent one |
| `kapitalbank-old-code-00545` | old code `00545` split by material: aluminium goods now take `00076` |
| `fiscal-payme-basket-code` | IKPU is 17 digits from tasnif.soliq.uz, as a string, plus `package_code` |
| `router-octo-multicard-units` | Multicard in tiyin, Octo `total_sum` in major units, each skill loaded |

## Writing a case

1. Write the prompt the way a developer would ask. Do not name the trap you are testing.
   A `lifecycle` case passes only when the agent raises the warning on its own.
2. Prefer `regex` graders on exact codes, field names and numbers. Use an `llm` grader only
   for what a pattern cannot express (for example "invents no card number"), and write its
   criteria so that a correct answer with extra detail still passes.
3. Add a `tool_used` grader for `Skill` with
   `input_match: '"skill"\s*:\s*"(uzfintech:)?<provider>"'`.
4. A case may set only `EVAL_*` environment variables. Put sandbox values in the prompt.
5. Run the new case three times before you commit it. Graders must pass a correct answer
   every time and fail a wrong one.
