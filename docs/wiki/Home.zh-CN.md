# uzfintech-skills

[English](Home.md) · [Русский](Home.ru.md) · [Oʻzbekcha](Home.uz.md) · **简体中文**

面向乌兹别克斯坦支付 API 的智能体技能：**Uzum Bank、Alif、Click、Paynet、Payme、Multicard、Atmos、Octo、Oson 和 Kapitalbank**，外加一个所有服务商共用的税务小票技能，以及一个用于选择和比较服务商的路由技能。加载了这些技能的智能体会依据精确的接口契约笔记作答，用两个小脚本校验签名和报文，并在截止时间、冲正和税务小票（fiscal receipt，经 OFD 登记）的问题演变成生产事故之前发出警告。

## 从这里开始

| 我想…… | 页面 |
|---|---|
| 在 Claude Code、Codex、Cursor 或其他智能体中安装这些技能 | [安装](Install.zh-CN.md) |
| 校验签名、鉴权头或报文 | [工具](Tools.zh-CN.md) |
| 了解智能体应如何使用这些技能，以及好的回答是什么样 | [智能体指南](Agent-guide.zh-CN.md) |
| 查看各服务商的时间窗口、取消 / 退款规则和小票规则 | [生命周期](Lifecycle.zh-CN.md) |
| 衡量这些技能是否让回答变得更好 | [评测](Evals.zh-CN.md) |
| 修正某个事实，或新增产品、服务商 | [参与贡献](Contributing.zh-CN.md) |
| 快速找到答案 | [常见问题](FAQ.zh-CN.md) |

## 支付服务商

| 技能 | 服务商 | 涵盖内容 |
|---|---|---|
| [`uzum`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/uzum/SKILL.md) | Uzum Bank | Merchant API webhook、Checkout、Fiscalization、FastPay、Dynamic QR、CrossBorder、Remit Core、Ratekeeper、Nasiya、PaymentHub |
| [`alif`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/alif/SKILL.md) | Alif (alifpay) | Checkout、Alif Nasiya 分期付款、Payments、Cards、Hold、Monitoring、Summary、旧版 API 对照表 |
| [`click`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/click/SKILL.md) | Click | SHOP API、Advanced / Split Shop、Merchant API、卡令牌（card token）、Fiscalization、CLICK Pass、支付按钮、Telegram Payments |
| [`paynet`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/paynet/SKILL.md) | Paynet | Humo 和 Uzcard 互联网收单 |
| [`payme`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/payme/SKILL.md) | Payme (Paycom) | Merchant API、Subscribe API、Checkout、Fiscalization |
| [`multicard`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/multicard/SKILL.md) | Multicard | 账单（invoice）、绑卡、支付、退款、预授权、代付（payout）、报表 |
| [`atmos`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/atmos/SKILL.md) | Atmos | Uzcard / Humo 支付与冲正、支付页面与小组件、绑卡、预授权、按 PINFL 扣款、Visa / Mastercard（MPS / IPS）、Callback API |
| [`octo`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/octo/SKILL.md) | Octo | 支付页面（一步式 / 两步式）、自有卡表单、卡令牌、全额和部分退款、税务登记 |
| [`oson`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/oson/SKILL.md) | Oson | Invoice API 与带签名的支付通知，依据 Oson 开源的商店插件整理 |
| [`kapitalbank`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/kapitalbank/SKILL.md) | Kapitalbank | 面向法人的 Kapital API（付款指令、状态、对账单、账户核验、汇率、发票）、中央银行付款用途代码 |
| [`fiscal`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/fiscal/SKILL.md) | 所有服务商 | MXIK（IKPU）与包装代码、增值税与优惠字段、标识、小票类型、各服务商的小票字段 |
| [`uzfintech`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/uzfintech/SKILL.md) | 所有服务商 | 路由：选择和比较服务商、跨服务商速查表（金额单位、鉴权、回调、退款、预授权、税务登记、测试主机）、UzQR 说明 |

如果任务是选择或比较服务商，请从 `uzfintech` 开始。

## 技能里有什么

```
skills/<provider>/
  SKILL.md                 router: products, decision table, rules, gotchas, warnings
  references/<product>/    README.md notes, schemas/*.json, examples/*.json
  references/sandbox/      vendor test hosts, cards, OTP codes, scenarios, kept exactly
  references/lifecycle/    deadlines, cancel / reverse / refund, retries, fiscal receipts
  checklists/*.md          review items: pass, fail or n.a. with a file:line citation
  scripts/sign.py          signatures and auth headers
  scripts/validate.py      JSON Schema check of request and response bodies
```

这些笔记依据公开的开发者文档编写。每条参考资料都注明了来源页面和抓取日期。一切以服务商文档为准。
