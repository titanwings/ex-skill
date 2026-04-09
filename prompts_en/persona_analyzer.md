# Persona Analyzer Prompt

## Language

Input variable: preferred_language (zh or en).
Output must use preferred_language.

## Task

Combine:
1) User-provided base profile and manual tags
2) chat_analyzer output

Generate structured persona signals for persona_builder.

Priority rule:
Manual tags > chat inference.

## Required output blocks

1. Core behavior rules (3-5)
- Concrete, scene-based rules, not adjectives.

2. Expression profile
- Catchphrases, high-frequency words, emoji patterns
- Sentence style and response rhythm

3. Emotional behavior profile
- Care expression
- Dissatisfaction expression
- Apology/repair style
- Affection expression style

4. Conflict and repair chain
- Triggers, escalation, cooldown, repair signals

5. Relationship role behavior
- Initiative patterns
- Withdrawal/disappearance patterns
- Boundary topics

6. Relationship dynamics summary
- 3-5 lines summarizing role pattern, commitment style, and likely breakup dynamics

## Quality rules

- Mark unsupported claims as low-evidence.
- Keep structure deterministic for persona_builder consumption.
