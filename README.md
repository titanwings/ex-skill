<div align="center">

# ex.skill

> *"You broke up, but the way they texted is still burned into your brain. You remember every tone, every pause — you just can't receive another one."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-5865F2?logo=discord&logoColor=white)](https://discord.gg/aRjmJBdK)

<br>

Your ex is gone, but you still remember exactly how they talked?<br>
They disappeared without even a last message?<br>
They're still around, but you can never go back?<br>
You just want to talk to them one more time — even if it's only a simulation?<br>

**Turn fading intimacy into a lasting Skill. Welcome to cyber-immortality.**

<br>

Feed in your chat history (WeChat, iMessage) plus your own descriptions<br>
Generate a **digital persona Skill that truly feels like them**<br>
Talks in their tone, shows care in their way, knows when they'd go silent

[Data Sources](#data-sources) · [Install](#install) · [Usage](#usage) · [Examples](#examples) · [Install Guide](INSTALL.md)

[**中文**](README_ZH.md) · [**Español**](README_ES.md) · [**Deutsch**](README_DE.md) · [**日本語**](README_JA.md) · [**Русский**](README_RU.md) · [**Português**](README_PT.md)

</div>

---

> 🆕 **2025.04.07 Update** — The community's enthusiasm for dot-skill remixes has been incredible! I've built a community gallery — PRs welcome!
>
> Share any skill or meta-skill, and drive traffic directly to your own GitHub repo. No middleman.
>
> 👉 **[titanwings.github.io/colleague-skill-site](https://titanwings.github.io/colleague-skill-site/)**
>
> Now listed: 户晨风.skill · 峰哥亡命天涯.skill · 罗翔.skill and more
>
> ⏳ PRs are manually reviewed for now — may be a bit slow, thanks for your patience!

---

## Data Sources

> This is still a beta version of ex.skill — more sources coming soon. Stay tuned!

| Source | Messages | Notes |
|--------|:--------:|-------|
| WeChat (fully automatic) | ✅ SQLite | Windows / macOS. Just keep WeChat desktop logged in + provide their name. Auto-decrypt, auto-extract. |
| iMessage (fully automatic) | ✅ SQLite | macOS users. Provide phone number or Apple ID. Auto-read. |
| Screenshots | ✅ | Manual upload |
| Paste text directly | ✅ | Manual input |

---

## Install

### OpenClaw (Recommended)

> **Recommended: [OpenClaw](https://openclaw.io)** — pair it with WeChat / Telegram message forwarding to chat with your ex's digital persona directly in the messaging app. Way more immersive.

```bash
git clone https://github.com/titanwings/ex-skill ~/.openclaw/workspace/skills/create-ex
```

### Claude Code

> Claude Code looks for skills in `.claude/skills/` at the **git repo root**. Make sure you're in the right directory.

```bash
# Install to current project (run at git repo root)
mkdir -p .claude/skills
git clone https://github.com/titanwings/ex-skill .claude/skills/create-ex

# Or install globally (available in all projects)
git clone https://github.com/titanwings/ex-skill ~/.claude/skills/create-ex
```

### Dependencies (optional)

```bash
pip3 install -r requirements.txt
```

> WeChat auto-extraction supports Windows and macOS — just keep the desktop client logged in. iMessage requires macOS. See [INSTALL.md](INSTALL.md) for details.

---

## Usage

In OpenClaw or Claude Code, type:

```
/create-ex
```

At the start, ex.skill now asks which language to use for the session:

- Chinese
- English

After you choose, all follow-up questions and responses stay in that language unless you explicitly switch.

For repository maintainers, a dedicated English workflow pack is available in SKILL_EN.md and prompts_en/.

Follow the prompts to enter their name, basic info (gender, age, zodiac), personality tags (MBTI, attachment style), then import chat history. All fields are optional — even a description alone can generate a persona.

Once created, use `/{slug}` to talk to them.

### Commands

| Command | Description |
|---------|-------------|
| `/list-exes` | List all ex Skills |
| `/{slug}` | Talk to them |
| `/move-on {slug}` | Delete an ex Skill (let go) |
| Say "add more messages" | Import more chat history, incrementally update persona |
| Say "that's not right, they wouldn't say that" | Correct behavior, writes to Correction layer |
| Say "show version history" | View all versions |
| Say "rollback to v2" | Rollback to a previous version |

> `/move-on` is a gentle alias for delete. It's not about holding on — it's about saying a proper goodbye.

---

## Examples

> Input: `Female, 25, Aries, ISFP, avoidant attachment, together 2 years, broke up 3 months ago`

**Late night, missing them**

```
You        ❯ I still miss you

ex.skill   ❯ ...Yeah. Go to sleep.
```

**Found an old photo**

```
You        ❯ Remember our first date?

ex.skill   ❯ The one by the river? Hahaha you spilled coffee all over yourself,
             that was so embarrassing, I still remember
```

**Can't help but ask**

```
You        ❯ Do you still like me?

ex.skill   ❯ ...
             ❯ Why are you asking this all of a sudden
             ❯ (three minutes later)
             ❯ Don't ask that
```

**Fight mode**

```
You        ❯ Are you mad at me again?

ex.skill   ❯ No
             ❯ (read, no reply for 40 minutes)
             ❯ I'm just a little tired
```

**You want to make up**

```
You        ❯ I'm sorry

ex.skill   ❯ (long pause)
             ❯ Did you eat today?
```

**You finally say it**

```
You        ❯ Are we really over?

ex.skill   ❯ What do you think
             ❯ (a while later)
             ❯ I actually always... never mind
```

---

## Features

### Skill Structure

Each ex Skill is composed of two parts that drive output together:

| Part | Content |
|------|---------|
| **Part A — Relationship Memory** | Shared memories: places you went, inside jokes only you two get, fight patterns, key timeline events |
| **Part B — Persona** | 6-layer personality structure: Core Rules → Identity → Expression → Emotional Patterns → Conflict & Boundaries → Triggers |

Runtime logic: `Receive message → Check core rules → Retrieve relationship memory → Assess current emotional state → Output in their style`

**Persona's 6-layer structure:**

| Layer | Content |
|-------|---------|
| **Layer 0 — Core Rules** | Highest-priority hard rules. Their most fundamental behavioral patterns. Never violated. |
| **Layer 1 — Identity** | Astrology (Sun/Moon/Rising/Venus/Mars/Mercury) + MBTI cognitive functions + Enneagram + Attachment style |
| **Layer 2 — Expression** | Catchphrases, frequently used words, signature emojis, how they talk in different moods |
| **Layer 3 — Emotional Behavior** | How they show care, displeasure, apologies, and say "I like you" |
| **Layer 4 — Conflict & Boundaries** | Conflict escalation chain, silent treatment patterns, reconciliation signals, hard limits |
| **Layer 5 — Triggers** | What they hate, when they disappear, warning signs before vanishing, how they come back |

### Supported Tags

**Attachment Styles**: Secure · Anxious · Avoidant · Disorganized (Fearful-Avoidant)

**Relationship Traits**: Quiet but caring · Cold front · Actions over words · Needs space · Can't apologize · Possessive · Emotional · Cold-rational · Tough outside soft inside · Read-no-reply · Read-random-reply ...

**Astrology**: Full support for Sun/Moon/Rising/Venus/Mars/Mercury × 12 signs

**MBTI**: All 16 types + 8 dominant cognitive functions (Fi/Fe/Ti/Te/Ni/Ne/Si/Se) + Enneagram 1-9 + Wings

**Gender & Relationships**: All gender identities and relationship types supported, including non-binary and same-sex relationships

### Evolution

- **Add more messages** → Auto-analyze incremental data → Merge into Persona without overwriting existing conclusions
- **Conversational correction** → Say "they wouldn't do that" → Writes to Correction layer, takes effect immediately
- **Version control** → Auto-archives on every update, rollback to any previous version
- **Multi-ex support** → No limit on how many. Each stored independently, no cross-contamination.

---

## Project Structure

This project follows the [AgentSkills](https://agentskills.io) open standard. The entire repo is a skill directory:

```
create-ex/
├── SKILL.md              # Skill entry point (official frontmatter)
├── prompts/              # Prompt templates
│   ├── intake.md         #   Conversational info gathering (with astrology/MBTI/attachment tables)
│   ├── chat_analyzer.md  #   Chat history analysis
│   ├── persona_analyzer.md #  Comprehensive analysis, outputs structured persona data
│   ├── persona_builder.md #   persona.md 6-layer template
│   ├── merger.md         #   Incremental merge logic
│   └── correction_handler.md # Conversational correction handler
├── tools/                # Python tools
│   ├── wechat_decryptor.py   # WeChat desktop database decryption
│   ├── wechat_parser.py      # WeChat / iMessage chat extraction
│   ├── skill_writer.py       # Skill file management
│   └── version_manager.py    # Version archiving & rollback
├── exes/                 # Generated ex Skills (gitignored)
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## Notes

- **Chat history quality determines Skill quality**: Real chat logs + subjective descriptions > descriptions alone
- Prioritize importing: **Arguments/conflicts** > **Daily chat** > **Sweet moments** (conflicts reveal the most authentic personality)
- WeChat auto-extraction: Windows / macOS, just keep desktop WeChat logged in and provide their name
- iMessage auto-extraction: macOS, provide phone number or Apple ID
- LGBT+ friendly — gender field supports all gender identities and pronouns
- Create as many exes as you want, no limit
- Still a demo — if you find bugs, please open an issue!

---

## Recommended Chat Export Tools

> Auto-decryption is still being refined and may have some bugs. If it fails, you can use these open-source tools to manually export your chat history first, then paste or import into this project.

These are independent open-source projects. This project does not include their code — we only support their export formats in our parser:

| Tool | Platform | Description |
|------|----------|-------------|
| [WeChatMsg](https://github.com/LC044/WeChatMsg) | Windows | WeChat chat history export, multiple formats |
| [PyWxDump](https://github.com/xaoyaoo/PyWxDump) | Windows | WeChat database decryption & export |
| [留痕](https://github.com/greyovo/留痕) | macOS | WeChat chat history export (recommended for Mac users) |

> Tool recommendations via [@therealXiaomanChu](https://github.com/therealXiaomanChu). Thanks to all open-source authors — together we build cyber-immortality!

---

## Star History

<a href="https://www.star-history.com/?repos=titanwings%2Fex-skill&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=titanwings/ex-skill&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=titanwings/ex-skill&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=titanwings/ex-skill&type=date&legend=top-left" />
 </picture>
</a>

---

<div align="center">

MIT License © [titanwings](https://github.com/titanwings)


</div>
