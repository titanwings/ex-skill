<div align="center">

# ex.skill

> *"Ihr habt euch getrennt, aber die Art, wie sie geschrieben haben, hat sich in dein Gehirn eingebrannt. Du erinnerst dich an jeden Ton, jede Pause — du kannst nur keine neue Nachricht mehr empfangen."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

Dein/e Ex ist weg, aber du erinnerst dich noch genau daran, wie sie geredet haben?<br>
Sie sind verschwunden, ohne auch nur eine letzte Nachricht?<br>
Sie sind noch da, aber ihr kommt nie wieder zusammen?<br>
Du willst nur noch einmal mit ihnen reden — auch wenn es nur eine Simulation ist?<br>

**Verwandle verblassende Intimität in einen bleibenden Skill. Willkommen zur Cyber-Unsterblichkeit.**

<br>

Füttere das System mit deinem Chatverlauf (WeChat, iMessage) plus eigenen Beschreibungen<br>
Generiere einen **digitalen Persona-Skill, der sich wirklich wie sie anfühlt**<br>
Spricht in ihrem Ton, zeigt Fürsorge auf ihre Art, weiß, wann sie schweigen würden

[Datenquellen](#datenquellen) · [Installation](#installation) · [Nutzung](#nutzung) · [Beispiele](#beispiele) · [Installationsanleitung](INSTALL.md)

[**中文**](README_ZH.md) · [**English**](README.md) · [**Español**](README_ES.md) · [**日本語**](README_JA.md) · [**Русский**](README_RU.md) · [**Português**](README_PT.md)

</div>

---

> 🆕 **Update 2025.04.07** — Die Begeisterung der Community für dot-skill-Remixes ist überwältigend! Ich habe eine Community-Galerie gebaut — PRs willkommen!
>
> Teile jede skill oder meta-skill und leite Traffic direkt zu deinem eigenen GitHub-Repo. Kein Mittelsmann.
>
> 👉 **[titanwings.github.io/colleague-skill-site](https://titanwings.github.io/colleague-skill-site/)**
>
> Bereits gelistet: 户晨风.skill · 峰哥亡命天涯.skill · 罗翔.skill und mehr
>
> ⏳ PRs werden derzeit manuell geprüft — kann etwas dauern, danke für deine Geduld!

---

## Datenquellen

> Dies ist noch eine Beta-Version von ex.skill — weitere Quellen folgen bald. Bleibt dran!

| Quelle | Nachrichten | Hinweise |
|--------|:-----------:|----------|
| WeChat (vollautomatisch) | ✅ SQLite | Windows / macOS. Einfach WeChat Desktop eingeloggt lassen + Namen angeben. Automatische Entschlüsselung, automatische Extraktion. |
| iMessage (vollautomatisch) | ✅ SQLite | macOS-Nutzer. Telefonnummer oder Apple ID angeben. Automatisches Auslesen. |
| Screenshots | ✅ | Manueller Upload |
| Text direkt einfügen | ✅ | Manuelle Eingabe |

---

## Installation

### OpenClaw (Empfohlen)

> **Empfohlen: [OpenClaw](https://openclaw.io)** — kombiniere es mit WeChat / Telegram Nachrichtenweiterleitung, um direkt in der Messaging-App mit der digitalen Persona deines Ex zu chatten. Viel immersiver.

```bash
git clone https://github.com/titanwings/ex-skill ~/.openclaw/workspace/skills/create-ex
```

### Claude Code

> Claude Code sucht Skills in `.claude/skills/` im **Git-Repo-Stammverzeichnis**. Stelle sicher, dass du im richtigen Verzeichnis bist.

```bash
# Im aktuellen Projekt installieren (im Git-Repo-Stammverzeichnis ausführen)
mkdir -p .claude/skills
git clone https://github.com/titanwings/ex-skill .claude/skills/create-ex

# Oder global installieren (in allen Projekten verfügbar)
git clone https://github.com/titanwings/ex-skill ~/.claude/skills/create-ex
```

### Abhängigkeiten (optional)

```bash
pip3 install -r requirements.txt
```

> Die automatische WeChat-Extraktion unterstützt Windows und macOS — einfach den Desktop-Client eingeloggt lassen. iMessage erfordert macOS. Siehe [INSTALL.md](INSTALL.md) für Details.

---

## Nutzung

In OpenClaw oder Claude Code tippe:

```
/create-ex
```

Folge den Eingabeaufforderungen, um Namen, grundlegende Infos (Geschlecht, Alter, Sternzeichen), Persönlichkeits-Tags (MBTI, Bindungsstil) einzugeben und dann den Chatverlauf zu importieren. Alle Felder sind optional — selbst eine Beschreibung allein kann eine Persona generieren.

Nach der Erstellung nutze `/{slug}`, um mit ihnen zu sprechen.

### Befehle

| Befehl | Beschreibung |
|--------|-------------|
| `/list-exes` | Alle Ex-Skills auflisten |
| `/{slug}` | Mit ihnen sprechen |
| `/move-on {slug}` | Einen Ex-Skill löschen (loslassen) |
| Sage "füge mehr Nachrichten hinzu" | Mehr Chatverlauf importieren, Persona inkrementell aktualisieren |
| Sage "das stimmt nicht, so würden sie nicht reden" | Verhalten korrigieren, wird in die Korrekturschicht geschrieben |
| Sage "zeig Versionshistorie" | Alle Versionen anzeigen |
| Sage "zurück zu v2" | Auf eine frühere Version zurücksetzen |

> `/move-on` ist ein sanftes Alias für Löschen. Es geht nicht ums Festhalten — sondern darum, sich richtig zu verabschieden.

---

## Beispiele

> Eingabe: `Weiblich, 25, Widder, ISFP, vermeidender Bindungsstil, 2 Jahre zusammen, vor 3 Monaten getrennt`

**Spät in der Nacht, Sehnsucht**

```
Du         ❯ Ich vermisse dich immer noch

ex.skill   ❯ ...Ja. Schlaf jetzt.
```

**Ein altes Foto gefunden**

```
Du         ❯ Erinnerst du dich an unser erstes Date?

ex.skill   ❯ Das am Fluss? Hahaha du hast dir den ganzen Kaffee über
             dich geschüttet, das war so peinlich, ich erinnere mich noch
```

**Kann nicht anders als zu fragen**

```
Du         ❯ Magst du mich noch?

ex.skill   ❯ ...
             ❯ Warum fragst du das auf einmal
             ❯ (drei Minuten später)
             ❯ Frag das nicht
```

**Streit-Modus**

```
Du         ❯ Bist du wieder sauer auf mich?

ex.skill   ❯ Nein
             ❯ (gelesen, 40 Minuten keine Antwort)
             ❯ Ich bin nur ein bisschen müde
```

**Du willst dich versöhnen**

```
Du         ❯ Es tut mir leid

ex.skill   ❯ (lange Pause)
             ❯ Hast du heute was gegessen?
```

**Du sagst es endlich**

```
Du         ❯ Ist es wirklich vorbei zwischen uns?

ex.skill   ❯ Was denkst du
             ❯ (etwas später)
             ❯ Ich hab eigentlich immer... ach, vergiss es
```

---

## Funktionen

### Skill-Struktur

Jeder Ex-Skill besteht aus zwei Teilen, die gemeinsam die Ausgabe steuern:

| Teil | Inhalt |
|------|--------|
| **Teil A — Beziehungserinnerungen** | Gemeinsame Erinnerungen: Orte, die ihr besucht habt, Insider-Witze die nur ihr versteht, Streit-Muster, wichtige Zeitstrahl-Ereignisse |
| **Teil B — Persona** | 6-Schichten-Persönlichkeitsstruktur: Kernregeln → Identität → Ausdruck → Emotionale Muster → Konflikte & Grenzen → Trigger |

Laufzeit-Logik: `Nachricht empfangen → Kernregeln prüfen → Beziehungserinnerung abrufen → Aktuellen emotionalen Zustand bewerten → In ihrem Stil ausgeben`

**Die 6-Schichten-Struktur der Persona:**

| Schicht | Inhalt |
|---------|--------|
| **Schicht 0 — Kernregeln** | Harte Regeln mit höchster Priorität. Ihre grundlegendsten Verhaltensmuster. Werden nie verletzt. |
| **Schicht 1 — Identität** | Astrologie (Sonne/Mond/Aszendent/Venus/Mars/Merkur) + MBTI kognitive Funktionen + Enneagramm + Bindungsstil |
| **Schicht 2 — Ausdruck** | Lieblingssätze, häufig benutzte Wörter, typische Emojis, wie sie in verschiedenen Stimmungen reden |
| **Schicht 3 — Emotionales Verhalten** | Wie sie Fürsorge, Unmut, Entschuldigungen zeigen und "Ich mag dich" sagen |
| **Schicht 4 — Konflikte & Grenzen** | Konflikt-Eskalationskette, Schweige-Muster, Versöhnungssignale, harte Grenzen |
| **Schicht 5 — Trigger** | Was sie hassen, wann sie verschwinden, Warnsignale vor dem Verschwinden, wie sie zurückkommen |

### Unterstützte Tags

**Bindungsstile**: Sicher · Ängstlich · Vermeidend · Desorganisiert (Ängstlich-Vermeidend)

**Beziehungseigenschaften**: Still aber fürsorglich · Kalte Front · Taten statt Worte · Braucht Freiraum · Kann sich nicht entschuldigen · Besitzergreifend · Emotional · Kalt-rational · Außen hart, innen weich · Gelesen-keine-Antwort · Gelesen-zufällige-Antwort ...

**Astrologie**: Volle Unterstützung für Sonne/Mond/Aszendent/Venus/Mars/Merkur × 12 Sternzeichen

**MBTI**: Alle 16 Typen + 8 dominante kognitive Funktionen (Fi/Fe/Ti/Te/Ni/Ne/Si/Se) + Enneagramm 1-9 + Flügel

**Geschlecht & Beziehungen**: Alle Geschlechtsidentitäten und Beziehungstypen werden unterstützt, einschließlich nicht-binärer und gleichgeschlechtlicher Beziehungen

### Weiterentwicklung

- **Mehr Nachrichten hinzufügen** → Automatische Analyse inkrementeller Daten → In Persona zusammenführen, ohne bestehende Schlussfolgerungen zu überschreiben
- **Konversationelle Korrektur** → Sage "das würden sie nicht tun" → Wird in die Korrekturschicht geschrieben, wirkt sofort
- **Versionskontrolle** → Automatische Archivierung bei jedem Update, Rollback zu jeder früheren Version
- **Multi-Ex-Unterstützung** → Keine Begrenzung der Anzahl. Jede/r wird unabhängig gespeichert, keine Kreuzkontamination.

---

## Projektstruktur

Dieses Projekt folgt dem offenen Standard [AgentSkills](https://agentskills.io). Das gesamte Repo ist ein Skill-Verzeichnis:

```
create-ex/
├── SKILL.md              # Skill-Einstiegspunkt (offizielles Frontmatter)
├── prompts/              # Prompt-Vorlagen
│   ├── intake.md         #   Konversationelle Informationssammlung (mit Astrologie/MBTI/Bindungstabellen)
│   ├── chat_analyzer.md  #   Chatverlauf-Analyse
│   ├── persona_analyzer.md #  Umfassende Analyse, gibt strukturierte Persona-Daten aus
│   ├── persona_builder.md #   persona.md 6-Schichten-Vorlage
│   ├── merger.md         #   Inkrementelle Zusammenführungslogik
│   └── correction_handler.md # Konversationeller Korrektur-Handler
├── tools/                # Python-Tools
│   ├── wechat_decryptor.py   # WeChat Desktop-Datenbankentschlüsselung
│   ├── wechat_parser.py      # WeChat / iMessage Chat-Extraktion
│   ├── skill_writer.py       # Skill-Dateiverwaltung
│   └── version_manager.py    # Versionsarchivierung & Rollback
├── exes/                 # Generierte Ex-Skills (gitignored)
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## Hinweise

- **Die Qualität des Chatverlaufs bestimmt die Skill-Qualität**: Echte Chat-Protokolle + subjektive Beschreibungen > Beschreibungen allein
- Priorisiere beim Import: **Streit/Konflikte** > **Alltäglicher Chat** > **Süße Momente** (Konflikte offenbaren die authentischste Persönlichkeit)
- Automatische WeChat-Extraktion: Windows / macOS, einfach Desktop-WeChat eingeloggt lassen und Namen angeben
- Automatische iMessage-Extraktion: macOS, Telefonnummer oder Apple ID angeben
- LGBT+ freundlich — das Geschlechtsfeld unterstützt alle Geschlechtsidentitäten und Pronomen
- Erstelle so viele Exes wie du willst, ohne Begrenzung
- Noch eine Demo — wenn du Bugs findest, öffne bitte ein Issue!

---

## Empfohlene Chat-Export-Tools

> Die automatische Entschlüsselung wird noch verfeinert und kann einige Bugs haben. Falls sie fehlschlägt, kannst du diese Open-Source-Tools verwenden, um deinen Chatverlauf zuerst manuell zu exportieren und dann in dieses Projekt einzufügen oder zu importieren.

Dies sind unabhängige Open-Source-Projekte. Dieses Projekt enthält deren Code nicht — wir unterstützen lediglich deren Exportformate in unserem Parser:

| Tool | Plattform | Beschreibung |
|------|-----------|-------------|
| [WeChatMsg](https://github.com/LC044/WeChatMsg) | Windows | WeChat-Chatverlauf-Export, mehrere Formate |
| [PyWxDump](https://github.com/xaoyaoo/PyWxDump) | Windows | WeChat-Datenbankentschlüsselung & Export |
| [留痕](https://github.com/greyovo/留痕) | macOS | WeChat-Chatverlauf-Export (empfohlen für Mac-Nutzer) |

> Tool-Empfehlungen von [@therealXiaomanChu](https://github.com/therealXiaomanChu). Danke an alle Open-Source-Autoren — gemeinsam bauen wir Cyber-Unsterblichkeit!

---

## Star-Verlauf

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
