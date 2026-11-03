# uzfintech-skills

[English](README.md) · [Русский](README.ru.md) · [Oʻzbekcha](README.uz.md) · **简体中文**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-6%20providers-0a7c66.svg)](#支付服务商)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-d97757.svg)](#安装)
[![Python 3.9+ stdlib](https://img.shields.io/badge/tools-python3%20stdlib-3776ab.svg)](#工具)

面向乌兹别克斯坦支付服务商 API 的智能体技能（Agent Skills）：**Uzum Bank、Alif、Click、Paynet、Payme 和 Multicard**。可在 Claude Code、Codex、Cursor 以及任何读取 `SKILL.md` 文件的智能体中使用。

大模型对这些 API 只是一知半解。它们会把 tiyin 和 sum 搞混，对错误的字符串签名，还会编造错误码或沙箱测试卡。有了这些技能，智能体会依据精确的接口契约笔记作答，并用脚本校验签名和报文，而不是靠猜。每个技能包含：

- 接口端点、鉴权头、签名、金额单位和状态机；
- 精简后的 JSON Schema、错误码、幂等与重试规则；
- 匿名化的请求和响应示例；
- 服务商的沙箱数据，原样保留：测试主机、测试卡、OTP 验证码、测试场景；
- 用于审查集成的实现检查清单；
- `sign.py` 和 `validate.py`：两个确定性的工具，没有任何依赖。

## 支付服务商

| 技能 | 服务商 | 产品 |
|---|---|---|
| [`uzum`](skills/uzum/SKILL.md) | Uzum Bank | Merchant API（webhook）、Checkout、Fiscalization、FastPay、Dynamic QR、CrossBorder、Remit Core、Ratekeeper、Nasiya、PaymentHub |
| [`alif`](skills/alif/SKILL.md) | Alif (alifpay) | Checkout、Payments、Cards、Hold、Monitoring、Summary、旧版 API 迁移对照表 |
| [`click`](skills/click/SKILL.md) | Click | SHOP API、Advanced / Split Shop、Merchant API、卡令牌（card token）、Fiscalization、CLICK Pass、支付链接 / 按钮 / 小组件、Telegram Payments |
| [`paynet`](skills/paynet/SKILL.md) | Paynet | 互联网收单（Humo / Uzcard）：authorize、confirm、status、reverse |
| [`payme`](skills/payme/SKILL.md) | Payme (Paycom) | Merchant API、Subscribe API（卡片、收款单 receipts、预授权）、Checkout（GET / POST / 按钮 / 二维码）、Fiscalization |
| [`multicard`](skills/multicard/SKILL.md) | Multicard | 账单（invoice）与 scanpay、绑卡、支付（token / 卡 / app / 分账 split）、退款、预授权、代付（payout）、报表 |

## 安装

### 任意智能体：`skills` CLI

```sh
npx skills add ansoragroup/uzfintech-skills
```

[`skills`](https://github.com/vercel-labs/skills) CLI 会询问要安装到哪些智能体（Claude Code、Codex、Cursor、Gemini CLI、GitHub Copilot 等），以及是全局安装还是只装到一个项目。加上 `--skill payme` 可以只安装单个服务商。

### Claude Code：插件

```
/plugin marketplace add ansoragroup/uzfintech-skills
/plugin install uzfintech@uzfintech-skills
```

用 `/plugin marketplace update uzfintech-skills` 更新。插件会给技能加上命名空间，例如 `uzfintech:payme`、`uzfintech:click` 等。

### 手动复制

```sh
git clone https://github.com/ansoragroup/uzfintech-skills
cp -R uzfintech-skills/skills/* ~/.claude/skills/    # Claude Code, all projects
cp -R uzfintech-skills/skills/* ~/.codex/skills/     # Codex
```

如果只给一个项目使用，改为复制到 `<project>/.claude/skills/`。

### 不支持技能的智能体：AGENTS.md

把本仓库纳入你的项目（vendor，例如作为 git submodule 放在 `vendor/uzfintech-skills`），然后在项目的 `AGENTS.md` 中加入以下内容：

```md
## Payment provider contracts
For Uzbek payment provider work (Uzum Bank, Alif, Click, Paynet, Payme, Multicard), read
`vendor/uzfintech-skills/skills/<provider>/SKILL.md` first and follow its pointers. Run its
`scripts/sign.py` and `scripts/validate.py` instead of computing signatures by hand, and
review changes against the matching `checklists/*.md`.
```

[安装 wiki 页面](docs/wiki/Install.zh-CN.md)介绍了如何更新、锁定版本和排查问题。

## 工作原理

每个技能都分为路由器和工作者（router / worker）：由一个小巧的路由器决定去向，具体工作在各个专注的位置完成，只带上所需的上下文。

```
             your question
                   │
     ┌─────────────▼─────────────┐   ~140 lines, loaded when the description matches:
     │  skills/<provider>/       │   products, decision table, gotchas,
     │  SKILL.md   (router)      │   answering rules, tool commands
     └──────┬────────────┬───────┘
  slow path │            │ fast path
  (reading) │            │ (deterministic)
     ┌──────▼──────┐  ┌──▼───────────────────┐
     │ references/ │  │ scripts/sign.py      │  exact signed string, MATCH / MISMATCH
     │ checklists/ │  │ scripts/validate.py  │  OK / INVALID with JSON paths
     └─────────────┘  └──────────────────────┘
```

- **每个技能只对应一个服务商。** 涉及多个服务商的任务会分别加载各自的技能，最后再做对比。金额单位、鉴权、重试这类规则绝不会从一个服务商套用到另一个。
- **优先走快路径。** 签名、鉴权头、收银台 URL 和报文结构都由代码计算，绝不交给模型。智能体运行工具，并引用工具的输出。
- **内联与外置（inline and spill）。** `SKILL.md` 只内联每个任务都需要的内容。接口契约、Schema、示例、沙箱数据和检查清单都放在文件里，由智能体按需读取。
- **稳定的 ID。** 签名方案（`payme.basic`、`click.prepare`）、Schema 名称（`uzum/webhook-confirm`）和错误码在所有语言中都一样，绝不翻译。
- **输出适配渠道。** 在聊天中，智能体先给结论，约 100 个词。在 PR 或代码审查中，按 Problem、Change、Validation（问题、改动、验证）来写。它用你的语言回复，但 API 名称保持原样。
- **主动预警。** 支付 bug 往往藏在时间窗口和不可逆的步骤里。只要任务会创建、确认、取消、退款、重试一笔支付，或对其进行税务登记（fiscalize），即使你没有问，智能体也会说明截止时间、这一步能否撤销，以及税务小票（fiscal receipt，经 OFD 登记）会受到什么影响。参见[生命周期警告](#生命周期警告)。

## 生命周期警告

每个技能都有 `references/lifecycle/README.md`，列出该服务商的截止时间和时间窗口、取消 / 冲正 / 退款规则、重试与幂等规则、预授权和 OTP 的有效期，以及税务小票规则。代价最高的几条内联在 `SKILL.md` 的“Warn without being asked”一节，每条都有稳定的 ID。例如 `uzum.fiscal-receipt-24h`：Uzum 的税务小票必须带有距支付 24 小时以内的 `date_time`，所以退款小票不能简单地拖到下周再发。

[生命周期 wiki 页面](docs/wiki/Lifecycle.zh-CN.md)把它们汇总在一张表中。

## 工具

每个技能都附带 `scripts/sign.py` 和 `scripts/validate.py`。它们只需要 `python3`（3.9+）和标准库。密钥从环境变量读取，输出时显示为 `<SECRET>`。

```console
$ python3 skills/click/scripts/sign.py --list
click.prepare       SHOP API Prepare sign_string = md5(...)
                    fields: click_trans_id service_id merchant_trans_id amount action sign_time; secret: CLICK_SECRET_KEY
click.complete      SHOP API Complete sign_string = md5(...)
                    fields: click_trans_id service_id merchant_trans_id merchant_prepare_id amount action sign_time; secret: CLICK_SECRET_KEY
click.advanced      Advanced / Split Shop sign_string = md5(..., params values in body order, ...)
                    fields: click_paydoc_id attempt_trans_id service_id params action sign_time; secret: CLICK_SECRET_KEY
click.auth          Merchant API Auth: merchant_user_id:sha1(ts+secret):ts, ts in seconds
                    fields: merchant_user_id [timestamp]; secret: CLICK_SECRET_KEY

$ CLICK_SECRET_KEY=test-secret python3 skills/click/scripts/sign.py click.prepare body.txt \
    --expect d7696dbc2b950daf03e1191fbea5fbb3
input   12345100<SECRET>100011000.002026-11-03 10:00:00
value   24d6c366acd79c05457ddf0547d6d65c
MISMATCH, received d7696dbc2b950daf03e1191fbea5fbb3
```

`input` 这一行暴露了 bug。Click 发送的是 `amount=1000.00`，并对这个字符串签名。我们的处理程序把金额解析成数字，又重建成 `1000.0`，于是 `body.txt` 里已经不是 Click 签名时的内容。请严格按收到的原始值签名。

```console
$ python3 skills/payme/scripts/validate.py CreateTransaction body.json
INVALID references/merchant/schemas/CreateTransaction.json (params): 1 problem(s)
  $.amount: expected integer, got string
```

`validate.py` 会拆开 JSON-RPC 和 `{success, data}` 信封，能读取 form-urlencoded 请求体，并跳过 `<PLACEHOLDER>` 占位值。两个工具成功时退出码为 `0`，不匹配时为 `1`，用法错误时为 `2`，因此可以直接用在 CI 中。所有签名方案见[工具 wiki 页面](docs/wiki/Tools.zh-CN.md)。

## 试一试

- “Click 说我们 Prepare 的 `sign_string` 不对。这是请求体。”
- “实现 Payme Merchant API 的 `CreateTransaction`，包括 `-31008` / `-31050` 错误。”
- “Uzum Merchant 的 `/confirm` 会发送什么？遇到重试时我该怎么应答？”
- “用 Go 验证 Alif webhook 的签名。”
- “Uzum Checkout 沙箱使用哪些测试卡和 OTP 验证码？”
- “对照检查清单审查我们的 Multicard 集成。”
- “Payme sandboxida qaysi test kartalardan foydalanish mumkin?”

## 质量保证

| 检查 | 命令 | 证明了什么 |
|---|---|---|
| 仓库 lint | `scripts/lint` | 工具已同步并通过自检，每个示例都符合其 Schema，frontmatter 符合规范，没有失效链接，匿名化扫描通过，翻译齐全，版本号一致，每个警告 ID 都在其生命周期页面中有定义 |
| 解析器自检 | `scripts/sync --selftest` | 内置的 YAML 解析器与 PyYAML 结果一致 |
| 行为评测 | `claude plugin eval . --runs 3` | 加载了技能的智能体会选对服务商、引用准确的错误码、运行工具，并拒绝编造沙箱数据或商务条款 |

12 个评测用例在 [`evals/`](evals/README.md) 中。CI 会在每个 PR 上运行 lint。

## 内容时效

每条参考资料都注明了来源 URL 和抓取日期。`.github/workflows/sync.yml` 每周运行一次 `scripts/sync`，重新生成由 OpenAPI 派生的文件，并在上游规范或文档页面发生变化时开一个 PR。合并前，由人工重读被标记的页面。

```sh
scripts/sync --check            # report only; exit 1 when upstream changed
scripts/sync                    # regenerate derived files, update sources.yaml
```

## 文档

[wiki](docs/wiki/Home.zh-CN.md) 中有完整的指南：
[安装](docs/wiki/Install.zh-CN.md) · [工具](docs/wiki/Tools.zh-CN.md) ·
[智能体指南](docs/wiki/Agent-guide.zh-CN.md) · [生命周期](docs/wiki/Lifecycle.zh-CN.md) ·
[评测](docs/wiki/Evals.zh-CN.md) · [参与贡献](docs/wiki/Contributing.zh-CN.md) · [常见问题](docs/wiki/FAQ.zh-CN.md)

## 参与贡献

欢迎提交修正、新产品和新服务商。请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)：其中说明了内容规则（不照搬服务商原文、示例要匿名化、沙箱数据原样保留、不写商务条款），以及提 PR 前要运行的检查。安全问题请按 [SECURITY.md](SECURITY.md) 中的说明报告。

## 免责声明

本项目与所涉及的任何支付服务商均无关联。这些笔记整理自公开的开发者文档，一切以该文档为准。生产环境的实际行为请向你的服务商确认。手续费率和结算条款取决于每个商户的合同，因此这些技能不会给出。切勿提交真实的凭据或客户数据。

## 许可证

[MIT](LICENSE)
