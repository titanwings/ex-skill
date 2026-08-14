"""
Telegram 聊天记录解析器

支持格式：
  - Telegram Desktop 导出的 JSON（result.json）
  - Telegram Desktop 导出的 HTML（不推荐，用 JSON）

如何导出：
  1. 打开 Telegram Desktop
  2. 进入与 TA 的对话
  3. 右上角菜单 → 导出聊天记录
  4. 格式选「JSON」，取消勾选媒体文件（可选）
  5. 点击导出，得到 result.json

用法：
  # 解析 Telegram JSON 导出
  python telegram_parser.py --json ./result.json --output messages.txt

  # 列出导出文件中所有参与者（用于群组导出）
  python telegram_parser.py --json ./result.json --list-contacts

  # 指定 TA 的名字（群组聊天时需要）
  python telegram_parser.py --json ./result.json --target "Имя Фамилия" --output messages.txt

  # 仅输出原始 JSON（调试用）
  python telegram_parser.py --json ./result.json --raw-json

依赖：
  pip install python-dateutil  # 仅在日期解析失败时需要
"""

import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime


# ─── 关键词分类 ────────────────────────────────────────────────────────────────

CONFLICT_KEYWORDS = [
    # 中文
    "生气", "烦", "不想", "算了", "随便", "无所谓", "分手", "冷静", "伤心",
    "委屈", "失望", "不理", "沉默", "怎么了", "有什么问题", "道歉",
    # 俄语 / 英语
    "злой", "обидно", "расстался", "надоело", "устал", "sorry", "расстались",
    "прости", "не хочу", "всё", "хватит", "достало", "ignore", "disappointed",
    "angry", "upset", "break up", "leave me", "whatever",
]

SWEET_KEYWORDS = [
    # 中文
    "喜欢", "爱你", "想你", "宝贝", "亲爱", "么么", "抱抱", "好想",
    "心动", "甜", "开心", "幸福", "陪", "在一起",
    # 俄语 / 英语
    "люблю", "скучаю", "милый", "милая", "дорогой", "дорогая", "обнимаю",
    "love you", "miss you", "darling", "sweetheart", "❤", "😘", "🥰",
]


# ─── 解析 Telegram JSON ────────────────────────────────────────────────────────

def _extract_text(text_field) -> str:
    """
    Telegram JSON 的 text 字段可能是字符串或混合列表：
    "Hello" 或 [{"type": "bold", "text": "Hello"}, " world"]
    """
    if isinstance(text_field, str):
        return text_field
    if isinstance(text_field, list):
        parts = []
        for item in text_field:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(item.get("text", ""))
        return "".join(parts)
    return ""


def _parse_date(date_str: str) -> str:
    """Нормализует дату из Telegram JSON в читаемый вид."""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return date_str or ""


def load_telegram_export(json_path: str) -> dict:
    """Загружает и проверяет JSON-экспорт Telegram."""
    path = Path(json_path)
    if not path.exists():
        print(f"错误：文件不存在：{json_path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"错误：JSON 解析失败：{e}", file=sys.stderr)
            sys.exit(1)
    if "messages" not in data:
        print("错误：这不是有效的 Telegram 导出文件（缺少 messages 字段）", file=sys.stderr)
        sys.exit(1)
    return data


def list_participants(data: dict) -> list[dict]:
    """Возвращает всех участников беседы с количеством сообщений."""
    counts: dict[str, int] = {}
    for msg in data.get("messages", []):
        if msg.get("type") != "message":
            continue
        sender = msg.get("from") or msg.get("actor") or "Unknown"
        counts[sender] = counts.get(sender, 0) + 1
    return [{"name": name, "count": cnt} for name, cnt in sorted(counts.items(), key=lambda x: -x[1])]


def detect_my_name(data: dict) -> str | None:
    """
    В личных чатах Telegram экспорт содержит только двух участников.
    Имя владельца аккаунта — тот, кто отправляет сообщения с from_id начинающимся на 'user'.
    Heuristic: если тип чата personal_chat, второй участник — «TA».
    """
    chat_type = data.get("type", "")
    if chat_type != "personal_chat":
        return None
    participants = list_participants(data)
    if len(participants) == 2:
        # Имя чата обычно совпадает с именем собеседника
        chat_name = data.get("name", "")
        for p in participants:
            if p["name"] == chat_name:
                return None  # chat_name — это TA, значит второй — me
        # Если не совпало, предполагаем первый по убыванию — TA
    return None


def extract_messages(data: dict, target_name: str | None = None) -> list[dict]:
    """
    Извлекает сообщения из Telegram-экспорта.

    target_name: имя «TA» (собеседника). Если None — пытается определить автоматически
                 для личных чатов (собеседник = имя чата).
    """
    chat_type = data.get("type", "")
    chat_name = data.get("name", "")

    # Автоопределение TA для личных чатов
    if target_name is None:
        if chat_type == "personal_chat":
            target_name = chat_name
            print(f"自动识别对话对象：{target_name}")
        else:
            print("错误：群组聊天需要用 --target 指定 TA 的名字", file=sys.stderr)
            sys.exit(1)

    messages: list[dict] = []
    skipped = 0

    for msg in data.get("messages", []):
        if msg.get("type") != "message":
            skipped += 1
            continue

        sender_name = msg.get("from") or msg.get("actor") or ""
        text = _extract_text(msg.get("text", ""))

        # Пропускаем пустые (фото, стикеры без подписи и т.д.)
        if not text.strip():
            skipped += 1
            continue

        sender = "them" if sender_name == target_name else "me"
        timestamp = _parse_date(msg.get("date", ""))

        messages.append({
            "sender": sender,
            "content": text.strip(),
            "timestamp": timestamp,
        })

    if skipped:
        print(f"（已跳过 {skipped} 条非文本消息：贴纸/照片/服务消息）")

    return messages


# ─── 分类 & 格式化（与 wechat_parser 相同逻辑）─────────────────────────────────

def classify_messages(messages: list[dict], target_name: str = "them") -> dict:
    their_messages = [m for m in messages if m["sender"] == "them"]

    long_msgs, conflict_msgs, sweet_msgs, daily_msgs = [], [], [], []

    for msg in their_messages:
        content = msg["content"]
        if len(content) > 50:
            long_msgs.append(msg)
        elif any(kw in content for kw in CONFLICT_KEYWORDS):
            conflict_msgs.append(msg)
        elif any(kw in content for kw in SWEET_KEYWORDS):
            sweet_msgs.append(msg)
        else:
            daily_msgs.append(msg)

    return {
        "long_messages": long_msgs,
        "conflict_messages": conflict_msgs,
        "sweet_messages": sweet_msgs,
        "daily_messages": daily_msgs,
        "total_their_count": len(their_messages),
        "total_count": len(messages),
        "all_messages": messages,
    }


def format_output(target_name: str, classified: dict, include_context: bool = True) -> str:
    lines = [
        "# Telegram 聊天记录提取结果",
        f"目标人物：{target_name}",
        f"TA 发送的消息数：{classified['total_their_count']}",
        f"对话总消息数：{classified['total_count']}",
        "",
        "---",
        "",
        "## 长消息（>50字，权重最高：观点/情绪/解释）",
        "",
    ]

    for msg in classified["long_messages"]:
        ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
        lines.append(f"{ts}{msg['content']}")
        lines.append("")

    lines += ["---", "", "## 冲突/情绪消息（争吵/道歉/分手/冷战相关）", ""]

    for msg in classified["conflict_messages"]:
        ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
        lines.append(f"{ts}{msg['content']}")
        lines.append("")

    lines += ["---", "", "## 甜蜜消息（表白/想念/日常关心）", ""]

    for msg in classified["sweet_messages"]:
        ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
        lines.append(f"{ts}{msg['content']}")
        lines.append("")

    lines += ["---", "", f"## 日常闲聊（共 {len(classified['daily_messages'])} 条，全部输出）", ""]

    for msg in classified["daily_messages"]:
        ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
        lines.append(f"{ts}{msg['content']}")

    if include_context:
        all_msgs = classified["all_messages"]
        lines += [
            "",
            "---",
            "",
            f"## 完整对话（共 {len(all_msgs)} 条，按时间顺序）",
            "（格式：[时间] 发送方: 内容）",
            "",
        ]
        for msg in all_msgs:
            sender_label = target_name if msg["sender"] == "them" else "我"
            ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
            lines.append(f"{ts}{sender_label}: {msg['content']}")

    return "\n".join(lines)


def print_participant_list(participants: list[dict]):
    if not participants:
        print("未找到参与者数据")
        return
    print(f"找到 {len(participants)} 个参与者：\n")
    print(f"{'名字':<40} {'消息数':<10}")
    print("-" * 50)
    for p in participants:
        print(f"{p['name']:<40} {p['count']:<10}")


# ─── 主程序 ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Telegram 聊天记录解析器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 解析个人对话（自动识别 TA）
  python telegram_parser.py --json ./result.json --output messages.txt

  # 查看群组中的所有参与者
  python telegram_parser.py --json ./result.json --list-contacts

  # 指定 TA 的名字（群组或自动识别失败时）
  python telegram_parser.py --json ./result.json --target "Имя Фамилия" --output messages.txt

  # 输出原始 JSON（调试用）
  python telegram_parser.py --json ./result.json --raw-json
        """
    )

    parser.add_argument("--json", dest="json_path", required=True, help="Telegram 导出的 result.json 文件路径")
    parser.add_argument("--target", help="TA 的名字（个人聊天可省略，自动识别）")
    parser.add_argument("--output", default=None, help="输出文件路径（默认打印到 stdout）")
    parser.add_argument("--list-contacts", action="store_true", help="列出所有参与者")
    parser.add_argument("--no-context", action="store_true", help="不包含完整对话")
    parser.add_argument("--raw-json", action="store_true", help="输出原始 JSON 消息（调试用）")

    args = parser.parse_args()

    data = load_telegram_export(args.json_path)

    if args.list_contacts:
        participants = list_participants(data)
        print_participant_list(participants)
        return

    messages = extract_messages(data, args.target)
    target_name = args.target or data.get("name", "TA")

    if not messages:
        print("警告：未找到文本消息", file=sys.stderr)
        print("提示：确认文件是 Telegram JSON 导出，且对话包含文字消息", file=sys.stderr)
        sys.exit(1)

    their_count = sum(1 for m in messages if m["sender"] == "them")
    print(f"\n提取完成：共 {len(messages)} 条消息，其中 TA 发出 {their_count} 条")

    if their_count < 200:
        print(f"⚠️  警告：TA 的消息只有 {their_count} 条，样本偏少，生成的人格可信度较低")

    if args.raw_json:
        output_content = json.dumps(messages, ensure_ascii=False, indent=2)
    else:
        classified = classify_messages(messages, target_name)
        output_content = format_output(target_name, classified, include_context=not args.no_context)

    if args.output:
        Path(args.output).write_text(output_content, encoding="utf-8")
        print(f"已保存到：{args.output}")
    else:
        print(output_content)


if __name__ == "__main__":
    main()
