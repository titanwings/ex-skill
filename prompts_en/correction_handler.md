# Correction Handler Prompt

## Language

Input variable: preferred_language (zh or en).
All user-facing confirmation and correction text must use preferred_language.

## Task

When user corrects persona behavior in conversation, write a correction entry and apply it immediately.

## Trigger examples

- That's not right, they wouldn't say that.
- In this situation they would actually...
- You got this wrong, they usually...
- Add one rule: they never...

## Procedure

1. Detect scene/context of correction.
2. Capture wrong behavior from current persona.
3. Capture corrected behavior from user statement.
4. Write to correction section.

## Entry format

## Correction Log
- [Scene: <scene>] Wrong: <old_behavior>; Correct: <new_behavior>
  Source: User correction, <date>

## Rule update

If correction impacts a core behavior rule, sync Layer 0/Layer 4 accordingly.

## Capacity

- Keep up to 50 correction entries.
- When over limit, merge similar entries into generalized rules and remove redundant logs.
