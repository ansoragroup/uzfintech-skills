# uzfintech-skills

[English](Home.md) · [Русский](Home.ru.md) · **Oʻzbekcha** · [简体中文](Home.zh-CN.md)

Oʻzbekiston toʻlov APIʼlari uchun agent skillari: **Uzum Bank, Alif, Click, Paynet, Payme va
Multicard**. Bu skillarni yuklagan agent API kontrakti boʻyicha aniq qaydlarga tayanib javob
beradi, imzo va payloadlarni ikkita kichik skript bilan tekshiradi hamda muddatlar, toʻlovni
bekor qilish va fiskal cheklar haqida ular productionda muammoga aylanmasdan oldin ogohlantiradi.

## Shu yerdan boshlang

| Nima qilmoqchisiz? | Sahifa |
|---|---|
| skillarni Claude Code, Codex, Cursor yoki boshqa agentga oʻrnatish | [Oʻrnatish](Install.uz.md) |
| imzo, auth header yoki payloadni tekshirish | [Vositalar](Tools.uz.md) |
| agent skillardan qanday foydalanishi va yaxshi javob qanday boʻlishini bilish | [Agentlar uchun qoʻllanma](Agent-guide.uz.md) |
| har bir provayderning vaqt oraliqlari, bekor qilish / qaytarish qoidalari va chek qoidalarini koʻrish | [Toʻlov hayot sikli](Lifecycle.uz.md) |
| skillar javoblarni yaxshilayaptimi, buni oʻlchash | [Evallar](Evals.uz.md) |
| faktni tuzatish yoki mahsulot yoxud provayder qoʻshish | [Hissa qoʻshish](Contributing.uz.md) |
| tezkor javob topish | [FAQ](FAQ.uz.md) |

## Provayderlar

| Skill | Provayder | Nimalarni qamrab oladi |
|---|---|---|
| [`uzum`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/uzum/SKILL.md) | Uzum Bank | Merchant API webhooklari, Checkout, Fiscalization, FastPay, Dynamic QR, CrossBorder, Remit Core, Ratekeeper, Nasiya, PaymentHub |
| [`alif`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/alif/SKILL.md) | Alif (alifpay) | Checkout, Payments, Cards, Hold, Monitoring, Summary, eski API xaritasi |
| [`click`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/click/SKILL.md) | Click | SHOP API, Advanced / Split Shop, Merchant API, karta tokenlari, Fiscalization, CLICK Pass, toʻlov tugmasi, Telegram Payments |
| [`paynet`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/paynet/SKILL.md) | Paynet | Humo va Uzcard uchun internet-ekvayring |
| [`payme`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/payme/SKILL.md) | Payme (Paycom) | Merchant API, Subscribe API, Checkout, Fiscalization |
| [`multicard`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/multicard/SKILL.md) | Multicard | Invoyslar, karta bogʻlash, toʻlovlar, qaytarishlar, holdlar, payoutlar, hisobotlar |

## Skill ichida nimalar bor

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

Qaydlar ochiq dasturchi hujjatlari asosida yozilgan. Har bir reference faylida manba sahifasi
va u olingan sana koʻrsatilgan. Asosiy manba baribir provayder hujjatlari boʻlib qoladi.
