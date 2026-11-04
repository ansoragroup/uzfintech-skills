# Agent guide

**English** · [Русский](Agent-guide.ru.md) · [Oʻzbekcha](Agent-guide.uz.md) · [简体中文](Agent-guide.zh-CN.md)

This page is for two readers: people who wire these skills into an agent, and agents that
read the repository directly. It explains how the skills are built and what a good answer
looks like.

## The design

Each skill is split into a router and workers: a small router picks the work, and each
worker gets only the context it needs.

| Idea | How the skills apply it |
|---|---|
| A small router picks the worker | `SKILL.md` is the router. Its description decides when the skill loads; its body has the product table, the "which product?" table, the rules and the warnings. It stays under 180 lines. |
| Workers get only the context they need | Each product folder under `references/` has notes, schemas and examples. The agent opens only the folder the task needs. |
| A fast path in code, a slow path in the model | Signatures, auth headers, checkout URLs and payload shapes go through `sign.py` and `validate.py`. The model reads and reasons only where code cannot decide. |
| Inline and spill | What every task needs is inline in `SKILL.md`. Contracts, sandbox data and checklists spill to files read on demand. |
| Stable IDs | Scheme names (`click.prepare`), schema names (`merchant/CreateTransaction`), warning IDs (`uzum.fiscal-receipt-24h`) and error codes never change and are never translated. |
| Output fits the channel | Chat, PR review and code each have their own shape (below). |
| Evals keep it honest | Each case in `evals/` checks a behaviour, not a wording. See [Evals](Evals.md). |

## How an agent should work a task

1. **Load one provider at a time.** For a task that touches Payme and Click, open
   `payme/SKILL.md`, finish the Payme part, then open `click/SKILL.md`. Compare at the end.
   Units, auth and retry rules never carry over: Payme counts tiyin, Click counts sum. To
   choose or compare providers, start with the `uzfintech` router skill; it points to the
   provider skill that holds the contract.
2. **Pick the product from the decision table**, then open its `references/<product>/README.md`.
   Read `references/common/README.md` first when the skill has one: transport, auth and the
   error envelope live there.
3. **Run the tools** before calling a signature, header or payload correct. Quote their
   output.
4. **Check the lifecycle.** If the task creates, confirms, cancels, refunds, retries or
   fiscalizes anything, read the skill's "Warn without being asked" block and
   `references/lifecycle/README.md`. Say the deadline, whether the step can be undone and
   what happens to the fiscal receipt, even if nobody asked. See [Lifecycle](Lifecycle.md).
5. **Use sandbox data from `references/sandbox/`** for tests and examples: test hosts, cards,
   OTP codes and scenarios exactly as the vendor publishes them. Never invent a test card,
   and say so plainly when a provider publishes none (Paynet, Oson, Kapitalbank; Octo has no
   test cards).
6. **Say what is not documented.** When the references do not cover a fact, say the docs do
   not specify it and link the `Source:` page. Do not fill the gap from memory.
7. **Leave commercial terms out.** Commission rates, payout shares and settlement days depend
   on each merchant's contract. Fee fields in API responses are fine to explain.

## What a good answer looks like

**In chat.** The conclusion first, in about 100 words, unless the user asked for code.
Exact names and codes in backticks. One line of warning per lifecycle item that applies.

> Payme rejects it because the transaction is older than 12 h. Answer `CreateTransaction`
> and `PerformTransaction` on it with `-31008`, and cancel it with `reason: 4`. Do not
> fulfil the order. Retries with the same Payme `id` must return the stored answer.
> Warning: once performed, a refund is a full `CancelTransaction` (state `-2`, reason `5`).
> If Payme then sends `SetFiscalData` with `type: CANCEL`, store it as a separate receipt
> and keep the `PERFORM` one.

**In a PR or review.** Problem, Change, Validation. For a checklist review, mark each item
pass, fail or n.a. with a `file:line` citation.

**In code.** Runs as written against the sandbox, keeps secrets in environment variables,
verifies signatures over the raw body with a constant-time compare, and stores the provider's
transaction id as the idempotency key.

**In the user's language.** Russian, Uzbek, Chinese or English, but method names, fields,
headers, codes and enum values stay exactly as the API spells them.

## Writing prompts that get good answers

- Name the provider and the product: "Uzum Merchant API", "Click SHOP API", "Payme Subscribe".
- Paste the raw request body and headers when something fails. The tools need them as sent.
- Say where the answer goes: "for a PR description", "as a Go handler", "short, for chat".
- Ask for the checklist when you want a review: "review our Multicard integration against
  the checklist".
