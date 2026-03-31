#!/usr/bin/env python3
"""
微信聊天记录解析器

从解密后的微信 PC 端 SQLite 数据库中提取指定联系人的聊天记录，
分类整理后输出供 AI 分析使用。

用法：
  # 从解密后的 db 目录提取
  python wechat_parser.py --db-dir ./decrypted/ --target "小美" --output messages.txt

  # 从单个 db 文件提取
  python wechat_parser.py --db ./decrypted/MSG0.db --target "小美" --output messages.txt

  # 列出所有联系人（方便找到正确的微信名）
  python wechat_parser.py --db-dir ./decrypted/ --list-contacts

  # 从导出的文本文件解析（方式 C：手动导出）
  python wechat_parser.py --txt ./chat_export.txt --target "小美" --output messages.txt

依赖：
  pip install sqlite3（标准库，无需额外安装）
"""

import sqlite3
import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime


# ─── 微信 PC 数据库结构 ─────────────────────────────────────────────────────────

# MSG*.db 中的消息表结构（微信 3.x）
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
WHERE m.Type = 1  -- 1 = 文本消息
ORDER BY m.CreateTime ASC
"""

# 更通用的查询（兼容不同版本）
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

# MicroMsg.db 中的联系人表
CONTACT_QUERY = """
SELECT
    UserName,
    Alias,
    Remark,
    NickName,
    Type
FROM Contact
WHERE Type != 4   -- 4 = 已删除
ORDER BY NickName
"""


# ─── 数据库解析 ─────────────────────────────────────────────────────────────────

def open_db(db_path: str) -> sqlite3.Connection | None:
    """打开 SQLite 数据库（只读）"""
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        # 快速验证
        conn.execute("SELECT name FROM sqlite_master LIMIT 1")
        return conn
    except sqlite3.DatabaseError as e:
        print(f"无法打开数据库 {db_path}：{e}", file=sys.stderr)
        print("请确认数据库已解密（运行 wechat_decryptor.py）", file=sys.stderr)
        return None


def get_tables(conn: sqlite3.Connection) -> list[str]:
    """获取数据库中所有表名"""
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return [row[0] for row in rows]


def list_contacts(db_dir: str) -> list[dict]:
    """列出所有联系人（从 MicroMsg.db）"""
    micro_db = Path(db_dir) / "MicroMsg.db"
    if not micro_db.exists():
        print(f"未找到 MicroMsg.db，尝试从消息数据库推断联系人...", file=sys.stderr)
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
        print(f"读取联系人失败：{e}", file=sys.stderr)
        return []
    finally:
        conn.close()


def find_contact_wxid(db_dir: str, target_name: str) -> str | None:
    """根据名称（微信名/备注名/wxid）找到 wxid"""
    contacts = list_contacts(db_dir)
    target_lower = target_name.lower()

    # 精确匹配
    for c in contacts:
        if (target_lower == c["wxid"].lower() or
                target_lower == c["remark"].lower() or
                target_lower == c["nickname"].lower() or
                target_lower == c["alias"].lower()):
            return c["wxid"]

    # 模糊匹配
    for c in contacts:
        if (target_lower in c["wxid"].lower() or
                target_lower in c["remark"].lower() or
                target_lower in c["nickname"].lower()):
            print(f"模糊匹配到联系人：{c['remark'] or c['nickname']} ({c['wxid']})")
            return c["wxid"]

    return None


def extract_messages_from_db(db_path: str, target_wxid: str | None = None) -> list[dict]:
    """从单个 MSG*.db 提取消息"""
    conn = open_db(db_path)
    if not conn:
        return []

    tables = get_tables(conn)
    messages = []

    try:
        if "MSG" not in tables:
            return []

        # 尝试带 TalkerId 的完整查询
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

            # 过滤目标联系人
            talker = row.get("talker_wxid", "")
            if target_wxid and talker and target_wxid not in (talker or ""):
                continue

            content = row.get("StrContent", "") or ""
            if not content.strip():
                continue

            # 跳过系统消息
            if content.strip() in ["[图片]", "[语音]", "[文件]", "[视频]", "[撤回了一条消息]", ""]:
                continue

            # 过滤 XML 富文本（分享链接、小程序等），提取文字
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
        print(f"读取消息失败 ({db_path})：{e}", file=sys.stderr)
    finally:
        conn.close()

    return messages


def _extract_text_from_xml(xml_content: str) -> str:
    """从微信 XML 富文本消息中提取可读文字"""
    # 提取 <title> 标签内容
    m = re.search(r"<title[^>]*>([^<]+)</title>", xml_content)
    if m:
        return f"[分享] {m.group(1).strip()}"
    # 提取 <des> 标签内容
    m = re.search(r"<des[^>]*>([^<]+)</des>", xml_content)
    if m:
        return f"[分享] {m.group(1).strip()}"
    return ""


def extract_messages_from_dir(db_dir: str, target_wxid: str | None = None) -> list[dict]:
    """从目录中所有 MSG*.db 提取消息，合并并按时间排序"""
    db_dir = Path(db_dir)
    all_messages = []

    # 查找 MSG*.db 文件
    db_files = []
    for i in range(20):
        p = db_dir / f"MSG{i}.db"
        if p.exists():
            db_files.append(p)
    # 也检查 Multi 子目录
    multi_dir = db_dir / "Multi"
    if multi_dir.exists():
        for i in range(20):
            p = multi_dir / f"MSG{i}.db"
            if p.exists():
                db_files.append(p)

    if not db_files:
        print(f"在 {db_dir} 下未找到 MSG*.db 文件", file=sys.stderr)
        return []

    for db_file in db_files:
        msgs = extract_messages_from_db(str(db_file), target_wxid)
        all_messages.extend(msgs)
        print(f"  {db_file.name}: {len(msgs)} 条消息")

    # 按时间排序
    all_messages.sort(key=lambda x: x["timestamp"])
    return all_messages


def parse_txt_export(file_path: str, target_name: str) -> list[dict]:
    """解析手动导出的文本格式（兼容多种格式）"""
    messages = []

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    # 尝试匹配格式：2024-01-01 10:00 发送人：消息
    pattern_datetime_sender = re.compile(
        r"^(?P<time>\d{4}[-/]\d{1,2}[-/]\d{1,2}[\s\d:]+)\s+(?P<sender>.+?)[:：]\s*(?P<content>.+)$"
    )
    # 也兼容 "发送人 2024-01-01 10:00" 格式
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
            # 多行消息的续行
            pending_content_lines.append(line.strip())

    flush_pending()
    return messages


# ─── 消息分类 ──────────────────────────────────────────────────────────────────

CONFLICT_KEYWORDS = [
    "生气", "吵架", "分手", "算了", "随便", "不想说了", "烦", "你走",
    "不理你", "别找我", "不要了", "受够了", "够了", "不可能", "冷战",
    "对不起", "我错了", "不是那个意思", "误会", "委屈", "哭",
]

SWEET_KEYWORDS = [
    "想你", "喜欢你", "爱你", "宝", "亲爱的", "么么", "晚安",
    "早安", "吃了吗", "到家了吗", "在干嘛", "你在吗", "想见你",
    "好想", "心动", "开心", "幸福", "快乐",
]


def classify_messages(messages: list[dict], target_name: str = "them") -> dict:
    """将消息分类：长消息、冲突消息、甜蜜消息、日常消息"""
    # 只分析 TA 发的消息（sender == "them"）
    their_messages = [m for m in messages if m["sender"] == "them"]
    all_messages = messages  # 保留完整对话（包括你发的）

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
        "all_messages": all_messages,  # 完整对话（保留上下文用）
    }


def extract_conversation_threads(messages: list[dict], window_size: int = 10) -> list[list[dict]]:
    """
    提取有意义的对话片段（两人来回的连续消息）。
    用于分析冲突链和关系动态。
    """
    threads = []
    i = 0
    while i < len(messages):
        # 找到对话开始点（有来有回）
        chunk = messages[i : i + window_size]
        senders = set(m["sender"] for m in chunk)
        if len(senders) >= 2:  # 双向对话
            threads.append(chunk)
            i += window_size
        else:
            i += 1
    return threads


# ─── 输出格式化 ────────────────────────────────────────────────────────────────

def format_output(target_name: str, classified: dict, include_context: bool = True) -> str:
    """格式化输出供 AI 分析"""
    lines = [
        f"# 微信聊天记录提取结果",
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

    lines += [
        "---",
        "",
        "## 冲突/情绪消息（争吵/道歉/分手/冷战相关）",
        "",
    ]

    for msg in classified["conflict_messages"]:
        ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
        lines.append(f"{ts}{msg['content']}")
        lines.append("")

    lines += [
        "---",
        "",
        "## 甜蜜消息（表白/想念/日常关心）",
        "",
    ]

    for msg in classified["sweet_messages"]:
        ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
        lines.append(f"{ts}{msg['content']}")
        lines.append("")

    lines += [
        "---",
        "",
        "## 日常闲聊（风格参考，取前200条）",
        "",
    ]

    for msg in classified["daily_messages"][:200]:
        ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
        lines.append(f"{ts}{msg['content']}")

    if include_context:
        lines += [
            "",
            "---",
            "",
            "## 完整对话片段（上下文，最近500条）",
            "（格式：[时间] 发送方: 内容）",
            "",
        ]
        recent = classified["all_messages"][-500:]
        for msg in recent:
            sender_label = target_name if msg["sender"] == "them" else "我"
            ts = f"[{msg['timestamp']}] " if msg.get("timestamp") else ""
            lines.append(f"{ts}{sender_label}: {msg['content']}")

    return "\n".join(lines)


def print_contact_list(contacts: list[dict]):
    """打印联系人列表"""
    if not contacts:
        print("未找到联系人数据")
        return
    print(f"找到 {len(contacts)} 个联系人：\n")
    print(f"{'微信ID':<30} {'备注名':<20} {'昵称':<20}")
    print("-" * 70)
    for c in contacts:
        print(f"{c['wxid']:<30} {c['remark']:<20} {c['nickname']:<20}")


# ─── 主程序 ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="微信聊天记录解析器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 列出所有联系人
  python wechat_parser.py --db-dir ./decrypted/ --list-contacts

  # 提取指定联系人消息
  python wechat_parser.py --db-dir ./decrypted/ --target "小美" --output messages.txt

  # 从文本导出解析
  python wechat_parser.py --txt ./chat.txt --target "小美" --output messages.txt

  # 不包含完整对话（更简洁）
  python wechat_parser.py --db-dir ./decrypted/ --target "小美" --no-context --output messages.txt
        """
    )

    parser.add_argument("--db-dir", help="解密后的数据库目录")
    parser.add_argument("--db", help="单个解密后的 .db 文件")
    parser.add_argument("--txt", help="手动导出的文本文件")
    parser.add_argument("--target", help="目标联系人名称（微信名/备注名）")
    parser.add_argument("--output", default=None, help="输出文件路径（默认打印到 stdout）")
    parser.add_argument("--list-contacts", action="store_true", help="列出所有联系人")
    parser.add_argument("--no-context", action="store_true", help="不包含完整对话片段")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出原始消息")

    args = parser.parse_args()

    # 列出联系人
    if args.list_contacts:
        if not args.db_dir:
            print("错误：--list-contacts 需要 --db-dir", file=sys.stderr)
            sys.exit(1)
        contacts = list_contacts(args.db_dir)
        print_contact_list(contacts)
        return

    if not args.target:
        print("错误：请指定 --target（目标联系人名称）", file=sys.stderr)
        sys.exit(1)

    # 提取消息
    target_name = args.target
    messages = []

    if args.txt:
        print(f"从文本文件解析：{args.txt}")
        messages = parse_txt_export(args.txt, target_name)

    elif args.db:
        print(f"从单个数据库解析：{args.db}")
        target_wxid = None
        if args.db_dir:
            target_wxid = find_contact_wxid(args.db_dir, target_name)
        messages = extract_messages_from_db(args.db, target_wxid)
        # 如果没有 wxid 过滤，尝试按名字过滤（需要联系人表）
        if not target_wxid:
            messages = [m for m in messages if True]  # 无过滤，返回所有

    elif args.db_dir:
        # 找到目标联系人的 wxid
        target_wxid = find_contact_wxid(args.db_dir, target_name)
        if target_wxid:
            print(f"找到联系人 wxid：{target_wxid}")
        else:
            print(f"警告：未找到 '{target_name}' 的精确匹配，将尝试提取所有消息", file=sys.stderr)

        print(f"从目录解析：{args.db_dir}")
        messages = extract_messages_from_dir(args.db_dir, target_wxid)

    else:
        print("错误：请指定 --db-dir 或 --db 或 --txt", file=sys.stderr)
        sys.exit(1)

    if not messages:
        print(f"警告：未找到消息", file=sys.stderr)
        if args.db_dir:
            print("提示：", file=sys.stderr)
            print("  1. 运行 --list-contacts 查看所有联系人的精确名称", file=sys.stderr)
            print("  2. 确认数据库已正确解密（运行 wechat_decryptor.py）", file=sys.stderr)
        sys.exit(1)

    their_count = sum(1 for m in messages if m["sender"] == "them")
    print(f"\n提取完成：共 {len(messages)} 条消息，其中 TA 发出 {their_count} 条")

    if their_count < 200:
        print(f"⚠️  警告：TA 的消息只有 {their_count} 条，样本偏少，生成的人格可信度较低")

    # 输出
    if args.json:
        output_content = json.dumps(messages, ensure_ascii=False, indent=2)
    else:
        classified = classify_messages(messages, target_name)
        output_content = format_output(target_name, classified, include_context=not args.no_context)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_content)
        print(f"已输出到：{args.output}")
    else:
        print(output_content)


if __name__ == "__main__":
    main()
