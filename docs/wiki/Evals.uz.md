# Evallar

[English](Evals.md) · [Русский](Evals.ru.md) · **Oʻzbekcha** · [简体中文](Evals.zh-CN.md)

Skillar xatti-harakat boʻyicha tekshiriladi.
[`evals/`](https://github.com/ansoragroup/uzfintech-skills/tree/main/evals) ichidagi har bir
holat — dasturchi haqiqatan yuborishi mumkin boʻlgan soʻrov va javobdagi muhim narsalarni
tekshiradigan graderlar: toʻgʻri skill yuklandimi, xato kodi aniqmi, vosita ishga
tushirildimi, test karta oʻylab topilmadimi.

## Ishga tushirish

Sizga `claude plugin eval` buyrugʻi bor [Claude Code](https://claude.com/claude-code) kerak.

```sh
claude plugin eval . --runs 3                              # every case, three runs each
claude plugin eval . --tag payme                           # one provider
claude plugin eval . --case click-sign-mismatch --allow-tools Bash
claude plugin eval . --ablation with-without               # also run without the skills
```

- `--allow-tools Bash` agentga `sign.py` skriptini ishga tushirishga ruxsat beradi. `tools`
  holatlariga bu kerak.
- `--ablation with-without` har bir holatni skillar bilan va skillarsiz ishga tushiradi. Ikki
  natija orasidagi farq — skillar qoʻshadigan foyda. `skill` graderlari faqat "with"
  variantida hisobga olinadi.
- Butun toʻplamni bir marta ishga tushirish taxminan $2 turadi. Xarajatga chek qoʻyish uchun
  `--max-cost-usd` parametridan foydalaning.

CI jarayonida `.github/workflows/ci.yml` ichidagi `evals` jobi talab boʻyicha ishga tushadi
(`evals: true` bilan workflow dispatch), agar `ANTHROPIC_API_KEY` secreti oʻrnatilgan boʻlsa:

```sh
claude plugin eval . --runs 3 --allow-tools Bash --trust-plugin --no-publish \
  --threshold 0.8 --max-cost-usd 20 --json results.json
```

## Holat formati

```
evals/<case>/prompt.md       frontmatter: name, tags, runs, max_turns, allowed_tools
evals/<case>/graders/*.md    one grader per file
```

| Grader | Nimani tekshiradi | Nima uchun ishlatiladi |
|---|---|---|
| `regex` | yakuniy javobdagi pattern (`flags: i`, `match: contains`) | aniq kodlar, maydon nomlari, raqamlar |
| `tool_used` | vosita chaqirilganini, uning kirish maʼlumotlari boʻyicha `input_match` bilan | toʻgʻri skill yuklangani, `sign.py` ishga tushirilgani |
| `llm` | hakam model javobni yozma mezonlar asosida baholaydi | pattern bilan ifodalab boʻlmaydigan narsalar, masalan "karta raqamini oʻylab topmaydi" |

Holat faqat `EVAL_*` muhit oʻzgaruvchilarini oʻrnatishi mumkin. Sandbox qiymatlarini promptning
oʻziga yozing.

## Yaxshi holat yozish

1. Dasturchi qanday soʻrasa, shunday soʻrang. Qaysi tuzoqni tekshirayotganingizni aytmang.
2. Iloji boricha `regex` graderini ishlating. `llm` mezonlarini shunday yozingki, qoʻshimcha
   tafsilotlari bor toʻgʻri javob baribir oʻtsin, notoʻgʻrisi esa oʻtmasin.
3. Har bir grader bitta xatti-harakatni tekshirsin. Eng muhimlariga koʻproq vazn bering.
4. Yangi holatni uch marta ishga tushiring. Toʻgʻri javob har safar oʻtishi kerak.

Hozirgi holatlar va ularning har biri nimani tekshirishi
[`evals/README.md`](https://github.com/ansoragroup/uzfintech-skills/blob/main/evals/README.md)
faylida keltirilgan.
