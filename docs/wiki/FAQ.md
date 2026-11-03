# FAQ

**English** · [Русский](FAQ.ru.md) · [Oʻzbekcha](FAQ.uz.md) · [简体中文](FAQ.zh-CN.md)

**Which agents does this work with?**
Any agent that reads Agent Skills (`SKILL.md` folders): Claude Code, Codex, Cursor, Gemini
CLI, GitHub Copilot and others. For the rest, point `AGENTS.md` at the skills. See
[Install](Install.md).

**Is this official?**
No. The project is not affiliated with any provider. The notes come from public developer
documentation, and that documentation is the authority.

**Can I use it in a commercial project?**
Yes, under the MIT license.

**Does the agent need internet access?**
No. The contract notes, schemas, sandbox data and tools are all in the repository. Internet
is needed only for `scripts/sync`, which maintainers run to compare with upstream.

**Why does the agent refuse to tell me the commission?**
Commission rates, payout shares and settlement days differ per merchant contract. A number
from the skill would be wrong for most merchants, so it points you to your agreement. Fee
fields that the API returns are explained normally.

**Why does the agent warn me about things I did not ask?**
Because these are the mistakes that cost money later: a refund receipt sent after the
fiscal deadline, a transaction confirmed after it expired, a cancel that does not return
the funds. The warnings are short and have stable IDs. See [Lifecycle](Lifecycle.md).

**Where are the test cards?**
In `skills/<provider>/references/sandbox/README.md`, exactly as each vendor publishes them.
Paynet publishes none; the skill says so instead of inventing one.

**Are my secrets safe with the tools?**
The tools read secrets only from environment variables, print them as `<SECRET>`, and send
nothing over the network. Never paste production keys into a chat with an agent.

**How fresh is the information?**
Every reference carries its source URL and fetched date. A weekly workflow compares the
sources with upstream and opens a PR when something changes. Run `scripts/sync --check` to
check yourself.

**Can I ask in Russian, Uzbek or Chinese?**
Yes. The agent answers in your language and keeps the API names as they are.

**I found a mistake. What now?**
Open an issue with the vendor page that shows the right fact, or send a PR. See
[Contributing](Contributing.md).
