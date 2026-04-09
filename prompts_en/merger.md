# Incremental Merge Prompt

## Language

Input variable: preferred_language (zh or en).
Merge report and updated content must use preferred_language.

## Task

Merge newly provided chat evidence into the existing persona.md without destructive overwrite.

## Inputs

1) Existing persona.md
2) New chat text/screenshots/analysis snippets

## Merge rules

- Additive by default.
- Do not remove existing rules unless new evidence directly disproves them.
- If conflict occurs with user-corrected rules, preserve correction and mark conflict.

## Process

1. Extract new signals with chat_analyzer logic.
2. Compare against existing persona rules.
3. Apply by type:
- New catchphrase/emoji -> Layer 2
- New emotional signal -> Layer 3
- New conflict pattern -> Layer 4
- Contradiction -> annotate with conflict note

4. Update metadata: message_count and version.

## Output

- Merge report:
  - New messages count
  - Updated layers
  - Conflict list
- Updated full persona.md
