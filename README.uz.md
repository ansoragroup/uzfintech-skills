# uzfintech-skills

[English](README.md) · [Русский](README.ru.md) · **Oʻzbekcha** · [简体中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-10%20providers-0a7c66.svg)](#provayderlar)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-d97757.svg)](#oʻrnatish)
[![Python 3.9+ stdlib](https://img.shields.io/badge/tools-python3%20stdlib-3776ab.svg)](#vositalar)

Oʻzbekiston toʻlov provayderlari APIʼlari uchun agent skillari: **Uzum Bank, Alif, Click,
Paynet, Payme, Multicard, Atmos, Octo, Oson va Kapitalbank**, shuningdek ularning hammasi
uchun umumiy fiskal chek skilli hamda provayder tanlash va solishtirish uchun router skill.
Ular Claude Code, Codex, Cursor va `SKILL.md` fayllarini oʻqiy oladigan boshqa har qanday
agentda ishlaydi.

Modellar bu APIʼlarni yuzaki biladi. Tiyin bilan soʻmni adashtiradi, notoʻgʻri satrni
imzolaydi, xato kodlari va sandbox kartalarini oʻzidan toʻqib chiqaradi. Skillar bilan agent
taxmin qilmaydi: API kontrakti boʻyicha aniq qaydlarga tayanib javob beradi, imzo va
payloadlarni esa skriptlar bilan tekshiradi. Har bir skillda quyidagilar bor:

- endpointlar, auth headerlar, imzolar, pul birliklari va holatlar sxemasi (state machine);
- qisqartirilgan JSON Schemalar, xato kodlari, idempotentlik va takroriy soʻrov qoidalari;
- anonimlashtirilgan soʻrov va javob namunalari;
- provayderning sandbox maʼlumotlari, hech oʻzgarishsiz: test hostlar, test kartalar, OTP kodlar,
  ssenariylar;
- integratsiyani tekshirish uchun checklistlar;
- `sign.py` va `validate.py` — hech qanday bogʻliqliksiz ishlaydigan ikkita deterministik vosita.

## Provayderlar

| Skill | Provayder | Mahsulotlar |
|---|---|---|
| [`uzum`](skills/uzum/SKILL.md) | Uzum Bank | Merchant API (webhooklar), Checkout, Fiscalization, FastPay, Dynamic QR, CrossBorder, Remit Core, Ratekeeper, Nasiya, PaymentHub |
| [`alif`](skills/alif/SKILL.md) | Alif (alifpay) | Checkout, Alif Nasiya muddatli toʻlovi, Payments, Cards, Hold, Monitoring, Summary, eski APIʼdan oʻtish xaritasi |
| [`click`](skills/click/SKILL.md) | Click | SHOP API, Advanced / Split Shop, Merchant API, karta tokenlari, Fiscalization, CLICK Pass, toʻlov havolasi / tugmasi / vidjeti, Telegram Payments |
| [`paynet`](skills/paynet/SKILL.md) | Paynet | Internet-ekvayring (Humo / Uzcard): authorize, confirm, status, reverse |
| [`payme`](skills/payme/SKILL.md) | Payme (Paycom) | Merchant API, Subscribe API (kartalar, cheklar, holdlar), Checkout (GET / POST / tugma / QR), Fiscalization |
| [`multicard`](skills/multicard/SKILL.md) | Multicard | Invoyslar va scanpay, karta bogʻlash, toʻlovlar (token / karta / ilova / split), qaytarishlar, holdlar, payoutlar, hisobotlar |
| [`atmos`](skills/atmos/SKILL.md) | Atmos | Toʻlovlar (Uzcard / Humo: pay-create / pre-apply / apply, multi-toʻlovlar, toʻliq va qisman reverse, toʻlov sahifasi, HTML vidjet), karta bogʻlash, holdlar, PINFL boʻyicha yechib olish, Visa / Mastercard (MPS / IPS), Callback API |
| [`octo`](skills/octo/SKILL.md) | Octo | Visa / Mastercard / UnionPay va Uzcard / Humo ekvayringi: toʻlov sahifasi (bir bosqichli / ikki bosqichli), oʻz karta formangiz (PCI DSS), karta tokenlari, toʻliq va qisman qaytarish, fiskallashtirish (basket, fiscal-data) |
| [`oson`](skills/oson/SKILL.md) | Oson | Invoice API (pay_url qaytaradigan invoice/create, invoice/status) va imzolangan toʻlov xabarnomasi, Osonning ochiq kodli doʻkon plaginlari asosida tiklangan |
| [`kapitalbank`](skills/kapitalbank/SKILL.md) | Kapitalbank | Yuridik shaxslar uchun Kapital API: APILogin, SendPaymentIBK toʻlov topshiriqnomalari, CheckPayments2, koʻchirmalar (GetDoc1C, GetMT940), hisob va oluvchini tekshirish, valyuta kurslari, hisob-fakturalar; istalgan bankdagi soʻmli toʻlov topshiriqnomalari uchun Markaziy bank toʻlov maqsadi kodlari |
| [`fiscal`](skills/fiscal/SKILL.md) | Barcha provayderlar | Fiskal cheklar: Tasnifdagi MXIK (IKPU) kodlari, qadoq kodlari, QQS va imtiyoz maydonlari, Asl Belgisi markirovkasi, chek turlari, har bir provayderda chekni kim va qaysi maydonda roʻyxatdan oʻtkazadi |
| [`uzfintech`](skills/uzfintech/SKILL.md) | Barcha provayderlar | Router: vazifa uchun provayder tanlash, provayderlarni solishtirish, barcha provayderlar boʻyicha shpargalka (pul birliklari, auth, callbacklar, qaytarishlar, holdlar, fiskallashtirish, test hostlar), UzQR boʻyicha qaydlar |

Vazifa provayder tanlash yoki solishtirish boʻlsa, `uzfintech` skillidan boshlang. U
kontrakt saqlanadigan provayder skilliga yoʻl koʻrsatadi.

## Oʻrnatish

### Har qanday agent: `skills` CLI

```sh
npx skills add ansoragroup/uzfintech-skills
```

[`skills`](https://github.com/vercel-labs/skills) CLI qaysi agentlarga oʻrnatishni (Claude Code,
Codex, Cursor, Gemini CLI, GitHub Copilot va boshqalar) hamda global yoki faqat bitta loyiha
uchun oʻrnatishni soʻraydi. Faqat bitta provayderni oʻrnatish uchun `--skill payme` qoʻshing.

### Claude Code: plugin

```
/plugin marketplace add ansoragroup/uzfintech-skills
/plugin install uzfintech@uzfintech-skills
```

Yangilash uchun: `/plugin marketplace update uzfintech-skills`. Plugin ichida skillar
`uzfintech:payme`, `uzfintech:click` va hokazo deb nomlanadi.

### Qoʻlda nusxalash

```sh
git clone https://github.com/ansoragroup/uzfintech-skills
cp -R uzfintech-skills/skills/* ~/.claude/skills/    # Claude Code, all projects
cp -R uzfintech-skills/skills/* ~/.codex/skills/     # Codex
```

Faqat bitta loyiha uchun kerak boʻlsa, oʻrniga `<project>/.claude/skills/` papkasiga nusxalang.

### Skillarni qoʻllab-quvvatlamaydigan agentlar: AGENTS.md

Repozitoriyani loyihangiz ichiga qoʻshing (masalan, `vendor/uzfintech-skills` yoʻlida git
submodule sifatida) va loyihangizdagi `AGENTS.md` fayliga quyidagini yozing:

```md
## Payment provider contracts
For Uzbek payment provider work (Uzum Bank, Alif, Click, Paynet, Payme, Multicard, Atmos,
Octo, Oson, Kapitalbank), read `vendor/uzfintech-skills/skills/<provider>/SKILL.md` first and
follow its pointers. To choose or compare providers, start with
`vendor/uzfintech-skills/skills/uzfintech/SKILL.md`. Run its
`scripts/sign.py` and `scripts/validate.py` instead of computing signatures by hand, and
review changes against the matching `checklists/*.md`.
```

Yangilash, versiyani qotirib qoʻyish va muammolarni hal qilish haqida
[Oʻrnatish wiki sahifasida](docs/wiki/Install.uz.md) yozilgan.

## Qanday ishlaydi

Har bir skill router va workerlarga boʻlingan: kichik router qayerga borishni hal qiladi,
ish esa faqat kerakli kontekst berilgan alohida joylarda bajariladi.

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

- **Bitta skill — bitta provayder.** Bir nechta provayderga tegishli vazifada har bir skill
  alohida yuklanadi, solishtirish esa oxirida qilinadi. Pul birligi, auth yoki takroriy
  soʻrovlar kabi qoidalar bir provayderdan boshqasiga hech qachon koʻchirilmaydi.
  `uzfintech` routeri tanlash va solishtirishga yordam beradi, keyin ishni provayder
  skilliga topshiradi. Barcha provayderlar uchun umumiy chek kodlari (MXIK, qadoq kodlari,
  markirovka) `fiscal` skillida.
- **Avval tezkor yoʻl (fast path).** Imzolar, auth headerlar, checkout havolalari va payload
  tuzilishini model emas, kod hisoblaydi. Agent vositani ishga tushiradi va uning natijasini
  keltiradi.
- **Inline va spill.** `SKILL.md` ichida faqat har bir vazifada kerak boʻladigan narsa turadi.
  Kontraktlar, sxemalar, namunalar, sandbox maʼlumotlari va checklistlar alohida fayllarda,
  agent ularni kerak boʻlganda oʻqiydi.
- **Oʻzgarmas identifikatorlar.** Imzo sxemalari (`payme.basic`, `click.prepare`), sxema
  nomlari (`uzum/webhook-confirm`) va xato kodlari barcha tillarda bir xil, ular hech qachon
  tarjima qilinmaydi.
- **Javob kanalga mos.** Chatda agent avval xulosani beradi, taxminan 100 soʻzda. PR yoki
  review uchun Muammo, Oʻzgarish, Tekshiruv tartibida yozadi. Sizning tilingizda javob beradi,
  lekin API nomlarini oʻzgartirmaydi.
- **Soʻralmasa ham ogohlantiradi.** Toʻlov xatolari vaqt oraliqlarida va ortga qaytarib
  boʻlmaydigan qadamlarda yashirinadi. Vazifa toʻlovni yaratsa, tasdiqlasa, bekor qilsa,
  qaytarsa, qayta yuborsa yoki fiskallashtirsa, agent muddatni, bu qadamni ortga qaytarish
  mumkinmi va fiskal chek bilan nima boʻlishini aytadi — siz soʻramagan boʻlsangiz ham.
  Qarang: [Hayot sikli ogohlantirishlari](#hayot-sikli-ogohlantirishlari).

## Hayot sikli ogohlantirishlari

Har bir skillda `references/lifecycle/README.md` fayli bor. Unda provayderning muddatlari va
vaqt oraliqlari, bekor qilish / reverse / qaytarish qoidalari, takroriy soʻrov va idempotentlik
qoidalari, hold va OTP amal qilish muddatlari hamda fiskal chek qoidalari yigʻilgan. Qimmatga
tushadiganlari `SKILL.md` ichidagi "Warn without being asked" boʻlimiga kiritilgan, har biri
oʻzgarmas ID bilan. Masalan, `uzum.fiscal-receipt-24h`: Uzum fiskal chekidagi `date_time`
toʻlovdan keyin 24 soat ichida boʻlishi kerak, shuning uchun qaytarish chekini keyingi haftada
shunchaki yuborib boʻlmaydi.

Hammasi bitta jadvalda: [Toʻlov hayot sikli wiki sahifasi](docs/wiki/Lifecycle.uz.md).

## Vositalar

Har bir skill bilan birga `scripts/sign.py` va `scripts/validate.py` keladi. Ularga faqat
`python3` (3.9+) va standart kutubxona kerak. Maxfiy kalitlar muhit oʻzgaruvchilaridan
olinadi va natijada `<SECRET>` deb koʻrsatiladi.

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

Xato `input` qatorida koʻrinib turibdi. Click `amount=1000.00` yuborgan va aynan shu satrni
imzolagan. Bizning handler summani son sifatida oʻqib, uni `1000.0` qilib qayta yigʻgan,
shuning uchun `body.txt` ichida endi Click imzolagan satr yoʻq. Qiymatlarni qanday kelgan
boʻlsa, xuddi shunday xom holida imzolang.

```console
$ python3 skills/payme/scripts/validate.py CreateTransaction body.json
INVALID references/merchant/schemas/CreateTransaction.json (params): 1 problem(s)
  $.amount: expected integer, got string
```

`validate.py` JSON-RPC va `{success, data}` qobiqlarini (envelope) ochadi, form-urlencoded
soʻrov tanalarini oʻqiy oladi va `<PLACEHOLDER>` qiymatlarini tekshirmasdan oʻtkazib yuboradi.
Ikkala vosita ham muvaffaqiyatda `0`, mos kelmaslikda `1`, notoʻgʻri ishlatilganda `2` kodi
bilan chiqadi, shuning uchun ularni CI jarayonida ham ishlatsa boʻladi. Barcha sxemalar
[Vositalar wiki sahifasida](docs/wiki/Tools.uz.md).

Ikki skillning oʻz oflayn vositasi bor: `skills/kapitalbank/scripts/purpose_codes.py`
Markaziy bank toʻlov maqsadi kodlarini qidiradi va tekshiradi, `skills/fiscal/scripts/mxik.py` esa MXIK
kodlarini tekshiradi, Tasnifda qidirish faqat alohida flag bilan yoqiladi.

## Sinab koʻring

- "Click bizning Prepare `sign_string` notoʻgʻri deyapti. Mana soʻrov tanasi."
- "Payme Merchant API `CreateTransaction` metodini `-31008` / `-31050` xatolari bilan yozib ber."
- "Uzum Merchant `/confirm` nima yuboradi va takroriy soʻrovga nima deb javob berishim kerak?"
- "Alif webhook imzosini Go tilida tekshirib ber."
- "Uzum Checkout sandboxida qaysi test kartalar va OTP kodlar ishlatiladi?"
- "Multicard integratsiyamizni checklist boʻyicha tekshirib chiq."
- "Qaysi provayderlar mablagʻni hold qilib, keyin yecha oladi? Atmos va Octoni solishtir."
- "Toʻlov topshiriqnomamizda hali ham 00545 maqsad kodi turibdi. Uning oʻrniga nima?"
- "Payme sandboxida qaysi test kartalardan foydalanish mumkin?"

## Sifat

| Tekshiruv | Buyruq | Nimani isbotlaydi |
|---|---|---|
| Repozitoriy linti | `scripts/lint` | vositalar sinxron va oʻz-oʻzini tekshiruvdan oʻtgan, har bir namuna oʻz sxemasiga mos, frontmatter spetsifikatsiya doirasida, buzilgan havolalar yoʻq, anonimlashtirish tekshiruvi oʻtgan, tarjimalar joyida, versiyalar bir-biriga mos, har bir ogohlantirish ID oʻz hayot sikli sahifasida aniqlangan |
| Parser self-test | `scripts/sync --selftest` | ichki YAML parser PyYAML bilan bir xil natija beradi |
| Xatti-harakat evallari | `claude plugin eval . --runs 3` | skill ulangan agent toʻgʻri provayderni yuklaydi, aniq kodlarni keltiradi, vositalarni ishga tushiradi va sandbox maʼlumotlari yoki tijorat shartlarini oʻylab topmaydi |

21 ta eval holati [`evals/`](evals/README.md) papkasida. CI har bir PR uchun lintni ishga
tushiradi.

## Dolzarblik

Har bir reference faylida manba URL manzili va u olingan sana yozilgan. Haftada bir marta
`.github/workflows/sync.yml` workflowi `scripts/sync` skriptini ishga tushiradi, OpenAPI
asosida yaratilgan fayllarni qayta generatsiya qiladi va upstream spetsifikatsiya yoki hujjat
sahifasi oʻzgarsa, PR ochadi. Merge qilishdan oldin belgilangan sahifalarni odam qayta oʻqib
chiqadi.

```sh
scripts/sync --check            # report only; exit 1 when upstream changed
scripts/sync                    # regenerate derived files, update sources.yaml
```

## Hujjatlar

Toʻliq qoʻllanmalar [wikida](docs/wiki/Home.uz.md):
[Oʻrnatish](docs/wiki/Install.uz.md) · [Vositalar](docs/wiki/Tools.uz.md) ·
[Agentlar uchun qoʻllanma](docs/wiki/Agent-guide.uz.md) · [Toʻlov hayot sikli](docs/wiki/Lifecycle.uz.md) ·
[Evallar](docs/wiki/Evals.uz.md) · [Hissa qoʻshish](docs/wiki/Contributing.uz.md) · [FAQ](docs/wiki/FAQ.uz.md)

## Hissa qoʻshish

Tuzatishlar, yangi mahsulotlar va yangi provayderlarni mamnuniyat bilan qabul qilamiz.
[CONTRIBUTING.md](CONTRIBUTING.md) faylini oʻqing: unda kontent qoidalari (provayder matnini
soʻzma-soʻz koʻchirmaslik, namunalarni anonimlashtirish, sandbox maʼlumotlarini aynan saqlash,
tijorat shartlarini yozmaslik) va PR ochishdan oldin bajariladigan tekshiruvlar tushuntirilgan.
Xavfsizlik muammolari haqida [SECURITY.md](SECURITY.md) faylida yozilganidek xabar bering.

## Masʼuliyatdan voz kechish

Bu loyiha u qamrab olgan toʻlov provayderlarining hech biriga aloqador emas. Qaydlar ochiq
dasturchi hujjatlari asosida yozilgan va asosiy manba oʻsha hujjatlar hisoblanadi.
Productionda qanday ishlashini provayderingiz bilan aniqlashtiring. Komissiya stavkalari va
hisob-kitob shartlari har bir merchant shartnomasiga bogʻliq, shuning uchun skillar ularni
koʻrsatmaydi. Haqiqiy kirish maʼlumotlari yoki mijozlar maʼlumotlarini hech qachon commit
qilmang.

## Litsenziya

[MIT](LICENSE)
