# 安装说明

## 环境要求

- Python 3.9+
- macOS 或 Windows（自动读取微信/iMessage 时）
- 微信桌面端保持登录，或 macOS 自带 `~/Library/Messages/chat.db`

## 1. 克隆仓库

```bash
git clone https://github.com/titanwings/ex-skill
cd ex-skill
```

## 2. 创建虚拟环境并安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. 运行自检

```bash
python3 -m unittest discover -s tests -v
```

通过后说明核心 CLI 链路可用：

- `tools/skill_writer.py` 创建 / 更新 / 列表
- `tools/version_manager.py` 版本回滚
- `tools/wechat_parser.py --txt` 文本导入

## 4. 快速 smoke test

```bash
tmpdir="$(mktemp -d)"
cat > "$tmpdir/meta.json" <<'EOF'
{"name":"Alice","profile":{"gender":"女","rel_stage":"分手"}}
EOF
cat > "$tmpdir/persona.md" <<'EOF'
## Layer 0
- 嘴硬心软
EOF
python3 tools/skill_writer.py --action create --meta "$tmpdir/meta.json" --persona "$tmpdir/persona.md" --base-dir "$tmpdir/exes"
python3 tools/skill_writer.py --action list --base-dir "$tmpdir/exes"
```

如果看到 `触发词：/alice`，说明最基本的生成链路已经跑通。

## 5. 微信 / iMessage 读取说明

### 微信

```bash
python3 tools/wechat_decryptor.py --find-key-only
python3 tools/wechat_decryptor.py --db-dir "<微信消息目录>" --output ./decrypted
python3 tools/wechat_parser.py --db-dir ./decrypted --target "TA 的微信名" --output messages.txt
```

注意：

- Windows 读取内存时可能需要管理员权限
- macOS 需要给终端 Full Disk Access；iMessage 读取同样需要
- 自动解密依赖微信客户端正在登录状态

### iMessage

```bash
python3 tools/wechat_parser.py --imessage --db ~/Library/Messages/chat.db --target "+1xxxxxxxxxx" --output messages.txt
```

## 6. 常见问题

### `create` 提示需要 `--slug` 或 `--name`

更新到当前版本后，`--meta` 内已有 `name` 时可以直接创建；如果还报错，请确认 `meta.json` 至少包含：

```json
{"name":"Alice"}
```

### `No module named Crypto`

说明依赖未安装完整，重新执行：

```bash
pip install -r requirements.txt
```

### 提取不到微信密钥

- 先确认微信桌面端不是锁屏状态
- Windows 尝试管理员权限
- macOS 开启终端 Full Disk Access
- 仍失败时，先用 README 中推荐的第三方导出工具导出文本，再走 `--txt` 链路
