# Agentlar uchun qoʻllanma

[English](Agent-guide.md) · [Русский](Agent-guide.ru.md) · **Oʻzbekcha** · [简体中文](Agent-guide.zh-CN.md)

Bu sahifa ikki xil oʻquvchi uchun: bu skillarni agentga ulaydigan odamlar va repozitoriyani
bevosita oʻqiydigan agentlar. Unda skillar qanday tuzilgani va yaxshi javob qanday boʻlishi
tushuntiriladi.

## Dizayn

Tuzilma [DeepSeek super-agent dizayni](https://offloop.org/learn/exploring-deepseek-super-agent-design)
boʻyicha router / worker boʻlinishiga asoslangan.

| Gʻoya | Skillarda qanday qoʻllanadi |
|---|---|
| Kichik router workerni tanlaydi | `SKILL.md` — router. Uning tavsifi skill qachon yuklanishini hal qiladi. Asosiy qismida mahsulotlar jadvali, "qaysi mahsulot?" jadvali, qoidalar va ogohlantirishlar bor. U 180 qatordan oshmaydi. |
| Workerlar faqat kerakli kontekstni oladi | `references/` ichidagi har bir mahsulot papkasida qaydlar, sxemalar va namunalar bor. Agent faqat vazifaga kerakli papkani ochadi. |
| Tezkor yoʻl kodda, sekin yoʻl modelda | Imzolar, auth headerlar, checkout havolalari va payload tuzilishi `sign.py` va `validate.py` orqali tekshiriladi. Model faqat kod hal qila olmaydigan joyda oʻqiydi va mulohaza yuritadi. |
| Inline va spill | Har bir vazifaga kerak boʻladigan narsa `SKILL.md` ichida turadi. Kontraktlar, sandbox maʼlumotlari va checklistlar alohida fayllarga chiqarilgan, ular kerak boʻlganda oʻqiladi. |
| Oʻzgarmas identifikatorlar | Imzo sxemalari (`click.prepare`), JSON sxema nomlari (`merchant/CreateTransaction`), ogohlantirish IDʼlari (`uzum.fiscal-receipt-24h`) va xato kodlari hech qachon oʻzgarmaydi va tarjima qilinmaydi. |
| Javob kanalga mos | Chat, PR review va kodning har biri uchun oʻz shakli bor (pastda). |
| Evallar skillarni halol saqlaydi | `evals/` ichidagi har bir holat aniq soʻzlarni emas, xatti-harakatni tekshiradi. Qarang: [Evallar](Evals.uz.md). |

## Agent vazifani qanday bajarishi kerak

1. **Bir vaqtda bitta provayderni yuklang.** Vazifa ham Payme, ham Clickka tegishli boʻlsa,
   `payme/SKILL.md` faylini oching, Payme qismini tugating, keyin `click/SKILL.md` faylini
   oching. Solishtirishni oxirida qiling. Pul birligi, auth va takroriy soʻrov qoidalari bir
   provayderdan boshqasiga koʻchmaydi: Payme tiyinda hisoblaydi, Click esa soʻmda.
2. **Mahsulotni qaror jadvalidan tanlang**, keyin uning `references/<product>/README.md` faylini
   oching. Skillda `references/common/README.md` boʻlsa, avval uni oʻqing: transport, auth va
   xato qobigʻi oʻsha yerda yozilgan.
3. **Vositalarni ishga tushiring** — imzo, header yoki payloadni toʻgʻri deb aytishdan oldin.
   Ularning natijasini keltiring.
4. **Hayot siklini tekshiring.** Vazifa biror narsani yaratsa, tasdiqlasa, bekor qilsa,
   qaytarsa, qayta yuborsa yoki fiskallashtirsa, skilldagi "Warn without being asked" blokini
   va `references/lifecycle/README.md` faylini oʻqing. Hech kim soʻramagan boʻlsa ham muddatni,
   bu qadamni ortga qaytarish mumkinmi va fiskal chek bilan nima boʻlishini ayting. Qarang:
   [Toʻlov hayot sikli](Lifecycle.uz.md).
5. **Test va namunalar uchun `references/sandbox/` papkasidagi sandbox maʼlumotlaridan
   foydalaning**: test hostlar, kartalar, OTP kodlar va ssenariylar provayder qanday eʼlon
   qilgan boʻlsa, aynan shunday. Test kartani hech qachon oʻylab topmang. Provayder test karta
   eʼlon qilmagan boʻlsa (Paynet), buni ochiq ayting.
6. **Hujjatlarda yoʻq narsani ochiq ayting.** Reference fayllarda biror fakt boʻlmasa,
   hujjatlarda bu koʻrsatilmaganini ayting va `Source:` sahifasiga havola bering. Boʻshliqni
   xotiradan toʻldirmang.
7. **Tijorat shartlarini yozmang.** Komissiya stavkalari, payout ulushlari va hisob-kitob
   kunlari har bir merchant shartnomasiga bogʻliq. API javoblaridagi fee maydonlarini
   tushuntirsa boʻladi.

## Yaxshi javob qanday boʻladi

**Chatda.** Foydalanuvchi kod soʻramagan boʻlsa, avval xulosa, taxminan 100 soʻzda. Aniq
nomlar va kodlar backtick ichida. Tegishli har bir hayot sikli bandi uchun bir qatorlik
ogohlantirish.

> Payme uni rad etyapti, chunki tranzaksiya 12 soatdan eski. Bu tranzaksiya boʻyicha
> `CreateTransaction` va `PerformTransaction` soʻrovlariga `-31008` bilan javob bering va uni
> `reason: 4` bilan bekor qiling. Buyurtmani bajarmang. Xuddi shu Payme `id` bilan kelgan
> takroriy soʻrovlarga saqlangan javobni qaytaring.
> Ogohlantirish: tranzaksiya bajarilgandan keyin pulni qaytarish faqat toʻliq
> `CancelTransaction` orqali boʻladi (state `-2`, reason `5`). Agar shundan keyin Payme
> `SetFiscalData` soʻrovini `type: CANCEL` bilan yuborsa, uni alohida chek sifatida saqlang,
> `PERFORM` chekini esa saqlab qoling.

**PR yoki reviewda.** Muammo, Oʻzgarish, Tekshiruv. Checklist boʻyicha reviewda har bir bandni
`file:line` havolasi bilan pass, fail yoki n.a. deb belgilang.

**Kodda.** Sandboxda yozilgan holicha ishlaydi, maxfiy kalitlarni muhit oʻzgaruvchilarida
saqlaydi, imzolarni xom soʻrov tanasi boʻyicha constant-time taqqoslash bilan tekshiradi va
provayderning tranzaksiya IDʼsini idempotentlik kaliti sifatida saqlaydi.

**Foydalanuvchining tilida.** Rus, oʻzbek, xitoy yoki ingliz tilida, lekin metod nomlari,
maydonlar, headerlar, kodlar va enum qiymatlari API qanday yozgan boʻlsa, aynan shunday qoladi.

## Yaxshi javob olish uchun prompt yozish

- Provayder va mahsulotni ayting: "Uzum Merchant API", "Click SHOP API", "Payme Subscribe".
- Biror narsa ishlamasa, xom soʻrov tanasi va headerlarni joylang. Vositalarga ular aynan
  yuborilgan holida kerak.
- Javob qayerga ketishini ayting: "PR tavsifi uchun", "Go handler sifatida", "qisqa, chat
  uchun".
- Review kerak boʻlsa, checklistni soʻrang: "Multicard integratsiyamizni checklist boʻyicha
  tekshirib chiq".
