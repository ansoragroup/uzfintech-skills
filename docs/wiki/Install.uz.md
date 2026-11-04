# Oʻrnatish

[English](Install.md) · [Русский](Install.ru.md) · **Oʻzbekcha** · [简体中文](Install.zh-CN.md)

Skillar — ichida `SKILL.md` fayli bor oddiy papkalar. [Agent Skills](https://agentskills.io)
bilan ishlay oladigan har qanday agent ularni yuklay oladi. Boshqa agentlar uchun `AGENTS.md`
faylida ularga yoʻl koʻrsating.

## `skills` CLI (har qanday agent)

```sh
npx skills add ansoragroup/uzfintech-skills
```

[`skills`](https://github.com/vercel-labs/skills) CLI qaysi agentlarga oʻrnatishni va joriy
loyihaga yoki global oʻrnatishni soʻraydi. Foydali parametrlar:

| Parametr | Natija |
|---|---|
| `-g` | joriy loyihaga emas, global oʻrnatadi |
| `-a claude-code,codex` | faqat shu agentlar uchun oʻrnatadi |
| `-s payme,click` | faqat shu provayderlarni oʻrnatadi |
| `-l` | oʻrnatmasdan, repozitoriydagi skillar roʻyxatini chiqaradi |
| `-y` | barcha savollarga "ha" deb javob beradi (CI, skriptlar) |

Keyinchalik: `npx skills update`, `npx skills list`, `npx skills remove payme`.

## Claude Code plugini

```
/plugin marketplace add ansoragroup/uzfintech-skills
/plugin install uzfintech@uzfintech-skills
```

Plugin ichida skillar `uzfintech:payme`, `uzfintech:click` va hokazo deb nomlanadi. Yangilash
uchun: `/plugin marketplace update uzfintech-skills`.

## Qoʻlda nusxalash

```sh
git clone https://github.com/ansoragroup/uzfintech-skills
cp -R uzfintech-skills/skills/* ~/.claude/skills/    # Claude Code, every project
cp -R uzfintech-skills/skills/* ~/.codex/skills/     # Codex
```

Bitta loyiha uchun `<project>/.claude/skills/` papkasiga nusxalang. Papkalarni butunligicha
nusxalang: `SKILL.md` yonidagi `scripts/` va `references/` ham skillning bir qismi.

## Versiyani qotirib qoʻyish

Oʻzingiz yangilashga qaror qilmaguningizcha oʻsha kontrakt qaydlari bilan qolish uchun tag
orqali oʻrnating:

```sh
git submodule add https://github.com/ansoragroup/uzfintech-skills vendor/uzfintech-skills
git -C vendor/uzfintech-skills checkout v0.4.0
```

Har bir versiyada nima oʻzgargani
[CHANGELOG.md](https://github.com/ansoragroup/uzfintech-skills/blob/main/CHANGELOG.md)
faylida yozilgan.

## Skillarni qoʻllab-quvvatlamaydigan agentlar

Repozitoriyani loyihangiz ichiga qoʻshing (yuqoridagi submodule ham boʻladi) va loyihangizdagi
`AGENTS.md` fayliga quyidagini yozing:

```md
## Payment provider contracts
For Uzbek payment provider work (Uzum Bank, Alif, Click, Paynet, Payme, Multicard, Atmos,
Octo, Oson, Kapitalbank), read `vendor/uzfintech-skills/skills/<provider>/SKILL.md` first and
follow its pointers. To choose or compare providers, start with
`vendor/uzfintech-skills/skills/uzfintech/SKILL.md`. Run its
`scripts/sign.py` and `scripts/validate.py` instead of computing signatures by hand, and
review changes against the matching `checklists/*.md`. To look up or re-check MXIK codes in
the Tasnif catalogue, read `vendor/uzfintech-skills/skills/tasnif/SKILL.md`.
```

## Talablar

- Vositalar uchun `python3` 3.9 yoki yangirogʻi, `PATH` ichida boʻlishi kerak. Ular faqat
  standart kutubxonadan foydalanadi.
- Agent vositalarni oʻzi ishga tushirishini istasangiz, unga shell buyruqlarini bajarishga
  ruxsat bering. Claude Code uchun `Bash(python3:*)` ruxsatini qoʻshing yoki birinchi
  chaqiruvni tasdiqlang.

## Muammolarni hal qilish

| Muammo | Yechim |
|---|---|
| Agent skillni ochmasdan, xotirasidan javob beryapti | Soʻrovda provayder va mahsulot nomini yozing ("Payme Merchant API", "Click SHOP API"). Agent skillni tavsifidagi shu nomlarga qarab tanlaydi. |
| `python3: command not found` | Python 3.9+ oʻrnating yoki vositalarni oʻzingizda bor interpretator bilan chaqiring. |
| `sign.py: set CLICK_SECRET_KEY ...` | `sign.py --list` koʻrsatgan oʻzgaruvchini export qiling, masalan `CLICK_SECRET_KEY`. Vosita maxfiy kalitni hech qachon argument sifatida qabul qilmaydi. |
| Plugin oʻrnatilgan, lekin skillar koʻrinmayapti | `/plugin` buyrugʻini ishga tushiring va `uzfintech` yoqilganini tekshiring, keyin yangi sessiya boshlang. |
