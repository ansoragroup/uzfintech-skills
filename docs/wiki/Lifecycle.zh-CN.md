# 生命周期

[English](Lifecycle.md) · [Русский](Lifecycle.ru.md) · [Oʻzbekcha](Lifecycle.uz.md) · **简体中文**

代价最高的支付 bug 大多不是字段写错，而是某个步骤执行得太晚或执行了两次：退款窗口关闭后才尝试退款，截止时间过后才发送小票，部署期间 webhook 失败，结果悄悄把钱退给了付款人。本页把所有服务商的这类规则汇总在一处。

每个技能都把完整规则放在 `references/lifecycle/README.md` 中，它的 `SKILL.md` 则在“Warn without being asked”下列出代价最高的几条。加载了技能的智能体，只要任务会创建、确认、取消、退款、重试一笔支付，或对其进行税务登记（fiscalize），就会主动提出这些警告。

## 一览

| 服务商 | 容易踩坑的时间窗口 | 撤销支付 | 税务小票（fiscal receipt，经 OFD 登记） |
|---|---|---|---|
| [Uzum Bank](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/uzum/references/lifecycle/README.md) | Fiscalization 的 `date_time` 必须在支付确认后 **24 小时**内，否则返回 422。Merchant API 中超过 30 分钟的 `CREATED` 交易视为失败。 | Merchant API：没有主动发起退款的接口，由 Uzum 调用你的 `/reverse` 撤销全额。Checkout：TWO_STEP 在 `complete` 之前用 `reverse`，否则用 `refund`，最多退还 `completedAmount` 减去 `refundedAmount`。ONE_STEP 无法冲正（`3036`）。 | 由你开具，除非是开启了自动税务登记的 Checkout（仅限 ONE_STEP，由客户经理开通）。开具退款小票的前提是该笔销售已完成税务登记。 |
| [Alif](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/alif/references/lifecycle/README.md) | webhook 会重试约 **1 小时**；如果一直收不到 HTTP 200，支付会被取消并退款。预授权在 **10 天**（Humo）或 **30 天**（Uzcard）后结束。 | `refundPayment` 和 `refundInvoice` 都退还全额；只有分期付款支持部分退款。错误也会以 HTTP 200 返回，所以只有 `SUCCEEDED` 才代表已支付。 | 当你发送带 `spic` 的 `receipt` 时，由 Alif 登记。只有存在销售小票时，才会登记退款小票。 |
| [Click](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/click/references/lifecycle/README.md) | `payment/reversal` 只在**当前报表月**内可用；上个月的支付仅能在下个月的 **1 日**冲正。CLICK Pass 须在 **30 秒**内确认。 | 冲正只能全额，而且 UZCARD 仍可能拒绝。请另外准备一条退款途径。 | Click 根据 `submit_items` 开具小票，或者由你用 `submit_qrcode` 发送自己的小票链接，二者选其一。没有开具退款小票的接口。 |
| [Paynet](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/paynet/references/lifecycle/README.md) | `reverse` 只能在支付后 **1 个月**内执行。OTP 有效期由 `ttlSeconds` 给出。 | 调用 `reverse`，然后轮询 `status`（`CANCEL_PENDING` 不是最终状态）。锁定按钮，防止第二次点击。 | 由谁登记小票没有公开说明。接入时请向 Paynet 确认。 |
| [Payme](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/payme/references/lifecycle/README.md) | 处于 state `1` 的交易会在 **12 小时**后被取消（43 200 000 ms，reason `4`）。预授权：**30 天**。 | 退款就是对已执行的交易发起一次完整的 `CancelTransaction`（state `-2`，reason `5`）。如需拒绝，返回 `-31007`。 | Payme 根据 `detail` 开具小票，并发送 `SetFiscalData` `PERFORM` / `CANCEL`。把它们作为独立的小票分别存储，绝不要自己再登记一张。 |
| [Multicard](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/multicard/references/lifecycle/README.md) | 预授权的 `expiry` 以**分钟**计（最长 30 天）。账单的 `ttl` 以秒计（默认 1 天）。鉴权 token 有效期为 **24 小时**。 | 全额退款；只有 Multicard 在终端上开启后才支持部分退款，而且部分退款会开具一张新的税务小票。代付无法撤销。 | 由店铺的 `tax_registration` 决定：`1` 由 Multicard 开具，`0` 由你开具。 |

## 代价最高的警告

| ID | 适用场景 | 会出什么问题 |
|---|---|---|
| `uzum.fiscal-receipt-24h` | 从队列、批处理或重试循环中发送的小票 | 422 "date_time should be within 24 hours"；对部分支付来说，夜间批处理已经太晚了 |
| `uzum.merchant-lost-confirm` | `/confirm` 和 `/status` 处理程序 | confirm 丢失后，Uzum 会轮询 `/status`，而不会重发 confirm；先提交（commit）再应答 |
| `alif.webhook-1h-auto-refund` | webhook 处理程序、停机、部署 | 一个小时内没有 HTTP 200，支付就会被取消，钱也会退回 |
| `click.reversal-month-window` | 退款功能 | 过了下个月 1 日，就无法再冲正 |
| `click.complete-after-debit` | Complete 处理程序 | 付款人已经被扣款；应答成功（错误码只能是 `-4` / `-9`），如果无法交付，再做冲正 |
| `paynet.reverse-1-month` | 退款或取消按钮 | 超过一个月后，`reverse` 就无法执行 |
| `payme.create-timeout-12h` | 订单预留、Create / Perform | 12 小时后的 Create 或 Perform 必须返回 `-31008`；订单必须释放 |
| `payme.cancel-is-the-refund` | 退款功能 | 没有金额参数，所以退款总是全额退还整笔支付 |
| `multicard.callback-reject-refunds` | `callback_url` 处理程序 | 除 HTTP 200 `{"success": true}` 之外的任何应答，都会取消该支付并退款 |
| `multicard.payout-irreversible` | 代付 | 没有取消或冲正接口 |

每个 ID 都在其服务商的生命周期页面中定义；如果某个页面、`SKILL.md` 或本 wiki 提到了未定义的 ID，`scripts/lint` 就会失败。ID 从不重命名，也从不翻译。

## 重试与幂等

各服务商的规则不同，绝不要互相套用：

- **Uzum Merchant API：** 重复的 `/create` 返回 `10010`，重复的 `/confirm` 返回 `10016`，重复的 `/reverse` 返回 `10018`。`/confirm` 丢失后，Uzum 会轮询 `/status`。
- **Uzum Checkout：** `X-Operation-Id` 对每次操作唯一。调用前先持久化它；遇到 `3028` 时，读取 `getOperationState`，而不是发送新的 id。
- **Payme：** Create 和 Perform 会以相同参数重复发送，沙箱还会把每个方法发送两次。对同一个 Payme `id` 返回已存储的应答。
- **Click：** 同一个 `click_trans_id` 的 Prepare 和 Complete 可能会再次到达；按同样的方式应答。
- **Multicard：** 遇到超时、5xx 或 `ERROR_DEBIT_UNKNOWN` 后，绝不要重发涉及资金的请求。改为轮询该支付。
- **Paynet：** 可重试错误的意思是“去查 `status`”，而不是“再发一次”。

## 规则没有公开时

每个生命周期页面都以“Not documented — ask the provider”结尾。当文档没有规定截止时间时（例如 Click 没有规定 Prepare 到 Complete 的时限），智能体会如实说明，并建议向服务商询问，而不是编造一个数字。
