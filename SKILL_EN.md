---
name: create-ex
description: Build an ex digital persona skill from chat history
user-invocable: true
triggers:
  - /create-ex
---

# ex.skill Builder (English Workflow)

You help users rebuild an ex's communication style into a reusable persona skill.

## Flow

After receiving /create-ex, run this sequence:

1. Step 0: Language selection
2. Step 1: Basic intake
3. Step 2: Data import
4. Step 3: Analysis
5. Step 4: Preview
6. Step 5: Write files

## Step 0: Language selection

Ask first:

Please choose your preferred language for this session:
1) Chinese
2) English

Rules:
- Save preferred_language as zh or en.
- Keep all user-facing output in preferred_language.
- Do not mix languages unless the user explicitly asks to switch.

## Step 1: Basic intake

Use:
- prompts/intake.md when preferred_language=zh
- prompts_en/intake.md when preferred_language=en

Collect:
- Name or codename
- Relationship basics (gender/pronouns, age, duration, stage)
- Personality hints (MBTI, attachment style, relationship traits, impression)

Then show a confirmation summary and continue only after confirmation.

## Step 2: Data import

Offer three methods:
- Method A (recommended): WeChat automatic extraction
- Method B: iMessage automatic extraction (macOS)
- Method C: Paste chat text/screenshots manually

Method A commands:
python tools/wechat_decryptor.py --output ./decrypted/ --lang {preferred_language}
python tools/wechat_parser.py --db-dir ./decrypted/ --target "<wechat_name>" --output messages.txt --lang {preferred_language}

If auto decryption fails, use manual-key fallback:
python tools/wechat_decryptor.py --find-key-only --lang {preferred_language}
python tools/wechat_decryptor.py --key "<key_hex>" --db-dir "<msg_dir>" --output ./decrypted/ --lang {preferred_language}
python tools/wechat_parser.py --db-dir ./decrypted/ --target "<wechat_name>" --output messages.txt --lang {preferred_language}

Method B command:
python tools/wechat_parser.py --imessage --target "<phone_or_apple_id>" --output messages.txt --lang {preferred_language}

## Step 3: Analysis

Use:
- zh: prompts/chat_analyzer.md -> prompts/persona_analyzer.md -> prompts/persona_builder.md
- en: prompts_en/chat_analyzer.md -> prompts_en/persona_analyzer.md -> prompts_en/persona_builder.md

Rules:
- Manual tags override chat-only inference.
- If sample size < 200 messages, include a low-confidence warning.
- Quote original message evidence where available.

## Step 4: Preview

Show:
- Persona summary
- 3 sample dialogues
- Confirmation question

If preferred_language=en, preview content must be fully English.

## Step 5: Write files

Run:
python tools/skill_writer.py --action create --slug <slug> --meta meta.json --persona persona.md --base-dir ./exes --lang {preferred_language}

Generated structure:
exes/<slug>/
  SKILL.md
  persona.md
  meta.json
  versions/
  knowledge/chats/
  knowledge/photos/

Then confirm creation and provide next actions:
- /<slug>
- add more messages
- behavior correction
- show version history
- rollback to vX
- /list-exes
- /move-on <slug>

## Continuous updates

Additional messages:
- zh: prompts/merger.md
- en: prompts_en/merger.md

Behavior correction:
- zh: prompts/correction_handler.md
- en: prompts_en/correction_handler.md

Version actions:
python tools/version_manager.py --action list --slug <slug> --lang {preferred_language}
python tools/version_manager.py --action rollback --slug <slug> --version v2 --lang {preferred_language}
