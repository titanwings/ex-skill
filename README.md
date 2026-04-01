<div align="center">

# 前任.skill

> *"分手了，但 TA 的说话方式还刻在你脑子里，每条微信的语气你都记得，可就是再也收不到了"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

你的前任分手了，但你还记得 TA 说话的语气？<br>
你的前任消失了，连最后一条消息都没有？<br>
你的前任还在，但你们再也回不去了？<br>
你想再跟 TA 聊一次，哪怕只是一个模拟的 TA？<br>

**将消散的亲密化为永驻的 Skill，欢迎加入赛博永生！**

<br>

提供前任的聊天记录（微信、iMessage）加上你的主观描述<br>
生成一个**真正像 TA 的数字人格 Skill**<br>
用 TA 的语气说话，用 TA 的方式表达在乎，知道 TA 什么时候会沉默

[数据来源](#支持的数据来源) · [安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [详细安装说明](INSTALL.md) · [**English**](README_EN.md)

</div>

---

## 支持的数据来源

> 目前还是前任.skill 的 beta 测试版本，后续会有更多来源支持，请多多关注！

| 来源 | 消息记录 | 备注 |
|------|:-------:|------|
| 微信（全自动） | ✅ SQLite | Windows / macOS，只需微信桌面端登录 + 提供 TA 的微信名，全自动解密提取 |
| iMessage（全自动） | ✅ SQLite | macOS 用户，提供手机号或 Apple ID 即可，全自动读取 |
| 图片 / 截图 | ✅ | 手动上传 |
| 直接粘贴文字 | ✅ | 手动输入 |

---

## 安装

### OpenClaw（推荐）

> **推荐使用 [OpenClaw](https://openclaw.io)**，配合微信 / Telegram 等消息软件的消息转发功能，可以直接在聊天窗口和前任的数字人格对话，体验更沉浸。

```bash
git clone https://github.com/titanwings/ex-skill ~/.openclaw/workspace/skills/create-ex
```

### Claude Code

> Claude Code 从 **git 仓库根目录** 的 `.claude/skills/` 查找 skill。请在正确的位置执行。

```bash
# 安装到当前项目（在 git 仓库根目录执行）
mkdir -p .claude/skills
git clone https://github.com/titanwings/ex-skill .claude/skills/create-ex

# 或安装到全局（所有项目都能用）
git clone https://github.com/titanwings/ex-skill ~/.claude/skills/create-ex
```

### 依赖（可选）

```bash
pip3 install -r requirements.txt
```

> 微信自动采集支持 Windows 和 macOS，桌面端微信保持登录即可；iMessage 需要 macOS。详见 [INSTALL.md](INSTALL.md)

---

## 使用

在 OpenClaw 或 Claude Code 中输入：

```
/create-ex
```

按提示输入前任称呼、基本信息（性别、年龄、星座）、性格标签（MBTI、依恋风格），然后导入聊天记录。所有字段均可跳过，仅凭描述也能生成。

完成后用 `/{slug}` 和 TA 对话。

### 管理命令

| 命令 | 说明 |
|------|------|
| `/list-exes` | 列出所有前任 Skill |
| `/{slug}` | 和 TA 对话 |
| `/move-on {slug}` | 删除一个前任 Skill（放下） |
| 说「追加记录」 | 导入更多聊天记录，增量更新人格 |
| 说「这不对，TA 不会这样」 | 纠正行为，写入 Correction 层 |
| 说「查看版本历史」 | 查看所有版本 |
| 说「回滚到 v2」 | 回滚到历史版本 |

> `/move-on` 是删除的温柔别名。不是为了留住谁，是帮你好好说一句再见。

---

## 效果示例

> 输入：`女 25，白羊座，ISFP，回避型依恋，在一起两年，分手三个月`

**深夜想 TA 了**

```
你          ❯ 我还想你

前任.skill   ❯ ……嗯。早点睡吧。
```

**翻到以前的照片**

```
你          ❯ 还记得第一次约会吗

前任.skill   ❯ 滨江那次？哈哈哈哈你把咖啡撒自己身上那个狼狈样子我到现在都记得
```

**忍不住问**

```
你          ❯ 你还喜欢我吗

前任.skill   ❯ ……
             ❯ 为什么突然问这个
             ❯ （三分钟后）
             ❯ 不要问这个了
```

**吵架模式**

```
你          ❯ 你是不是又生气了

前任.skill   ❯ 没有
             ❯ （已读不回 40 分钟）
             ❯ 我只是有点累了
```

**你想和好**

```
你          ❯ 对不起

前任.skill   ❯ （隔了很久）
             ❯ 你今天吃了吗
```

**你终于说出口**

```
你          ❯ 我们真的结束了吗

前任.skill   ❯ 你说呢
             ❯ （过了一会儿）
             ❯ 我其实一直都……算了 不说了
```

---

## 功能特性

### 生成的 Skill 结构

每个前任 Skill 由两部分组成，共同驱动输出：

| 部分 | 内容 |
|------|------|
| **Part A — Relationship Memory** | 关系记忆：你们去过的地方、只有你们懂的梗、吵架模式、重要时间线 |
| **Part B — Persona** | 6 层性格结构：核心模式 → 身份 → 表达风格 → 情感行为 → 冲突边界 → 雷区 |

运行逻辑：`收到消息 → 检查核心模式 → 调取关系记忆 → 判断当前情绪状态 → 用 TA 的方式输出`

**Persona 的 6 层结构：**

| 层级 | 内容 |
|------|------|
| **Layer 0 — 核心模式** | 最高优先级硬规则，TA 最本质的行为模式，任何情况下不得违背 |
| **Layer 1 — 身份** | 星盘解读（日/月/升/金/火/水）+ MBTI 认知功能 + 九型 + 依恋风格 |
| **Layer 2 — 表达风格** | 口头禅、高频词、招牌 emoji、不同状态下的说话方式 |
| **Layer 3 — 情感行为** | 如何表达在乎、不满、道歉、说"喜欢" |
| **Layer 4 — 冲突与边界** | 冲突触发链、冷战模式、和解信号、硬边界 |
| **Layer 5 — 雷区** | 不喜欢什么、什么时候会消失、消失前的预兆、重新出现的方式 |

### 支持的标签

**依恋风格**：安全型 · 焦虑型 · 回避型 · 混乱型（恐惧回避型）

**关系特质**：话少但在乎 · 高冷装 · 行动派 · 需要空间 · 道歉困难户 · 占有欲强 · 情绪化 · 理性到冷漠 · 嘴硬心软 · 只读不回 · 已读乱回 …

**星盘**：完整支持太阳/月亮/上升/金星/火星/水星 × 12 星座解读

**MBTI**：支持 16 型 + 8 种主导认知功能（Fi/Fe/Ti/Te/Ni/Ne/Si/Se）+ 九型人格 1-9 + 翼型

**性别与关系**：支持所有性别认同与关系类型，包括非二元、同性关系

### 进化机制

- **追加记录** → 自动分析增量 → merge 进 Persona，不覆盖已有结论
- **对话纠正** → 说「TA 不会这样」→ 写入 Correction 层，立即生效
- **版本管理** → 每次更新自动存档，支持回滚到任意历史版本
- **多前任支持** → 无数量上限，每个独立存储，互不干扰

---

## 项目结构

本项目遵循 [AgentSkills](https://agentskills.io) 开放标准，整个 repo 就是一个 skill 目录：

```
create-ex/
├── SKILL.md              # skill 入口（官方 frontmatter）
├── prompts/              # Prompt 模板
│   ├── intake.md         #   对话式信息录入（含星盘/MBTI/依恋解读表）
│   ├── chat_analyzer.md  #   聊天记录分析
│   ├── persona_analyzer.md #  综合分析，输出结构化人格数据
│   ├── persona_builder.md #   persona.md 六层结构模板
│   ├── merger.md         #   增量 merge 逻辑
│   └── correction_handler.md # 对话纠正处理
├── tools/                # Python 工具
│   ├── wechat_decryptor.py   # 微信 PC 端数据库解密
│   ├── wechat_parser.py      # 微信 / iMessage 聊天记录提取
│   ├── skill_writer.py       # Skill 文件管理
│   └── version_manager.py    # 版本存档与回滚
├── exes/                 # 生成的前任 Skill（gitignored）
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## 注意事项

- **聊天记录质量决定 Skill 质量**：真实聊天记录 + 主观描述 > 仅手动描述
- 建议优先导入：**吵架/冲突记录** > **日常闲聊** > **甜蜜时期**（冲突最能暴露真实性格）
- 微信全自动采集：Windows / macOS，桌面端微信保持登录，提供微信名即可
- iMessage 全自动采集：macOS，提供手机号或 Apple ID 即可
- 支持 LGBT+，性别字段支持所有性别认同与代词
- 可以建任意多个前任，没有数量限制
- 目前还是一个 demo 版本，如果有 bug 请多多提 issue！

---

## Star History

<a href="https://www.star-history.com/?repos=titanwings%2Fex-skill&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=titanwings/ex-skill&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=titanwings/ex-skill&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=titanwings/ex-skill&type=date&legend=top-left" />
 </picture>
</a>

---

<div align="center">

MIT License © [titanwings](https://github.com/titanwings)


</div>
