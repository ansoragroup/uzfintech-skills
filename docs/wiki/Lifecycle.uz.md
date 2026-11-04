# Toʻlov hayot sikli

[English](Lifecycle.md) · [Русский](Lifecycle.ru.md) · **Oʻzbekcha** · [简体中文](Lifecycle.zh-CN.md)

Toʻlovlardagi eng qimmatga tushadigan xatolarning koʻpi notoʻgʻri maydon bilan bogʻliq emas.
Ular juda kech yoki ikki marta bajarilgan qadamdan kelib chiqadi: muddat tugaganidan keyin
qilingan qaytarish urinishi, kechikib yuborilgan chek, deploy paytida ishlamay qolib, pulni
toʻlovchiga jimgina qaytarib yuboradigan webhook. Bu sahifa barcha provayderlar uchun shu
qoidalarni bir joyga yigʻadi.

Har bir skill toʻliq qoidalarni `references/lifecycle/README.md` faylida saqlaydi, `SKILL.md`
esa ulardan qimmatga tushadiganlarini "Warn without being asked" boʻlimida sanab oʻtadi.
Skillni yuklagan agent vazifa toʻlovni yaratsa, tasdiqlasa, bekor qilsa, qaytarsa, qayta
yuborsa yoki fiskallashtirsa, bu ogohlantirishlarni oʻzi aytadi.

## Qisqacha

| Provayder | Xavfli vaqt oraliqlari | Toʻlovni ortga qaytarish | Fiskal chek |
|---|---|---|---|
| [Uzum Bank](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/uzum/references/lifecycle/README.md) | Fiscalization: `date_time` tasdiqlangan toʻlovdan keyin **24 soat** ichida boʻlishi kerak, aks holda 422. Merchant API: 30 daqiqadan eski `CREATED` tranzaksiya muvaffaqiyatsiz hisoblanadi. | Merchant API: siz tomondan qaytarish chaqiruvi yoʻq, Uzum sizning `/reverse` endpointingizni butun summa uchun chaqiradi. Checkout: TWO_STEP rejimida `complete` chaqirilishidan oldin `reverse`, aks holda `completedAmount` minus `refundedAmount` miqdorigacha `refund`. ONE_STEP toʻlovni reverse qilib boʻlmaydi (`3036`). | Fiskallashtirishni siz qilasiz. Istisno — avto-fiskallashtirish yoqilgan Checkout (faqat ONE_STEP, uni menejer yoqadi). Qaytarish cheki uchun sotuv avval fiskallashtirilgan boʻlishi kerak. |
| [Alif](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/alif/references/lifecycle/README.md) | Webhook taxminan **1 soat** davomida qayta yuboriladi; HTTP 200 kelmasa, toʻlov bekor qilinadi va pul qaytariladi. Holdlar **10 kundan** (Humo) yoki **30 kundan** (Uzcard) keyin tugaydi. | `refundPayment` va `refundInvoice` butun summani qaytaradi; qisman qaytarish faqat boʻlib toʻlash uchun bor. Xatolar ham HTTP 200 bilan keladi, shuning uchun faqat `SUCCEEDED` toʻlov oʻtganini bildiradi. | `spic` koʻrsatilgan `receipt` yuborsangiz, chekni Alif roʻyxatdan oʻtkazadi. Qaytarish cheki faqat sotuv cheki mavjud boʻlsa roʻyxatdan oʻtkaziladi. |
| [Click](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/click/references/lifecycle/README.md) | `payment/reversal` **joriy hisobot oyi** ichida ishlaydi, oʻtgan oy toʻlovlari uchun esa faqat keyingi oyning **1-sanasida**. CLICK Pass: **30 soniya** ichida tasdiqlash kerak. | Reversal faqat toʻliq summaga boʻladi va UZCARD uni baribir rad etishi mumkin. Pulni qaytarishning boshqa yoʻlini ham oldindan rejalashtiring. | Click `submit_items` boʻyicha fiskallashtiradi yoki siz oʻz chekingiz havolasini `submit_qrcode` bilan yuborasiz — ikkalasidan faqat bittasi. Qaytarish cheki uchun alohida chaqiruv yoʻq. |
| [Paynet](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/paynet/references/lifecycle/README.md) | `reverse` faqat toʻlovdan keyin **1 oy** ichida. OTP amal qilish muddati `ttlSeconds` maydonidan olinadi. | `reverse` chaqiring, keyin `status` orqali holatni tekshirib turing (`CANCEL_PENDING` yakuniy holat emas). Ikkinchi marta bosilmasligi uchun tugmani bloklang. | Chekni kim roʻyxatdan oʻtkazishi eʼlon qilinmagan. Ulanish bosqichida Paynetdan soʻrang. |
| [Payme](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/payme/references/lifecycle/README.md) | State `1` holatidagi tranzaksiya **12 soatdan** keyin bekor qilinadi (43 200 000 ms, reason `4`). Holdlar: **30 kun**. | Qaytarish — bajarilgan (performed) tranzaksiya boʻyicha toʻliq `CancelTransaction` (state `-2`, reason `5`). Rad etish uchun `-31007` bilan javob bering. | Payme `detail` boʻyicha fiskallashtiradi va `SetFiscalData` (`PERFORM` / `CANCEL`) yuboradi. Ularni alohida cheklar sifatida saqlang va ikkinchi chekni hech qachon oʻzingiz roʻyxatdan oʻtkazmang. |
| [Multicard](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/multicard/references/lifecycle/README.md) | Hold `expiry` **daqiqalarda** beriladi (30 kungacha). Invoys `ttl` soniyalarda (standart 1 kun). Auth token **24 soat** amal qiladi. | Toʻliq qaytarish; qisman qaytarish faqat Multicard uni terminalda yoqsa ishlaydi va bunda yangi chek fiskallashtiriladi. Payoutlarni ortga qaytarib boʻlmaydi. | Doʻkondagi `tax_registration` hal qiladi: `1` — Multicard fiskallashtiradi, `0` — siz. |
| [Atmos](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/atmos/references/lifecycle/README.md) | Hold `duration` **daqiqalarda** beriladi; `hold_till` dan oldin yeching, aks holda `STPIMS-ERR-144`. Bearer token **3600 soniya** amal qiladi. Billing callback HTTP 200 `{"status": 1}` bilan javob berishi kerak, aks holda pul yechilmaydi. | `pay/reverse` qoralama `transaction_id` ni emas, `success_trans_id` ni qabul qiladi. Qisman qaytarish: `create-reverse-partial`, keyin `ofd_items` bilan `confirm-reverse-partial`. PINFL boʻyicha yechib olishni faqat `confirm` dan oldin bekor qilish mumkin. Holdsiz MPS toʻlovi uchun qaytarish tavsiflanmagan. | `ofd_items` ni IKPU bilan yuboring; Atmos `ofd_url` qaytaradi, demak chekni u roʻyxatdan oʻtkazadi (xulosa). Toʻliq reverse uchun qaytarish cheki tavsiflanmagan. |
| [Octo](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/octo/references/lifecycle/README.md) | Ikki bosqichli hold: ikki bosqichli toʻlov sahifalariga koʻra `set_accept` **30 daqiqa** ichida (bekor qilish sahifasida Humo / Uzcard uchun 30 kungacha, Visa / Mastercard uchun 7 kun deyilgan), aks holda Octo uni bekor qiladi. Toʻlanmagan toʻlov `ttl` daqiqadan keyin tugaydi. Uch marta notoʻgʻri OTP toʻlovni bekor qiladi. | `set_accept` `cancel` faqat holdda ishlaydi. `succeeded` holatidagi toʻlov `/refund` orqali toʻliq yoki qisman qaytariladi, bir chaqiruvda kamida 1 USD ekvivalenti va koʻpi bilan 10 mln UZS. | Octo chekni bank menejeringiz oldindan roʻyxatdan oʻtkazgan `basket` pozitsiyalari boʻyicha roʻyxatdan oʻtkazadi, aks holda `error: 403`; uni `fiscal-data` bilan oʻqing. Qaytarish cheklari tavsiflanmagan. |
| [Oson](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/oson/references/lifecycle/README.md) | Invoys `lifetime` birligi hujjatlashtirilmagan (plaginlar `30` yoki `14400` yuboradi); undan keyin holat `EXPIRED`. | Hech bir plaginda bekor qilish yoki qaytarish metodi yoʻq; qaytarish Oson kabineti yoki qoʻllab-quvvatlash xizmati orqali. | Hech bir plagin chek maydonlarini yubormaydi, chekni kim roʻyxatdan oʻtkazishi hujjatlashtirilmagan. Oson tasdiqlamaguncha uni oʻzingiz roʻyxatdan oʻtkazing. |
| [Kapitalbank](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/kapitalbank/references/lifecycle/README.md) | Eski toʻlov maqsadi kodlari **26.05.2026** dan rad etiladi (yangi kodlar 06.05.2026 dan amalda). `anor: 0` (СЭП) ish kunlari 9:00–17:00 da, `anor: 1` (Anor) 24/7 ishlaydi. `fin: 0` koʻchirma yakuniy emas. | Chaqirib olish metodi eʼlon qilinmagan; bankdan soʻrang. Qayta yuborilgan `SendPaymentIBK` ikkinchi haqiqiy topshiriqnoma boʻladi. | Tegishli emas: yuridik shaxslar oʻrtasidagi toʻlov topshiriqnomalari bank oʻtkazmalaridir. |

[`fiscal`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/fiscal/references/lifecycle/README.md) skilli provayderlar boʻyicha chek
qoidalarini solishtiradi. Muddatni faqat Uzum Fiscalization eʼlon qiladi (24 soat); Payme,
Alif, Multicard, Octo va Atmos eʼlon qilmaydi, shuning uchun chekni toʻlov tasdiqlangan
zahoti roʻyxatdan oʻtkazing.

## Eng qimmatga tushadigan ogohlantirishlar

| ID | Qachon tegishli | Nima buziladi |
|---|---|---|
| `uzum.fiscal-receipt-24h` | navbat, batch yoki takroriy urinishlar siklidan yuboriladigan cheklar | 422 "date_time should be within 24 hours"; tungi batch baʼzi toʻlovlar uchun allaqachon kech boʻladi |
| `uzum.merchant-lost-confirm` | `/confirm` va `/status` handlerlari | confirm yoʻqolsa, Uzum uni qayta yubormaydi, `/status` orqali soʻraydi; javob berishdan oldin commit qiling |
| `alif.webhook-1h-auto-refund` | webhook handlerlari, ishlamay qolish, deploylar | bir soat davomida HTTP 200 boʻlmasa, toʻlov bekor qilinadi va pul qaytariladi |
| `click.reversal-month-window` | qaytarish funksiyalari | keyingi oyning 1-sanasidan keyin reversal endi mumkin emas |
| `click.complete-after-debit` | Complete handlerlari | toʻlovchidan pul allaqachon yechilgan; muvaffaqiyat bilan javob bering (xatolar faqat `-4` / `-9`), buyurtmani bajara olmasangiz, reverse qiling |
| `paynet.reverse-1-month` | qaytarish yoki bekor qilish tugmalari | bir oydan keyin `reverse` qilib boʻlmaydi |
| `payme.create-timeout-12h` | buyurtmani band qilish, Create / Perform | 12 soatdan keyin kelgan Create yoki Perform `-31008` olishi kerak; buyurtma bandlikdan chiqarilishi kerak |
| `payme.cancel-is-the-refund` | qaytarish funksiyalari | summa parametri yoʻq, shuning uchun qaytarish doim toʻlovning toʻliq summasiga boʻladi |
| `multicard.callback-reject-refunds` | `callback_url` handlerlari | javob HTTP 200 `{"success": true}` boʻlmasa, toʻlov bekor qilinadi va pul qaytariladi |
| `multicard.payout-irreversible` | payoutlar | bekor qilish yoki reversal uchun endpoint yoʻq |
| `atmos.callback-ack` | billing URL handlerlari | HTTP 200 `{"status": 1}` dan boshqa har qanday javob pul yechilmaganini bildiradi |
| `atmos.apply-no-resend` | timeout yoki 5xx dan keyingi `pay/apply`, hold yechish va confirm chaqiruvlari | pul bilan bogʻliq ikkinchi chaqiruv; buning oʻrniga holatni `pay/get` yoki `GET /hold/{id}` bilan oʻqing |
| `atmos.reverse-success-id` | qaytarish funksiyalari | `success_trans_id` oʻrniga qoralama `transaction_id` bilan `pay/reverse` |
| `octo.test-flag-real-money` | production boʻlmagan muhitlar | `test: true` boʻlmasa, `secure.octo.uz` dagi toʻlov haqiqiy |
| `octo.hold-auto-cancel` | ikki bosqichli toʻlovlar | hold tugashidan oldin `set_accept` yoʻq; Octo uni bekor qiladi va pul toʻlovchiga qaytadi |
| `oson.verify-notify-signature` | xabarnoma handlerlari | tekshirilmagan imzo soxta `PAID` ni oʻtkazib yuboradi |
| `oson.no-refund-api` | qaytarish funksiyalari | bekor qilish yoki qaytarish metodi yoʻq; qaytarish kabinet yoki qoʻllab-quvvatlash xizmati orqali |
| `kapitalbank.old-purpose-codes-rejected` | istalgan bankdagi soʻmli toʻlov topshiriqnomalari | 26.05.2026 dan keyin eski maqsad kodi bilan topshiriqnoma rad etiladi yoki kechiktiriladi |
| `kapitalbank.poll-status-not-resend` | yoʻqolgan yoki noaniq `SendPaymentIBK` javoblari | qayta yuborish ikkinchi haqiqiy topshiriqnoma yaratadi |
| `fiscal.one-receipt-per-payment` | chekni oʻzi roʻyxatdan oʻtkazadigan provayderlar | oʻz fiskal modulingizdan bitta sotuv uchun ikkinchi chek |

Har bir ID oʻz provayderining hayot sikli sahifasida aniqlangan. Biror sahifa, `SKILL.md` yoki
shu wiki aniqlanmagan IDʼni tilga olsa, `scripts/lint` xato beradi. IDʼlar hech qachon qayta
nomlanmaydi va tarjima qilinmaydi.

## Takroriy soʻrovlar va idempotentlik

Qoidalar provayderga qarab farq qiladi, shuning uchun ularni bir provayderdan boshqasiga hech
qachon koʻchirmang:

- **Uzum Merchant API:** takroriy `/create` soʻroviga `10010`, takroriy `/confirm` soʻroviga
  `10016`, takroriy `/reverse` soʻroviga `10018` qaytariladi. `/confirm` yoʻqolsa, Uzum
  `/status` orqali holatni soʻraydi.
- **Uzum Checkout:** `X-Operation-Id` har bir operatsiya uchun yagona. Uni chaqiruvdan oldin
  saqlab qoʻying; `3028` kelsa, yangi id yubormasdan `getOperationState` orqali holatni oʻqing.
- **Payme:** Create va Perform bir xil parametrlar bilan takrorlanadi, sandbox esa har bir
  metodni ikki marta yuboradi. Bir xil Payme `id` uchun saqlangan javobni qaytaring.
- **Click:** Prepare va Complete bir xil `click_trans_id` bilan yana kelishi mumkin; ularga
  bir xil javob bering.
- **Multicard:** timeout, 5xx yoki `ERROR_DEBIT_UNKNOWN` xatosidan keyin pul bilan bogʻliq
  soʻrovni hech qachon qayta yubormang. Buning oʻrniga toʻlov holatini soʻrab turing.
- **Paynet:** qayta urinsa boʻladigan xato "yana yuboring" degani emas, "`status` orqali
  tekshiring" degani.
- **Atmos:** timeout, 5xx, `STPIMS-ERR-118`, `STPIMS-ERR-065` yoki `INFO-202` dan keyin
  `pay/apply`, hold yechish, MPS apply yoki PINFL confirm ni hech qachon qayta yubormang.
  Buning oʻrniga `pay/get`, `GET /hold/{id}`, `get/ext_id` yoki `check` ni oʻqing.
- **Octo:** `shop_transaction_id` va `shop_refund_id` har bir urinish uchun yagona va
  chaqiruvdan oldin saqlanadi. Javob yoʻqolsa, holatni uch maydonli `prepare_payment`
  chaqiruvi bilan tekshiring.
- **Oson:** har bir urinish uchun yangi `transaction_id`. Javob yoʻqolsa, yangi invoys
  yaratishdan oldin xuddi shu id bilan `invoice/status` ni chaqiring.
- **Kapitalbank:** `SendPaymentIBK` dan oldin `uniq` ni saqlang. Javob yoʻqolsa,
  `CheckPayments2` dan `uniq` boʻyicha soʻrang va topshiriqnoma topilmagandagina qayta
  yuboring. Webhooklar yoʻq, shuning uchun holatni soʻrab turing.

## Qoida eʼlon qilinmagan boʻlsa

Har bir hayot sikli sahifasi "Not documented — ask the provider" boʻlimi bilan tugaydi.
Hujjatlarda muddat belgilanmagan boʻlsa (masalan, Click Prepare va Complete orasida hech
qanday vaqt chegarasini belgilamaydi), agent buni ochiq aytadi va raqamni oʻylab topish
oʻrniga provayderdan soʻrashni taklif qiladi.
