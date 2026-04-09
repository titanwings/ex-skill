#!/usr/bin/env python3
"""
Chat parser (WeChat + iMessage).

Supported platforms:
    - WeChat Desktop (Windows): decrypted MSG*.db files
    - iMessage (macOS): ~/Library/Messages/chat.db

Usage:
    # WeChat - extract from a decrypted DB directory
    python wechat_parser.py --db-dir ./decrypted/ --target "contact_name" --output messages.txt

    # WeChat - list all contacts
    python wechat_parser.py --db-dir ./decrypted/ --list-contacts

    # iMessage - extract from macOS chat.db
    python wechat_parser.py --imessage --db ~/Library/Messages/chat.db \
            --target "+1xxxxxxxxxx" --output messages.txt

    # iMessage - list all iMessage contacts
    python wechat_parser.py --imessage --db ~/Library/Messages/chat.db --list-contacts

    # Parse an exported text file (generic)
    python wechat_parser.py --txt ./chat_export.txt --target "contact_name" --output messages.txt

Dependencies:
    sqlite3 (Python standard library, no extra install needed)

iMessage access note:
    On macOS, grant Full Disk Access to your terminal/Python process.
"""

import sqlite3
import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional


CLI_LANG = "zh"


def normalize_language(language: Optional[str]) -> str:
    value = (language or "").strip().lower()
    if value in {"en", "english"}:
        return "en"
    return "zh"


def tr(zh: str, en: str) -> str:
    return en if CLI_LANG == "en" else zh


# ─── WeChat Desktop database structure ─────────────────────────────────────────

# Message table structure in MSG*.db (WeChat 3.x)
MSG_QUERY = """
SELECT
    m.localId,
    m.MsgSvrID,
    m.Type,
    m.IsSender,
    m.CreateTime,
    m.StrContent,
    n.UsrName AS talker_wxid
FROM MSG m
LEFT JOIN Name2ID n ON n.UsrName = (
    SELECT UsrName FROM Name2ID WHERE _id = m.TalkerId LIMIT 1
)
WHERE m.Type = 1  -- 1 = text message
ORDER BY m.CreateTime ASC
"""

# More generic query (compatible across versions)
MSG_QUERY_SIMPLE = """
SELECT
    localId,
    Type,
    IsSender,
    CreateTime,
    StrContent
FROM MSG
WHERE Type = 1
ORDER BY CreateTime ASC
"""

# Contacts table in MicroMsg.db
CONTACT_QUERY = """
SELECT
    UserName,
    Alias,
    Remark,
    NickName,
    Type
FROM Contact
WHERE Type != 4   -- 4 = deleted
ORDER BY NickName
"""


# ─── Database parsing ───────────────────────────────────────────────────────────

def open_db(db_path: str) -> Optional[sqlite3.Connection]:
    """Open a SQLite database in read-only mode."""
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        # Quick sanity check
        conn.execute("SELECT name FROM sqlite_master LIMIT 1")
        return conn
    except sqlite3.DatabaseError as e:
        print(tr(f"无法打开数据库 {db_path}：{e}", f"Cannot open database {db_path}: {e}"), file=sys.stderr)
        print(tr("请确认数据库已解密（运行 wechat_decryptor.py）", "Please make sure the database is decrypted first (run wechat_decryptor.py)."), file=sys.stderr)
        return None


def get_tables(conn: sqlite3.Connection) -> list[str]:
    """Get all table names in a database."""
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return [row[0] for row in rows]


def list_contacts(db_dir: str) -> list[dict]:
    """List all contacts from MicroMsg.db."""
    micro_db = Path(db_dir) / "MicroMsg.db"
    if not micro_db.exists():
        print(tr("未找到 MicroMsg.db，尝试从消息数据库推断联系人...", "MicroMsg.db not found, trying to infer contacts from message databases..."), file=sys.stderr)
        return []

    conn = open_db(str(micro_db))
    if not conn:
        return []

    try:
        contacts = []
        for row in conn.execute(CONTACT_QUERY):
            contacts.append({
                "wxid": row["UserName"],
                "alias": row["Alias"] or "",
                "remark": row["Remark"] or "",
                "nickname": row["NickName"] or "",
            })
        return contacts
    except Exception as e:
        print(tr(f"读取联系人失败：{e}", f"Failed to read contacts: {e}"), file=sys.stderr)
        return []
    finally:
        conn.close()


def find_contact_wxid(db_dir: str, target_name: str) -> Optional[str]:
    """Find a contact wxid by name (nickname/remark/wxid)."""
    contacts = list_contacts(db_dir)
    target_lower = target_name.lower()

    # Exact match
    for c in contacts:
        if (target_lower == c["wxid"].lower() or
                target_lower == c["remark"].lower() or
                target_lower == c["nickname"].lower() or
                target_lower == c["alias"].lower()):
            return c["wxid"]

    # Fuzzy match
    for c in contacts:
        if (target_lower in c["wxid"].lower() or
                target_lower in c["remark"].lower() or
                target_lower in c["nickname"].lower()):
            print(tr(
                f"模糊匹配到联系人：{c['remark'] or c['nickname']} ({c['wxid']})",
                f"Fuzzy matched contact: {c['remark'] or c['nickname']} ({c['wxid']})",
            ))
            return c["wxid"]

    return None


def extract_messages_from_db(db_path: str, target_wxid: Optional[str] = None) -> list[dict]:
    """Extract messages from a single MSG*.db file."""
    conn = open_db(db_path)
    if not conn:
        return []

    tables = get_tables(conn)
    messages = []

    try:
        if "MSG" not in tables:
            return []

        # Try the full query with TalkerId join first
        try:
            if "Name2ID" in tables:
                rows = conn.execute("""
                    SELECT
                        m.localId,
                        m.Type,
                        m.IsSender,
                        m.CreateTime,
                        m.StrContent,
                        n.UsrName AS talker_wxid
                    FROM MSG m
                    LEFT JOIN Name2ID n ON n._id = m.TalkerId
                    WHERE m.Type = 1
                    ORDER BY m.CreateTime ASC
                """).fetchall()
            else:
                rows = conn.execute(MSG_QUERY_SIMPLE).fetchall()
                rows = [dict(r) | {"talker_wxid": None} for r in rows]
        except Exception:
            rows = conn.execute(MSG_QUERY_SIMPLE).fetchall()
            rows = [dict(r) | {"talker_wxid": None} for r in rows]

        for row in rows:
            if isinstance(row, sqlite3.Row):
                row = dict(row)

            # Filter by the target contact (exact match only)
            talker = row.get("talker_wxid") or ""
            if target_wxid:
                if not talker:
                    # Name2ID join failed; cannot filter this row reliably.
                    continue
                if talker != target_wxid:
                    continue

            content = row.get("StrContent", "") or ""
            if not content.strip():
                continue

            # Skip system/media placeholder messages
            if content.strip() in ["[图片]", "[语音]", "[文件]", "[视频]", "[撤回了一条消息]", ""]:
                continue

            # For XML-rich content (shares/miniprograms), extract readable text.
            if content.strip().startswith("<"):
                content = _extract_text_from_xml(content)
                if not content:
                    continue

            ts = row.get("CreateTime", 0) or 0
            try:
                timestamp = datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                timestamp = str(ts)

            messages.append({
                "sender": "me" if row.get("IsSender", 0) == 1 else "them",
                "content": content.strip(),
                "timestamp": timestamp,
                "talker_wxid": talker or "",
            })

    except Exception as e:
        print(tr(f"读取消息失败 ({db_path})：{e}", f"Failed to read messages ({db_path}): {e}"), file=sys.stderr)
    finally:
        conn.close()

    return messages


def _extract_text_from_xml(xml_content: str) -> str:
    """Extract readable text from WeChat XML-rich messages."""
    # Extract <title> text
    m = re.search(r"<title[^>]*>([^<]+)</title>", xml_content)
    if m:
        return tr(f"[分享] {m.group(1).strip()}", f"[Share] {m.group(1).strip()}")
    # Extract <des> text
    m = re.search(r"<des[^>]*>([^<]+)</des>", xml_content)
    if m:
        return tr(f"[分享] {m.group(1).strip()}", f"[Share] {m.group(1).strip()}")
    return ""


def extract_messages_from_dir(db_dir: str, target_wxid: Optional[str] = None) -> list[dict]:
    """Extract messages from all MSG*.db files in a directory and sort by time."""
    db_dir = Path(db_dir)
    all_messages = []

    # Find MSG*.db files
    db_files = []
    for i in range(20):
        p = db_dir / f"MSG{i}.db"
        if p.exists():
            db_files.append(p)
    # Also scan the Multi subdirectory
    multi_dir = db_dir / "Multi"
    if multi_dir.exists():
        for i in range(20):
            p = multi_dir / f"MSG{i}.db"
            if p.exists():
                db_files.append(p)

    if not db_files:
        print(tr(f"在 {db_dir} 下未找到 MSG*.db 文件", f"No MSG*.db files found under {db_dir}"), file=sys.stderr)
        return []

    for db_file in db_files:
        msgs = extract_messages_from_db(str(db_file), target_wxid)
        all_messages.extend(msgs)
        print(tr(f"  {db_file.name}: {len(msgs)} 条消息", f"  {db_file.name}: {len(msgs)} messages"))

    # Sort by timestamp
    all_messages.sort(key=lambda x: x["timestamp"])
    return all_messages


def parse_txt_export(file_path: str, target_name: str) -> list[dict]:
    """Parse manually exported text chat files across common formats."""
    messages = []

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    # Format: 2024-01-01 10:00 Sender: Message
    pattern_datetime_sender = re.compile(
        r"^(?P<time>\d{4}[-/]\d{1,2}[-/]\d{1,2}[\s\d:]+)\s+(?P<sender>.+?)[:：]\s*(?P<content>.+)$"
    )
    # Also supports: "Sender 2024-01-01 10:00"
    pattern_sender_datetime = re.compile(
        r"^(?P<sender>.+?)\s+(?P<time>\d{4}[-/]\d{1,2}[-/]\d{1,2}[\s\d:]+)\s*$"
    )

    current_sender = None
    current_time = None
    pending_content_lines = []

    def flush_pending():
        if current_sender and pending_content_lines:
            content = " ".join(pending_content_lines).strip()
            if content and content not in ["[图片]", "[语音]", "[文件]", "[视频]"]:
                is_target = target_name.lower() in (current_sender or "").lower()
                messages.append({
                    "sender": "them" if is_target else "me",
                    "content": content,
                    "timestamp": current_time or "",
                    "talker_wxid": "",
                })
        return []

    for line in lines:
        line = line.rstrip("\n")
        m = pattern_datetime_sender.match(line)
        if m:
            pending_content_lines = flush_pending()
            current_time = m.group("time").strip()
            current_sender = m.group("sender").strip()
            pending_content_lines = [m.group("content").strip()]
        elif line.strip() and current_sender:
            # Continuation lines for multi-line messages
            pending_content_lines.append(line.strip())

    flush_pending()
    return messages


# ─── iMessage parsing ──────────────────────────────────────────────────────────

def list_imessage_contacts(db_path: str) -> list[dict]:
    """List all contacts in an iMessage database."""
    conn = open_db(db_path)
    if not conn:
        return []
    try:
        rows = conn.execute("""
            SELECT DISTINCT
                h.id AS handle_id,
                COUNT(m.ROWID) AS message_count
            FROM handle h
            LEFT JOIN message m ON m.handle_id = h.ROWID
            GROUP BY h.id
            ORDER BY message_count DESC
        """).fetchall()
        return [{"handle": row["handle_id"], "count": row["message_count"]} for row in rows]
    except Exception as e:
        print(tr(f"读取 iMessage 联系人失败：{e}", f"Failed to read iMessage contacts: {e}"), file=sys.stderr)
        return []
    finally:
        conn.close()


def extract_imessage_messages(db_path: str, target_handle: str) -> list[dict]:
    """
        Extract messages for a target contact from macOS iMessage chat.db.

        chat.db structure:
            - message table: ROWID, text, is_from_me, date (Apple epoch), handle_id
            - handle table: ROWID, id (phone/email)
            - chat_message_join / chat_handle_join: many-to-many links

        Apple epoch starts at 2001-01-01 (Unix offset: 978307200 seconds).
    """
    conn = open_db(db_path)
    if not conn:
        return []

    APPLE_EPOCH_OFFSET = 978307200  # 2001-01-01 00:00:00 UTC

    messages = []
    try:
        # Find target handle ROWIDs (supports fuzzy matching)
        handle_rows = conn.execute(
            "SELECT ROWID, id FROM handle WHERE id LIKE ?",
            (f"%{target_handle}%",)
        ).fetchall()

        if not handle_rows:
            print(tr(f"未找到联系人 '{target_handle}'，尝试模糊匹配...", f"Contact '{target_handle}' not found, trying fuzzy match..."), file=sys.stderr)
            handle_rows = conn.execute("SELECT ROWID, id FROM handle").fetchall()
            handle_rows = [r for r in handle_rows if target_handle.lower() in r["id"].lower()]

        if not handle_rows:
            print(tr(f"未找到 '{target_handle}'，使用 --list-contacts 查看所有联系人", f"No match for '{target_handle}'. Use --list-contacts to view all contacts."), file=sys.stderr)
            return []

        handle_ids = [r["ROWID"] for r in handle_rows]
        matched_handle = handle_rows[0]["id"]
        print(tr(f"匹配到联系人：{matched_handle}（共 {len(handle_ids)} 个 handle）", f"Matched contact: {matched_handle} ({len(handle_ids)} handles)"))

        placeholders = ",".join("?" * len(handle_ids))
        rows = conn.execute(f"""
            SELECT
                m.ROWID,
                m.text,
                m.is_from_me,
                m.date,
                m.date / 1000000000 AS date_sec,
                h.id AS handle_id
            FROM message m
            LEFT JOIN handle h ON h.ROWID = m.handle_id
            WHERE m.handle_id IN ({placeholders})
               OR (m.is_from_me = 1 AND m.ROWID IN (
                   SELECT message_id FROM chat_message_join
                   WHERE chat_id IN (
                       SELECT chat_id FROM chat_handle_join
                       WHERE handle_id IN ({placeholders})
                   )
               ))
            ORDER BY m.date ASC
        """, handle_ids + handle_ids).fetchall()

        for row in rows:
            text = row["text"] or ""
            if not text.strip():
                continue

            # Skip system rows (often special unicode placeholders)
            if text.startswith("\ufffc"):  # attachment placeholder
                continue

            # Convert timestamp
            raw_date = row["date"] or 0
            # iOS 11+ uses nanoseconds; older versions use seconds.
            if raw_date > 1e12:
                unix_ts = raw_date / 1e9 + APPLE_EPOCH_OFFSET
            else:
                unix_ts = raw_date + APPLE_EPOCH_OFFSET

            try:
                timestamp = datetime.fromtimestamp(unix_ts).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                timestamp = str(raw_date)

            messages.append({
                "sender": "me" if row["is_from_me"] else "them",
                "content": text.strip(),
                "timestamp": timestamp,
                "talker_wxid": row["handle_id"] or matched_handle,
            })

    except Exception as e:
        print(tr(f"读取 iMessage 消息失败：{e}", f"Failed to read iMessage messages: {e}"), file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

    return messages


# ─── Message categorization ────────────────────────────────────────────────────

CONFLICT_KEYWORDS = [
    # Chinese
    "生气", "吵架", "分手", "算了", "随便", "不想说了", "烦", "你走",
    "不理你", "别找我", "不要了", "受够了", "够了", "不可能", "冷战",
    "对不起", "我错了", "不是那个意思", "误会", "委屈", "哭",
    # English (iMessage)
    "break up", "breakup", "i'm done", "we're done", "leave me alone",
    "i'm sorry", "sorry", "i was wrong", "stop texting", "don't text",
    "fighting", "argument", "upset", "angry", "hurt", "crying",
    "whatever", "fine", "nevermind", "forget it",
]

SWEET_KEYWORDS = [
    # Chinese
    "想你", "喜欢你", "爱你", "宝", "亲爱的", "么么", "晚安",
    "早安", "吃了吗", "到家了吗", "在干嘛", "你在吗", "想见你",
    "好想", "心动", "开心", "幸福", "快乐",
    # English (iMessage)
    "miss you", "love you", "i love", "good morning", "good night",
    "thinking of you", "how are you", "are you okay", "cute", "sweet",
    "made me think of you", "can't stop thinking", "wanna see you",
]


def classify_messages(messages: list[dict], target_name: str = "them") -> dict:
    """Categorize messages into long, conflict, sweet, and daily buckets."""
    # Analyze only messages sent by TA (sender == "them")
    their_messages = [m for m in messages if m["sender"] == "them"]
    all_messages = messages  # Keep full conversation (including your messages)

    long_msgs = []
    conflict_msgs = []
    sweet_msgs = []
    daily_msgs = []

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
        "total_count": len(all_messages),
        "all_messages": all_messages,  # Keep complete context for downstream analysis
    }


def extract_conversation_threads(messages: list[dict], window_size: int = 10) -> list[list[dict]]:
    """
    Extract meaningful conversation turns (back-and-forth windows).
    Useful for conflict-chain and relationship-dynamics analysis.
    """
    threads = []
    i = 0
    while i < len(messages):
        # Find potential conversation starts with both senders present.
        chunk = messages[i : i + window_size]
        senders = set(m["sender"] for m in chunk)
        if len(senders) >= 2:  # two-way conversation
            threads.append(chunk)
            i += window_size
        else:
            i += 1
    return threads


# ─── Output formatting ─────────────────────────────────────────────────────────

def format_output(target_name: str, classified: dict, include_context: bool = True, source: str = "WeChat", language: str = "zh") -> str:
    """Format parsed output for downstream AI analysis."""
    is_en = normalize_language(language) == "en"
    i_label = "Me" if is_en else "我"
    lines = [
        f"# {source} {('Chat Extraction Result' if is_en else '聊天记录提取结果')}",
        f"{('Target' if is_en else '目标人物')}：{target_name}",
        f"{('Messages sent by TA' if is_en else 'TA 发送的消息数')}：{classified['total_their_count']}",
        f"{('Total messages' if is_en else '对话总消息数')}：{classified['total_count']}",
        "",
        "---",
        "",
        "## " + ("Long Messages (>50 chars, highest weight: viewpoints/emotions/explanations)" if is_en else "长消息（>50字，权重最高：观点/情绪/解释）"),
        "",
    ]

    for msg in classified["long_messages"]:
        ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
        lines.append(f"{ts}{msg['content']}")
        lines.append("")

    lines += [
        "---",
        "",
        "## " + ("Conflict/Emotional Messages (arguments/apologies/breakup/silent-treatment)" if is_en else "冲突/情绪消息（争吵/道歉/分手/冷战相关）"),
        "",
    ]

    for msg in classified["conflict_messages"]:
        ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
        lines.append(f"{ts}{msg['content']}")
        lines.append("")

    lines += [
        "---",
        "",
        "## " + ("Sweet Messages (confessions/missing you/daily care)" if is_en else "甜蜜消息（表白/想念/日常关心）"),
        "",
    ]

    for msg in classified["sweet_messages"]:
        ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
        lines.append(f"{ts}{msg['content']}")
        lines.append("")

    daily_count = len(classified["daily_messages"])
    daily_heading = (
        f"Daily Chat (style reference, {daily_count} messages, full output)"
        if is_en
        else f"日常闲聊（风格参考，共 {daily_count} 条，全部输出）"
    )

    lines += [
        "---",
        "",
        f"## {daily_heading}",
        "",
    ]

    for msg in classified["daily_messages"]:  # keep full output
        ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
        lines.append(f"{ts}{msg['content']}")

    if include_context:
        all_msgs = classified["all_messages"]
        lines += [
            "",
            "---",
            "",
            f"## {(f'Full Conversation ({len(all_msgs)} messages, chronological, full output)' if is_en else f'完整对话（共 {len(all_msgs)} 条，按时间顺序，全部输出）')}",
            ("(Format: [time] sender: content)" if is_en else "（格式：[时间] 发送方: 内容）"),
            "",
        ]
        for msg in all_msgs:  # keep full output
            sender_label = target_name if msg["sender"] == "them" else i_label
            ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
            lines.append(f"{ts}{sender_label}: {msg['content']}")

    return "\n".join(lines)


def print_contact_list(contacts: list[dict], is_imessage: bool = False, language: str = "zh"):
    """Print contact list in the selected language."""
    is_en = normalize_language(language) == "en"
    if not contacts:
        print("No contacts found" if is_en else "未找到联系人数据")
        return
    if is_imessage:
        print((f"Found {len(contacts)} iMessage contacts:\n" if is_en else f"找到 {len(contacts)} 个 iMessage 联系人：\n"))
        print(f"{'Handle (Phone/Apple ID)' if is_en else 'Handle (手机号/Apple ID)':<45} {'Messages' if is_en else '消息数':<10}")
        print("-" * 55)
        for c in contacts:
            print(f"{c['handle']:<45} {c['count']:<10}")
    else:
        print((f"Found {len(contacts)} contacts:\n" if is_en else f"找到 {len(contacts)} 个联系人：\n"))
        print(f"{'WeChat ID' if is_en else '微信ID':<30} {'Remark' if is_en else '备注名':<20} {'Nickname' if is_en else '昵称':<20}")
        print("-" * 70)
        for c in contacts:
            print(f"{c['wxid']:<30} {c['remark']:<20} {c['nickname']:<20}")


# ─── Main entrypoint ───────────────────────────────────────────────────────────

def main():
    global CLI_LANG

    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--lang", choices=["zh", "en"], default="zh")
    pre_args, _ = pre_parser.parse_known_args()
    CLI_LANG = normalize_language(pre_args.lang)

    epilog_en = """
Examples:
  # WeChat - list contacts
  python wechat_parser.py --db-dir ./decrypted/ --list-contacts

  # WeChat - extract one contact's messages
  python wechat_parser.py --db-dir ./decrypted/ --target \"contact_name\" --output messages.txt

  # iMessage - list contacts (macOS)
  python wechat_parser.py --imessage --db ~/Library/Messages/chat.db --list-contacts

  # iMessage - extract messages
  python wechat_parser.py --imessage --db ~/Library/Messages/chat.db \\
      --target \"+1xxxxxxxxxx\" --output messages.txt

  # Parse exported text (generic)
  python wechat_parser.py --txt ./chat.txt --target \"contact_name\" --output messages.txt
        """

    epilog_zh = """
示例：
  # 微信 - 列出联系人
  python wechat_parser.py --db-dir ./decrypted/ --list-contacts

  # 微信 - 提取某个联系人的消息
  python wechat_parser.py --db-dir ./decrypted/ --target \"联系人名称\" --output messages.txt

  # iMessage - 列出联系人（macOS）
  python wechat_parser.py --imessage --db ~/Library/Messages/chat.db --list-contacts

  # iMessage - 提取消息
  python wechat_parser.py --imessage --db ~/Library/Messages/chat.db \\
      --target \"+1xxxxxxxxxx\" --output messages.txt

  # 解析导出的文本聊天记录
  python wechat_parser.py --txt ./chat.txt --target \"联系人名称\" --output messages.txt
        """

    parser = argparse.ArgumentParser(
        description=tr("聊天记录解析器（微信 + iMessage）", "Chat parser (WeChat + iMessage)"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog_en if CLI_LANG == "en" else epilog_zh,
    )

    parser.add_argument("--imessage", action="store_true", help=tr("使用 iMessage 模式（macOS chat.db）", "Use iMessage mode (macOS chat.db)"))
    parser.add_argument("--db-dir", help=tr("解密后微信数据库目录", "Directory containing decrypted WeChat databases"))
    parser.add_argument("--db", help=tr("单个 .db 文件路径（微信或 iMessage）", "Single .db file (WeChat or iMessage)"))
    parser.add_argument("--txt", help=tr("导出的文本聊天文件路径", "Path to exported text chat file"))
    parser.add_argument("--target", help=tr("目标联系人（微信名/备注名，或 iMessage 手机号/Apple ID）", "Target contact (WeChat name/remark, or iMessage phone/Apple ID)"))
    parser.add_argument("--output", default=None, help=tr("输出文件路径（默认打印到标准输出）", "Output file path (default: print to stdout)"))
    parser.add_argument("--list-contacts", action="store_true", help=tr("列出所有联系人", "List all contacts"))
    parser.add_argument("--no-context", action="store_true", help=tr("不输出完整对话上下文", "Exclude full conversation context"))
    parser.add_argument("--json", action="store_true", help=tr("以 JSON 输出原始消息", "Output raw messages in JSON"))
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help=tr("CLI/输出语言", "CLI/output language"))

    args = parser.parse_args()
    CLI_LANG = normalize_language(args.lang)
    source_label = "iMessage" if args.imessage else ("WeChat" if CLI_LANG == "en" else "微信")

    # ── iMessage mode ──────────────────────────────────────────────────────────
    if args.imessage:
        if not args.db:
            # Default path
            default_path = Path.home() / "Library" / "Messages" / "chat.db"
            if default_path.exists():
                args.db = str(default_path)
                print(tr(f"使用默认 iMessage 数据库：{args.db}", f"Using default iMessage database: {args.db}"))
            else:
                print(tr("错误：未找到 iMessage 数据库，请用 --db 指定路径", "Error: iMessage database not found. Please provide --db."), file=sys.stderr)
                print(tr("默认路径：~/Library/Messages/chat.db", "Default path: ~/Library/Messages/chat.db"), file=sys.stderr)
                print(tr("注意：需要在系统偏好设置中给终端授权「完全磁盘访问权限」", "Note: grant Full Disk Access to terminal/Python in macOS settings."), file=sys.stderr)
                sys.exit(1)

        if args.list_contacts:
            contacts = list_imessage_contacts(args.db)
            print_contact_list(contacts, is_imessage=True, language=CLI_LANG)
            return

        if not args.target:
            print(tr("错误：请指定 --target（手机号或 Apple ID）", "Error: please provide --target (phone number or Apple ID)."), file=sys.stderr)
            sys.exit(1)

        print(tr(f"从 iMessage 数据库提取：{args.db}", f"Extracting from iMessage database: {args.db}"))
        messages = extract_imessage_messages(args.db, args.target)

    # ── WeChat mode ────────────────────────────────────────────────────────────
    else:
        # List contacts
        if args.list_contacts:
            if not args.db_dir:
                print(tr("错误：--list-contacts 需要 --db-dir", "Error: --list-contacts requires --db-dir."), file=sys.stderr)
                sys.exit(1)
            contacts = list_contacts(args.db_dir)
            print_contact_list(contacts, is_imessage=False, language=CLI_LANG)
            return

        if not args.target:
            print(tr("错误：请指定 --target（目标联系人名称）", "Error: please provide --target (contact name)."), file=sys.stderr)
            sys.exit(1)

        messages = []

        if args.txt:
            print(tr(f"从文本文件解析：{args.txt}", f"Parsing from text export: {args.txt}"))
            if not Path(args.txt).exists():
                print(tr(
                    f"错误：找不到文本文件 {args.txt}",
                    f"Error: text export file not found: {args.txt}",
                ), file=sys.stderr)
                sys.exit(1)
            try:
                messages = parse_txt_export(args.txt, args.target)
            except OSError as e:
                print(tr(
                    f"错误：读取文本文件失败：{e}",
                    f"Error: failed to read text export file: {e}",
                ), file=sys.stderr)
                sys.exit(1)

        elif args.db:
            print(tr(f"从单个数据库解析：{args.db}", f"Parsing from single database: {args.db}"))
            target_wxid = find_contact_wxid(args.db_dir, args.target) if args.db_dir else None
            messages = extract_messages_from_db(args.db, target_wxid)

        elif args.db_dir:
            target_wxid = find_contact_wxid(args.db_dir, args.target)
            if target_wxid:
                print(tr(f"找到联系人 wxid：{target_wxid}", f"Matched contact wxid: {target_wxid}"))
            else:
                print(tr(f"警告：未找到 '{args.target}' 的精确匹配", f"Warning: no exact match found for '{args.target}'."), file=sys.stderr)
            print(tr(f"从目录解析：{args.db_dir}", f"Parsing from directory: {args.db_dir}"))
            messages = extract_messages_from_dir(args.db_dir, target_wxid)

        else:
            print(tr("错误：请指定 --db-dir 或 --db 或 --txt（或加 --imessage 使用 iMessage 模式）", "Error: provide --db-dir, --db, or --txt (or use --imessage mode)."), file=sys.stderr)
            sys.exit(1)

    target_name = args.target

    if not messages:
        print(tr("警告：未找到消息", "Warning: no messages found."), file=sys.stderr)
        if not args.imessage and args.db_dir:
            print(tr("提示：", "Tips:"), file=sys.stderr)
            print(tr("  1. 运行 --list-contacts 查看所有联系人的精确名称", "  1. Run --list-contacts to get exact contact names."), file=sys.stderr)
            print(tr("  2. 确认数据库已正确解密（运行 wechat_decryptor.py）", "  2. Confirm databases are decrypted (run wechat_decryptor.py)."), file=sys.stderr)
        sys.exit(1)

    their_count = sum(1 for m in messages if m["sender"] == "them")
    print(tr(f"\n提取完成：共 {len(messages)} 条消息，其中 TA 发出 {their_count} 条", f"\nExtraction completed: {len(messages)} total messages, {their_count} sent by TA"))

    if their_count < 200:
        print(tr(f"⚠️  警告：TA 的消息只有 {their_count} 条，样本偏少，生成的人格可信度较低", f"⚠️  Warning: TA only has {their_count} messages. Sample size is small and persona reliability may be low."))

    # Output
    if args.json:
        output_content = json.dumps(messages, ensure_ascii=False, indent=2)
    else:
        classified = classify_messages(messages, target_name)
        output_content = format_output(target_name, classified, include_context=not args.no_context, source=source_label, language=CLI_LANG)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_content)
        print(tr(f"已输出到：{args.output}", f"Output written to: {args.output}"))
    else:
        print(output_content)


if __name__ == "__main__":
    main()
