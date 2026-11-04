# 工具

[English](Tools.md) · [Русский](Tools.ru.md) · [Oʻzbekcha](Tools.uz.md) · **简体中文**

每个技能都在 `skills/<provider>/scripts/` 中附带两个脚本。它们只需要 `python3` 3.9+，别无其他依赖。模型靠“心算”得出 MD5 或 base64 请求头时，出错的频率足以造成麻烦；这些脚本每次都能算对，而且会展示计算过程。

| 脚本 | 回答的问题 | 输出 |
|---|---|---|
| `sign.py` | “这个签名或鉴权头对吗？应该是什么？” | 精确的待签名字符串（密钥已遮盖）、计算出的值、`MATCH` / `MISMATCH` |
| `validate.py` | “这个请求体符合契约吗？” | `OK`，或 `INVALID` 加上 JSON 路径 |

两者成功时退出码为 `0`，不匹配或请求体无效时为 `1`，用法错误时为 `2`。

## sign.py

```
sign.py --list                          schemes, the fields they need, the secret variable
sign.py SCHEME [PAYLOAD] [-f k=v ...]   compute; verifies too when PAYLOAD carries the sign
sign.py SCHEME ... --expect VALUE       verify a received signature or header
sign.py --selftest                      check the implementation against fixed vectors
```

`PAYLOAD` 是一个文件，或用 `-` 表示 stdin，格式为 JSON 或 form-urlencoded。`alif.webhook` 则对原始请求体字节签名。`-f key=value` 用于添加或覆盖字段。技能内附带的副本只列出该服务商的签名方案；没有自有方案的技能（`kapitalbank`、`fiscal`、`uzfintech`）会列出全部方案。

### 签名方案

| 方案 | 计算内容 | 密钥变量 |
|---|---|---|
| `alif.webhook` | `Signature` 请求头 = base64(HMAC-SHA256(secret, raw body)) | `ALIF_WEBHOOK_SECRET` |
| `atmos.basic` | `POST /token` 的 `Authorization: Basic base64(consumer_key:consumer_secret)` | `ATMOS_CONSUMER_SECRET` |
| `atmos.callback` | Callback API 的 `sign`，基于 store_id transaction_id invoice amount api_key；文档未说明哈希算法，因此会尝试 MD5、SHA1 和 SHA256，并指出匹配的是哪一种 | `ATMOS_API_KEY` |
| `click.prepare` | SHOP API Prepare 的 `sign_string`（MD5） | `CLICK_SECRET_KEY` |
| `click.complete` | SHOP API Complete 的 `sign_string`（MD5） | `CLICK_SECRET_KEY` |
| `click.advanced` | Advanced / Split Shop 的 `sign_string`，`params` 的值按请求体中的顺序排列 | `CLICK_SECRET_KEY` |
| `click.auth` | Merchant API 的 `Auth` 请求头：`merchant_user_id:sha1(ts+secret):ts`，单位为秒 | `CLICK_SECRET_KEY` |
| `multicard.callback` | 成功回调的 `sign` = md5(store_id invoice_id amount secret) | `MULTICARD_SECRET` |
| `multicard.webhook` | 状态 webhook 的 `sign`；会尝试 MD5 和 SHA1 两种形式，并指出匹配的是哪一种 | `MULTICARD_SECRET` |
| `octo.notify` | `notify_url` 的 `signature` = upper(sha1(unique_key octo_payment_UUID status))；分隔符未写明，按直接拼接处理 | `OCTO_UNIQUE_KEY` |
| `oson.notify` | 通知的 `signature` = sha256(sha256(token:merchant_id):transaction_id:bill_id:status)，小写 hex，与服务商插件的计算方式一致；用 `-f` 传入 `merchant_id` | `OSON_TOKEN` |
| `payme.basic` | Merchant API 的 `Authorization: Basic base64(login:KEY)` | `PAYME_KEY` |
| `payme.xauth` | Subscribe API 的 `X-Auth`：`CASHBOX_ID`，加 `--backend` 时为 `CASHBOX_ID:KEY` | `PAYME_KEY` |
| `payme.checkout` | 收银台 GET URL = host + base64(`m=..;ac.<field>=..;a=..;l=..`) | 无 |
| `paynet.basic` | `Authorization: Basic base64(service_id:secret_key)` | `PAYNET_SECRET_KEY` |
| `uzum.fastpay` | FastPay / Dynamic QR 的 `Authorization`：`user:sha1(ts+secret):ts`，单位为毫秒 | `UZUM_SECRET_KEY` |
| `uzum.basic` | Merchant API webhook、CrossBorder、PaymentHub：Basic `login:password` | `UZUM_PASSWORD` |

Kapitalbank 没有签名方案：`SendPaymentIBK` 中 `signs[]` 所需的电子数字签名（ЭЦП）未公开。

### 密钥

密钥只从表中列出的环境变量（或你用 `--secret-env` 指定的变量）读取，绝不通过参数传入，因此不会留在 shell 历史和智能体日志里。输出中密钥显示为 `<SECRET>`。包含明文密钥的值（例如 Basic 请求头）只有加上 `--reveal` 才会打印。

### 示例

排查 Click 为什么拒绝 Prepare 请求：

```console
$ CLICK_SECRET_KEY=test-secret python3 skills/click/scripts/sign.py click.prepare body.txt \
    --expect d7696dbc2b950daf03e1191fbea5fbb3
input   12345100<SECRET>100011000.002026-11-03 10:00:00
value   24d6c366acd79c05457ddf0547d6d65c
MISMATCH, received d7696dbc2b950daf03e1191fbea5fbb3
```

Click 按发送时的原样对 `amount=1000.00` 签名，而处理程序把它重建成了 `1000.0`。请按收到的原始值签名。

生成 Payme 收银台链接：

```console
$ python3 skills/payme/scripts/sign.py payme.checkout \
    -f m=5e730e8e0b852a417aa49ceb -f ac.order_id=10001 -f a=500000 -f l=uz
input   m=5e730e8e0b852a417aa49ceb;ac.order_id=10001;a=500000;l=uz
value   https://checkout.paycom.uz/bT01ZTczMGU4ZTBiODUyYTQxN2FhNDljZWI7YWMub3JkZXJfaWQ9MTAwMDE7YT01MDAwMDA7bD11eg==
```

`a` 的单位是 tiyin：`500000` 即 5 000 sum。

生成 Click Merchant API 的 `Auth` 请求头：

```console
$ CLICK_SECRET_KEY=... python3 skills/click/scripts/sign.py click.auth \
    -f merchant_user_id=1 -f timestamp=1762160400
input   sha1(1762160400<SECRET>)
value   1:0df3d3bac209c59a2feefb9ad688c7e003f411c3:1762160400
```

省略 `timestamp` 时使用当前时间。

不确定店铺用的是哪个公式时，可以这样检查 Multicard 状态 webhook：

```console
$ MULTICARD_SECRET=... python3 skills/multicard/scripts/sign.py multicard.webhook \
    -f uuid=u-1 -f amount=500000 -f invoice_id=10001
30501c3fbfec8d8fa0a9451049a92fda  md5(u-1500000<SECRET>)
33faffb79880f2af5ca164b7ce5e890aa87a29a2  sha1(u-110001500000<SECRET>)
```

## validate.py

```
validate.py --list [TEXT]                 list schemas: name, method, endpoint
validate.py SCHEMA PAYLOAD [--part PART]  validate PAYLOAD (file, '-' = stdin)
```

`SCHEMA` 可以是 Schema 名称（`CreateTransaction`）；同一个名称出现在两个产品中时，写成 `product/name`（`merchant/CreateTransaction`）；也可以是文件路径。

| 选项 | 用途 |
|---|---|
| `--part params` / `result` | JSON-RPC 方法：请求参数（默认）或你返回的 result |
| `--part body` / `query` / `path` | 手写的 REST Schema |
| `--part request` / `response` 配合 `--status 400` | 由 OpenAPI 生成的 Schema（`schemas/ops/*.json`） |

它会替你处理这些情况：

- JSON-RPC 信封（无论有没有 `"jsonrpc"`）和 `{success, data}` 信封都会被拆开。作为 result 传入的错误信封会被报告为错误，而不是判为有效。
- 接受 form-urlencoded 请求体（`a=1&b=2`）；在 Schema 要求数字的地方，数字字符串会按数字读取，因为表单中的每个值到达时都是字符串。
- `"<CARD_TOKEN>"` 这类占位符可以匹配任何值，并会在输出中计数。

```console
$ python3 skills/payme/scripts/validate.py CreateTransaction body.json
INVALID references/merchant/schemas/CreateTransaction.json (params): 1 problem(s)
  $.amount: expected integer, got string

$ python3 skills/uzum/scripts/validate.py --list crossborder/confirm
crossborder/confirmcredit                    POST /cbt/v1/transfer/confirm_credit Confirm Transfer to Uzbekistan
crossborder/confirmdebit                     POST /cbt/v1/transfer/confirm_debit Confirm Transfer from Uzbekistan
crossborder/confirmpayment                   POST /cbt/v1/payment/confirm_payment Confirm a Cross-border Payment
```

## 技能专用工具

有两个技能在共用的两个工具之外，还带有各自的离线脚本：

| 脚本 | 用途 |
|---|---|
| `skills/kapitalbank/scripts/purpose_codes.py` | 适用于任何银行苏姆付款指令的中央银行付款用途代码：`check` 校验代码（可加 `--date`），`old` 把旧代码映射到新代码，`search` 按文本搜索，`details` 组装并校验“Детали платежа”，`account` 结合 MFO 校验账号 |
| `skills/fiscal/scripts/mxik.py` | `check` 离线校验 17 位 MXIK（IKPU）代码；`lookup` 打印 Tasnif 链接，只有加 `--online` 才会访问 tasnif.soliq.uz；`--selftest` |

`purpose_codes.py` 输出 `OK`、`NO ...` 或 `INVALID`，输入被拒绝、未知或无效时退出码为 `1`。`mxik.py check` 遇到无效代码时退出码为 `1`。

```console
$ python3 skills/kapitalbank/scripts/purpose_codes.py old 00545
old 00545  Сантехнические товары | Сантехника товарлари
  -> 00039  ПЛАСТМАССЫ И ИЗДЕЛИЯ ИЗ НИХ | ...   [note: изготовленные из пластмассы / ...]
  -> 00068  ...
  -> 00069  ...
  -> 00076  ...
  several new codes: pick the one whose note or name fits the goods

$ python3 skills/fiscal/scripts/mxik.py check 04016001002000000
04016001002000000
  OK: 17 digits
  ...
  confirm on https://tasnif.soliq.uz/ and take the package code from the code's card
```

## 在你的 CI 中使用

这些脚本是确定性的，所以你可以在自己仓库的测试数据（fixtures）上运行它们：

```sh
for f in tests/fixtures/payme/create-*.json; do
  python3 vendor/uzfintech-skills/skills/payme/scripts/validate.py CreateTransaction "$f" || exit 1
done
```

## 维护者须知

两个脚本的源码都在 `scripts/shared/`。`scripts/lint --fix` 会把它复制到每个技能中；当某个副本出现偏差、`sign.py --selftest` 失败，或 `validate.py` 在任一 Schema 上崩溃时，`scripts/lint --only tools` 都会失败。每新增一个签名方案，都要同时在 `sign.py` 中添加测试向量。
