# QAGente — Documento de Continuidade para Claude Code

## 1. Objetivo do projeto

O QAGente é um harness de agente especializado em Qualidade de Software, com foco em QA/SDET. A proposta é permitir que diferentes times usem o mesmo núcleo de qualidade, informando seus próprios padrões por meio de um perfil configurável.

O projeto deve funcionar em diferentes ferramentas de IA, especialmente:

- Claude Code;
- GitHub Copilot;
- Cursor;
- Windsurf.

A unidade compartilhada do projeto é o modelo de qualidade, composto por princípios, fluxo, skills e perfil. Cada ferramenta recebe um adaptador no formato que consegue interpretar.

## 2. Estado atual

O MVP de configuração multiplataforma foi implementado.

### Entregas concluídas

- Criados perfis JSON configuráveis por projeto/time.
- Criados os perfis `default`, `backend-api` e `frontend-web`.
- `agent.md` passou a exigir a leitura de `.qagente/quality-profile.json` quando o arquivo existir.
- `AGENTS.md` passou a definir a precedência de configuração e as regras que não podem ser removidas pelo perfil.
- Criados adaptadores para Copilot, Cursor e Windsurf.
- `install.py` passou a aceitar `--tool`, `--tools` e `--profile`.
- O instalador passou a descobrir as skills automaticamente lendo o diretório `skills/`.
- O instalador passou a copiar skills para `.qagente/skills/` em instalações não-Claude.
- O instalador evita criar `CLAUDE.md` quando a instalação é exclusiva para Copilot, Cursor ou Windsurf.
- O README foi atualizado com os novos comandos.

### Arquivos principais

| Arquivo | Responsabilidade |
|---|---|
| `agent.md` | Identidade, escopo, roteamento e missão do agente `qa-especialista` |
| `AGENTS.md` | Princípios, fluxo, limites, convenções e contrato de comportamento |
| `CLAUDE.md` | Ponteiro para `AGENTS.md` |
| `install.py` | Instalação em projetos Claude Code e geração dos adaptadores |
| `profiles/default.json` | Perfil base do QAGente |
| `profiles/backend-api.json` | Perfil para times focados em API/backend |
| `profiles/frontend-web.json` | Perfil para times focados em frontend/UI |
| `adapters/copilot/` | Instruções e agente customizado para GitHub Copilot |
| `adapters/cursor/` | Regra `.mdc` para Cursor |
| `adapters/windsurf/` | Regra Markdown para Windsurf |
| `skills/` | Workflows de análise, BDD, Robot Framework e Cypress |
| `README.md` | Visão geral, uso e instalação |

## 3. Arquitetura atual

```text
QAGente/
├── agent.md
├── AGENTS.md
├── CLAUDE.md
├── install.py
├── profiles/
│   ├── default.json
│   ├── backend-api.json
│   └── frontend-web.json
├── adapters/
│   ├── copilot/
│   │   ├── copilot-instructions.md
│   │   └── qa-especialista.agent.md
│   ├── cursor/
│   │   └── qagente.mdc
│   └── windsurf/
│       └── qagente.md
└── skills/
    ├── analise-documentacao-testes/
    ├── gherkin-palavras-chave/
    ├── escrita-casos-teste/
    ├── robot-framework-api/
    └── cypress-ui-automation/
```

### Modelo de instalação Claude Code

```text
projeto/
├── AGENTS.md
├── CLAUDE.md
├── .claude/
│   ├── agents/
│   │   └── qa-especialista.md
│   └── skills/
│       └── <skills copiadas>
└── .qagente/
    └── quality-profile.json
```

### Modelo de instalação multiplataforma

```text
projeto/
├── AGENTS.md
├── .qagente/
│   ├── quality-profile.json
│   └── skills/
├── .github/
│   ├── copilot-instructions.md
│   └── agents/
│       └── qa-especialista.agent.md
├── .cursor/
│   └── rules/
│       └── qagente.mdc
└── .windsurf/
    └── rules/
        └── qagente.md
```

## 4. Perfis de qualidade

O perfil é um contrato JSON versionado no projeto consumidor:

```text
.qagente/quality-profile.json
```

Ele contém decisões variáveis do time, como:

- idioma dos artefatos;
- formato dos casos de teste;
- níveis de risco;
- método de análise de risco;
- diretórios de entrada e saída;
- framework de API;
- framework de UI;
- linguagem de automação;
- estratégia de seletores;
- nomes de variáveis de ambiente;
- padrão de IDs;
- gates de aprovação e evidência.

Exemplo de uso:

```bash
python QAGente/install.py --target ./projeto --tool copilot --profile frontend-web
```

O argumento `--profile` aceita tanto o nome de um arquivo dentro de `profiles/` quanto o caminho para um JSON customizado:

```bash
python QAGente/install.py --target ./projeto --tool cursor --profile ./meu-time.json
```

### Precedência definida

1. Instrução explícita do usuário.
2. `.qagente/quality-profile.json` do projeto.
3. Valores padrão documentados nas skills.
4. Defaults do QAGente.

As seguintes regras são universais e não devem ser desativadas pelo perfil:

- rastreabilidade;
- proteção de credenciais e segredos;
- independência e determinismo dos testes;
- registro de ambiguidades e lacunas;
- proibição de dados reais de produção;
- evidência real de execução antes de declarar automação concluída.

## 5. Comandos implementados

### Claude Code

```bash
python QAGente/install.py --target /caminho/do/projeto --tool claude --profile default
```

### Copilot

```bash
python QAGente/install.py --target /caminho/do/projeto --tool copilot --profile frontend-web
```

### Cursor

```bash
python QAGente/install.py --target /caminho/do/projeto --tool cursor --profile frontend-web
```

### Windsurf

```bash
python QAGente/install.py --target /caminho/do/projeto --tool windsurf --profile backend-api
```

### Várias ferramentas

```bash
python QAGente/install.py --target /caminho/do/projeto --tools claude,copilot,cursor,windsurf --profile default
```

### Simulação

```bash
python QAGente/install.py --target /caminho/do/projeto --tools copilot,cursor,windsurf --profile frontend-web --dry-run
```

### Sobrescrita

```bash
python QAGente/install.py --target /caminho/do/projeto --tool claude --profile default --force
```

Use `--force` com cuidado: skills, agente e perfil existentes podem ser substituídos.

### Instalação global

O modo global continua limitado ao Claude Code:

```bash
python QAGente/install.py --global --tool claude --profile default
```

O instalador rejeita `--global` combinado com Copilot, Cursor ou Windsurf, pois essas ferramentas usam regras específicas do projeto.

## 6. Skills existentes

### `analise-documentacao-testes`

Transforma PRD, user story, ticket, especificação técnica, ADR ou descrição informal em cenários priorizados por risco.

Cobre:

- caminho feliz;
- entradas inválidas;
- valores limite;
- regras de negócio;
- estados e transições;
- permissões;
- falhas de integração;
- lacunas documentais.

### `escrita-casos-teste`

Transforma cenários em casos BDD/Gherkin dentro de Markdown, com rastreabilidade, tópicos, cenários, esquemas e observações.

### `gherkin-palavras-chave`

Define a semântica de `Dado`, `Quando`, `Então`, `E` e `Mas` em português.

### `robot-framework-api`

Orienta automação de APIs REST/GraphQL com Robot Framework e RequestsLibrary, incluindo:

- keywords reutilizáveis;
- autenticação por ambiente;
- dados parametrizados;
- independência;
- limpeza;
- execução e evidência.

### `cypress-ui-automation`

Orienta automação E2E web com Cypress, incluindo:

- seletores estáveis;
- `data-cy`/`data-testid`;
- interceptação de rede;
- fixtures;
- `cy.session`;
- ausência de esperas fixas;
- execução e evidência.

## 7. Validações já realizadas

Foram executadas as seguintes validações:

- `python -m py_compile Agente de QA\\QAGente\\install.py`: aprovado.
- Validação dos três perfis com `ConvertFrom-Json`: aprovada.
- `get_errors` no instalador: nenhum erro encontrado.
- `dry-run` para Cursor com perfil `frontend-web`: aprovado.
- `dry-run` combinado para Claude Code, Copilot e Windsurf com perfil `backend-api`: aprovado.
- Instalação real em pasta temporária para Copilot, Cursor e Windsurf: arquivos gerados corretamente.
- Verificação de que instalações sem Claude não criam `CLAUDE.md`: aprovada.
- Fluxo de compatibilidade do Claude Code em `dry-run`: aprovado.

A pasta temporária usada no teste real não foi removida completamente pelo Windows devido a uma restrição de acesso, mas isso ocorreu depois da validação dos arquivos e não afetou o projeto QAGente.

## 8. Pendências técnicas conhecidas

### 8.1 Caminhos do perfil ainda não controlam o instalador — RESOLVIDO (2026-08-28)

`install_io_dirs()` passou a criar as pastas declaradas em `profile.paths`. `resolve_profile()`
agora devolve `(Path, dict)` em vez de só o caminho, que era o que bloqueava a correção.

Decisões tomadas:

- os diretórios continuam sendo criados automaticamente (com `.gitkeep`);
- `DEFAULT_IO_PATHS` (antiga `IO_DIRS`) virou fallback, usado só quando o perfil não traz
  `paths` utilizável;
- uma fase desligada no perfil não ganha pasta (`api.enabled: false` pula `api_tests`,
  `ui.enabled: false` pula `ui_tests`);
- caminhos absolutos, vazios ou com `..` são recusados com aviso, nunca criados;
- quando um perfil já existe no projeto e não há `--force`, ele é preservado **e passa a ser
  o perfil efetivo** — as pastas criadas são as dele, não as do perfil passado em `--profile`;
- `--dry-run` imprime os caminhos efetivos com o rótulo da fase.

`README.md` e `AGENTS.md` foram atualizados junto.

### 8.2 As skills ainda contêm defaults prescritivos

O agente já manda ler o perfil, mas as skills ainda mencionam diretamente padrões como:

- Gherkin em português;
- prefixo `Validar que`;
- níveis `Alta/Média/Baixa`;
- Robot Framework para API;
- Cypress para UI;
- `data-cy`/`data-testid`;
- estruturas de diretórios fixas.

Próxima correção recomendada: alterar cada skill para dizer “aplique o perfil; use este valor como default apenas quando o campo não existir”.

### 8.3 Profile schema ainda é mínimo

`resolve_profile()` valida apenas a presença de campos básicos. Ainda não valida:

- tipos dos campos;
- valores permitidos;
- coerência entre `enabled` e `framework`;
- existência de diretórios;
- nomes de variáveis de ambiente;
- versão suportada do perfil.

Próxima correção recomendada: criar `profiles/schema.json` ou uma validação Python sem dependências externas.

### 8.4 Adaptadores não têm testes próprios — RESOLVIDO (2026-08-28)

`test_install.py` cobre os 60 cenários da Etapa 2, incluindo os oito itens que estavam
listados aqui. Roda com `python -m unittest test_install -v`, sem dependências externas.

Ainda fora de cobertura, de propósito:

- instalação global de verdade (escreveria em `~/.claude`; só o caminho de recusa
  `--global` + ferramenta não-Claude é testado);
- `--symlink` (depende de privilégio no Windows);
- carregamento real dos adaptadores dentro de cada ferramenta (isso é a 8.6).

### 8.5 Não há adaptador Playwright

O núcleo menciona Cypress e Robot Framework. Um próximo perfil frontend pode escolher Playwright, mas ainda não há skill/template/adaptador específico para essa opção.

### 8.6 Integração com o formato real de cada ferramenta precisa de validação manual

Os arquivos foram gerados e têm sintaxe Markdown/frontmatter coerente, mas é necessário validar dentro de cada ferramenta:

- se o Claude Code carrega corretamente skills e agente;
- se o Copilot reconhece o `.agent.md` e `copilot-instructions.md`;
- se o Cursor aplica o `.mdc`;
- se o Windsurf carrega a regra no workspace.

### 8.7 Bugs corrigidos junto com a 8.1 (2026-08-28)

- `install_adapter()` estourava `KeyError` com qualquer arquivo novo dentro de um diretório de
  adaptador (`destinations[tool][source.name]`). Agora usa `.get()`, ignora diretórios e avisa
  em vez de derrubar a instalação.
- `install_skills()` assumia que toda entrada em `skills/` era diretório de skill (`is_dir=True`
  fixo) — um arquivo solto quebrava o `copytree`. Agora há `is_skill_dir()`: diretório, sem
  prefixo `.`/`__`, contendo `SKILL.md`.
- `profile_version` era exigida mas nunca conferida. Agora há `SUPPORTED_PROFILE_VERSIONS` e um
  aviso (não erro) para versões desconhecidas — a validação estrita fica para a 8.3.
- Docstring incorreta de `resolve_dirs()` (dizia que `project_root` era vazio no modo `--global`).

### 8.8 Referência `../../AGENTS.md` quebra na instalação Claude

As 4 skills apontam para `../../AGENTS.md`. O caminho resolve corretamente no repositório do
QAGente e em `.qagente/skills/`, mas em `.claude/skills/<skill>/SKILL.md` ele aponta para
`.claude/AGENTS.md`, que não existe — o arquivo fica na raiz do projeto. A ferramenta principal
é justamente a única com o link quebrado.

### 8.9 Adaptador do Copilot é contraditório

`adapters/copilot/copilot-instructions.md` manda usar `.qagente/skills/` (correto, é o que o
instalador cria); `adapters/copilot/qa-especialista.agent.md` manda usar `.github/skills/`, que
o instalador nunca cria.

## 9. Próxima sequência recomendada

### Etapa 1 — Corrigir caminhos configuráveis — CONCLUÍDA (2026-08-28)

Todos os critérios de aceite foram validados com instalação real em pasta temporária:

- perfil com caminhos customizados (`backend-api`) cria `docs/requisitos`, `qa/cenarios`,
  `qa/casos-de-teste`, `tests/api` — e não cria mais `entrada/`/`saida/*`;
- o perfil `default` continua produzindo os caminhos históricos;
- `--dry-run` mostra os caminhos efetivos e não toca no disco;
- `tests/e2e` é pulado no `backend-api` e `tests/api` é pulado no `frontend-web`;
- perfil hostil (`../../`, `C:/Windows/Temp`, `/etc`, string vazia) é recusado com aviso e
  nada vaza para fora da raiz do projeto;
- reinstalação é idempotente bit a bit (32 arquivos, hashes idênticos).

### Etapa 2 — Testar o instalador — CONCLUÍDA (2026-08-28)

`test_install.py`: 60 testes, `unittest` puro, ~9 s. Estrutura em duas camadas — testes de
unidade para as funções puras (`profile_io_dirs`, `disabled_path_keys`, `is_skill_dir`,
`merge_block`) e testes de integração que executam o `install.py` real como subprocesso em
diretório temporário.

A suíte foi verificada por mutação: cinco regressões introduzidas de propósito em `install.py`
foram todas detectadas — ignorar `profile.paths` (8 falhas), não recusar caminho absoluto
(5), perfil preservado deixar de governar os diretórios (1), voltar o `KeyError` do adaptador
(1) e fase desligada voltar a criar pasta (3).

Cenários cobertos:

Cenários mínimos:

- instalação Claude;
- instalação Copilot;
- instalação Cursor;
- instalação Windsurf;
- instalação combinada;
- perfil inexistente;
- perfil inválido;
- ferramenta inválida;
- projeto com `AGENTS.md` existente;
- perfil existente sem `--force`;
- reinstalação com `--force`;
- perfil com `paths` customizado cria exatamente esses diretórios (regressão da Etapa 1);
- perfil com fase desligada não cria a pasta daquela fase;
- perfil com caminho absoluto ou `..` é recusado sem criar nada fora da raiz;
- perfil preservado sem `--force` governa os diretórios criados;
- arquivo solto em `skills/` ou em `adapters/<tool>/` não derruba a instalação;
- perfil em disco ilegível não derruba a reinstalação;
- `--dry-run` não escreve nada e mostra os caminhos efetivos;
- reinstalação é idempotente bit a bit.

Decisão tomada durante os testes: um caminho de perfil com barra inicial (`/qa/casos`) é
tratado como absoluto e recusado, em vez de ser reinterpretado como relativo à raiz do
projeto — recusar com aviso é mais previsível do que adivinhar a intenção.

### Etapa 3 — Criar validador de perfil

Adicionar validação estrutural e semântica dos perfis.

Possíveis comandos:

```bash
python QAGente/install.py --validate-profile profiles/frontend-web.json
```

ou um comando separado:

```bash
python QAGente/validate.py --profile profiles/frontend-web.json
```

### Etapa 4 — Tornar as skills orientadas ao perfil

Adicionar, no início de cada skill, uma seção equivalente a:

```markdown
## Configuração

Leia `.qagente/quality-profile.json`. Quando uma configuração estiver presente,
aplique-a. Os valores desta skill são defaults e não devem substituir uma decisão
explícita do perfil ou do usuário.
```

Depois substituir as prescrições rígidas por regras condicionais.

### Etapa 5 — Validar cada ferramenta

Abrir um projeto de teste separado em cada ferramenta e confirmar:

1. o adaptador é carregado;
2. o perfil é localizado;
3. as skills estão acessíveis;
4. o agente produz uma análise simples de requisito;
5. a configuração efetiva aparece na resposta;
6. os artefatos são criados nos caminhos do perfil.

## 10. Prompt para retomada no Claude Code

Copie o texto abaixo em uma nova janela do Claude Code:

```text
Estamos continuando o desenvolvimento do projeto QAGente.

Leia primeiro:
- CONTINUIDADE-CLAUDE-CODE.md
- README.md
- agent.md
- AGENTS.md
- install.py
- profiles/default.json
- profiles/backend-api.json
- profiles/frontend-web.json
- adapters/

O MVP multiplataforma já foi implementado para Claude Code, GitHub Copilot,
Cursor e Windsurf. O instalador aceita --tool, --tools e --profile, cria
.qagente/quality-profile.json, instala skills portáteis e gera adaptadores.
A Etapa 1 (caminhos vindos de profile.paths) está concluída e validada — veja
a seção 8.1 e a Etapa 1 na seção 9 antes de mexer em install_io_dirs().

A Etapa 2 também está concluída: test_install.py tem 60 testes em unittest puro
(python -m unittest test_install -v). Rode a suíte antes e depois de qualquer
alteração no instalador.

Próximas tarefas, em ordem de custo/benefício:

1. Pendências 8.8 e 8.9 — correções pequenas e independentes: a referência
   ../../AGENTS.md quebra em .claude/skills/, e o adaptador do Copilot aponta
   para .github/skills/, que o instalador não cria.
2. Etapa 3 — validador de perfil (schema estrutural e semântico).
3. Etapa 4 — tornar as skills orientadas ao perfil (pendência 8.2): hoje
   nenhuma das 5 skills menciona .qagente/quality-profile.json.

Antes de editar, formule uma hipótese local e um teste discriminante. Faça a
menor alteração possível, valide imediatamente com py_compile e os testes
focados, e só então prossiga para documentação ou refatorações adjacentes.
Não faça commit. Não reverta alterações existentes.
```

## 11. Regras para continuidade

- Não recriar a arquitetura do zero.
- Preservar o núcleo universal de qualidade.
- Não duplicar instruções específicas para cada ferramenta sem necessidade.
- Preferir perfis declarativos a cópias do agente por time.
- Tratar as regras de segurança e rastreabilidade como invariantes.
- Validar o instalador em pasta temporária antes de testar em projetos reais.
- Não executar instalação real em `game/` ou outro projeto existente sem solicitação explícita.
- Não fazer commit automaticamente.
