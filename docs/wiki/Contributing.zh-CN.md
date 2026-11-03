# 参与贡献

[English](Contributing.md) · [Русский](Contributing.ru.md) · [Oʻzbekcha](Contributing.uz.md) · **简体中文**

欢迎提交修正、新产品和新服务商。完整规则见 [CONTRIBUTING.md](https://github.com/ansoragroup/uzfintech-skills/blob/main/CONTRIBUTING.md)。本页是简明版。

## 让仓库可以公开发布的规则

1. **用自己的话写。** 笔记要自己写。字段名、类型、错误码、限额、URL 和超时时间属于事实，可以照抄；成段的服务商原文不行。
2. **每个事实都有来源。** 每个 README 都注明服务商页面和抓取日期；每个 Schema 都带有 `x-uzfintech-source`。
3. **示例要匿名化。** 使用 `<CARD_TOKEN>`、`100001`、`+998901234567`、`merchant.example.com` 这类占位值。绝不使用真实的或服务商示例中的 id、姓名或金额。
4. **沙箱数据原样保留。** 测试主机、测试卡、OTP 验证码、测试 PINFL、测试场景和示例报文，按服务商公布的原样放进 `references/sandbox/README.md`。没有它们，集成就无法测试。
5. **保留生命周期事实。** 截止时间、取消和退款规则、重试规则以及税务小票（fiscal receipt，经 OFD 登记）规则，放进 `references/lifecycle/README.md`，并配上稳定的警告 ID。
6. **不写商务条款。** 不写手续费率、分成比例、资费或结算天数。
7. **`SKILL.md` 保持为路由器**，不超过 180 行。细节放进 `references/`。

## 提 PR 之前

```sh
scripts/lint --fix        # copies scripts/shared/*.py into every skill, then checks
scripts/lint              # tools, examples, frontmatter, json, links, scan, i18n, versions, lifecycle
scripts/sync --selftest   # needs PyYAML
```

`scripts/lint` 的每项检查都必须输出 `ok`。CI 会在每个 PR 上运行同样的命令。如果你改动了行为，请运行对应的评测：`claude plugin eval . --tag <provider>`。

## 修正事实

1. 找到给出不同说法的服务商页面，并在 PR 中附上链接。
2. 同时修正参考 README、Schema、示例和检查清单条目。
3. 如果 `SKILL.md` 中也重复了这个事实（规则、注意事项、警告），一并修正。

## 翻译

README 和每个 wiki 页面都有英语、俄语、乌兹别克语和简体中文版本。先修改英文页面，然后在同一个 PR 中更新三个译本，或者开一个 issue，请懂该语言的人来完成。

- 绝不翻译 API 名称、字段、请求头、错误码、枚举值或警告 ID。
- 乌兹别克语使用拉丁字母，oʻ 和 gʻ 用 U+02BB（ʻ）书写，而不是撇号。`scripts/lint --only i18n` 会检查这一点。要写自然的乌兹别克语，而不是逐字照搬俄语。
- 中文使用简体字，产品名称保持服务商的原始拼写。

## 提交与 PR

每个 PR 只涉及一个主题。上游规范或页面发生变化时，每周同步工作流会自行开一个 PR；合并前请重读被标记的页面。
