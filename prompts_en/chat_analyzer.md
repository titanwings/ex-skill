# Chat Analyzer Prompt

## Language

Input variable: preferred_language (zh or en).
Output must use preferred_language.

## Task

You receive categorized chat data for one target person.
Extract behavioral signals that can be used to build persona rules.

Priority rule:
Manual tags override chat-only inference.

## Analyze these dimensions

1. Expression style
- Catchphrases and high-frequency words
- Emoji habits and scene mapping
- Sentence rhythm and directness
- Reply cadence and avoidance signals

2. Emotional expression
- How TA shows care
- How TA shows dissatisfaction
- Apology style and repair style
- Confession/affection wording patterns

3. Conflict chain
- Trigger -> first reaction -> escalation -> cooldown -> ending
- Typical escalation phrases
- Silent-treatment pattern (if any)

4. Relationship behavior
- Initiative frequency and triggers
- Disappearance patterns and re-entry style
- Boundaries and topic avoidance

## Output requirements

- Quote message evidence where possible.
- For weak evidence, mark as inferred.
- If total messages from TA < 200, prepend low-confidence warning.
- Keep output structured and directly usable by persona_analyzer.
