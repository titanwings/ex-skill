#!/usr/bin/env python3
"""
WeChat desktop database decryptor (Windows + macOS).

EN:
    Purpose:
        Extract SQLCipher keys from a running WeChat process and decrypt local
        message databases for personal export workflows.

    Prerequisites:
        - WeChat must be running and logged in before memory key extraction.
        - On macOS, grant Full Disk Access to terminal/Python.
        - On some macOS setups, SIP may block memory attach/read operations.

    Dependencies:
        - psutil (process discovery)
        - pymem (Windows memory extraction)
        - pycryptodome (SQLCipher-compatible decryption)

    Safety notes:
        - Personal-use only. Follow local laws and platform terms.
        - Protect extracted keys and decrypted databases; they contain private data.
        - If memory extraction fails, extract the key manually and pass --key.

ZH:
    用途：
        从运行中的微信进程提取 SQLCipher 密钥，并解密本地消息数据库，
        用于个人导出场景。

    前置条件：
        - 提取内存密钥前，微信必须已打开且已登录。
        - macOS 需要给终端/Python 授予完全磁盘访问权限。
        - 部分 macOS 环境下，SIP 可能阻止内存附加/读取。

    依赖：
        - psutil（进程查找）
        - pymem（Windows 内存提取）
        - pycryptodome（SQLCipher 参数解密）

    安全提示：
        - 仅限个人合法用途，请遵守当地法律与平台条款。
        - 妥善保护提取出的密钥与解密后的数据库，其中包含隐私数据。
        - 若内存提取失败，可手动提取密钥并通过 --key 指定。
"""

import os
import sys
import struct
import hashlib
import argparse
import subprocess
from pathlib import Path
from typing import Optional


CLI_LANG = "zh"


def normalize_language(language: Optional[str]) -> str:
    value = (language or "").strip().lower()
    if value in {"en", "english"}:
        return "en"
    return "zh"


def tr(zh: str, en: str) -> str:
    return en if CLI_LANG == "en" else zh


# ─── Platform detection ───────────────────────────────────

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"


# ─── Process discovery (cross-platform) ───────────────────

def find_wechat_pid() -> Optional[int]:
    """Find the PID of the running WeChat process."""
    try:
        import psutil
    except ImportError:
        print(tr(
            "请先安装依赖：pip install psutil",
            "Please install dependency first: pip install psutil",
        ), file=sys.stderr)
        sys.exit(1)

    target_names = (
        ("wechat.exe", "wechatapp.exe") if IS_WINDOWS
        else ("wechat", "微信")
    )

    for proc in psutil.process_iter(["pid", "name"]):
        name = (proc.info["name"] or "").lower()
        if name in target_names:
            return proc.info["pid"]
    return None


# ─── Data directory discovery (cross-platform) ────────────

def get_wechat_data_dir() -> Optional[str]:
    """Get the WeChat user data directory."""
    if IS_WINDOWS:
        documents = Path.home() / "Documents" / "WeChat Files"
        if documents.exists():
            return str(documents)
        alt = Path("C:/Users") / os.getlogin() / "Documents" / "WeChat Files"
        if alt.exists():
            return str(alt)
    elif IS_MACOS:
        # Current macOS WeChat data directory
        containers = Path.home() / "Library" / "Containers" / "com.tencent.xinWeChat" / "Data"
        if containers.exists():
            return str(containers)
        # Legacy path
        app_support = Path.home() / "Library" / "Application Support" / "com.tencent.xinWeChat"
        if app_support.exists():
            return str(app_support)
    return None


def find_db_files(db_dir: str) -> list[str]:
    """Find WeChat message database files under a directory."""
    db_dir = Path(db_dir)
    candidates = []

    # Primary message DBs: MSG0.db ~ MSG19.db
    for i in range(20):
        p = db_dir / f"MSG{i}.db"
        if p.exists():
            candidates.append(str(p))

    # Multi directory (some versions)
    multi_dir = db_dir / "Multi"
    if multi_dir.exists():
        for i in range(20):
            p = multi_dir / f"MSG{i}.db"
            if p.exists():
                candidates.append(str(p))

    # macOS-specific directory: Message
    message_dir = db_dir / "Message"
    if message_dir.exists():
        for f in sorted(message_dir.glob("msg_*.db")):
            candidates.append(str(f))

    # Contacts DB
    micro_msg = db_dir / "MicroMsg.db"
    if micro_msg.exists():
        candidates.insert(0, str(micro_msg))

    # If nothing is found directly, recurse one level
    if not candidates:
        for f in sorted(db_dir.glob("**/MSG*.db")):
            candidates.append(str(f))
        for f in sorted(db_dir.glob("**/msg_*.db")):
            candidates.append(str(f))
        micro = list(db_dir.glob("**/MicroMsg.db"))
        if micro:
            candidates.insert(0, str(micro[0]))

    return candidates


# ─── Windows key extraction ────────────────────────────────

def extract_key_windows(pid: int) -> Optional[str]:
    """Extract database key from WeChat process memory on Windows."""
    try:
        import pymem
        import pymem.process
    except ImportError:
        print(tr(
            "请先安装依赖：pip install pymem",
            "Please install dependency first: pip install pymem",
        ), file=sys.stderr)
        sys.exit(1)

    pm = pymem.Pymem(pid)
    key_candidates = []

    try:
        wechat_module = pymem.process.module_from_name(pm.process_handle, "WeChatWin.dll")
        if not wechat_module:
            print(tr(
                "错误：未找到 WeChatWin.dll，请确认微信已登录",
                "Error: WeChatWin.dll not found. Make sure WeChat is logged in.",
            ), file=sys.stderr)
            return None

        module_base = wechat_module.lpBaseOfDll
        module_size = wechat_module.SizeOfImage
        chunk_size = 0x100000  # 1MB

        phone_pattern = b"iphone\x00"
        offset = 0

        while offset < module_size:
            to_read = min(chunk_size, module_size - offset)
            try:
                chunk = pm.read_bytes(module_base + offset, to_read)
            except Exception:
                offset += chunk_size
                continue

            pos = 0
            while True:
                idx = chunk.find(phone_pattern, pos)
                if idx == -1:
                    break
                key_offset = idx - 0x70
                if key_offset >= 0:
                    key_candidate = chunk[key_offset : key_offset + 32]
                    if len(key_candidate) == 32 and key_candidate != b"\x00" * 32:
                        key_candidates.append(key_candidate)
                pos = idx + 1
            offset += chunk_size

    except Exception as e:
        print(tr(f"内存扫描出错：{e}", f"Memory scan failed: {e}"), file=sys.stderr)

    if not key_candidates:
        print(tr("未找到密钥候选，尝试备用方法...", "No key candidates found, trying fallback..."), file=sys.stderr)
        return _fallback_key_windows(pm)

    return key_candidates[0].hex()


def _fallback_key_windows(pm) -> Optional[str]:
    """Windows 备用密钥提取（适用于微信 3.9.x 以下版本）"""
    known_prefixes = [
        bytes.fromhex("0400000020000000"),
        bytes.fromhex("0100000020000000"),
    ]

    try:
        import pymem.process
        for module in pm.list_modules():
            if b"WeChatWin" in module.szModule:
                base = module.lpBaseOfDll
                size = module.SizeOfImage
                chunk_size = 0x200000
                offset = 0
                while offset < size:
                    to_read = min(chunk_size, size - offset)
                    try:
                        chunk = pm.read_bytes(base + offset, to_read)
                    except Exception:
                        offset += chunk_size
                        continue
                    for prefix in known_prefixes:
                        idx = 0
                        while True:
                            found = chunk.find(prefix, idx)
                            if found == -1:
                                break
                            key_start = found + len(prefix)
                            key_candidate = chunk[key_start : key_start + 32]
                            if len(key_candidate) == 32 and key_candidate != b"\x00" * 32:
                                return key_candidate.hex()
                            idx = found + 1
                    offset += chunk_size
    except Exception:
        pass
    return None


# ─── macOS key extraction ──────────────────────────────────

def extract_key_macos(pid: int) -> Optional[str]:
    """
    Extract database key from WeChat process memory on macOS.

    macOS WeChat uses SQLCipher; the key is 32 bytes.
    This scans readable memory regions for known markers.

    Method 1: attach with lldb and scan memory
    Method 2: fallback to keychain-based lookup
    """
    # Method 1: try lldb-based memory extraction
    key = _extract_key_macos_lldb(pid)
    if key:
        return key

    # Method 2: try macOS Keychain (older versions)
    key = _extract_key_macos_keychain()
    if key:
        return key

    return None


def _extract_key_macos_lldb(pid: int) -> Optional[str]:
    """Extract key by reading WeChat process memory through lldb."""
    try:
        # Build lldb script
        lldb_script = f"""
import lldb
debugger = lldb.SBDebugger.Create()
debugger.SetAsync(False)
target = debugger.CreateTarget("")
error = lldb.SBError()
process = target.AttachToProcessWithID(debugger.GetListener(), {pid}, error)
if error.Fail():
    print("ATTACH_FAILED:" + error.GetCString())
else:
    # 遍历内存区域，搜索密钥特征
    regions = process.GetMemoryRegions()
    found_keys = []
    for i in range(regions.GetSize()):
        region = lldb.SBMemoryRegionInfo()
        regions.GetMemoryRegionAtIndex(i, region)
        if not region.IsReadable():
            continue
        base = region.GetRegionBase()
        size = region.GetRegionEnd() - base
        if size > 0x1000000 or size < 0x1000:
            continue
        try:
            content = process.ReadMemory(base, min(size, 0x200000), error)
            if error.Fail() or not content:
                continue
            # 搜索 "iphone" 或 "android" 特征
            for pattern in [b"iphone\\x00", b"android\\x00"]:
                idx = 0
                while True:
                    pos = content.find(pattern, idx)
                    if pos == -1:
                        break
                    key_offset = pos - 0x70
                    if key_offset >= 0:
                        candidate = content[key_offset:key_offset+32]
                        if len(candidate) == 32 and candidate != b"\\x00" * 32:
                            found_keys.append(candidate.hex())
                    idx = pos + 1
        except:
            continue
    process.Detach()
    if found_keys:
        print("KEY_FOUND:" + found_keys[0])
    else:
        print("KEY_NOT_FOUND")
"""
        result = subprocess.run(
            ["python3", "-c", f"exec({repr(lldb_script)})"],
            capture_output=True, text=True, timeout=30,
        )

        for line in result.stdout.splitlines():
            if line.startswith("KEY_FOUND:"):
                return line.split(":", 1)[1].strip()

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(tr(f"lldb 方法失败：{e}", f"lldb extraction failed: {e}"), file=sys.stderr)

    # Fallback: vmmap-based path
    return _extract_key_macos_vmmap(pid)


def _extract_key_macos_vmmap(pid: int) -> Optional[str]:
    """Locate candidate memory regions via vmmap (manual-assist fallback)."""
    try:
        result = subprocess.run(
            ["vmmap", "-p", str(pid)],
            capture_output=True, text=True, timeout=10,
        )
        # Parse vmmap output and locate __DATA segments.
        # This is a simplified path and may require tighter filtering.
        print(tr(
            "vmmap 方法暂不支持自动提取，请使用 --key 手动指定密钥",
            "vmmap extraction is not fully automated yet. Please provide --key manually.",
        ), file=sys.stderr)
    except Exception:
        pass
    return None


def _extract_key_macos_keychain() -> Optional[str]:
    """Try to read WeChat key material from macOS Keychain (legacy fallback)."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "com.tencent.xinWeChat", "-w"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


# ─── Cross-platform key extraction entrypoint ─────────────

def extract_key_from_memory(pid: int) -> Optional[str]:
    """Dispatch key extraction by platform."""
    if IS_WINDOWS:
        return extract_key_windows(pid)
    elif IS_MACOS:
        return extract_key_macos(pid)
    else:
        print(tr(
            "错误：不支持的操作系统，仅支持 Windows 和 macOS",
            "Error: unsupported OS. Only Windows and macOS are supported.",
        ), file=sys.stderr)
        return None


# ─── Key validation ────────────────────────────────────────

def test_key(db_path: str, key_hex: str) -> bool:
    """Validate key by attempting to decrypt database header bytes."""
    try:
        key_bytes = bytes.fromhex(key_hex)

        with open(db_path, "rb") as f:
            header = f.read(4096)

        if len(header) < 4096:
            return False

        from Crypto.Hash import HMAC, SHA1
        from Crypto.Protocol.KDF import PBKDF2
        from Crypto.Cipher import AES

        salt = header[:16]
        key = PBKDF2(key_bytes, salt, dkLen=32, count=4000, prf=lambda p, s: HMAC.new(p, s, SHA1).digest())
        iv = header[16:32]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(header[32:48])

        return decrypted != b"\x00" * 16
    except Exception:
        return False


# ─── Database decryption ───────────────────────────────────

def decrypt_db(db_path: str, key_hex: str, output_path: str) -> bool:
    """
    Decrypt a single WeChat database file.
    Uses SQLCipher-compatible parameters (AES-256-CBC, PBKDF2-SHA1, 4000 iterations)
    and writes a standard SQLite output page-by-page.
    """
    try:
        from Crypto.Hash import HMAC, SHA1
        from Crypto.Protocol.KDF import PBKDF2
        from Crypto.Cipher import AES
    except ImportError:
        print(tr(
            "请先安装依赖：pip install pycryptodome",
            "Please install dependency first: pip install pycryptodome",
        ), file=sys.stderr)
        sys.exit(1)

    PAGE_SIZE = 4096
    SQLITE_HEADER = b"SQLite format 3\x00"

    key_bytes = bytes.fromhex(key_hex)

    with open(db_path, "rb") as f:
        raw = f.read()

    if len(raw) < PAGE_SIZE:
        print(tr(
            f"文件太小，可能不是有效的数据库：{db_path}",
            f"File too small, may not be a valid database: {db_path}",
        ), file=sys.stderr)
        return False

    salt = raw[:16]
    key = PBKDF2(key_bytes, salt, dkLen=32, count=4000, prf=lambda p, s: HMAC.new(p, s, SHA1).digest())

    output = bytearray()

    for page_num in range(len(raw) // PAGE_SIZE):
        page = raw[page_num * PAGE_SIZE : (page_num + 1) * PAGE_SIZE]

        if page_num == 0:
            iv = page[16:32]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_content = cipher.decrypt(page[32 : PAGE_SIZE - 32])
            decrypted_page = SQLITE_HEADER + decrypted_content[len(SQLITE_HEADER):]
            output.extend(decrypted_page)
            output.extend(b"\x00" * 32)
        else:
            iv = page[-48:-32]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_content = cipher.decrypt(page[: PAGE_SIZE - 48])
            output.extend(decrypted_content)
            output.extend(b"\x00" * 48)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(output)

    # Verify decrypted output can be opened by SQLite
    import sqlite3
    try:
        conn = sqlite3.connect(output_path)
        conn.execute("SELECT name FROM sqlite_master LIMIT 1")
        conn.close()
        return True
    except sqlite3.DatabaseError:
        os.remove(output_path)
        return False


# ─── Auto-discover wxid/account directories ───────────────

def find_wxid_dirs(data_dir: str) -> list[Path]:
    """Find account directories under WeChat data root."""
    data_path = Path(data_dir)

    if IS_WINDOWS:
        # Windows: wxid_xxx directories
        wxid_dirs = [d for d in data_path.iterdir() if d.is_dir() and d.name.startswith("wxid_")]
        if not wxid_dirs:
            wxid_dirs = [d for d in data_path.iterdir() if d.is_dir() and (d / "Msg").exists()]
    elif IS_MACOS:
        # macOS: version/account-hash directory layout
        wxid_dirs = []
        for version_dir in data_path.iterdir():
            if not version_dir.is_dir():
                continue
            for account_dir in version_dir.iterdir():
                if not account_dir.is_dir():
                    continue
                msg_dir = account_dir / "Message"
                if msg_dir.exists():
                    wxid_dirs.append(account_dir)
                # Some versions use Msg instead of Message
                msg_dir2 = account_dir / "Msg"
                if msg_dir2.exists():
                    wxid_dirs.append(account_dir)
    else:
        wxid_dirs = []

    return wxid_dirs


def find_msg_dir(wxid_dir: Path) -> Path:
    """Locate the message DB directory inside an account directory."""
    # macOS usually uses Message, Windows usually uses Msg
    for name in ("Message", "Msg", "msg"):
        candidate = wxid_dir / name
        if candidate.exists():
            return candidate
    return wxid_dir


# ─── Main entrypoint ───────────────────────────────────────

def main():
    global CLI_LANG

    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--lang", choices=["zh", "en"], default="zh")
    pre_args, _ = pre_parser.parse_known_args()
    CLI_LANG = normalize_language(pre_args.lang)

    if not IS_WINDOWS and not IS_MACOS:
        print(tr("错误：此工具仅支持 Windows 和 macOS", "Error: this tool supports only Windows and macOS"), file=sys.stderr)
        sys.exit(1)

    epilog_en = """
Examples:
  # Extract key from memory and decrypt all databases
  python wechat_decryptor.py --db-dir <MSG_DIR> --output ./decrypted/

  # Print key only
  python wechat_decryptor.py --find-key-only

  # Decrypt one DB with a known key
  python wechat_decryptor.py --key "abcdef1234..." --db "./MSG0.db" --output "./out/"

  # Validate key against a DB
  python wechat_decryptor.py --key "abcdef1234..." --test-db "./MSG0.db"
        """

    epilog_zh = """
示例：
  # 从内存提取密钥并解密全部数据库
  python wechat_decryptor.py --db-dir <MSG目录> --output ./decrypted/

  # 仅打印密钥
  python wechat_decryptor.py --find-key-only

  # 使用已知密钥解密单个数据库
  python wechat_decryptor.py --key "abcdef1234..." --db "./MSG0.db" --output "./out/"

  # 使用数据库验证密钥
  python wechat_decryptor.py --key "abcdef1234..." --test-db "./MSG0.db"
        """

    parser = argparse.ArgumentParser(
        description=tr("微信桌面数据库解密工具", "WeChat desktop database decryptor"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog_en if CLI_LANG == "en" else epilog_zh,
    )
    parser.add_argument("--db-dir", help=tr("微信消息数据库目录", "Directory containing WeChat message databases"))
    parser.add_argument("--db", help=tr("单个数据库文件路径", "Path to a single database file"))
    parser.add_argument("--output", default="./decrypted", help=tr("解密文件输出目录（默认：./decrypted）", "Output directory for decrypted files (default: ./decrypted)"))
    parser.add_argument("--key", help=tr("已知密钥（十六进制，跳过内存提取）", "Known key in hex format (skip memory extraction)"))
    parser.add_argument("--find-key-only", action="store_true", help=tr("仅输出提取到的密钥，不执行解密", "Print extracted key only; do not decrypt"))
    parser.add_argument("--test-db", help=tr("用单个数据库测试密钥（需配合 --key）", "Validate key against one DB file (use with --key)"))
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help=tr("CLI 语言", "CLI language"))

    args = parser.parse_args()
    CLI_LANG = normalize_language(args.lang)

    platform_name = "Windows" if IS_WINDOWS else "macOS"
    print(tr(f"运行平台：{platform_name}", f"Platform: {platform_name}"))

    key_hex = args.key

    if not key_hex:
        print(tr("正在查找微信进程...", "Searching for WeChat process..."))
        pid = find_wechat_pid()
        if not pid:
            print(tr("错误：未找到微信进程，请先打开微信并登录", "Error: WeChat process not found. Please open WeChat and log in first."), file=sys.stderr)
            sys.exit(1)
        print(tr(f"找到微信进程，PID: {pid}", f"WeChat process found, PID: {pid}"))

        print(tr("正在从内存提取密钥...", "Extracting key from process memory..."))
        key_hex = extract_key_from_memory(pid)
        if not key_hex:
            print(tr("错误：无法提取密钥。请尝试：", "Error: failed to extract key. Try the following:"), file=sys.stderr)
            if IS_WINDOWS:
                print(tr("  1. 确认微信已登录（不是锁屏状态）", "  1. Ensure WeChat is logged in (not locked)."), file=sys.stderr)
                print(tr("  2. 以管理员身份运行本脚本", "  2. Run this script as Administrator."), file=sys.stderr)
                print(tr("  3. 尝试使用 WeChatMsg 或 PyWxDump 工具手动提取密钥", "  3. Try extracting the key manually with WeChatMsg or PyWxDump."), file=sys.stderr)
            elif IS_MACOS:
                print(tr("  1. 确认微信已登录（不是锁屏状态）", "  1. Ensure WeChat is logged in (not locked)."), file=sys.stderr)
                print(tr("  2. 授予终端 Full Disk Access 权限（系统设置 → 隐私与安全）", "  2. Grant Full Disk Access to terminal (Privacy & Security settings)."), file=sys.stderr)
                print(tr("  3. 如果开启了 SIP，可能需要关闭（csrutil disable）", "  3. If SIP is enabled, you may need to disable it (csrutil disable)."), file=sys.stderr)
                print(tr("  4. 尝试手动提取密钥后用 --key 指定", "  4. Extract key manually and pass it with --key."), file=sys.stderr)
            sys.exit(1)
        print(tr(f"密钥提取成功：{key_hex}", f"Key extracted successfully: {key_hex}"))

    if args.find_key_only:
        print(tr(f"\n密钥（hex）：{key_hex}", f"\nKey (hex): {key_hex}"))
        print(tr("使用方法：python wechat_decryptor.py --key <上面的密钥> --db-dir <MSG目录> --output ./decrypted/", "Usage: python wechat_decryptor.py --key <above_key> --db-dir <MSG_dir> --output ./decrypted/"))
        return

    if args.test_db:
        print(tr("正在验证密钥...", "Validating key..."))
        if test_key(args.test_db, key_hex):
            print(tr("✓ 密钥正确", "✓ Key is valid"))
        else:
            print(tr("✗ 密钥错误或文件格式不支持", "✗ Invalid key or unsupported file format"))
        return

    db_files = []
    if args.db:
        db_files = [args.db]
    elif args.db_dir:
        db_files = find_db_files(args.db_dir)
        if not db_files:
            print(tr(f"错误：在 {args.db_dir} 下未找到数据库文件", f"Error: no database files found under {args.db_dir}"), file=sys.stderr)
            sys.exit(1)
        print(tr(f"找到 {len(db_files)} 个数据库文件", f"Found {len(db_files)} database files"))
    else:
        data_dir = get_wechat_data_dir()
        if not data_dir:
            print(tr("错误：未找到微信数据目录，请手动指定 --db-dir", "Error: WeChat data directory not found. Please provide --db-dir."), file=sys.stderr)
            sys.exit(1)
        print(tr(f"微信数据目录：{data_dir}", f"WeChat data directory: {data_dir}"))

        wxid_dirs = find_wxid_dirs(data_dir)
        if not wxid_dirs:
            print(tr(f"错误：在 {data_dir} 下未找到账号目录，请手动指定 --db-dir", f"Error: no account directory found under {data_dir}. Please provide --db-dir."), file=sys.stderr)
            sys.exit(1)
        if len(wxid_dirs) > 1:
            print(tr("找到多个账号：", "Multiple accounts found:"))
            for i, d in enumerate(wxid_dirs):
                print(f"  [{i}] {d.name}")
            choice = int(input(tr("请选择账号序号：", "Select account index: ")))
            wxid_dir = wxid_dirs[choice]
        else:
            wxid_dir = wxid_dirs[0]

        msg_dir = find_msg_dir(wxid_dir)
        db_files = find_db_files(str(msg_dir))
        print(tr(f"账号目录：{wxid_dir.name}，找到 {len(db_files)} 个数据库", f"Account directory: {wxid_dir.name}, found {len(db_files)} databases"))

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    for db_path in db_files:
        db_name = Path(db_path).name
        out_path = str(output_dir / db_name)
        print(tr(f"解密 {db_name}...", f"Decrypting {db_name}..."), end=" ", flush=True)
        if decrypt_db(db_path, key_hex, out_path):
            print("✓")
            success_count += 1
        else:
            print(tr("✗ 失败（密钥可能不匹配）", "✗ Failed (key may not match)"))

    print(tr(f"\n完成：{success_count}/{len(db_files)} 个文件解密成功", f"\nDone: {success_count}/{len(db_files)} files decrypted successfully"))
    print(tr(f"解密文件保存在：{output_dir.absolute()}", f"Decrypted files saved to: {output_dir.absolute()}"))
    print(tr("\n下一步：运行 wechat_parser.py 提取聊天记录", "\nNext: run wechat_parser.py to extract messages"))
    print(tr(f"  python wechat_parser.py --db-dir {output_dir.absolute()} --target \"TA的微信名\" --output messages.txt", f"  python wechat_parser.py --db-dir {output_dir.absolute()} --target \"contact_name\" --output messages.txt"))


if __name__ == "__main__":
    main()
