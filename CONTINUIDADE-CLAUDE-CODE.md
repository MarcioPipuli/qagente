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
- Criados os perfis `default`, `backend-api`, `frontend-web` e `fullstack`.
- `agent.md` passou a exigir a leitura de `.qagente/quality-profile.json` quando o arquivo existir.
- `AGENTS.md` passou a definir a precedência de configuração e as regras que não podem ser removidas pelo perfil.
- Criados adaptadores para Copilot, Cursor e Windsurf.
- `install.py` passou a aceitar `--tool`, `--tools` e `--profile`.
- O instalador passou a descobrir as skills automaticamente lendo o diretório `skills/`.
- O instalador passou a copiar skills para `.qagente/skills/` em instalações não-Claude.
- O instalador evita criar `CLAUDE.md` quando a instalação é exclusiva para Copilot, Cursor ou Windsurf.
- O README foi atualizado com os novos comandos.
- Suíte de testes (`test_install.py`, 70 testes em `unittest` puro).
- CI no GitHub Actions rodando a suíte em Linux e Windows, Python 3.9 e 3.13.

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
| `profiles/fullstack.json` | Perfil para times que cuidam de API e UI no mesmo repositório |
| `adapters/copilot/` | Instruções e agente customizado para GitHub Copilot |
| `adapters/cursor/` | Regra `.mdc` para Cursor |
| `adapters/windsurf/` | Regra Markdown para Windsurf |
| `skills/` | Workflows de análise, BDD, Robot Framework e Cypress |
| `README.md` | Visão geral, uso e instalação |
| `test_install.py` | Testes do instalador e do conteúdo do harness |
| `.github/workflows/tests.yml` | CI: suíte em Linux e Windows a cada push |

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
│   ├── frontend-web.json
│   └── fullstack.json
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

### 8.2 As skills ainda contêm defaults prescritivos — RESOLVIDO (2026-08-28)

As 5 skills ganharam uma seção `## Configuração` logo após a introdução, com: a regra de
precedência, uma tabela `decisão → campo do perfil → default`, e a ressalva de que o perfil não
remove as regras universais de `AGENTS.md`.

As prescrições normativas viraram condicionais (prefixo do título, escala de risco, idioma do
Gherkin, atributo de seletor, variáveis de ambiente, diretórios de saída). Os exemplos de
código continuam concretos — `data-cy`, `QA_API_USER` — mas cada skill declara explicitamente
que são ilustrativos e que o valor do perfil vence no código gerado. Reescrever cada ocorrência
nos exemplos deixaria o código genérico e menos didático sem ganho real.

Duas guardas foram acrescentadas nas skills de automação: se `api.framework`/`ui.framework` não
for a ferramenta da skill, ela avisa que não se aplica em vez de gerar código na ferramenta
errada; se `api.enabled`/`ui.enabled` for `false`, pede confirmação antes de prosseguir.

`gherkin-palavras-chave` documenta só o português, então sua seção Configuração diz que a skill
se aplica quando `conventions.gherkin_language` for `pt` e manda usar a gramática oficial do
Gherkin nos demais idiomas.

Coberto por `test_install.ReferenciasDeCaminhoTest` (3 testes novos): toda skill cita o perfil,
as skills de automação citam os campos de framework, e cada default rígido cita o campo que
pode substituí-lo.

**Ponto aberto:** os `risk_levels` são declarados no perfil em inglês (`high`, `medium`, `low`)
enquanto os artefatos saem em pt-BR. A skill de análise manda traduzir para o idioma de
`language`, mas isso é convenção em texto, não contrato. Se a 8.3 (validador de perfil) evoluir,
vale decidir se o perfil deve trazer os rótulos já no idioma do time.

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

### 8.8 Referência `../../AGENTS.md` quebra na instalação Claude — RESOLVIDO (2026-08-28)

As 4 skills passaram a citar ``AGENTS.md``, na raiz do projeto, em vez de um caminho relativo.
A referência descritiva vale nos três contextos (repositório do QAGente, `.claude/skills/` e
`.qagente/skills/`), enquanto `../../AGENTS.md` só valia em dois.

O import `../../resources/api_client.resource` na skill de Robot Framework **não** foi
alterado: aquilo é um caminho do próprio Robot dentro da suíte gerada, não uma referência a
arquivo do harness.

### 8.9 Adaptador do Copilot é contraditório — RESOLVIDO (2026-08-28)

`adapters/copilot/qa-especialista.agent.md` passou a apontar para `.qagente/skills/`, que é
onde o instalador de fato copia as skills portáteis. Os dois arquivos do adaptador concordam.

### 8.10 Guarda de regressão para 8.8 e 8.9

`test_install.ReferenciasDeCaminhoTest` lê o conteúdo das skills e dos adaptadores e falha se
`../../AGENTS.md` ou `.github/skills` reaparecerem. Inclui um teste que confere que as cinco
skills existem, para que os outros não passem por vacuidade caso o diretório mude de lugar.

Vale como modelo: erro em texto de skill não quebra o instalador — faz o agente procurar
arquivo no lugar errado em silêncio, que é pior. Referências de caminho no conteúdo merecem
teste como código.

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

`test_install.py`: 70 testes na última contagem, `unittest` puro, ~9 s (eram 60 ao fim desta etapa; as demais cresceram a suíte). Estrutura em duas camadas — testes de
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

### Etapa 3 — Tornar as skills orientadas ao perfil — CONCLUÍDA (2026-08-28)

Ver pendência 8.2. As 5 skills ganharam a seção `## Configuração` e as prescrições normativas
viraram condicionais. Coberto por 3 testes em `ReferenciasDeCaminhoTest`.

### Etapa 4 — Validar cada ferramenta (PRÓXIMA — depende do usuário)

É o único item que nenhum teste automatizado cobre, e o que decide se o MVP multiplataforma é
real ou apenas plausível. Abrir um projeto de teste separado em cada ferramenta e confirmar:

1. o adaptador é carregado;
2. o perfil é localizado;
3. as skills estão acessíveis;
4. o agente produz uma análise simples de requisito;
5. a configuração efetiva aparece na resposta;
6. os artefatos são criados nos caminhos do perfil.

Sugestão de roteiro: instalar com `--profile fullstack` numa pasta vazia, colocar um requisito
curto em `docs/requisitos/`, pedir "analisa esse requisito e me diz o que testar", e conferir se
a saída cita o perfil aplicado e cai em `qa/cenarios/`.

### Etapa 5 — Criar validador de perfil

Ver pendência 8.3. Adicionar validação estrutural e semântica dos perfis: tipos dos campos,
valores permitidos, coerência entre `enabled` e `framework`, nomes de variáveis de ambiente.

Possíveis comandos:

```bash
python QAGente/install.py --validate-profile profiles/frontend-web.json
```

ou um comando separado:

```bash
python QAGente/validate.py --profile profiles/frontend-web.json
```

Decidir junto o ponto aberto registrado na 8.2: os `risk_levels` são declarados em inglês e
escritos nos artefatos no idioma de `language`. Hoje isso é convenção em texto, não contrato.

### Etapa 6 — Deixar de prescrever framework acima das skills

As skills já respeitam `api.framework`/`ui.framework`, mas o nível acima delas não acompanhou:

- a `description` de `agent.md` diz "automatizar testes com Robot Framework (APIs) e Cypress
  (interfaces web)";
- as fases em `AGENTS.md` se chamam "Fase 3a — Automação de API (`skills/robot-framework-api`)"
  e "Fase 3b — Automação de UI (`skills/cypress-ui-automation`)".

Num projeto com perfil Playwright, o agente se descreve pela ferramenta errada. Esta etapa é
pré-requisito natural da pendência 8.5 (skill de Playwright): primeiro o núcleo deixa de assumir
a ferramenta, depois a nova skill entra sem conflito.

### Etapa 7 — Higiene do repositório

- `LICENSE`: as 5 skills declaram `license: CC-BY-4.0` no frontmatter e o README credita o
  `agent-skills-main` como origem dos padrões, mas o repositório não tem arquivo de licença.
  Resolver antes de tornar o repositório público.
- Alinhar o perfil `default` com a família dos outros três, ou documentar por que ele diverge:
  3 níveis de risco contra 4, `CT-` contra `TC-`, `data-cy` contra `data-testid`.

## 10. Prompt para retomada no Claude Code

Copie o texto abaixo em uma nova janela do Claude Code:

```text
Estamos continuando o desenvolvimento do projeto QAGente.

Leia primeiro:
- CONTINUIDADE-CLAUDE-CODE.md (seções 8 e 9 dizem o que já está feito)
- README.md
- agent.md
- AGENTS.md
- install.py
- test_install.py
- profiles/
- adapters/

Estado: o MVP multiplataforma está implementado para Claude Code, GitHub
Copilot, Cursor e Windsurf. O instalador aceita --tool, --tools e --profile,
cria .qagente/quality-profile.json, instala skills portáteis, gera adaptadores
e cria as pastas declaradas em profile.paths. As 5 skills leem o perfil. Há 4
perfis embarcados: default, backend-api, frontend-web e fullstack.

As Etapas 1, 2 e 3 estão concluídas (caminhos configuráveis, suíte de testes,
skills orientadas ao perfil). test_install.py tem 70 testes em unittest puro:

    python -m unittest test_install -v

Rode a suíte antes e depois de qualquer alteração. O CI (.github/workflows)
roda a mesma suíte em Linux e Windows a cada push.

Próximas tarefas, na ordem da seção 9:

1. Etapa 4 — validação manual dentro de cada ferramenta. Único item que nenhum
   teste cobre e o que decide se o MVP multiplataforma é real. Depende do
   usuário abrir cada ferramenta; não tente automatizar.
2. Etapa 5 — validador de perfil, resolvendo junto o ponto aberto sobre
   risk_levels registrado na 8.2.
3. Etapa 6 — deixar de prescrever Robot Framework/Cypress em agent.md e
   AGENTS.md, pré-requisito da skill de Playwright (8.5).
4. Etapa 7 — LICENSE e alinhamento do perfil default.

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
