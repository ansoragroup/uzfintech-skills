# Hissa qoʻshish

[English](Contributing.md) · [Русский](Contributing.ru.md) · **Oʻzbekcha** · [简体中文](Contributing.zh-CN.md)

Tuzatishlar, yangi mahsulotlar va yangi provayderlarni mamnuniyat bilan qabul qilamiz. Toʻliq
qoidalar [CONTRIBUTING.md](https://github.com/ansoragroup/uzfintech-skills/blob/main/CONTRIBUTING.md)
faylida. Bu sahifa — ularning qisqa varianti.

## Repozitoriy ochiq boʻlib qolishi uchun qoidalar

1. **Oʻz soʻzlaringiz bilan.** Qaydlarni oʻzingiz yozing. Maydon nomlari, turlar, kodlar,
   limitlar, URL manzillar va timeoutlar — bular fakt, ularni koʻchirish mumkin. Provayder
   matnidan butun xatboshilarni koʻchirib boʻlmaydi.
2. **Har bir faktning manbasi bor.** Har bir README oʻz provayder sahifasini va u olingan
   sanani koʻrsatadi; har bir sxemada `x-uzfintech-source` bor.
3. **Namunalar anonimlashtiriladi.** `<CARD_TOKEN>`, `100001`, `+998901234567`,
   `merchant.example.com` kabi placeholderlar ishlatiladi. Haqiqiy yoki provayder
   namunalaridagi IDʼlar, ismlar va summalar hech qachon ishlatilmaydi.
4. **Sandbox maʼlumotlari aynan saqlanadi.** Test hostlar, kartalar, OTP kodlar, test PINFL,
   ssenariylar va namuna payloadlar provayder qanday eʼlon qilgan boʻlsa, shunday
   `references/sandbox/README.md` fayliga yoziladi. Ularsiz integratsiyani tekshirib boʻlmaydi.
5. **Hayot sikli faktlari saqlanadi.** Muddatlar, bekor qilish va qaytarish qoidalari,
   takroriy soʻrov qoidalari va fiskal chek qoidalari oʻzgarmas ogohlantirish IDʼsi bilan
   `references/lifecycle/README.md` fayliga yoziladi.
6. **Tijorat shartlari yozilmaydi.** Komissiya stavkalari, payout ulushlari, tariflar va
   hisob-kitob kunlari boʻlmaydi.
7. **`SKILL.md` router boʻlib qoladi**, 180 qatordan oshmaydi. Tafsilotlar `references/`
   papkasiga yoziladi.

## PR ochishdan oldin

```sh
scripts/lint --fix        # copies scripts/shared/*.py into every skill, then checks
scripts/lint              # tools, examples, frontmatter, json, links, scan, i18n, versions, lifecycle
scripts/sync --selftest   # needs PyYAML
```

`scripts/lint` har bir tekshiruv uchun `ok` chiqarishi kerak. CI har bir PR uchun xuddi shu
buyruqlarni ishga tushiradi. Xatti-harakatni oʻzgartirgan boʻlsangiz, tegishli evalni ishga
tushiring: `claude plugin eval . --tag <provider>`.

## Faktni tuzatish

1. Fakt boshqacha yozilgan provayder sahifasini toping va PRda unga havola bering.
2. Reference README, sxema, namuna va checklist bandini birgalikda tuzating.
3. Agar `SKILL.md` bu faktni takrorlasa (qoidalar, nozik joylar, ogohlantirishlar), uni
   u yerda ham tuzating.

## Tarjimalar

README va har bir wiki sahifasi ingliz, rus, oʻzbek va soddalashtirilgan xitoy tillarida
mavjud. Avval inglizcha sahifani oʻzgartiring, keyin uchala tarjimani shu PRning oʻzida
yangilang yoki shu tilni biladigan odam bajarishi uchun issue oching.

- API nomlari, maydonlar, headerlar, kodlar, enum qiymatlari va ogohlantirish IDʼlarini hech
  qachon tarjima qilmang.
- Oʻzbekcha matn lotin yozuvida yoziladi, oʻ va gʻ harflarida apostrof emas, U+02BB (ʻ)
  belgisi ishlatiladi. `scripts/lint --only i18n` buni tekshiradi. Ruschadan soʻzma-soʻz
  emas, tabiiy oʻzbek tilida yozing.
- Xitoycha matn soddalashtirilgan ieroglif bilan yoziladi, mahsulot nomlari esa provayderlar
  qanday yozsa, shunday qoladi.

## Commitlar va PRlar

Bitta PR — bitta mavzu. Haftalik sync workflowi upstream spetsifikatsiya yoki sahifa
oʻzgarganda oʻz PRini ochadi; uni merge qilishdan oldin belgilangan sahifalarni qayta oʻqib
chiqing.
