# QAGente

[![Testes](https://github.com/MarcioPipuli/qagente/actions/workflows/tests.yml/badge.svg)](https://github.com/MarcioPipuli/qagente/actions/workflows/tests.yml)

Harness de um agente especialista em Qualidade de Software (QA/SDET), extraído dos padrões de qualidade e estrutura observados no repositório [`agent-skills-main`](../agent-skills-main) (Tech Leads Club — formato `SKILL.md`, convenção `AGENTS.md`/`CLAUDE.md`, definição de subagente).

## O que tem aqui

```
QAGente/
├── agent.md              # Definição do subagente "qa-especialista" (identidade, missão, roteamento)
├── AGENTS.md              # Regras de comportamento (rastreabilidade, risco, independência de testes, DoD)
├── CLAUDE.md               # Ponteiro para AGENTS.md (mesmo padrão usado pelo agent-skills-main)
├── contexto/               # Template de contexto do projeto (fatos do produto)
├── profiles/               # Perfis configuráveis por tipo de time/projeto
│   ├── default.json
│   ├── backend-api.json
│   ├── frontend-web.json
│   ├── frontend-playwright.json
│   └── fullstack.json
├── adapters/               # Instruções para cada ferramenta de IA
├── install.py              # Instalador automático (copia/mescla o harness em um projeto)
├── validate_skills.py      # Validador estrutural das skills (frontmatter, templates, referências)
├── run_evals.py            # Evals estáticos: o que cada skill precisa ensinar e desaconselhar
├── evals/                  # Uma spec por skill, 8+ casos cada
├── test_install.py         # Testes do instalador, do validador e dos evals (unittest, sem dependências externas)
├── .github/workflows/      # CI: valida, roda os evals e a suíte no Linux e no Windows
├── CONTRIBUTING.md         # Regras para quem mantém o harness (invariantes, validação, instalação real)
└── skills/
    ├── analise-documentacao-testes/   # Fase 1: PRD/ticket → cenários de teste priorizados por risco
    ├── gherkin-palavras-chave/        # Referência: gramática de Dado/Quando/Então/E/Mas (usada pela Fase 2)
    ├── escrita-casos-teste/           # Fase 2: cenários → documento BDD em Gherkin (pt) + rastreabilidade
    │   └── templates/
    ├── robot-framework-api/           # Fase 3a: casos de teste → automação de API em Robot Framework
    │   └── templates/
    ├── cypress-ui-automation/         # Fase 3b: casos de teste → automação de UI em Cypress
    │   └── templates/
    ├── playwright-ui-automation/      # Fase 3b (alternativa): automação de UI em Playwright
    │   └── templates/
    ├── priorizacao-por-risco/         # Apoio: matriz impacto × probabilidade → prioridade da Fase 1
    │   └── templates/
    ├── reproducao-bugs/               # Apoio: relato de bug → reprodução mínima → teste de regressão
    │   └── templates/
    ├── revisao-qualidade-testes/      # Apoio: revisão de testes existentes (6 dimensões de mau cheiro)
    │   └── templates/
    ├── confiabilidade-testes/         # Apoio: teste que oscila → causa raiz, correção e quarentena
    │   └── templates/
    └── dados-de-teste/                # Apoio: fábricas, isolamento, limpeza e anonimização da massa
        └── templates/
```

As seis primeiras skills são o fluxo (as fases mais a referência gramatical). As cinco últimas
são **skills de apoio**: entram fora da sequência das fases, quando o pedido não é "transforme
este requisito em teste" — e continuam sujeitas às mesmas regras universais de
[AGENTS.md](AGENTS.md). Detalhe do roteamento em
[AGENTS.md](AGENTS.md#skills-de-apoio-fora-da-sequência-das-fases).

## Pastas de entrada e saída

Os caminhos vêm do bloco `paths` do perfil (`.qagente/quality-profile.json`) — o instalador cria exatamente as pastas que o perfil declara, e o agente lê e grava nelas. Quando o perfil não traz `paths` utilizável, valem os defaults do QAGente: entrada em `entrada/` e saída em `saida/cenarios/`, `saida/casos-de-teste/`, `saida/robot/` e `saida/cypress/` (uma subpasta por fase).

Uma fase desligada no perfil não ganha pasta: com `"api": {"enabled": false}` o `api_tests` é pulado, e o mesmo vale para `ui_tests` com `"ui": {"enabled": false}`.

O nome-base do documento de origem é preservado no arquivo gerado, para manter a rastreabilidade entre entrada e saída. Um caminho indicado explicitamente pelo usuário no pedido tem prioridade sobre o perfil e sobre essa convenção. Detalhes em [AGENTS.md](AGENTS.md#entradas-e-saídas-convenção-de-pastas).

## Os dois arquivos de configuração

O instalador cria dois arquivos em `.qagente/`, e eles respondem perguntas diferentes:

| Arquivo | Responde | Formato |
|---|---|---|
| `quality-profile.json` | **Como** trabalhar: idioma, caminhos, frameworks, escala de risco, convenções | JSON, também lido pelo instalador |
| `contexto-projeto.md` | **O que é o produto**: fluxos críticos, áreas de risco com impacto de negócio, terminologia do domínio, ambientes, maturidade do time | Markdown, lido só pelo agente |

O contexto vem como template com placeholders e precisa ser preenchido — é dele que sai o
**impacto** na priorização da Fase 1. Sem ele, o agente prioriza por palpite e diz que está
fazendo isso. Com ele, um cenário é `critical` porque toca uma área que o time declarou
crítica, e o artefato cita qual.

Como o perfil, ele é preservado numa reinstalação: só `--force` substitui um arquivo já
preenchido.

Uma seção que ainda esteja com `[colchetes]` conta como não respondida, não como resposta.

## O que o perfil controla

O perfil (`.qagente/quality-profile.json`) é o contrato entre o núcleo do QAGente e as decisões
de cada time. Ele governa o instalador **e** o comportamento das skills:

| Campo | Governa |
|---|---|
| `language`, `artifact_format` | Idioma e formato dos artefatos gerados |
| `paths.*` | Onde o agente lê a entrada e grava cada fase; quais pastas o instalador cria |
| `paths.risk_matrix`, `paths.reviews` | Opcionais: saída das skills de apoio. Só criadas se declaradas — sem elas, a skill cai no fallback de [AGENTS.md](AGENTS.md#entradas-e-saídas-convenção-de-pastas) |
| `risk_levels`, `risk_method` | Escala e método de priorização dos cenários |
| `conventions.gherkin_language` | Idioma das palavras-chave do Gherkin |
| `conventions.scenario_title_prefix` | Prefixo dos títulos de cenário (`Validar que` por default) |
| `conventions.test_id_pattern` | Padrão de ID para rastreabilidade |
| `api.enabled`, `api.framework` | Se a automação de API existe e em qual ferramenta |
| `api.base_url_env`, `api.user_env`, `api.password_env` | Nomes das variáveis de ambiente |
| `ui.enabled`, `ui.framework` | Se a automação de UI existe e em qual ferramenta (`cypress` ou `playwright`) |
| `ui.selector_attribute`, `ui.language`, `ui.base_url_env` | Convenções dos specs de UI |

### Perfis prontos

| Perfil | API | UI | Para quem |
|---|---|---|---|
| `default` | ligada | ligada | Primeiro contato ou projeto sem convenção própria; pastas neutras (`entrada/`, `saida/`) |
| `backend-api` | ligada | **desligada** | Time de API/backend |
| `frontend-web` | **desligada** | ligada | Time de frontend/UI usando Cypress; specs em `cypress/e2e/` |
| `frontend-playwright` | **desligada** | ligada | Time de frontend/UI usando Playwright e TypeScript |
| `fullstack` | ligada | ligada | Time que cuida das duas pontas; automação agrupada em `tests/api` e `tests/e2e` |

Os quatro compartilham a mesma família de convenções: 4 níveis de risco com `critical`, IDs
`TC-{DOMAIN}-{NUMBER}` e seletor `data-testid`. O que distingue o `default` são os caminhos
neutros (`entrada/`, `saida/`), pensados para quem ainda não tem estrutura de repositório
definida; os outros três assumem `docs/requisitos/`, `qa/` e `tests/`.

Copie o mais próximo do seu contexto e ajuste.

Cada skill traz uma seção **Configuração** com os campos que a afetam e o default de cada um.
A precedência é sempre: **instrução explícita do usuário → perfil do projeto → defaults da
skill**. O perfil não pode desligar as regras universais de [AGENTS.md](AGENTS.md)
(rastreabilidade, proteção de segredos, independência dos testes, entrada tratada como dado
não confiável, registro de lacunas e evidência real de execução).

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

# Reinstalar sobrescrevendo as skills e o agente já copiados anteriormente
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

### Validação das skills

```bash
python QAGente/validate_skills.py
python QAGente/validate_skills.py --strict
```

Enquanto `--validate-profile` valida a configuração do time, este valida o conteúdo que o
agente lê como instrução: `name` do frontmatter igual ao diretório, `metadata.category` na
lista (`analise`, `escrita`, `automacao`, `referencia`), as quatro seções de formato
(`<objetivo>`, `## Perguntas de descoberta`, `## Pronto quando`, `## Skills relacionadas`),
presença da seção `## Configuração` e da leitura do perfil, template citado que existe e
template em disco que é citado, referência `skills/<nome>` que resolve, teto de linhas, e
toda skill roteada por `agent.md` ou `AGENTS.md`.

Usa os mesmos dois níveis do validador de perfil. Um erro em texto de skill não quebra o
instalador — faz o agente procurar arquivo no lugar errado, em silêncio, que é pior.

Uma categoria pode dispensar uma seção que genuinamente não se aplica a ela: a skill de
referência (`gherkin-palavras-chave`) é consultada dentro de outra fase e não tem fluxo de
descoberta a percorrer. A dispensa é estreita de propósito — seção vazia só para satisfazer
o validador é pior que a ausência dela. O CI roda com `--strict`, então hoje qualquer aviso
também reprova.

### Evals das skills

```bash
python QAGente/run_evals.py
python QAGente/run_evals.py --skill cypress-ui-automation --verbose
```

Enquanto o validador cuida da forma da skill, os evals cuidam do conteúdo. Cada caso em
`evals/<skill>-evals.json` é um pedido que o usuário poderia fazer, com dois campos:

- `expected_patterns` — o que a skill precisa **ensinar**. Falha se o padrão não aparece no
  SKILL.md nem nos templates.
- `anti_patterns` — o que a skill precisa **desaconselhar**. Falha se o padrão nunca é
  mencionado (a skill deixou de avisar contra ele) ou se aparece em contexto de recomendação.

A segunda regra é o ponto: a leitura ingênua — "o anti-padrão não pode aparecer no texto" —
reprovaria justamente a skill que faz a coisa certa, que é mostrar o erro para ensinar a
evitá-lo. Uma ocorrência conta como aviso quando a linha, uma das três acima ou o título da
seção carrega marca de negação (`❌`, "nunca", "evite", "em vez de"...).

Estático significa que a checagem é contra o texto da skill, não contra a resposta de um
modelo: é determinístico, roda em CI e não custa chamada de API. Um eval verde não prova que
o agente acertou — prova que a skill continua ensinando o que o caso exige. Modo `--live`
não existe de propósito: exigiria dependência de rede e de modelo.

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

Para alterar o harness — invariantes de arquitetura, método de trabalho e a sequência de
validação completa —, veja [CONTRIBUTING.md](CONTRIBUTING.md).

### Opção B — Manual

1. Copie `AGENTS.md` e `CLAUDE.md` para a raiz do projeto (ou mescle o conteúdo de `AGENTS.md` no `CLAUDE.md`/`AGENTS.md` já existente do projeto).
2. Copie o conteúdo de `skills/` para `.claude/skills/` do projeto (ou `~/.claude/skills/` para instalação global).
3. Copie `agent.md` para `.claude/agents/qa-especialista.md` para disponibilizá-lo como subagente invocável (`@qa-especialista` ou delegação automática pela `description`).

## Como usar

- "Analisa esse PRD e me diz o que precisamos testar" → aciona `analise-documentacao-testes`.
- "Escreve os casos de teste em Gherkin para esses cenários" → aciona `escrita-casos-teste`.
- "Automatiza esses testes de API em Robot Framework" → aciona `robot-framework-api`.
- "Automatiza esse fluxo de checkout em Cypress" → aciona `cypress-ui-automation`.
- "Automatiza esse fluxo em Playwright" → aciona `playwright-ui-automation`. A skill de UI que responde é a de `ui.framework`; a outra recusa e aponta para ela.
- "Pega esse ticket e já entrega os testes de API automatizados" → o agente percorre a análise e a escrita dos casos de teste (Fases 1-2), mostrando cada artefato intermediário, e então pede aprovação explícita antes de iniciar a automação (Fase 3a/3b) — mesmo que o pedido original já tenha pedido automação de ponta a ponta.

## Licença

| Parte | Licença |
|---|---|
| Código (`install.py`, `test_install.py`) | [MIT](LICENSE) |
| Conteúdo das skills do fluxo (`SKILL.md`) | CC-BY-4.0, declarado no frontmatter de cada arquivo |
| Conteúdo das 5 skills de apoio | MIT, declarado no frontmatter — são adaptações de material MIT (ver abaixo) |

O arranjo espelha deliberadamente o do projeto de origem (ver abaixo), que separa o código do
conteúdo pelo mesmo critério. Se você redistribuir as skills, preserve a atribuição.

As skills de apoio ficam em MIT porque foram **adaptadas** de
[qa-skills](https://github.com/petrkindlmann/qa-skills), de Petr Kindlmann, licenciado sob MIT —
manter a licença de origem é o que preserva a atribuição exigida por ela. O campo
`metadata.adaptado_de` no frontmatter de cada uma diz de qual skill de lá ela veio.

## Origem dos padrões

As convenções estruturais do QAGente vêm de **[agent-skills](https://github.com/tech-leads-club/agent-skills)**,
de **Tech Leads Club**, cujo conteúdo de skills é licenciado sob
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).

O que foi adotado de lá:

- frontmatter `name`/`description`/`license`/`metadata`;
- o formato `[O quê] + [Quando usar] + [Quando NÃO usar]` na descrição;
- a pasta `templates/` ao lado de cada `SKILL.md`;
- `CLAUDE.md` como ponteiro de uma linha para `AGENTS.md`;
- o formato de subagente com `name`/`description`/`model`/`tools`.

Essas convenções foram observadas principalmente nas skills `skill-architect`, `subagent-creator`
e `playwright-skill`, e no `AGENTS.md`/`CLAUDE.md` do repositório.

**Indicação de mudanças:** o conteúdo das seis skills do fluxo é original, escrito para o domínio
de QA/SDET — o que foi reaproveitado é a estrutura, não o texto. Nenhuma skill do fluxo é cópia ou
adaptação de uma skill de lá.

### Skills de apoio: adaptadas de qa-skills

As cinco skills de apoio são adaptações declaradas de
**[qa-skills](https://github.com/petrkindlmann/qa-skills)**, de Petr Kindlmann, licenciado sob
[MIT](https://opensource.org/licenses/MIT):

| Skill do QAGente | Origem em qa-skills |
|---|---|
| `priorizacao-por-risco` | `risk-based-testing` |
| `reproducao-bugs` | `bug-reproduction` |
| `revisao-qualidade-testes` | `ai-qa-review` |
| `confiabilidade-testes` | `test-reliability` |
| `dados-de-teste` | `test-data-management` |

**O que mudou na adaptação:** texto reescrito em português; os exemplos de framework passaram de
Vitest/Jest/Playwright para os frameworks que o perfil do QAGente declara (Robot Framework,
Cypress, Playwright); a leitura de `.agents/qa-project-context.md` foi substituída pela dupla
`.qagente/quality-profile.json` + `.qagente/contexto-projeto.md`; cada skill ganhou a seção
`## Configuração` com a tabela de campos do perfil, as seções obrigatórias do validador, o
enquadramento nas regras universais de [AGENTS.md](AGENTS.md) (aprovação antes de automatizar,
proteção de segredos, evidência real de execução, testabilidade como achado e não como alteração),
templates próprios e uma spec de evals. Referências a ferramentas e fornecedores que não se
aplicam ao harness foram removidas; GDPR virou LGPD onde o contexto é brasileiro.
