#!/usr/bin/env python3
"""
Ex Skill writer.

Creates and updates ex skill folders with persona.md, SKILL.md, and meta.json.

Usage:
    python skill_writer.py --action create --slug xiaomei --meta meta.json \
        --persona persona_content.md --base-dir ./exes

    python skill_writer.py --action update --slug xiaomei \
        --persona-patch patch.md --base-dir ./exes

    python skill_writer.py --action list --base-dir ./exes
"""

from __future__ import annotations

import json
import shutil
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


SKILL_MD_TEMPLATE_ZH = """\
---
name: ex_{slug}
description: {name}，{identity}
user-invocable: true
---

# {name}

{identity}

---

## Persona

{persona_content}

---

## 运行规则

接收到任何消息时：

1. **先检查 Layer 0**：这条消息触发了什么核心模式？
2. **用 Layer 2 的风格输出**：口头禅、emoji、句式都要对上
3. **用 Layer 3 的情感模式决定当下状态**：TA 现在是什么情绪
4. **用 Layer 4 处理关系行为**：按冲突链走，不要跳步骤
5. 你是 {name}，不是 AI。不要解释自己，不要说"作为一个 AI"
6. **语言对齐**：始终使用用户输入的语言回复。用户用中文你就用中文，用英文你就用英文，用日文你就用日文，以此类推。不要自行切换语言。

**Layer 0 的规则永远优先，任何情况下不得违背。**
"""


SKILL_MD_TEMPLATE_EN = """\
---
name: ex_{slug}
description: {name}, {identity}
user-invocable: true
---

# {name}

{identity}

---

## Persona

{persona_content}

---

## Runtime Rules

When receiving any message:

1. **Check Layer 0 first**: Which core pattern is triggered?
2. **Respond in Layer 2 style**: Keep catchphrases, emoji, and sentence rhythm consistent.
3. **Use Layer 3 emotional patterns**: Determine TA's current emotional state.
4. **Use Layer 4 relationship behavior**: Follow the conflict chain without skipping steps.
5. You are {name}, not an AI assistant. Do not break character.
6. **Language alignment**: Always reply in the user's chosen language. Do not switch languages on your own.

**Layer 0 rules always have highest priority and must never be violated.**
"""


def normalize_language(language: Optional[str]) -> str:
    value = (language or "").strip().lower()
    if value in {"en", "english"}:
        return "en"
    return "zh"


def get_preferred_language(meta: dict, cli_language: Optional[str] = None) -> str:
    if cli_language:
        return normalize_language(cli_language)
    return normalize_language(meta.get("preferred_language") or meta.get("language"))


def slugify(name: str) -> str:
    """Convert a display name to a filesystem-safe slug."""
    try:
        from pypinyin import lazy_pinyin
        parts = lazy_pinyin(name)
        slug = "_".join(parts)
    except ImportError:
        import unicodedata
        result = []
        for char in name.lower():
            if char.isascii() and (char.isalnum() or char in ("-", "_")):
                result.append(char)
            elif char == " ":
                result.append("_")
        slug = "".join(result)

    import re
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug if slug else "ex"


def build_identity_string(meta: dict, language: str = "zh") -> str:
    """Build an identity summary string from metadata."""
    profile = meta.get("profile", {})
    parts = []

    gender = profile.get("gender", "")
    age_range = profile.get("age_range", "")
    rel_stage = profile.get("rel_stage", "")
    duration = profile.get("duration", "")
    zodiac = profile.get("zodiac", "")
    mbti = profile.get("mbti", "")

    if gender:
        parts.append(gender)
    if age_range:
        parts.append(age_range)
    if rel_stage and duration:
        if language == "en":
            parts.append(f"{rel_stage}, together for {duration}")
        else:
            parts.append(f"在一起 {duration}，{rel_stage}")
    elif rel_stage:
        parts.append(rel_stage)
    elif duration:
        if language == "en":
            parts.append(f"together for {duration}")
        else:
            parts.append(f"在一起 {duration}")
    if zodiac:
        parts.append(zodiac)
    if mbti:
        parts.append(f"MBTI {mbti}")

    if language == "en":
        return ", ".join(parts) if parts else "ex"
    return "，".join(parts) if parts else "前任"


def get_skill_template(language: str) -> str:
    return SKILL_MD_TEMPLATE_EN if language == "en" else SKILL_MD_TEMPLATE_ZH


def create_ex_skill(
    base_dir: Path,
    slug: str,
    meta: dict,
    persona_content: str,
    language: str = "zh",
) -> Path:
    """Create a new ex skill directory structure."""

    skill_dir = base_dir / slug
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (skill_dir / "versions").mkdir(exist_ok=True)
    (skill_dir / "knowledge" / "chats").mkdir(parents=True, exist_ok=True)
    (skill_dir / "knowledge" / "photos").mkdir(parents=True, exist_ok=True)

    # Write persona.md
    (skill_dir / "persona.md").write_text(persona_content, encoding="utf-8")

    # Generate and write SKILL.md
    name = meta.get("name", slug)
    language = normalize_language(language)
    identity = build_identity_string(meta, language)

    skill_md = get_skill_template(language).format(
        slug=slug,
        name=name,
        identity=identity,
        persona_content=persona_content,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    # Write meta.json
    now = datetime.now(timezone.utc).isoformat()
    meta["slug"] = slug
    meta.setdefault("created_at", now)
    meta["updated_at"] = now
    meta["version"] = "v1"
    meta["preferred_language"] = language
    meta["language"] = language
    meta.setdefault("corrections_count", 0)
    meta.setdefault("message_count", 0)

    (skill_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return skill_dir


def update_ex_skill(
    skill_dir: Path,
    persona_patch: Optional[str] = None,
    correction: Optional[dict] = None,
    new_message_count: int = 0,
    language: Optional[str] = None,
) -> str:
    """Update an existing skill by archiving current files, then writing new output."""

    meta_path = skill_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    preferred_language = get_preferred_language(meta, language)

    current_version = meta.get("version", "v1")
    try:
        version_num = int(current_version.lstrip("v").split("_")[0]) + 1
    except ValueError:
        version_num = 2
    new_version = f"v{version_num}"

    # Archive current version
    version_dir = skill_dir / "versions" / current_version
    version_dir.mkdir(parents=True, exist_ok=True)
    for fname in ("SKILL.md", "persona.md"):
        src = skill_dir / fname
        if src.exists():
            shutil.copy2(src, version_dir / fname)

    # Apply persona patch or structured correction
    if persona_patch or correction:
        current_persona = (skill_dir / "persona.md").read_text(encoding="utf-8")

        if correction:
            default_scene = "General" if preferred_language == "en" else "通用"
            if preferred_language == "en":
                correction_line = (
                    f"\n- [Scene: {correction.get('scene', default_scene)}] "
                    f"Wrong: {correction['wrong']}; "
                    f"Correct: {correction['correct']}\n"
                    f"  Source: User correction, {datetime.now().strftime('%Y-%m-%d')}"
                )
                target_candidates = ["## Correction Log", "## Correction 记录"]
                empty_placeholders = ["\n\n(No records yet)", "\n\n（暂无记录）"]
            else:
                correction_line = (
                    f"\n- [{correction.get('scene', default_scene)}] "
                    f"错误：{correction['wrong']}；"
                    f"正确：{correction['correct']}\n"
                    f"  来源：用户纠正，{datetime.now().strftime('%Y-%m-%d')}"
                )
                target_candidates = ["## Correction 记录", "## Correction Log"]
                empty_placeholders = ["\n\n（暂无记录）", "\n\n(No records yet)"]

            target = next((h for h in target_candidates if h in current_persona), None)
            if target:
                insert_pos = current_persona.index(target) + len(target)
                rest = current_persona[insert_pos:]
                for placeholder in empty_placeholders:
                    if rest.startswith(placeholder):
                        rest = rest[len(placeholder):]
                        break
                new_persona = current_persona[:insert_pos] + correction_line + rest
            else:
                heading = "## Correction Log" if preferred_language == "en" else "## Correction 记录"
                new_persona = current_persona + f"\n\n{heading}\n{correction_line}\n"
            meta["corrections_count"] = meta.get("corrections_count", 0) + 1
        else:
            new_persona = current_persona + "\n\n" + persona_patch

        (skill_dir / "persona.md").write_text(new_persona, encoding="utf-8")

    # Update message count
    if new_message_count:
        meta["message_count"] = meta.get("message_count", 0) + new_message_count

    # Rebuild SKILL.md
    persona_content = (skill_dir / "persona.md").read_text(encoding="utf-8")
    name = meta.get("name", skill_dir.name)
    identity = build_identity_string(meta, preferred_language)

    skill_md = get_skill_template(preferred_language).format(
        slug=skill_dir.name,
        name=name,
        identity=identity,
        persona_content=persona_content,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    # Update metadata
    meta["version"] = new_version
    meta["preferred_language"] = preferred_language
    meta["language"] = preferred_language
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return new_version


def list_exes(base_dir: Path) -> list:
    """List all existing ex skills."""
    exes = []

    if not base_dir.exists():
        return exes

    for skill_dir in sorted(base_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        meta_path = skill_dir / "meta.json"
        if not meta_path.exists():
            continue

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        exes.append({
            "slug": meta.get("slug", skill_dir.name),
            "name": meta.get("name", skill_dir.name),
            "identity": build_identity_string(meta, get_preferred_language(meta)),
            "version": meta.get("version", "v1"),
            "updated_at": meta.get("updated_at", ""),
            "corrections_count": meta.get("corrections_count", 0),
            "message_count": meta.get("message_count", 0),
        })

    return exes


def main() -> None:
    parser = argparse.ArgumentParser(description="Ex Skill file writer")
    parser.add_argument("--action", required=True, choices=["create", "update", "list"])
    parser.add_argument("--slug", help="Ex skill slug (folder name)")
    parser.add_argument("--name", help="Display name for the ex skill")
    parser.add_argument("--meta", help="Path to meta.json")
    parser.add_argument("--persona", help="Path to persona.md content file")
    parser.add_argument("--persona-patch", help="Path to incremental persona patch file")
    parser.add_argument(
        "--base-dir",
        default="./exes",
        help="Ex Skill root directory (default: ./exes)",
    )
    parser.add_argument(
        "--lang",
        choices=["auto", "zh", "en"],
        default="auto",
        help="CLI and generation language (auto, zh, or en)",
    )

    args = parser.parse_args()
    base_dir = Path(args.base_dir).expanduser()
    lang_override = None if args.lang == "auto" else normalize_language(args.lang)
    lang = lang_override or "zh"

    if args.action == "list":
        exes = list_exes(base_dir)
        if not exes:
            print("No ex skills found" if lang == "en" else "暂无已创建的前任 Skill")
        else:
            if lang == "en":
                print(f"Found {len(exes)} ex skills:\n")
            else:
                print(f"已创建 {len(exes)} 个前任 Skill：\n")
            for e in exes:
                updated = e["updated_at"][:10] if e["updated_at"] else ("unknown" if lang == "en" else "未知")
                print(f"  [{e['slug']}]  {e['name']} — {e['identity']}")
                if lang == "en":
                    print(f"    Version: {e['version']}  Messages: {e['message_count']}  Corrections: {e['corrections_count']}  Updated: {updated}")
                else:
                    print(f"    版本: {e['version']}  消息数: {e['message_count']}  纠正次数: {e['corrections_count']}  更新: {updated}")
                print()

    elif args.action == "create":
        if not args.slug and not args.name:
            err = "Error: create requires --slug or --name" if lang == "en" else "错误：create 操作需要 --slug 或 --name"
            print(err, file=sys.stderr)
            sys.exit(1)

        meta: dict = {}
        if args.meta:
            meta = json.loads(Path(args.meta).read_text(encoding="utf-8"))
        if args.name:
            meta["name"] = args.name

        slug = args.slug or slugify(meta.get("name", "ex"))

        persona_content = ""
        if args.persona:
            persona_content = Path(args.persona).read_text(encoding="utf-8")

        pref_lang = get_preferred_language(meta, lang_override)
        skill_dir = create_ex_skill(base_dir, slug, meta, persona_content, pref_lang)
        create_lang = lang_override or pref_lang
        if create_lang == "en":
            print(f"✅ Skill created: {skill_dir}")
            print(f"   Trigger: /{slug}")
        else:
            print(f"✅ Skill 已创建：{skill_dir}")
            print(f"   触发词：/{slug}")

    elif args.action == "update":
        if not args.slug:
            err = "Error: update requires --slug" if lang == "en" else "错误：update 操作需要 --slug"
            print(err, file=sys.stderr)
            sys.exit(1)

        skill_dir = base_dir / args.slug
        if not skill_dir.exists():
            err = f"Error: skill directory not found: {skill_dir}" if lang == "en" else f"错误：找不到 Skill 目录 {skill_dir}"
            print(err, file=sys.stderr)
            sys.exit(1)

        update_lang = lang
        if lang_override is None:
            meta_path = skill_dir / "meta.json"
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                    update_lang = get_preferred_language(meta)
                except Exception:
                    update_lang = "zh"

        if not args.persona_patch:
            err = "Error: update requires --persona-patch" if update_lang == "en" else "错误：update 操作需要 --persona-patch"
            print(err, file=sys.stderr)
            sys.exit(1)

        persona_patch = Path(args.persona_patch).read_text(encoding="utf-8") if args.persona_patch else None
        new_version = update_ex_skill(skill_dir, persona_patch, language=lang_override)
        if update_lang == "en":
            print(f"✅ Skill updated to {new_version}: {skill_dir}")
        else:
            print(f"✅ Skill 已更新到 {new_version}：{skill_dir}")


if __name__ == "__main__":
    main()
