<div align="center">

# ex.skill

> *「別れたけど、あの人のメッセージの書き方が脳に焼きついている。口調も、間の取り方も、全部覚えてる――ただもう、新しいメッセージは届かない。」*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

元カレ・元カノはもういないのに、あの人の話し方だけは鮮明に覚えている？<br>
最後のメッセージすら残さずに消えてしまった？<br>
まだ近くにいるのに、もう戻れない？<br>
もう一度だけ話したい――たとえシミュレーションだとしても？<br>

**薄れゆく親密さを永続するSkillに変える。サイバー不死の世界へようこそ。**

<br>

チャット履歴（WeChat、iMessage）とあなた自身の説明を入力<br>
**本当にあの人らしいデジタルペルソナSkill**を生成<br>
あの人の口調で話し、あの人なりの気遣いを見せ、いつ黙るかも知っている

[データソース](#データソース) · [インストール](#インストール) · [使い方](#使い方) · [例](#例) · [インストールガイド](INSTALL.md)

[**中文**](README_ZH.md) · [**English**](README.md) · [**Español**](README_ES.md) · [**Deutsch**](README_DE.md) · [**Русский**](README_RU.md) · [**Português**](README_PT.md)

</div>

---

> 🆕 **2025.04.07 更新** — dot-skill リミックスへのコミュニティの熱意がすごい！コミュニティギャラリーを作りました — PR お待ちしています！
>
> skill や meta-skill を共有して、自分の GitHub リポジトリに直接トラフィックを誘導できます。中間業者なし。
>
> 👉 **[titanwings.github.io/colleague-skill-site](https://titanwings.github.io/colleague-skill-site/)**
>
> 収録済み：户晨风.skill · 峰哥亡命天涯.skill · 罗翔.skill など
>
> ⏳ 現在 PR は手動レビュー中です。少し時間がかかる場合があります。ご辛抱ください！

---

## データソース

> これはまだex.skillのベータ版です。対応ソースは今後追加予定です。お楽しみに！

| ソース | メッセージ | 備考 |
|--------|:--------:|-------|
| WeChat（完全自動） | ✅ SQLite | Windows / macOS。WeChatデスクトップにログインしたまま、相手の名前を入力するだけ。自動復号、自動抽出。 |
| iMessage（完全自動） | ✅ SQLite | macOSユーザー向け。電話番号またはApple IDを入力。自動読み取り。 |
| スクリーンショット | ✅ | 手動アップロード |
| テキスト直接貼り付け | ✅ | 手動入力 |

---

## インストール

### OpenClaw（推奨）

> **推奨：[OpenClaw](https://openclaw.io)** — WeChat / Telegramのメッセージ転送と組み合わせれば、メッセージアプリ上で直接元カレ・元カノのデジタルペルソナとチャットできます。没入感が段違いです。

```bash
git clone https://github.com/titanwings/ex-skill ~/.openclaw/workspace/skills/create-ex
```

### Claude Code

> Claude Codeは**gitリポジトリのルート**にある `.claude/skills/` からスキルを読み込みます。正しいディレクトリにいることを確認してください。

```bash
# 現在のプロジェクトにインストール（gitリポジトリのルートで実行）
mkdir -p .claude/skills
git clone https://github.com/titanwings/ex-skill .claude/skills/create-ex

# またはグローバルにインストール（全プロジェクトで利用可能）
git clone https://github.com/titanwings/ex-skill ~/.claude/skills/create-ex
```

### 依存関係（任意）

```bash
pip3 install -r requirements.txt
```

> WeChat自動抽出はWindowsとmacOSに対応しています。デスクトップクライアントにログインしたままにしてください。iMessageにはmacOSが必要です。詳細は[INSTALL.md](INSTALL.md)を参照してください。

---

## 使い方

OpenClawまたはClaude Codeで以下を入力：

```
/create-ex
```

プロンプトに従って、名前、基本情報（性別、年齢、星座）、性格タグ（MBTI、アタッチメントスタイル）を入力し、チャット履歴をインポートします。すべてのフィールドは任意です。説明だけでもペルソナを生成できます。

作成後、`/{slug}` で話しかけられます。

### コマンド

| コマンド | 説明 |
|---------|-------------|
| `/list-exes` | すべての元カレ・元カノSkillを一覧表示 |
| `/{slug}` | あの人と話す |
| `/move-on {slug}` | 元カレ・元カノSkillを削除する（手放す） |
| 「もっとメッセージを追加して」と言う | チャット履歴を追加インポートし、ペルソナを差分更新 |
| 「それは違う、あの人はそんなこと言わない」と言う | 行動を修正し、補正レイヤーに書き込む |
| 「バージョン履歴を見せて」と言う | すべてのバージョンを表示 |
| 「v2にロールバックして」と言う | 以前のバージョンにロールバック |

> `/move-on` は削除のやさしい別名です。しがみつくためではなく、ちゃんとお別れを言うためのものです。

---

## 例

> 入力：`女性、25歳、牡羊座、ISFP、回避型アタッチメント、交際2年、3ヶ月前に別れた`

**深夜、あの人が恋しい**

```
あなた      ❯ まだ会いたい

ex.skill   ❯ ...うん。もう寝なよ。
```

**昔の写真を見つけた**

```
あなた      ❯ 初デートのこと覚えてる？

ex.skill   ❯ 川沿いのやつ？ ははは コーヒー自分にぶちまけてたよね、
             めっちゃ恥ずかしかったでしょ、まだ覚えてるよ
```

**聞かずにはいられない**

```
あなた      ❯ まだ私のこと好き？

ex.skill   ❯ ...
             ❯ なんで急にそんなこと聞くの
             ❯（3分後）
             ❯ そういうこと聞かないで
```

**ケンカモード**

```
あなた      ❯ また怒ってるの？

ex.skill   ❯ 別に
             ❯（既読、40分返信なし）
             ❯ ちょっと疲れてるだけ
```

**仲直りしたい**

```
あなた      ❯ ごめん

ex.skill   ❯（長い沈黙）
             ❯ 今日ちゃんとご飯食べた？
```

**ついに言う**

```
あなた      ❯ 本当に終わりなの？

ex.skill   ❯ どう思う？
             ❯（しばらくして）
             ❯ 実はずっと...やっぱりなんでもない
```

---

## 機能

### Skillの構造

各元カレ・元カノSkillは、出力を共同で駆動する2つのパートで構成されています：

| パート | 内容 |
|------|---------|
| **パートA — 関係の記憶** | 共有の思い出：一緒に行った場所、二人だけの内輪ネタ、ケンカのパターン、重要なタイムラインイベント |
| **パートB — ペルソナ** | 6層の性格構造：コアルール → アイデンティティ → 表現 → 感情パターン → 対立と境界線 → トリガー |

ランタイムロジック：`メッセージ受信 → コアルール確認 → 関係の記憶を検索 → 現在の感情状態を評価 → あの人のスタイルで出力`

**ペルソナの6層構造：**

| レイヤー | 内容 |
|-------|---------|
| **レイヤー0 — コアルール** | 最優先のハードルール。あの人の最も根本的な行動パターン。絶対に違反しない。 |
| **レイヤー1 — アイデンティティ** | 占星術（太陽/月/アセンダント/金星/火星/水星）+ MBTI認知機能 + エニアグラム + アタッチメントスタイル |
| **レイヤー2 — 表現** | 口癖、よく使う言葉、お気に入りの絵文字、気分による話し方の変化 |
| **レイヤー3 — 感情行動** | 気遣い、不満、謝罪、「好き」の伝え方 |
| **レイヤー4 — 対立と境界線** | 対立のエスカレーション連鎖、無視パターン、仲直りのサイン、絶対的な限界線 |
| **レイヤー5 — トリガー** | 嫌いなこと、いなくなるタイミング、消える前の予兆、戻ってくる方法 |

### 対応タグ

**アタッチメントスタイル**：安定型 · 不安型 · 回避型 · 混乱型（恐れ回避型）

**関係の特徴**：静かだけど思いやりがある · 冷たい態度 · 行動で示すタイプ · スペースが必要 · 謝れない · 束縛型 · 感情的 · クール理性派 · 外は強気中は柔らか · 既読スルー · 既読ランダム返信 ...

**占星術**：太陽/月/アセンダント/金星/火星/水星 × 12星座を完全サポート

**MBTI**：全16タイプ + 8つの主要認知機能（Fi/Fe/Ti/Te/Ni/Ne/Si/Se）+ エニアグラム1-9 + ウイング

**性別と関係**：ノンバイナリーや同性カップルを含む、すべてのジェンダーアイデンティティと関係タイプに対応

### 進化

- **メッセージを追加** → 差分データを自動分析 → 既存の結論を上書きせずにペルソナにマージ
- **会話による修正** → 「あの人はそんなことしない」と言う → 補正レイヤーに書き込み、即座に反映
- **バージョン管理** → 更新のたびに自動アーカイブ、任意の過去バージョンにロールバック可能
- **複数の元カレ・元カノ対応** → 人数制限なし。それぞれ独立して保存、相互干渉なし。

---

## プロジェクト構造

このプロジェクトは[AgentSkills](https://agentskills.io)オープン標準に準拠しています。リポジトリ全体がスキルディレクトリです：

```
create-ex/
├── SKILL.md              # Skillエントリーポイント（公式フロントマター）
├── prompts/              # プロンプトテンプレート
│   ├── intake.md         #   会話形式の情報収集（占星術/MBTI/アタッチメント表付き）
│   ├── chat_analyzer.md  #   チャット履歴分析
│   ├── persona_analyzer.md #  総合分析、構造化されたペルソナデータを出力
│   ├── persona_builder.md #   persona.md 6層テンプレート
│   ├── merger.md         #   差分マージロジック
│   └── correction_handler.md # 会話修正ハンドラー
├── tools/                # Pythonツール
│   ├── wechat_decryptor.py   # WeChatデスクトップデータベース復号
│   ├── wechat_parser.py      # WeChat / iMessageチャット抽出
│   ├── skill_writer.py       # Skillファイル管理
│   └── version_manager.py    # バージョンアーカイブ＆ロールバック
├── exes/                 # 生成された元カレ・元カノSkill（gitignored）
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## 注意事項

- **チャット履歴の質がSkillの質を決める**：実際のチャットログ + 主観的な説明 > 説明のみ
- インポートの優先順位：**ケンカ・対立** > **日常会話** > **甘い瞬間**（対立が最も本当の性格を明らかにする）
- WeChat自動抽出：Windows / macOS、デスクトップ版WeChatにログインしたまま、相手の名前を入力するだけ
- iMessage自動抽出：macOS、電話番号またはApple IDを入力
- LGBT+フレンドリー — 性別フィールドはすべてのジェンダーアイデンティティと代名詞に対応
- 元カレ・元カノは何人でも作成可能、制限なし
- まだデモ段階です。バグを見つけたらissueを立ててください！

---

## おすすめチャットエクスポートツール

> 自動復号はまだ改善中で、バグがある可能性があります。失敗した場合は、以下のオープンソースツールを使って手動でチャット履歴をエクスポートし、本プロジェクトに貼り付けまたはインポートしてください。

これらは独立したオープンソースプロジェクトです。本プロジェクトにそれらのコードは含まれていません。パーサーでそれらのエクスポート形式をサポートしているだけです：

| ツール | プラットフォーム | 説明 |
|------|----------|-------------|
| [WeChatMsg](https://github.com/LC044/WeChatMsg) | Windows | WeChatチャット履歴エクスポート、複数フォーマット対応 |
| [PyWxDump](https://github.com/xaoyaoo/PyWxDump) | Windows | WeChatデータベース復号＆エクスポート |
| [留痕](https://github.com/greyovo/留痕) | macOS | WeChatチャット履歴エクスポート（Macユーザー推奨） |

> ツール推薦：[@therealXiaomanChu](https://github.com/therealXiaomanChu)。すべてのオープンソース作者に感謝します。共にサイバー不死を築きましょう！

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
