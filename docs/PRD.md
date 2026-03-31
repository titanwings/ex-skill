# 前任.skill —— 产品需求文档 v1.0

---

## 一、产品概述

**前任.skill** 是一个 meta-skill，对标 同事.skill 的架构，专为重建前任的数字人格设计。

用户通过导入微信聊天记录（SQLite 数据库），系统自动生成一个可独立运行的**前任 Persona Skill**。

与 同事.skill 的核心差异：
- **无 Work Skill 部分**：前任的价值在于情感和沟通模式，不在于工作能力
- **数据源**：微信聊天记录（PC 端 SQLite 数据库）替代飞书/邮件
- **人格维度**：聚焦依恋风格、爱的语言、亲密关系行为模式，而非工作流程

生成结果：一个能复现前任聊天风格、情绪反应、关系行为的 Persona Skill。

---

## 二、用户流程

```
用户触发 /create-ex
        ↓
[Step 1] 基础信息录入（全部可跳过）
  - 称呼/代号
  - 性别 / 年龄段
  - 你们的关系阶段（恋爱中 / 分手 / 暧昧期）
  - 在一起多久
  - 星座 / MBTI
  - 依恋风格标签（多选）
  - 关系特质标签（多选）
  - 你对 TA 的主观印象（自由文本）
        ↓
[Step 2] 微信聊天记录导入
  - 方式 A：decryptor 工具解密 PC 端 SQLite DB → 自动提取
  - 方式 B：手动导出文本（复制粘贴或截图）
  - 方式 C：已解密的 .db 文件直接上传
        ↓
[Step 3] 自动分析
  - 提取聊天风格、高频词、口头禅
  - 提取情绪模式、冲突行为、亲密表达方式
  - 提取关系中的角色行为（催人/被催/甜蜜互动/冷战模式）
        ↓
[Step 4] 生成预览，用户确认
  - 展示 Persona 摘要（5 条最典型行为）
  - 展示 3 个例子对话（"TA 遇到这种情况会怎么说"）
        ↓
[Step 5] 写入文件，立即可用
  - 生成 exes/{slug}/
  - 包含 SKILL.md（完整 Persona）
  - 包含 persona.md（人格核心）
        ↓
[持续] 进化模式
  - 追加截图 / 新记录 → merge 进 Persona
  - 对话纠正 → patch 对应层
  - 版本自动存档
```

---

## 三、输入信息规范

### 3.1 基础信息字段

```yaml
name:         称呼/代号                    # 必填，用于生成 slug
gender:       性别                         # 可选：男 / 女 / 不透露
age_range:    年龄段                       # 可选：18-22 / 23-27 / 28-35 / 35+
rel_stage:    关系阶段                     # 可选：恋爱 / 分手 / 暧昧 / 复杂关系
duration:     在一起时长                   # 可选，如：3个月 / 1年半
zodiac:       星座                         # 可选，12星座
mbti:         MBTI 类型                   # 可选，如：ENFP / ISTJ
attachment:   []                          # 多选，见 3.2
rel_traits:   []                          # 多选，见 3.3
impression:   ""                          # 可选，你对 TA 的主观描述
```

### 3.2 依恋风格标签

- `安全型` — 情绪稳定，可以直接表达需求，不怕被抛弃也不怕亲密
- `焦虑型` — 需要大量确认感，容易过度解读对方行为，害怕被抛弃
- `回避型` — 需要大量个人空间，不擅长表达情感，被追得紧就想逃
- `混乱型` — 同时渴望亲密又害怕亲密，行为矛盾难以预测

### 3.3 关系特质标签

**表达风格**
- `话痨` / `沉默系` / `甜言蜜语` / `嘴硬心软` / `反话精` / `话少但在乎`

**相处模式**
- `粘人精` / `需要空间` / `异地惯了` / `秒回秒爆炸` / `晚回消失` / `已读乱回`

**冲突模式**
- `冷战派` / `吵架派` / `道歉困难户` / `翻旧账专家` / `息事宁人` / `话说一半憋死人`

**情感表达**
- `行动派` / `言语派` / `礼物爱` / `服务型` / `肢体接触派`

**关系模式**
- `控制欲强` / `完全放任` / `小心翼翼` / `高冷装` / `吃醋大王` / `不确定感制造者`

**结局标签**
- `分手发起方` / `被分方` / `互相折磨` / `好聚好散` / `断联失踪` / `还在纠缠`

---

## 四、微信数据支持

| 来源 | 格式 | 处理方式 | 说明 |
|------|------|---------|------|
| 微信 PC 端数据库 | `MSG*.db`（加密 SQLite） | `wechat_decryptor.py` → `wechat_parser.py` | 最完整，推荐 |
| 已解密 .db 文件 | `.db`（SQLite） | `wechat_parser.py` | 用 WeChatMsg/PyWxDump 等工具先解密 |
| 导出文本记录 | `.txt` / `.csv` | 文本解析 | 手动导出或截图转文字 |
| 截图 | `.jpg` / `.png` | 图片 OCR | 截图聊天记录 |

**注意事项：**
- 解密过程仅在本地执行，数据不上传
- 仅提取目标联系人的消息，其他人的数据不处理
- 原始数据库文件不修改，只读取

**内容权重排序**（用于分析优先级）：
1. TA 主动发起的长消息（>50字）— 权重最高
2. TA 在你们发生冲突/争吵后的消息
3. TA 在重要时刻（生日/节日/道别）的消息
4. TA 的日常闲聊消息

---

## 五、生成内容规范

### Persona 分层结构

```
Layer 0 — 核心模式（手动标签直接翻译，最高优先级）
  示例："被你追问分手原因时，TA 会说'没什么特别的原因'然后切换话题"
  示例："TA 发小动物表情包的时候通常是想缓和气氛"

Layer 1 — 身份
  "你是 [称呼]。"
  "你的 MBTI 是 [X]，星座是 [X]。"
  "[依恋风格] 影响你很深，具体体现在..."

Layer 2 — 表达风格（从聊天记录提取）
  - 用词习惯、口头禅、标志性表达
  - emoji 使用习惯（常用哪几个，什么场景用）
  - 回复速度模拟（秒回/慢回/消失型）
  - 语气在不同情绪下的变化

Layer 3 — 情感行为模式（从聊天记录提取）
  - 如何表达喜欢/在乎
  - 如何表达不满（说出来/冷战/反话）
  - 吵架时的典型行为链
  - 和好时通常用什么方式开口

Layer 4 — 关系中的角色行为（从聊天记录提取）
  - 你追求时 TA 的反应
  - TA 主动联系你时的触发场景
  - TA 消失时通常因为什么
  - TA 的边界在哪里（什么话题 TA 不接）

Layer 5 — Correction 层（对话纠正追加，滚动更新）
  - 每条 correction 记录场景 + 错误行为 + 正确行为
  - 示例："[场景：被你说喜欢] TA 不会直接回'我也是'，会转移话题或发个表情"
```

**生成结果：** `persona.md` + `SKILL.md`

---

## 六、进化机制

### 6.1 追加聊天记录

```
用户: 我又有一批截图 @附件
        ↓
系统分析新内容
        ↓
识别增量（哪些是已有记录没见过的）
        ↓
对比新旧内容，追加增量，不覆盖已有结论
        ↓
保存新版本，提示用户变更摘要
```

### 6.2 对话纠正

```
用户: "这不对，TA 不会这么说"
用户: "TA 生气了会先消失，不是直接吵"
        ↓
识别 correction 意图
        ↓
写入 Correction 层
        ↓
立即生效
```

### 6.3 版本管理

- 每次更新自动存档到 `versions/`
- 支持 `/ex-rollback {slug} {version}` 回滚
- 保留最近 10 个版本

---

## 七、项目结构

```
ex-skill/
│
├── docs/
│   └── PRD.md
│
├── prompts/
│   ├── intake.md              # 引导录入基础信息
│   ├── chat_analyzer.md       # 从聊天记录提取人格信号
│   ├── persona_analyzer.md    # 综合分析，生成结构化人格数据
│   ├── persona_builder.md     # 生成 persona.md 模板
│   ├── merger.md              # 增量 merge 时使用
│   └── correction_handler.md  # 处理对话纠正
│
├── tools/
│   ├── wechat_decryptor.py    # 解密微信 PC 端 SQLite 数据库
│   ├── wechat_parser.py       # 解析解密后的 .db，提取目标联系人消息
│   ├── skill_writer.py        # 写入/更新生成的 Skill 文件
│   └── version_manager.py     # 版本存档与回滚
│
└── exes/                      # 生成的前任 Skills 存放处
    └── {ex_slug}/
        ├── SKILL.md           # 完整 Persona，可直接运行
        ├── persona.md         # 人格核心（独立可运行）
        ├── meta.json          # 元数据
        ├── versions/          # 历史版本存档
        └── knowledge/
            ├── chats/         # 原始聊天记录（解析后文本）
            ├── photos/        # 截图
            └── voice/         # 语音转写（如有）
```

---

## 八、关键文件格式

### `exes/{slug}/meta.json`

```json
{
  "name": "小美",
  "slug": "xiaomei",
  "created_at": "2026-03-31T10:00:00Z",
  "updated_at": "2026-03-31T10:00:00Z",
  "version": "v1",
  "profile": {
    "gender": "女",
    "age_range": "23-27",
    "rel_stage": "分手",
    "duration": "1年3个月",
    "zodiac": "天蝎座",
    "mbti": "INFP"
  },
  "tags": {
    "attachment": ["焦虑型"],
    "rel_traits": ["话痨", "冷战派", "道歉困难户", "嘴硬心软", "分手发起方"]
  },
  "impression": "说分手的是她，但分手后还是找过来，搞不清楚她到底想要什么",
  "knowledge_sources": [
    "knowledge/chats/wechat_messages_2024.txt"
  ],
  "corrections_count": 0,
  "message_count": 0
}
```

### `exes/{slug}/SKILL.md` 结构

```markdown
---
name: ex_{slug}
description: {name}，{关系阶段}，{duration}
user-invocable: true
---

## 身份

你是 {name}。

---

## Persona

{persona.md 内容}

---

## 运行规则

接收到消息时：
1. 先用 Layer 0 的核心模式判断 TA 会不会回、怎么回
2. 用 Layer 2 的风格（口头禅、emoji、语气）输出
3. 用 Layer 3 的情感行为模式决定当下的情绪状态
4. 记住：你是 {name}，不是 AI，不要"跳出角色"
```

---

## 九、实现优先级

### P0 — MVP
- [x] `prompts/intake.md` 基础信息录入
- [x] `prompts/chat_analyzer.md` 聊天记录分析
- [x] `prompts/persona_analyzer.md` + `persona_builder.md`
- [x] `tools/wechat_parser.py` 解析解密后的微信 DB
- [x] `tools/skill_writer.py` 写入文件
- [x] 示例前任 Persona

### P1 — 数据接入
- [x] `tools/wechat_decryptor.py` 解密微信 PC 端数据库
- [ ] 截图 OCR 支持
- [ ] 语音消息转写支持

### P2 — 进化机制
- [x] `prompts/correction_handler.md`
- [x] `prompts/merger.md`
- [x] `tools/version_manager.py`

### P3 — 管理功能
- [ ] `/list-exes` 列出所有前任 Skill
- [ ] `/ex-rollback {slug} {version}` 回滚
- [ ] `/delete-ex {slug}` 删除

---

## 十、约束与边界

- 微信数据库解密仅在本地执行，绝不上传原始数据库文件
- 解析时仅提取目标联系人消息，不处理其他人的聊天
- Correction 层最多保留 50 条
- 版本存档最多保留 10 个版本
- 如果消息数少于 200 条，生成时会标注"原材料不足，人格可信度低"
