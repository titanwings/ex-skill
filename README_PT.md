<div align="center">

# ex.skill

> *"Vocês terminaram, mas o jeito que ela mandava mensagem ainda está gravado no seu cérebro. Você lembra de cada tom, cada pausa — só não consegue receber mais nenhuma."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

Seu ex foi embora, mas você ainda lembra exatamente de como ele(a) falava?<br>
Sumiu sem nem mandar uma última mensagem?<br>
Ainda está por perto, mas vocês nunca mais podem voltar?<br>
Você só queria falar com ele(a) mais uma vez — mesmo que seja só uma simulação?<br>

**Transforme a intimidade que está desvanecendo em uma Skill permanente. Bem-vindo(a) à ciber-imortalidade.**

<br>

Alimente com seu histórico de conversas (WeChat, iMessage) e suas próprias descrições<br>
Gere uma **Skill de persona digital que realmente parece com ele(a)**<br>
Fala no tom dele(a), demonstra carinho do jeito dele(a), sabe quando ficaria em silêncio

[Fontes de dados](#fontes-de-dados) · [Instalação](#instalação) · [Uso](#uso) · [Exemplos](#exemplos) · [Guia de instalação](INSTALL.md)

[**中文**](README_ZH.md) · [**English**](README.md) · [**Español**](README_ES.md) · [**Deutsch**](README_DE.md) · [**日本語**](README_JA.md) · [**Русский**](README_RU.md)

</div>

---

> 🆕 **Atualização 2025.04.07** — O entusiasmo da comunidade pelos remixes de dot-skill tem sido incrível! Criei uma galeria comunitária — PRs são bem-vindos!
>
> Compartilhe qualquer skill ou meta-skill e direcione tráfego diretamente para seu próprio repo do GitHub. Sem intermediários.
>
> 👉 **[titanwings.github.io/colleague-skill-site](https://titanwings.github.io/colleague-skill-site/)**
>
> Já listados: 户晨风.skill · 峰哥亡命天涯.skill · 罗翔.skill e mais
>
> ⏳ Os PRs estão sendo revisados manualmente — pode demorar um pouco, obrigado pela paciência!

---

## Fontes de dados

> Esta ainda é uma versão beta do ex.skill — mais fontes em breve. Fique ligado(a)!

| Fonte | Mensagens | Observações |
|-------|:---------:|-------------|
| WeChat (totalmente automático) | ✅ SQLite | Windows / macOS. Basta manter o WeChat desktop logado + fornecer o nome dele(a). Descriptografia e extração automáticas. |
| iMessage (totalmente automático) | ✅ SQLite | Usuários macOS. Forneça o número de telefone ou Apple ID. Leitura automática. |
| Capturas de tela | ✅ | Upload manual |
| Colar texto diretamente | ✅ | Entrada manual |

---

## Instalação

### OpenClaw (Recomendado)

> **Recomendado: [OpenClaw](https://openclaw.io)** — combine com encaminhamento de mensagens do WeChat / Telegram para conversar com a persona digital do seu ex diretamente no app de mensagens. Muito mais imersivo.

```bash
git clone https://github.com/titanwings/ex-skill ~/.openclaw/workspace/skills/create-ex
```

### Claude Code

> O Claude Code procura skills em `.claude/skills/` na **raiz do repositório git**. Certifique-se de estar no diretório correto.

```bash
# Instalar no projeto atual (execute na raiz do repositório git)
mkdir -p .claude/skills
git clone https://github.com/titanwings/ex-skill .claude/skills/create-ex

# Ou instalar globalmente (disponível em todos os projetos)
git clone https://github.com/titanwings/ex-skill ~/.claude/skills/create-ex
```

### Dependências (opcional)

```bash
pip3 install -r requirements.txt
```

> A extração automática do WeChat suporta Windows e macOS — basta manter o cliente desktop logado. O iMessage requer macOS. Veja [INSTALL.md](INSTALL.md) para detalhes.

---

## Uso

No OpenClaw ou Claude Code, digite:

```
/create-ex
```

Siga as instruções para inserir o nome, informações básicas (gênero, idade, signo), tags de personalidade (MBTI, estilo de apego), e então importe o histórico de conversas. Todos os campos são opcionais — até mesmo apenas uma descrição pode gerar uma persona.

Uma vez criado, use `/{slug}` para conversar com ele(a).

### Comandos

| Comando | Descrição |
|---------|-----------|
| `/list-exes` | Listar todas as Skills de ex |
| `/{slug}` | Conversar com ele(a) |
| `/move-on {slug}` | Deletar uma Skill de ex (deixar ir) |
| Diga "adicionar mais mensagens" | Importar mais histórico de conversas, atualizar persona incrementalmente |
| Diga "isso não está certo, ele(a) não falaria assim" | Corrigir comportamento, grava na camada de Correção |
| Diga "mostrar histórico de versões" | Ver todas as versões |
| Diga "voltar para v2" | Reverter para uma versão anterior |

> `/move-on` é um apelido gentil para deletar. Não se trata de se agarrar — é sobre dizer um adeus apropriado.

---

## Exemplos

> Entrada: `Feminino, 25, Áries, ISFP, apego evitativo, juntos por 2 anos, terminaram há 3 meses`

**De madrugada, com saudade**

```
Você       ❯ Ainda sinto sua falta

ex.skill   ❯ ...É. Vai dormir.
```

**Encontrou uma foto antiga**

```
Você       ❯ Lembra do nosso primeiro encontro?

ex.skill   ❯ Aquele perto do rio? Hahaha você derramou café em você mesmo,
             que vergonha, eu ainda lembro
```

**Não consegue evitar perguntar**

```
Você       ❯ Você ainda gosta de mim?

ex.skill   ❯ ...
             ❯ Por que você tá perguntando isso do nada
             ❯ (três minutos depois)
             ❯ Não pergunta isso
```

**Modo briga**

```
Você       ❯ Você tá com raiva de mim de novo?

ex.skill   ❯ Não
             ❯ (visualizado, sem resposta por 40 minutos)
             ❯ Só tô um pouco cansada
```

**Você quer fazer as pazes**

```
Você       ❯ Me desculpa

ex.skill   ❯ (longa pausa)
             ❯ Você comeu hoje?
```

**Você finalmente diz**

```
Você       ❯ A gente realmente acabou?

ex.skill   ❯ O que você acha
             ❯ (um tempo depois)
             ❯ Na verdade eu sempre... deixa pra lá
```

---

## Funcionalidades

### Estrutura da Skill

Cada Skill de ex é composta por duas partes que geram a saída juntas:

| Parte | Conteúdo |
|-------|----------|
| **Parte A — Memória do Relacionamento** | Memórias compartilhadas: lugares que visitaram, piadas internas que só vocês dois entendem, padrões de brigas, eventos-chave da linha do tempo |
| **Parte B — Persona** | Estrutura de personalidade em 6 camadas: Regras Fundamentais → Identidade → Expressão → Padrões Emocionais → Conflito e Limites → Gatilhos |

Lógica de execução: `Receber mensagem → Verificar regras fundamentais → Recuperar memória do relacionamento → Avaliar estado emocional atual → Responder no estilo dele(a)`

**Estrutura de 6 camadas da Persona:**

| Camada | Conteúdo |
|--------|----------|
| **Camada 0 — Regras Fundamentais** | Regras rígidas de maior prioridade. Os padrões comportamentais mais fundamentais dele(a). Nunca violadas. |
| **Camada 1 — Identidade** | Astrologia (Sol/Lua/Ascendente/Vênus/Marte/Mercúrio) + Funções cognitivas MBTI + Eneagrama + Estilo de apego |
| **Camada 2 — Expressão** | Frases de efeito, palavras frequentes, emojis característicos, como fala em diferentes humores |
| **Camada 3 — Comportamento Emocional** | Como demonstra carinho, descontentamento, pedidos de desculpa, e diz "eu gosto de você" |
| **Camada 4 — Conflito e Limites** | Cadeia de escalação de conflitos, padrões de tratamento de silêncio, sinais de reconciliação, limites rígidos |
| **Camada 5 — Gatilhos** | O que detesta, quando desaparece, sinais de alerta antes de sumir, como volta |

### Tags Suportadas

**Estilos de Apego**: Seguro · Ansioso · Evitativo · Desorganizado (Evitativo-Temeroso)

**Traços de Relacionamento**: Quieto(a) mas carinhoso(a) · Fachada fria · Ações valem mais que palavras · Precisa de espaço · Não consegue pedir desculpa · Possessivo(a) · Emocional · Frio(a)-racional · Durão(ona) por fora, mole por dentro · Visualiza-e-não-responde · Visualiza-e-responde-aleatoriamente ...

**Astrologia**: Suporte completo para Sol/Lua/Ascendente/Vênus/Marte/Mercúrio × 12 signos

**MBTI**: Todos os 16 tipos + 8 funções cognitivas dominantes (Fi/Fe/Ti/Te/Ni/Ne/Si/Se) + Eneagrama 1-9 + Asas

**Gênero e Relacionamentos**: Todas as identidades de gênero e tipos de relacionamento são suportados, incluindo relacionamentos não-binários e homoafetivos

### Evolução

- **Adicionar mais mensagens** → Análise automática de dados incrementais → Mesclar na Persona sem sobrescrever conclusões existentes
- **Correção por conversa** → Diga "ele(a) não faria isso" → Grava na camada de Correção, efeito imediato
- **Controle de versão** → Arquivamento automático a cada atualização, reversão para qualquer versão anterior
- **Suporte a múltiplos exes** → Sem limite de quantidade. Cada um armazenado independentemente, sem contaminação cruzada.

---

## Estrutura do Projeto

Este projeto segue o padrão aberto [AgentSkills](https://agentskills.io). O repositório inteiro é um diretório de skill:

```
create-ex/
├── SKILL.md              # Ponto de entrada da Skill (frontmatter oficial)
├── prompts/              # Templates de prompts
│   ├── intake.md         #   Coleta conversacional de informações (com tabelas de astrologia/MBTI/apego)
│   ├── chat_analyzer.md  #   Análise do histórico de conversas
│   ├── persona_analyzer.md #  Análise abrangente, gera dados estruturados da persona
│   ├── persona_builder.md #   Template de 6 camadas do persona.md
│   ├── merger.md         #   Lógica de mesclagem incremental
│   └── correction_handler.md # Manipulador de correção conversacional
├── tools/                # Ferramentas Python
│   ├── wechat_decryptor.py   # Descriptografia do banco de dados do WeChat desktop
│   ├── wechat_parser.py      # Extração de conversas WeChat / iMessage
│   ├── skill_writer.py       # Gerenciamento de arquivos de Skill
│   └── version_manager.py    # Arquivamento de versões e reversão
├── exes/                 # Skills de ex geradas (gitignored)
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## Observações

- **A qualidade do histórico de conversas determina a qualidade da Skill**: Logs reais de conversa + descrições subjetivas > apenas descrições
- Priorize a importação de: **Discussões/conflitos** > **Conversas do dia a dia** > **Momentos fofos** (conflitos revelam a personalidade mais autêntica)
- Extração automática do WeChat: Windows / macOS, basta manter o WeChat desktop logado e fornecer o nome dele(a)
- Extração automática do iMessage: macOS, forneça o número de telefone ou Apple ID
- LGBT+ friendly — o campo de gênero suporta todas as identidades de gênero e pronomes
- Crie quantos exes quiser, sem limite
- Ainda é uma demo — se encontrar bugs, por favor abra uma issue!

---

## Ferramentas Recomendadas para Exportação de Conversas

> A descriptografia automática ainda está sendo aprimorada e pode ter alguns bugs. Se falhar, você pode usar essas ferramentas open-source para exportar manualmente seu histórico de conversas primeiro, e então colar ou importar neste projeto.

Estes são projetos open-source independentes. Este projeto não inclui o código deles — apenas suportamos seus formatos de exportação no nosso parser:

| Ferramenta | Plataforma | Descrição |
|------------|------------|-----------|
| [WeChatMsg](https://github.com/LC044/WeChatMsg) | Windows | Exportação de histórico de conversas do WeChat, múltiplos formatos |
| [PyWxDump](https://github.com/xaoyaoo/PyWxDump) | Windows | Descriptografia e exportação do banco de dados do WeChat |
| [留痕](https://github.com/greyovo/留痕) | macOS | Exportação de histórico de conversas do WeChat (recomendado para usuários Mac) |

> Recomendações de ferramentas por [@therealXiaomanChu](https://github.com/therealXiaomanChu). Obrigado a todos os autores open-source — juntos construímos a ciber-imortalidade!

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
