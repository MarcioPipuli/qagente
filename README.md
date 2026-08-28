# QAGente

[![Testes](https://github.com/MarcioPipuli/qagente/actions/workflows/tests.yml/badge.svg)](https://github.com/MarcioPipuli/qagente/actions/workflows/tests.yml)

Harness de um agente especialista em Qualidade de Software (QA/SDET), extraído dos padrões de qualidade e estrutura observados no repositório [`agent-skills-main`](../agent-skills-main) (Tech Leads Club — formato `SKILL.md`, convenção `AGENTS.md`/`CLAUDE.md`, definição de subagente).

## O que tem aqui

```
QAGente/
├── agent.md              # Definição do subagente "qa-especialista" (identidade, missão, roteamento)
├── AGENTS.md              # Regras de comportamento (rastreabilidade, risco, independência de testes, DoD)
├── CLAUDE.md               # Ponteiro para AGENTS.md (mesmo padrão usado pelo agent-skills-main)
├── profiles/               # Perfis configuráveis por tipo de time/projeto
│   ├── default.json
│   ├── backend-api.json
│   ├── frontend-web.json
│   └── fullstack.json
├── adapters/               # Instruções para cada ferramenta de IA
├── install.py              # Instalador automático (copia/mescla o harness em um projeto)
├── test_install.py         # Testes do instalador (unittest, sem dependências externas)
├── .github/workflows/      # CI: roda a suíte no Linux e no Windows a cada push
└── skills/
    ├── analise-documentacao-testes/   # Fase 1: PRD/ticket → cenários de teste priorizados por risco
    ├── gherkin-palavras-chave/        # Referência: gramática de Dado/Quando/Então/E/Mas (usada pela Fase 2)
    ├── escrita-casos-teste/           # Fase 2: cenários → documento BDD em Gherkin (pt) + rastreabilidade
    │   └── templates/
    ├── robot-framework-api/           # Fase 3a: casos de teste → automação de API em Robot Framework
    │   └── templates/
    └── cypress-ui-automation/         # Fase 3b: casos de teste → automação de UI em Cypress
        └── templates/
```

## Pastas de entrada e saída

Os caminhos vêm do bloco `paths` do perfil (`.qagente/quality-profile.json`) — o instalador cria exatamente as pastas que o perfil declara, e o agente lê e grava nelas. Quando o perfil não traz `paths` utilizável, valem os defaults do QAGente: entrada em `entrada/` e saída em `saida/cenarios/`, `saida/casos-de-teste/`, `saida/robot/` e `saida/cypress/` (uma subpasta por fase).

Uma fase desligada no perfil não ganha pasta: com `"api": {"enabled": false}` o `api_tests` é pulado, e o mesmo vale para `ui_tests` com `"ui": {"enabled": false}`.

O nome-base do documento de origem é preservado no arquivo gerado, para manter a rastreabilidade entre entrada e saída. Um caminho indicado explicitamente pelo usuário no pedido tem prioridade sobre o perfil e sobre essa convenção. Detalhes em [AGENTS.md](AGENTS.md#entradas-e-saídas-convenção-de-pastas).

## O que o perfil controla

O perfil (`.qagente/quality-profile.json`) é o contrato entre o núcleo do QAGente e as decisões
de cada time. Ele governa o instalador **e** o comportamento das skills:

| Campo | Governa |
|---|---|
| `language`, `artifact_format` | Idioma e formato dos artefatos gerados |
| `paths.*` | Onde o agente lê a entrada e grava cada fase; quais pastas o instalador cria |
| `risk_levels`, `risk_method` | Escala e método de priorização dos cenários |
| `conventions.gherkin_language` | Idioma das palavras-chave do Gherkin |
| `conventions.scenario_title_prefix` | Prefixo dos títulos de cenário (`Validar que` por default) |
| `conventions.test_id_pattern` | Padrão de ID para rastreabilidade |
| `api.enabled`, `api.framework` | Se a automação de API existe e em qual ferramenta |
| `api.base_url_env`, `api.user_env`, `api.password_env` | Nomes das variáveis de ambiente |
| `ui.enabled`, `ui.framework` | Se a automação de UI existe e em qual ferramenta |
| `ui.selector_attribute`, `ui.language`, `ui.base_url_env` | Convenções dos specs de UI |

### Perfis prontos

| Perfil | API | UI | Para quem |
|---|---|---|---|
| `default` | ligada | ligada | Primeiro contato ou projeto sem convenção própria; pastas neutras (`entrada/`, `saida/`) |
| `backend-api` | ligada | **desligada** | Time de API/backend |
| `frontend-web` | **desligada** | ligada | Time de frontend/UI; specs em `cypress/e2e/` |
| `fullstack` | ligada | ligada | Time que cuida das duas pontas; automação agrupada em `tests/api` e `tests/e2e` |

Os quatro compartilham a mesma família de convenções: 4 níveis de risco com `critical`, IDs
`TC-{DOMAIN}-{NUMBER}` e seletor `data-testid`. O que distingue o `default` são os caminhos
neutros (`entrada/`, `saida/`), pensados para quem ainda não tem estrutura de repositório
definida; os outros três assumem `docs/requisitos/`, `qa/` e `tests/`.

Copie o mais próximo do seu contexto e ajuste.

Cada skill traz uma seção **Configuração** com os campos que a afetam e o default de cada um.
A precedência é sempre: **instrução explícita do usuário → perfil do projeto → defaults da
skill**. O perfil não pode desligar as regras universais de [AGENTS.md](AGENTS.md)
(rastreabilidade, proteção de segredos, independência dos testes, registro de lacunas e
evidência real de execução).

## Fluxo do agente

```
Documentação → Cenários → Casos de Teste → [aprovação do usuário] → Automação (Robot Framework | Cypress)
```

A função principal do agente é entregar Cenários e Casos de Teste (as duas primeiras setas). A Automação é opcional e só começa depois que o usuário aprovar explicitamente os Casos de Teste — o agente nunca avança sozinho para automação, mesmo quando o pedido original já a menciona. Cada seta é uma skill. O detalhamento completo de princípios (rastreabilidade, cobertura por risco, independência/determinismo de testes, gestão de dados/segredos, Definition of Done) está em [AGENTS.md](AGENTS.md).

## Como instalar em um projeto com Claude Code

### Opção A — Instalador automático (recomendado)

```bash
# Instala no diretório atual
python QAGente/install.py --target /caminho/do/projeto --tool claude --profile default

# Instala globalmente (~/.claude, disponível em todos os projetos — regras de AGENTS.md/CLAUDE.md
# não se aplicam ao modo global, pois são específicas de cada projeto)
python QAGente/install.py --global

# Veja o que seria feito sem alterar nada
python QAGente/install.py --target /caminho/do/projeto --dry-run

# Reinstalar sobrescrevendo skills/agente já copiados anteriormente
python QAGente/install.py --target /caminho/do/projeto --force
```

Para instalar em outras ferramentas:

```bash
python QAGente/install.py --target /caminho/do/projeto --tool copilot --profile frontend-web
python QAGente/install.py --target /caminho/do/projeto --tool cursor --profile frontend-web
python QAGente/install.py --target /caminho/do/projeto --tool windsurf --profile backend-api
python QAGente/install.py --target /caminho/do/projeto --tools claude,copilot,cursor,windsurf --profile default
```

Instalações em projeto criam `.qagente/quality-profile.json`. As regras comuns ficam no núcleo do QAGente; o adaptador traduz o núcleo para o formato reconhecido pela ferramenta selecionada. Os perfis podem ser copiados e adaptados pelo time.

Não usa dependências externas (só a biblioteca padrão do Python 3). O instalador:

- copia `skills/*` para `<projeto>/.claude/skills/` (idempotente — roda de novo sem duplicar; usa `--force` para atualizar skills já instaladas);
- copia `agent.md` para `<projeto>/.claude/agents/qa-especialista.md`;
- **mescla** (não sobrescreve) o conteúdo de `AGENTS.md` no `AGENTS.md` do projeto alvo, dentro de um bloco marcado (`<!-- QAGente:start/end -->`) que é atualizado, não duplicado, em reinstalações;
- cria `CLAUDE.md` (ponteiro para `AGENTS.md`) se não existir, ou apenas adiciona uma nota referenciando `AGENTS.md` se o projeto já tiver seu próprio `CLAUDE.md`;
- copia o perfil escolhido para `<projeto>/.qagente/quality-profile.json` (um perfil já existente é preservado, salvo com `--force`);
- cria as pastas de entrada/saída declaradas em `paths` **pelo perfil efetivo do projeto** — ou seja, se um perfil anterior foi preservado, são as pastas dele que são criadas, não as do perfil passado em `--profile`.

Caminhos absolutos ou que escapem da raiz do projeto (`../`) são recusados com aviso, e `--dry-run` mostra os caminhos efetivos antes de qualquer alteração.

Use `--symlink` em vez de cópia se preferir manter os arquivos vinculados a este harness (pode exigir privilégio no Windows).

### Validando um perfil

```bash
python QAGente/install.py --validate-profile fullstack
python QAGente/install.py --validate-profile ./meu-time.json
```

Valida e sai, sem instalar nada. Reporta dois níveis:

- **erro** — o perfil está estruturalmente quebrado (tipo errado, nível de risco duplicado,
  `enabled` não booleano, framework ausente com a fase ligada). Impede a instalação.
- **aviso** — o perfil é utilizável, mas algo será ignorado ou não faz o que parece: chave
  desconhecida, caminho absoluto, nome de variável de ambiente fora do padrão, ou uma
  invariante de `AGENTS.md` declarada como `false` (o que não a desliga).

Sai com código 1 se houver erros. A mesma validação roda a cada instalação.

### Testes do instalador

```bash
python -m unittest test_install -v
```

Só usa `unittest` da biblioteca padrão. Os testes de integração executam o `install.py` real
como subprocesso dentro de um diretório temporário — nenhum teste escreve no harness nem em
`~/.claude`.

O CI roda a mesma suíte a cada push, em `ubuntu-latest` e `windows-latest`, nos Python 3.9 e
3.13. O instalador manipula caminhos nos dois sistemas, então rodar nos dois evita que uma
suposição de separador ou de quebra de linha passe despercebida.

### Opção B — Manual

1. Copie `AGENTS.md` e `CLAUDE.md` para a raiz do projeto (ou mescle o conteúdo de `AGENTS.md` no `CLAUDE.md`/`AGENTS.md` já existente do projeto).
2. Copie o conteúdo de `skills/` para `.claude/skills/` do projeto (ou `~/.claude/skills/` para instalação global).
3. Copie `agent.md` para `.claude/agents/qa-especialista.md` para disponibilizá-lo como subagente invocável (`@qa-especialista` ou delegação automática pela `description`).

## Como usar

- "Analisa esse PRD e me diz o que precisamos testar" → aciona `analise-documentacao-testes`.
- "Escreve os casos de teste em Gherkin para esses cenários" → aciona `escrita-casos-teste`.
- "Automatiza esses testes de API em Robot Framework" → aciona `robot-framework-api`.
- "Automatiza esse fluxo de checkout em Cypress" → aciona `cypress-ui-automation`.
- "Pega esse ticket e já entrega os testes de API automatizados" → o agente percorre a análise e a escrita dos casos de teste (Fases 1-2), mostrando cada artefato intermediário, e então pede aprovação explícita antes de iniciar a automação (Fase 3a/3b) — mesmo que o pedido original já tenha pedido automação de ponta a ponta.

## Licença

O código (`install.py`, `test_install.py`) está sob a [licença MIT](LICENSE).

O conteúdo das skills carrega `license: CC-BY-4.0` no frontmatter de cada `SKILL.md`, herdado do
formato de origem — veja a seção abaixo. Se você redistribuir as skills, preserve a atribuição.

## Origem dos padrões

Estrutura e convenções (frontmatter `name`/`description`/`license`/`metadata`, formato `[O quê] + [Quando usar] + [Quando NÃO usar]` na descrição, pasta `templates/`, arquivo `CLAUDE.md` como ponteiro de uma linha para `AGENTS.md`, formato de subagente com `name`/`description`/`model`/`tools`) foram extraídas de `agent-skills-main`, principalmente das skills `skill-architect`, `subagent-creator` e `playwright-skill`, e do próprio `AGENTS.md`/`CLAUDE.md` do repositório.
