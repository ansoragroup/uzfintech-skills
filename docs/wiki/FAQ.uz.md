# FAQ

[English](FAQ.md) · [Русский](FAQ.ru.md) · **Oʻzbekcha** · [简体中文](FAQ.zh-CN.md)

**Bu qaysi agentlar bilan ishlaydi?**
Agent Skills (`SKILL.md` papkalari) bilan ishlay oladigan har qanday agent: Claude Code, Codex,
Cursor, Gemini CLI, GitHub Copilot va boshqalar. Qolganlari uchun `AGENTS.md` faylida
skillarga yoʻl koʻrsating. Qarang: [Oʻrnatish](Install.uz.md).

**Bu rasmiy loyihami?**
Yoʻq. Loyiha hech qaysi provayderga aloqador emas. Qaydlar ochiq dasturchi hujjatlari asosida
yozilgan va asosiy manba oʻsha hujjatlar hisoblanadi.

**Uni tijorat loyihasida ishlatsam boʻladimi?**
Ha, MIT litsenziyasi asosida.

**Agentga internet kerakmi?**
Yoʻq. Kontrakt qaydlari, sxemalar, sandbox maʼlumotlari va vositalar — hammasi repozitoriyda.
Internet faqat `scripts/sync` uchun kerak, uni maintainerlar upstream bilan solishtirish uchun
ishga tushiradi.

**Nega agent menga komissiyani aytmaydi?**
Komissiya stavkalari, payout ulushlari va hisob-kitob kunlari har bir merchant shartnomasida
har xil. Skilldagi raqam koʻpchilik merchantlar uchun notoʻgʻri boʻlardi, shuning uchun agent
sizni shartnomangizga yoʻnaltiradi. API qaytaradigan fee maydonlari odatdagidek tushuntiriladi.

**Nega agent men soʻramagan narsalar haqida ogohlantiradi?**
Chunki aynan shu xatolar keyinchalik pulga tushadi: fiskal muddat oʻtgandan keyin yuborilgan
qaytarish cheki, muddati tugagandan keyin tasdiqlangan tranzaksiya, pulni qaytarmaydigan bekor
qilish. Ogohlantirishlar qisqa va oʻzgarmas IDʼlarga ega. Qarang: [Toʻlov hayot sikli](Lifecycle.uz.md).

**Test kartalar qayerda?**
`skills/<provider>/references/sandbox/README.md` faylida, har bir provayder qanday eʼlon qilgan
boʻlsa, aynan shunday. Paynet test karta eʼlon qilmaydi; skill karta oʻylab topish oʻrniga buni
ochiq aytadi.

**Vositalar maxfiy kalitlarimni xavfsiz saqlaydimi?**
Vositalar maxfiy kalitlarni faqat muhit oʻzgaruvchilaridan oʻqiydi, ularni `<SECRET>` deb
chiqaradi va tarmoq orqali hech narsa yubormaydi. Production kalitlarini agent bilan chatga
hech qachon joylamang.

**Maʼlumotlar qanchalik yangi?**
Har bir reference faylida manba URL manzili va u olingan sana bor. Haftalik workflow manbalarni
upstream bilan solishtiradi va biror narsa oʻzgarsa, PR ochadi. Oʻzingiz tekshirish uchun
`scripts/sync --check` buyrugʻini ishga tushiring.

**Rus, oʻzbek yoki xitoy tilida soʻrasam boʻladimi?**
Ha. Agent sizning tilingizda javob beradi, API nomlarini esa oʻzgartirmaydi.

**Xato topdim. Endi nima qilay?**
Toʻgʻri faktni koʻrsatadigan provayder sahifasi bilan issue oching yoki PR yuboring. Qarang:
[Hissa qoʻshish](Contributing.uz.md).
