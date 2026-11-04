# Cheatsheet: the rules that differ per provider

Hand-written notes. One row per provider, one link per cell to the file the value comes
from. Use it to see **that** providers differ, then open the linked file and the provider's
skill before you write code. Never fill a cell for one provider from another provider's row.

- Source: the provider files linked in each cell; scheme names from
  `python3 scripts/sign.py --list`
- Fetched: 2026-11-04

## Units, auth and callbacks

| Provider | Amount unit | Auth / signature (`sign.py` scheme) | Callback success answer |
|---|---|---|---|
| payme | integer tiyin; times in ms ([skill](../../../payme/SKILL.md#rules-that-apply-everywhere)) | Merchant API Basic `payme.basic`; Subscribe X-Auth `payme.xauth`; Checkout link `payme.checkout` ([common](../../../payme/references/common/README.md#two-protocols)) | HTTP 200 with `{"result": {...}, "id"}`; errors also HTTP 200, in `error` ([merchant](../../../payme/references/merchant/README.md)) |
| click | soum (may have decimals); fiscalization in integer tiyin ([common](../../../click/references/common/README.md#units)) | inbound `sign_string` MD5 `click.prepare`, `click.complete`, `click.advanced`; outbound `Auth` header `click.auth` ([common](../../../click/references/common/README.md#auth-scheme-1-shop-api-signature-click---you)) | HTTP 200 JSON with `error` `0` and `error_note` ([skill](../../../click/SKILL.md#cross-product-rules)) |
| uzum | integer tiyin, unless a product README says otherwise; Nasiya unstated ([skill](../../../uzum/SKILL.md#cross-product-rules)) | Merchant API Basic `uzum.basic`; FastPay / Dynamic QR `uzum.fastpay`; Checkout `X-Terminal-Id` + `X-API-Key` ([skill](../../../uzum/SKILL.md#cross-product-rules)) | Merchant API: HTTP 200 with `status`; business error HTTP 400 with a string `errorCode`; no callback is signed ([merchant](../../../uzum/references/merchant/README.md)) |
| alif | integer tiyin ([skill](../../../alif/SKILL.md#rules-that-apply-everywhere)) | `Token` header; webhook `Signature` `alif.webhook` ([common](../../../alif/references/common/README.md#webhooks)) | HTTP 200 fast; about an hour without it cancels and refunds ([common](../../../alif/references/common/README.md#webhooks)) |
| multicard | integer tiyin ([common](../../../multicard/references/common/README.md#transport)) | Bearer JWT from `POST /auth`; callback `multicard.callback`, webhook `multicard.webhook` ([common](../../../multicard/references/common/README.md#auth)) | success callback HTTP 200 `{"success": true}`, anything else refunds; status webhook any 2xx ([invoice](../../../multicard/references/invoice/README.md)) |
| atmos | integer tiyin ([skill](../../../atmos/SKILL.md)) | Bearer from `POST /token` with Basic `atmos.basic`; callback `atmos.callback` ([common](../../../atmos/references/common/README.md#auth)) | HTTP 200 `{"status": 1}`; any other answer means no debit ([skill](../../../atmos/SKILL.md#warn-without-being-asked)) |
| octo | decimal major units (`1000.0` UZS) ([common](../../../octo/references/common/README.md#transport)) | `octo_shop_id` + `octo_secret` in the JSON body; notify `octo.notify` over `unique_key` ([common](../../../octo/references/common/README.md#auth)) | capture callback: `{accept_status, final_amount}`; notify: answer not documented, HTTP 200 derived ([common](../../../octo/references/common/README.md#notifications-notify_url)) |
| paynet | integer tiyin ([skill](../../../paynet/SKILL.md#rules-that-apply-everywhere)) | Basic `paynet.basic` ([skill](../../../paynet/SKILL.md)) | no callbacks; poll `status` ([lifecycle](../../../paynet/references/lifecycle/README.md)) |
| oson | soum, major units ([skill](../../../oson/SKILL.md#rules-that-apply-everywhere)) | `token` header + `merchant_id`; notify `oson.notify` ([common](../../../oson/references/common/README.md#auth)) | not documented; answer HTTP 200 quickly (derived) ([notify](../../../oson/references/notify/README.md)) |
| kapitalbank | not stated; confirm in writing ([skill](../../../kapitalbank/SKILL.md#rules-that-apply-everywhere)) | Basic `IB#login:password` and ЭЦП `signs[]`; no `sign.py` recipe ([skill](../../../kapitalbank/SKILL.md#which-product)) | no webhooks; poll CheckPayments2 ([skill](../../../kapitalbank/SKILL.md#rules-that-apply-everywhere)) |

## Refunds, holds, receipts and test hosts

| Provider | Refund / cancel rule | Holds | Who fiscalizes | Test host(s) |
|---|---|---|---|---|
| payme | `CancelTransaction` is the refund, full only ([lifecycle](../../../payme/references/lifecycle/README.md#cancel-reverse-and-refund)) | `hold: true` in create and pay ([skill](../../../payme/SKILL.md#warn-without-being-asked)) | Payme, from `detail` ([fiscalization](../../../payme/references/fiscalization/README.md)) | `test.paycom.uz`, `checkout.test.paycom.uz/api` ([sandbox](../../../payme/references/sandbox/README.md#environments)) |
| click | `payment/reversal`, full, current month ([lifecycle](../../../click/references/lifecycle/README.md#cancel-reverse-and-refund)) | not published ([skill](../../../click/SKILL.md#which-product)) | Click on `submit_items`, or you with `submit_qrcode`; either, not both, per payment ([fiscalization](../../../click/references/fiscalization/README.md)) | none; test tools call your server ([sandbox](../../../click/references/sandbox/README.md#what-click-publishes-for-testing)) |
| uzum | Checkout: TWO_STEP `reverse`, ONE_STEP refund only; Merchant API: inbound `/reverse` only ([lifecycle](../../../uzum/references/lifecycle/README.md#cancel-reverse-and-refund)) | Checkout TWO_STEP; expiry not published ([lifecycle](../../../uzum/references/lifecycle/README.md#cancel-reverse-and-refund)) | Checkout auto-fiscalization, or you through Fiscalization ([fiscal map](../../../fiscal/references/providers/README.md#mapping)) | `test-chk-api.uzumcheckout.uz`, `test-ofd.ipt-merch.com` and others ([sandbox](../../../uzum/references/sandbox/README.md#test-hosts)) |
| alif | full only; partial for instalments ([lifecycle](../../../alif/references/lifecycle/README.md#cancel-reverse-and-refund)) | `hold`, lifetime per card type ([hold](../../../alif/references/hold/README.md)) | Alif when asked, or you + `registerReceipt` ([fiscal map](../../../fiscal/references/providers/README.md#mapping)) | `api-dev.alifpay.uz`, `checkout-dev.alifpay.uz` ([sandbox](../../../alif/references/sandbox/README.md#environments)) |
| multicard | full and partial `DELETE /payment/...` ([lifecycle](../../../multicard/references/lifecycle/README.md#cancel-reverse-and-refund)) | `expiry` in minutes ([hold](../../../multicard/references/hold/README.md)) | store `tax_registration`: `1` Multicard, `0` off (you send the receipt link), `2` / `3` commission only ([common](../../../multicard/references/common/README.md#fiscal-items-ofd)) | `dev-mesh.multicard.uz` ([sandbox](../../../multicard/references/sandbox/README.md#environments)) |
| atmos | full by `success_trans_id`; partial needs confirm ([lifecycle](../../../atmos/references/lifecycle/README.md#cancel-reverse-and-refund)) | Holding; MPS hold ([hold](../../../atmos/references/hold/README.md)) | Atmos from `ofd_items`, returns `ofd_url` ([common](../../../atmos/references/common/README.md#fiscal-items)) | API host not published; test page and widget only ([sandbox](../../../atmos/references/sandbox/README.md#environments)) |
| octo | `set_accept` `cancel` for holds; `/refund` for paid, with limits ([lifecycle](../../../octo/references/lifecycle/README.md#cancel-reverse-and-refund)) | two-stage, auto-cancelled if not captured ([skill](../../../octo/SKILL.md#warn-without-being-asked)) | Octo, from registered `basket` items ([fiscal](../../../octo/references/fiscal/README.md)) | none; `test: true` on the production host ([sandbox](../../../octo/references/sandbox/README.md#environments)) |
| paynet | `reverse`, full, within 1 month ([lifecycle](../../../paynet/references/lifecycle/README.md#cancel-reverse-and-refund)) | not published ([skill](../../../paynet/SKILL.md#which-operation)) | not documented ([lifecycle](../../../paynet/references/lifecycle/README.md#fiscal-receipts)) | none published ([sandbox](../../../paynet/references/sandbox/README.md)) |
| oson | no API method; cabinet or support ([lifecycle](../../../oson/references/lifecycle/README.md#cancel-reverse-and-refund)) | not published ([skill](../../../oson/SKILL.md#which-product)) | not documented; register yourself until Oson confirms ([lifecycle](../../../oson/references/lifecycle/README.md#fiscal-receipts)) | none; no test mode ([sandbox](../../../oson/references/sandbox/README.md)) |
| kapitalbank | no recall method published; ask the bank ([lifecycle](../../../kapitalbank/references/lifecycle/README.md#cancel-reverse-and-refund)) | n.a. | n.a. (bank transfers) ([lifecycle](../../../kapitalbank/references/lifecycle/README.md#fiscal-receipts)) | none published ([sandbox](../../../kapitalbank/references/sandbox/README.md)) |

## How to use a row

- A cell is a pointer, not a contract. Open the linked file for the exact field, value and
  error code, and quote it from there.
- Signature recipes run with `sign.py` from the provider's skill:
  `python3 scripts/sign.py --list` prints every scheme; the provider's SKILL.md shows the
  command and the secret it reads.
- Fiscal fields per provider are in the
  [fiscal providers table](../../../fiscal/references/providers/README.md#mapping).
