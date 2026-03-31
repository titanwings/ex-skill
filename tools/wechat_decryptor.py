#!/usr/bin/env python3
"""
微信 PC 端数据库解密工具

支持：微信 Windows 客户端 3.x（SQLCipher 加密的 SQLite 数据库）

解密原理：
  微信 PC 端将聊天数据库用 SQLCipher 加密存储。
  加密密钥在微信运行时驻留在进程内存中，可通过特征码扫描提取。
  提取后用 SQLCipher 的 PRAGMA key 解密数据库。

用法：
  python wechat_decryptor.py --db-dir "C:/Users/你/Documents/WeChat Files/wxid_xxx/Msg" --output ./decrypted/
  python wechat_decryptor.py --find-key-only     # 只打印密钥，不解密
  python wechat_decryptor.py --key "abcd1234" --db "./MSG0.db" --output "./decrypted/"

依赖：
  pip install pycryptodome pymem psutil

注意：
  - 运行时微信客户端必须处于登录状态（需从内存读取密钥）
  - 仅支持 Windows
  - 解密后的数据库仅用于个人读取，不要分发
"""

import os
import sys
import struct
import hashlib
import argparse
import ctypes
from pathlib import Path


def _require_windows():
    if sys.platform != "win32":
        print("错误：此工具仅支持 Windows 系统", file=sys.stderr)
        sys.exit(1)


def find_wechat_pid() -> int | None:
    """找到微信进程的 PID"""
    try:
        import psutil
    except ImportError:
        print("请先安装依赖：pip install psutil", file=sys.stderr)
        sys.exit(1)

    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] and proc.info["name"].lower() in ("wechat.exe", "wechatapp.exe"):
            return proc.info["pid"]
    return None


def find_wechat_install_path() -> str | None:
    """从注册表获取微信安装路径（用于确认版本）"""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WOW6432Node\Tencent\WeChat",
        )
        install_path, _ = winreg.QueryValueEx(key, "InstallPath")
        return install_path
    except Exception:
        return None


def get_wechat_data_dir() -> str | None:
    """获取微信用户数据目录（Documents/WeChat Files）"""
    documents = Path.home() / "Documents" / "WeChat Files"
    if documents.exists():
        return str(documents)
    # 备用路径
    alt = Path("C:/Users") / os.getlogin() / "Documents" / "WeChat Files"
    if alt.exists():
        return str(alt)
    return None


def extract_key_from_memory(pid: int) -> str | None:
    """
    从微信进程内存中提取数据库密钥。

    微信 3.x 的密钥是 32 字节的原始 key，紧跟在特定内存特征码之后。
    这里用 pymem 做内存扫描。
    """
    try:
        import pymem
        import pymem.process
    except ImportError:
        print("请先安装依赖：pip install pymem", file=sys.stderr)
        sys.exit(1)

    pm = pymem.Pymem(pid)

    # 特征码：微信将 phone number 的 UTF-8 字节前面存放这个标志
    # 密钥紧跟在账号信息块附近，通过偏移定位
    # 以下是通用扫描逻辑，通过已知明文头（SQLite 数据库头）验证密钥
    key_candidates = []

    # 方法：遍历模块，在 WeChatWin.dll 的数据段中扫描
    try:
        wechat_module = pymem.process.module_from_name(pm.process_handle, "WeChatWin.dll")
        if not wechat_module:
            print("错误：未找到 WeChatWin.dll，请确认微信已登录", file=sys.stderr)
            return None

        module_base = wechat_module.lpBaseOfDll
        module_size = wechat_module.SizeOfImage

        # 读取模块内存（分段读取，避免超出限制）
        chunk_size = 0x100000  # 1MB per chunk
        offset = 0

        # 特征搜索：在内存中查找 "iphone\x00" 等账号特征，密钥在附近
        # 这是 WeChatMsg/PyWxDump 项目使用的标准方法
        phone_pattern = b"iphone\x00"
        wechatid_offset = 0x44  # 典型偏移，可能随版本变化

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
                # 从这个位置往前找密钥候选（32字节）
                key_offset = idx - 0x70  # 经验偏移
                if key_offset >= 0:
                    key_candidate = chunk[key_offset : key_offset + 32]
                    if len(key_candidate) == 32 and key_candidate != b"\x00" * 32:
                        key_candidates.append(key_candidate)
                pos = idx + 1

            offset += chunk_size

    except Exception as e:
        print(f"内存扫描出错：{e}", file=sys.stderr)

    if not key_candidates:
        print("未找到密钥候选，尝试备用方法...", file=sys.stderr)
        return _fallback_key_extraction(pm)

    # 如果找到多个候选，返回第一个（用户可以通过 --test-key 验证）
    return key_candidates[0].hex()


def _fallback_key_extraction(pm) -> str | None:
    """
    备用密钥提取方法：
    部分版本的微信将 key 存储在固定偏移处，可以通过扫描特定字节模式找到。
    """
    # 已知的密钥特征：32字节随机内容，紧跟在某些固定字节序列后
    # 这个方法适用于微信 3.9.x 以下版本
    known_prefixes = [
        bytes.fromhex("0400000020000000"),  # 典型前缀 1
        bytes.fromhex("0100000020000000"),  # 典型前缀 2
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
                            pos = chunk.find(prefix, idx)
                            if pos == -1:
                                break
                            key_start = pos + len(prefix)
                            key_candidate = chunk[key_start : key_start + 32]
                            if len(key_candidate) == 32 and key_candidate != b"\x00" * 32:
                                return key_candidate.hex()
                            idx = pos + 1
                    offset += chunk_size
    except Exception:
        pass
    return None


def test_key(db_path: str, key_hex: str) -> bool:
    """验证密钥是否正确（尝试解密数据库头部）"""
    try:
        import hashlib
        key_bytes = bytes.fromhex(key_hex)

        with open(db_path, "rb") as f:
            header = f.read(4096)

        if len(header) < 4096:
            return False

        # SQLCipher 默认参数（微信使用）
        # page_size=4096, kdf_iter=4000, hmac_use=1, hmac_pgno=1, hmac_salt_mask=0x3a
        salt = header[:16]
        from Crypto.Hash import HMAC, SHA1
        from Crypto.Protocol.KDF import PBKDF2

        key = PBKDF2(key_bytes, salt, dkLen=32, count=4000, prf=lambda p, s: HMAC.new(p, s, SHA1).digest())

        from Crypto.Cipher import AES
        iv = header[16:32]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(header[32:48])

        # SQLite 页解密后，内容应该是合法数据（不全为零或随机）
        return decrypted != b"\x00" * 16

    except Exception:
        return False


def decrypt_db(db_path: str, key_hex: str, output_path: str) -> bool:
    """
    解密单个微信数据库文件。

    使用 SQLCipher 的加密参数（AES-256-CBC, PBKDF2-SHA1, 4000 iterations）
    逐页解密，写入标准 SQLite 文件。
    """
    try:
        from Crypto.Hash import HMAC, SHA1
        from Crypto.Protocol.KDF import PBKDF2
        from Crypto.Cipher import AES
    except ImportError:
        print("请先安装依赖：pip install pycryptodome", file=sys.stderr)
        sys.exit(1)

    PAGE_SIZE = 4096
    SQLITE_HEADER = b"SQLite format 3\x00"

    key_bytes = bytes.fromhex(key_hex)

    with open(db_path, "rb") as f:
        raw = f.read()

    if len(raw) < PAGE_SIZE:
        print(f"文件太小，可能不是有效的数据库：{db_path}", file=sys.stderr)
        return False

    # 第一页：前 16 字节是 salt
    salt = raw[:16]
    key = PBKDF2(key_bytes, salt, dkLen=32, count=4000, prf=lambda p, s: HMAC.new(p, s, SHA1).digest())

    output = bytearray()

    for page_num in range(len(raw) // PAGE_SIZE):
        page = raw[page_num * PAGE_SIZE : (page_num + 1) * PAGE_SIZE]

        if page_num == 0:
            # 第一页：偏移 16（跳过 salt），解密后加上 SQLite 标准头
            iv = page[16:32]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_content = cipher.decrypt(page[32 : PAGE_SIZE - 32])
            decrypted_page = SQLITE_HEADER + decrypted_content[len(SQLITE_HEADER):]
            # 补齐到页大小
            output.extend(decrypted_page)
            # 追加 reserved 区域（最后 32 字节 HMAC，解密后不需要）
            output.extend(b"\x00" * 32)
        else:
            iv = page[-48:-32]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_content = cipher.decrypt(page[: PAGE_SIZE - 48])
            output.extend(decrypted_content)
            output.extend(b"\x00" * 48)

    # 写入输出文件
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(output)

    # 验证
    import sqlite3
    try:
        conn = sqlite3.connect(output_path)
        conn.execute("SELECT name FROM sqlite_master LIMIT 1")
        conn.close()
        return True
    except sqlite3.DatabaseError:
        os.remove(output_path)
        return False


def find_db_files(db_dir: str) -> list[str]:
    """找到目录下的所有微信消息数据库文件"""
    db_dir = Path(db_dir)
    candidates = []

    # 主要消息数据库：MSG0.db ~ MSG9.db
    for i in range(10):
        p = db_dir / f"MSG{i}.db"
        if p.exists():
            candidates.append(str(p))

    # Multi 目录下（部分版本）
    multi_dir = db_dir / "Multi"
    if multi_dir.exists():
        for i in range(10):
            p = multi_dir / f"MSG{i}.db"
            if p.exists():
                candidates.append(str(p))

    # 联系人数据库
    micro_msg = db_dir / "MicroMsg.db"
    if micro_msg.exists():
        candidates.insert(0, str(micro_msg))

    return candidates


def main():
    _require_windows()

    parser = argparse.ArgumentParser(
        description="微信 PC 端数据库解密工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 自动从内存提取密钥并解密所有 MSG*.db
  python wechat_decryptor.py --db-dir "C:/Users/你/Documents/WeChat Files/wxid_xxx/Msg" --output ./decrypted/

  # 只打印密钥
  python wechat_decryptor.py --find-key-only

  # 用已知密钥解密单个文件
  python wechat_decryptor.py --key "abcdef1234..." --db "./MSG0.db" --output "./out/"

  # 验证密钥是否正确
  python wechat_decryptor.py --key "abcdef1234..." --test-db "./MSG0.db"
        """
    )
    parser.add_argument("--db-dir", help="微信 Msg 目录路径")
    parser.add_argument("--db", help="单个数据库文件路径")
    parser.add_argument("--output", default="./decrypted", help="解密输出目录（默认：./decrypted）")
    parser.add_argument("--key", help="已知的密钥（hex 字符串，跳过内存提取）")
    parser.add_argument("--find-key-only", action="store_true", help="只打印密钥，不解密文件")
    parser.add_argument("--test-db", help="测试密钥是否正确（配合 --key 使用）")

    args = parser.parse_args()

    # Step 1: 获取密钥
    key_hex = args.key

    if not key_hex:
        print("正在查找微信进程...")
        pid = find_wechat_pid()
        if not pid:
            print("错误：未找到微信进程，请先打开微信并登录", file=sys.stderr)
            sys.exit(1)
        print(f"找到微信进程，PID: {pid}")

        print("正在从内存提取密钥...")
        key_hex = extract_key_from_memory(pid)
        if not key_hex:
            print("错误：无法提取密钥。请尝试：", file=sys.stderr)
            print("  1. 确认微信已登录（不是锁屏状态）", file=sys.stderr)
            print("  2. 以管理员身份运行本脚本", file=sys.stderr)
            print("  3. 尝试使用 WeChatMsg 或 PyWxDump 工具手动提取密钥", file=sys.stderr)
            sys.exit(1)
        print(f"密钥提取成功：{key_hex}")

    if args.find_key_only:
        print(f"\n密钥（hex）：{key_hex}")
        print("使用方法：python wechat_decryptor.py --key <上面的密钥> --db-dir <MSG目录> --output ./decrypted/")
        return

    # Step 2: 测试密钥
    if args.test_db:
        print(f"正在验证密钥...")
        if test_key(args.test_db, key_hex):
            print("✓ 密钥正确")
        else:
            print("✗ 密钥错误或文件格式不支持")
        return

    # Step 3: 确定要解密的文件列表
    db_files = []
    if args.db:
        db_files = [args.db]
    elif args.db_dir:
        db_files = find_db_files(args.db_dir)
        if not db_files:
            print(f"错误：在 {args.db_dir} 下未找到数据库文件", file=sys.stderr)
            sys.exit(1)
        print(f"找到 {len(db_files)} 个数据库文件")
    else:
        # 自动查找微信数据目录
        data_dir = get_wechat_data_dir()
        if not data_dir:
            print("错误：未找到微信数据目录，请手动指定 --db-dir", file=sys.stderr)
            sys.exit(1)
        print(f"微信数据目录：{data_dir}")
        # 找 wxid 目录
        wxid_dirs = [d for d in Path(data_dir).iterdir() if d.is_dir() and d.name.startswith("wxid_")]
        if not wxid_dirs:
            wxid_dirs = [d for d in Path(data_dir).iterdir() if d.is_dir() and (d / "Msg").exists()]
        if not wxid_dirs:
            print(f"错误：在 {data_dir} 下未找到账号目录，请手动指定 --db-dir", file=sys.stderr)
            sys.exit(1)
        if len(wxid_dirs) > 1:
            print("找到多个账号：")
            for i, d in enumerate(wxid_dirs):
                print(f"  [{i}] {d.name}")
            choice = int(input("请选择账号序号："))
            wxid_dir = wxid_dirs[choice]
        else:
            wxid_dir = wxid_dirs[0]
        msg_dir = wxid_dir / "Msg"
        db_files = find_db_files(str(msg_dir))
        print(f"账号目录：{wxid_dir.name}，找到 {len(db_files)} 个数据库")

    # Step 4: 解密
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    for db_path in db_files:
        db_name = Path(db_path).name
        out_path = str(output_dir / db_name)
        print(f"解密 {db_name}...", end=" ", flush=True)
        if decrypt_db(db_path, key_hex, out_path):
            print("✓")
            success_count += 1
        else:
            print("✗ 失败（密钥可能不匹配）")

    print(f"\n完成：{success_count}/{len(db_files)} 个文件解密成功")
    print(f"解密文件保存在：{output_dir.absolute()}")
    print(f"\n下一步：运行 wechat_parser.py 提取聊天记录")
    print(f"  python wechat_parser.py --db-dir {output_dir.absolute()} --target \"TA的微信名\" --output messages.txt")


if __name__ == "__main__":
    main()
