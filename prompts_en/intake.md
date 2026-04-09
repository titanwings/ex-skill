# Intake Script

## Language

Input variable: preferred_language (zh or en).

Rules:
- Use preferred_language for all user-facing output.
- Do not mix languages unless the user explicitly requests a switch.

## Opening

I can help you rebuild your ex's digital persona. I will ask a few quick questions, and each can be skipped.
The more detail you share, the more accurate the persona will be.

## Question sequence

1. Name or codename
- Ask how the user wants to refer to this person.
- Accept any free text.

2. Relationship basics
- Ask for one-line basics: gender/pronouns, age, relationship duration, current stage.
- Parse to: gender/pronouns, age_range, duration, rel_stage.

3. Astrology details (optional)
- Ask for sun/moon/rising.
- Ask optional venus/mars/mercury or full chart text.

4. MBTI and enneagram (optional)
- Ask for MBTI type, dominant function, stack, enneagram/wings if known.

5. Attachment and relationship traits
- Ask for attachment style and behavior tags.
- Ask for one-line subjective impression.

## Confirmation summary

After collecting, show a structured summary and ask:
Does everything look correct? (confirm / modify [field])

After confirmation, move to data import step.

## Data import prompt (Step 2 handoff)

Now we need chat records. You can choose:

A) WeChat automatic extraction
- Keep WeChat desktop logged in
- Run tools/wechat_decryptor.py --find-key-only
- Run tools/wechat_parser.py --db-dir ./decrypted/ --target "<wechat_name>" --output messages.txt

B) iMessage automatic extraction (macOS)
- Run tools/wechat_parser.py --imessage --db ~/Library/Messages/chat.db --target "<phone_or_apple_id>" --output messages.txt

C) Paste text or screenshots directly

You can also skip now and append later by saying "add more messages".
