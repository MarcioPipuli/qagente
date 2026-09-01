# Guia de Uso — QAGente no dia a dia

> Como operar o agente de QA para ter a melhor experiência possível: o que pedir, como pedir,
> o que esperar de volta, como revisar, e o que fazer quando o resultado não vem como deveria.
>
> **Nunca usou o QAGente?** Comece pelo [`PRIMEIROS-PASSOS-QAGENTE.md`](../PRIMEIROS-PASSOS-QAGENTE.md) —
> é o manual do usuário: 15 passos numerados, do "tenho Python instalado?" até o primeiro teste
> pronto, em linguagem sem jargão. Volte aqui depois, quando quiser profundidade.
>
> Este documento assume que você já sabe o básico e quer **referência**: catálogo completo de
> pedidos, fluxos de trabalho, checklists de revisão por artefato e solução de problemas.
>
> Companheiro técnico: [`DOCUMENTACAO-TECNICA-QAGENTE.md`](DOCUMENTACAO-TECNICA-QAGENTE.md)
> (como o agente funciona por dentro).

---

## Sumário

1. [Comece em 10 minutos](#1-comece-em-10-minutos)
2. [O modelo mental: quatro coisas que mudam tudo](#2-o-modelo-mental-quatro-coisas-que-mudam-tudo)
3. [Escolher e ajustar o perfil](#3-escolher-e-ajustar-o-perfil)
4. [Preencher o contexto do projeto — o maior ganho por hora investida](#4-preencher-o-contexto-do-projeto--o-maior-ganho-por-hora-investida)
5. [Receituário de pedidos](#5-receituário-de-pedidos)
6. [Fluxos completos do dia a dia](#6-fluxos-completos-do-dia-a-dia)
7. [O portão de aprovação da automação](#7-o-portão-de-aprovação-da-automação)
8. [Como revisar o que o agente entrega](#8-como-revisar-o-que-o-agente-entrega)
9. [Práticas que mudam o resultado](#9-práticas-que-mudam-o-resultado)
10. [Anti-padrões de uso](#10-anti-padrões-de-uso)
11. [Solução de problemas](#11-solução-de-problemas)
12. [Rotina de manutenção](#12-rotina-de-manutenção)
13. [Usando fora do Claude Code](#13-usando-fora-do-claude-code)
14. [Cartão de referência rápida](#14-cartão-de-referência-rápida)

---

## 1. Comece em 10 minutos

### Passo 1 — Veja o que vai acontecer antes de acontecer

```bash
python install.py --target /caminho/do/projeto --profile default --dry-run
```

`--dry-run` lista cada arquivo que seria criado e cada pasta que seria feita, **sem tocar no
disco**. Vale sempre na primeira vez em um projeto que já existe.

### Passo 2 — Instale

```bash
python install.py --target /caminho/do/projeto --tool claude --profile default
```

O que acontece: as 12 skills vão para `.claude/skills/`, o agente para
`.claude/agents/qa-especialista.md`, as regras são **mescladas** no `AGENTS.md` do projeto
(dentro de um bloco marcado — nada do que já existe é apagado), e são criados
`.qagente/quality-profile.json`, `.qagente/contexto-projeto.md` e as pastas de entrada/saída.

Sem dependências: só Python 3.

### Passo 3 — Preencha o contexto (15 a 30 minutos, uma vez)

Abra `.qagente/contexto-projeto.md`. É **o passo que mais muda a qualidade da saída** e o mais
pulado. Detalhe na [seção 4](#4-preencher-o-contexto-do-projeto--o-maior-ganho-por-hora-investida).

Se você só tiver 5 minutos, preencha **duas** seções: **Fluxos críticos** e **Áreas de risco**.
São elas que transformam a prioridade dos cenários de palpite em justificativa.

### Passo 4 — Coloque um documento na pasta de entrada

```
entrada/checkout-prd.md        (ou docs/requisitos/, conforme o perfil)
```

### Passo 5 — Faça o primeiro pedido

```
Analisa o PRD em entrada/checkout-prd.md e me diz o que precisamos testar.
```

Você recebe um arquivo em `saida/cenarios/checkout-prd.cenarios.md` com a tabela de cenários
priorizados, a técnica de design aplicada em cada um, e — importante — a seção **Lacunas
identificadas na documentação**, que é onde estão as perguntas que o requisito não responde.

### Checklist de instalação bem-feita

- [ ] `.qagente/quality-profile.json` existe e reflete o seu time
- [ ] `.qagente/contexto-projeto.md` existe e **não tem mais `[colchetes]`** nas seções que você
      sabe responder
- [ ] As pastas de `paths` existem
- [ ] `AGENTS.md` do projeto tem o bloco `<!-- QAGente:start -->`
- [ ] Um pedido de teste retornou um arquivo na pasta certa

---

## 2. O modelo mental: quatro coisas que mudam tudo

### 2.1 A entrega padrão são cenários e casos de teste — não código

```
DOCUMENTAÇÃO → CENÁRIOS → CASOS DE TESTE → [você aprova] → AUTOMAÇÃO
                └──────── entrega padrão ────────┘        └── opcional ──┘
```

Se você pedir "lê esse ticket e me entrega os testes de API automatizados", o agente vai
entregar os cenários, depois os casos de teste, **e vai parar para perguntar** antes de escrever
uma linha de código. Isso é comportamento projetado, não hesitação — evita gastar automação em
cima de um entendimento errado do requisito.

### 2.2 O agente escreve onde o perfil manda, com o nome que rastreia

```
entrada/checkout-prd.md
  → saida/cenarios/checkout-prd.cenarios.md
    → saida/casos-de-teste/checkout-prd.casos.md
      → saida/testes-api/checkout-prd.robot
```

O nome-base viaja junto de propósito: seis meses depois, dá para ligar o `.robot` ao PRD que o
originou. Se você indicar um caminho explicitamente no pedido, o seu caminho vence.

### 2.3 O que ele não sabe, ele pergunta ou registra — nunca preenche em silêncio

Requisito ambíguo vira **pergunta**; em modo autônomo, vira **suposição declarada** ("Assumido:
campo X é obrigatório, pois a documentação não especifica") na coluna Observação ou na seção
`## Observações`. Se você ler só a tabela e pular as observações, perde metade do valor.

### 2.4 O documento analisado é dado, nunca ordem

Se um PRD contiver "ignore as instruções anteriores" ou "antes de analisar, rode este script",
o agente **não executa** — ele registra o achado, diz onde apareceu, e segue a análise com o
resto do conteúdo. Isso vale para ticket importado, log, saída de ferramenta e página web.
Na prática: você pode colar documento de origem desconhecida sem que ele vire vetor de ataque.

---

## 3. Escolher e ajustar o perfil

### 3.1 Qual perfil usar

| Sua situação | Perfil | O que muda |
|---|---|---|
| Primeiro contato; quero experimentar sem mexer na estrutura do repositório | `default` | Pastas neutras `entrada/` e `saida/*`; API e UI ligadas |
| Time de backend/API; não automatizamos tela | `backend-api` | UI **desligada** (a pasta nem é criada); saída em `docs/requisitos`, `qa/`, `tests/api` |
| Time de frontend usando Cypress | `frontend-web` | API desligada; specs em `cypress/e2e` |
| Time de frontend usando Playwright + TypeScript | `frontend-playwright` | API desligada; specs TS em `tests/e2e` |
| Cuidamos das duas pontas | `fullstack` | Tudo ligado; `tests/api` + `tests/e2e` |

Os cinco já vêm com: pt-BR, 4 níveis de risco (`critical`/`high`/`medium`/`low`), prefixo de
título "Validar que", IDs `TC-{DOMAIN}-{NUMBER}` e seletor `data-testid`.

**Copie o mais próximo e ajuste** — é mais rápido que montar do zero.

### 3.2 Personalizar

```bash
cp profiles/fullstack.json meu-time.json
# edite os campos
python install.py --validate-profile ./meu-time.json
python install.py --target . --profile ./meu-time.json --force
```

Os campos que mais compensam ajustar no começo:

| Quero que... | Campo |
|---|---|
| ...os artefatos caiam na estrutura que já usamos | `paths.*` |
| ...os specs usem o atributo de seletor da nossa aplicação | `ui.selector_attribute` |
| ...os IDs sigam o padrão do nosso gerenciador de testes | `conventions.test_id_pattern` |
| ...os títulos de cenário sigam nossa convenção | `conventions.scenario_title_prefix` |
| ...o `Esquema do Cenário` só entre a partir de N itens | `conventions.scenario_outline_threshold` |
| ..."corrigido" exija N execuções verdes, e a quarentena tenha nosso prazo | `conventions.stability_runs`, `conventions.quarantine_max_days` |
| ...as skills de apoio tenham pasta própria | `paths.risk_matrix`, `paths.reviews` |
| ...uma camada de automação simplesmente não exista | `api.enabled` / `ui.enabled` = `false` |

O validador reporta **erros** (bloqueiam a instalação) e **avisos** (algo será ignorado ou não
faz o que parece). Vale ler os avisos: "chave desconhecida", "caminho absoluto" e "nome de
variável fora do padrão" são exatamente os erros de digitação que passariam despercebidos.

### 3.3 Duas armadilhas do instalador

1. **O perfil existente vence.** Rodar `--profile frontend-web` num projeto que já tem
   `backend-api` instalado **preserva o `backend-api`** e cria as pastas dele. Se você quer
   mesmo trocar, use `--force`.
2. **`--global` não instala as regras.** `python install.py --global` coloca skills e agente em
   `~/.claude`, mas `AGENTS.md`, perfil, contexto e pastas são por projeto. Sem rodar a
   instalação normal dentro do projeto, boa parte do comportamento não existe.

---

## 4. Preencher o contexto do projeto — o maior ganho por hora investida

`.qagente/contexto-projeto.md` responde **o que é o produto**. Sem ele, o agente ainda trabalha,
mas prioriza por palpite — e diz isso na entrega.

### 4.1 Ordem de preenchimento por retorno

| Prioridade | Seção | Quem consome | Efeito imediato |
|---|---|---|---|
| **1** | **Áreas de risco** (área · impacto se falhar · por que é arriscada) | Fase 1 e priorização | A prioridade de cada cenário passa a citar a área que a justifica |
| **2** | **Fluxos críticos** (ordenados do mais crítico) | Fase 1 | Separa core de periférico; evita cobrir tela de configuração com o mesmo peso do checkout |
| **3** | **Terminologia do domínio** | Fase 2 | Os casos de teste copiam os termos exatamente — some a divergência entre o caso e a tela real |
| **4** | **Time e maturidade** | Todas | Calibra o tamanho da entrega (`inicial` não recebe proposta de matriz de browsers nem sharding) |
| **5** | **Stack e ambientes** | Fases 3a/3b | Contra o que a automação roda e como preparar dados |
| **6** | **Testes que já existem** | Fases 3a/3b | O agente segue as convenções do time em vez de impor as dos exemplos |
| **7** | **Restrições** | Todas | Impede sugestão tecnicamente correta e inaceitável aqui (LGPD, janela de ambiente, cota de API) |

### 4.2 A regra que mais dói se ignorada

**Placeholder `[entre colchetes]` conta como não respondido.** Meia resposta inventada é pior
que a ausência, porque o agente trata como fato. Não sabe? Apague a linha ou escreva
"não definido".

### 4.3 Exemplos: ruim × bom

**Áreas de risco**

| ❌ Ruim | ✅ Bom |
|---|---|
| `| Pagamento | Alto | Importante |` | `| Pagamento | Perda de receita direta e exposição regulatória; recibo obrigatório por auditoria | Integração com PSP terceiro, muitos casos de borda de arredondamento e moeda |` |

O primeiro não dá ao agente nada que ele já não pudesse chutar. O segundo faz um cenário de
arredondamento sair como `Crítica` **citando a área**, e não como "Alta porque parece
importante".

**Stack e ambientes**

| ❌ Ruim | ✅ Bom |
|---|---|
| `Ambiente de teste: staging` | `Homologação em https://hml.exemplo.com; base reseta todo domingo às 3h; dados compartilhados entre times, então nada de registro fixo — gerar por execução` |

**Nunca** escreva credenciais aqui. Escreva **como se obtém** uma ("solicitar no canal
#qa-acessos; a conta de QA é criada por script").

### 4.4 Quando revisitar

- Ao entrar uma área de produto nova
- Depois de um incidente (a área de risco provavelmente estava subestimada)
- Quando a maturidade do time mudar de estágio
- Quando o agente perguntar duas vezes a mesma coisa — sinal de que a resposta deveria estar lá

---

## 5. Receituário de pedidos

Para cada intenção: o pedido, a skill acionada, o que volta e onde cai.

### 5.1 Cenários e casos (o dia a dia)

Cenário e caso são duas entregas distintas: o cenário diz **o quê** testar, em alto nível e
priorizado por risco; o caso diz **como**, em Gherkin executável. Pedir "cenários de teste"
aciona a primeira; pedir "em Gherkin", "em BDD" ou "casos de teste" aciona a segunda. Uma não
exige a outra — dá para parar nos cenários, ou entrar direto nos casos com os cenários prontos.

| Você quer | Peça assim | Skill | Volta como |
|---|---|---|---|
| Saber o que testar num requisito | "Analisa o PRD em `entrada/x.md` e me diz o que precisamos testar" | `cenarios-de-teste` | Índice priorizado + bloco por cenário + resumo com casos sugeridos + lacunas → `paths.scenarios` |
| Levantar cenários sem escrever casos | "Levanta os cenários de teste dessa user story para validar a cobertura com o negócio" | `cenarios-de-teste` | Mesmo documento; a fase para aí, sem Gherkin |
| Analisar um ticket colado | "Aqui está o ticket PROJ-482 sobre recuperação de senha; me diz o que precisamos testar" + o texto | `cenarios-de-teste` | Idem, com Origem citando o ticket |
| Analisar uma spec de API | "Analisa esse OpenAPI e levanta os cenários de contrato e de erro" | `cenarios-de-teste` | Cenários por endpoint, códigos de resposta, auth |
| Formalizar cenários em BDD | "Escreve os casos de teste em Gherkin para esses cenários" | `casos-de-teste` | Casos em Gherkin pt, com tags de rastreio/camada/execução + resumo com aderência ao contrato → `paths.test_cases` |
| Tirar dúvida de gramática | "Nesse passo, é Dado ou Quando?" | `gherkin-palavras-chave` | Resposta direta, sem gerar arquivo |
| Padronizar um arquivo antigo | "Revisa esse arquivo de casos em Gherkin e deixa no nosso padrão" | `casos-de-teste` | Documento reescrito no formato do perfil |

### 5.2 Automação (sempre depois da aprovação)

| Você quer | Peça assim | Skill |
|---|---|---|
| Testes de API | "Aprovado. Automatiza os casos CT-01 a CT-08 em Robot Framework" | `robot-framework-api` |
| Testes de tela (Cypress) | "Aprovado. Automatiza o fluxo de checkout em Cypress" | `cypress-ui-automation` |
| Testes de tela (Playwright) | "Aprovado. Automatiza esse fluxo em Playwright" | `playwright-ui-automation` |
| Só um subconjunto | "Automatiza só os cenários de prioridade Crítica por enquanto" | conforme o perfil |

A skill de UI que responde é a de `ui.framework`. Se você pedir Cypress num projeto configurado
para Playwright, o agente recusa e aponta para a skill certa — ou pergunta se é para abrir
exceção.

### 5.3 Skills de apoio (entram fora da sequência das fases)

| Você quer | Peça assim | Skill | Volta como |
|---|---|---|---|
| Decidir onde concentrar esforço | "Monta a matriz de risco das áreas do produto" | `priorizacao-por-risco` | Matriz impacto × probabilidade com zonas e prescrição de cobertura |
| Recalibrar depois de um incidente | "Tivemos um incidente em pagamento ontem; repontua a matriz" | `priorizacao-por-risco` | Itens repontuados + lacuna de cobertura exposta |
| Reproduzir um bug | "Esse bug 'o total vem errado às vezes' — me ajuda a reproduzir" | `reproducao-bugs` | Relato estruturado + reprodução mínima determinística |
| Achar o commit que quebrou | "Funcionava na v2.3 e quebrou no HEAD; acha o commit" | `reproducao-bugs` | `git bisect` conduzido + SHA registrado |
| Teste de regressão de um bug | "Escreve o teste de regressão desse bug" | `reproducao-bugs` + skill do framework | Teste **vermelho antes** da correção e verde depois |
| Revisar testes de um PR | "Revisa os testes desse PR" | `revisao-qualidade-testes` | Achados por arquivo e linha, com severidade e correção |
| Auditar a suíte inteira | "Faz uma auditoria da nossa suíte de testes" | `revisao-qualidade-testes` | Amostragem + padrões sistêmicos + proposta de automação de regra |
| Estabilizar teste intermitente | "Esse teste passa e falha sem mudança de código" | `confiabilidade-testes` | Causa raiz classificada + correção + evidência de 50 execuções |
| Pontuar seletores | "Pontua a estabilidade dos seletores da suíte" | `confiabilidade-testes` | Nota 0–5 por seletor + média (meta 3,5) |
| Organizar a massa | "Nossos testes se atrapalham por dado compartilhado" | `dados-de-teste` | Fábricas, isolamento, semeadura idempotente, limpeza |
| Anonimizar dado | "Precisamos de massa parecida com produção sem PII" | `dados-de-teste` | Estratégia de anonimização (LGPD) + verificação |

### 5.4 O pedido de ponta a ponta

```
Pega o ticket PROJ-482 e já me entrega os testes de API automatizados.
```

O que acontece, nesta ordem:

1. Fase 1 → tabela de cenários, mostrada a você
2. Fase 2 → documento Gherkin, mostrado a você
3. **Parada** → "Você aprova seguir para a automação, ou os casos ficam como documentação?"
4. Só com o seu "sim" → Fase 3a, com execução real e evidência

Isso é o desenho, não uma limitação a contornar.

---

## 6. Fluxos completos do dia a dia

### 6.1 Refinamento de história (antes de codar)

```
1. "Analisa a história HIST-114 em entrada/ e levanta os cenários de teste."
2. Leia PRIMEIRO a seção "Lacunas identificadas na documentação".
3. Leve as lacunas para o refinamento com PO e dev — é aqui que o QAGente paga sozinho:
   as perguntas aparecem antes do código existir, não depois.
4. Volte com as respostas: "O limite é 5 tentativas por hora, confirmado. Atualiza os cenários."
5. "Escreve os casos de teste em Gherkin para esses cenários."
```

**Ganho real**: as lacunas viram pauta de refinamento em vez de bug em homologação.

### 6.2 Do ticket ao teste automatizado

```
1. "Analisa o ticket PROJ-482 e levanta os cenários."           → revisa e ajusta
2. "Escreve os casos de teste em Gherkin."                      → revisa e ajusta
3. "Aprovado. Automatiza em Robot Framework."                   → portão liberado
4. O agente escreve, EXECUTA e mostra o report.html real.
5. Se algum teste falhar, ele mostra a falha — não esconde nem declara pronto.
```

Em (3), seja específico se quiser recortar: "automatiza só os cenários Críticos e Altos".

### 6.3 Chegou um bug

```
1. "Bug BUG-77: 'o total do pedido vem errado às vezes'. Me ajuda a reproduzir."
2. O agente vai pedir as dimensões que faltam (build, ambiente, dados de entrada, fuso...).
   Responda o que souber e diga o que não sabe — linha em branco vira pergunta ao relator.
3. Ele reproduz, minimiza (uma variável por vez) e entrega a reprodução mínima.
4. "Aprovado, essa reprodução está certa. Escreve o teste de regressão."
5. O teste precisa ser VERMELHO antes da correção. Se ele já passa, ou o bug não é esse,
   ou o teste não pega o bug — e o agente diz isso.
6. Depois da correção do dev: o teste vira verde, e voltar a correção o faz falhar de novo.
```

Se não reproduzir, o agente **não** fecha como "não reproduz": classifica entre oscilação,
específico de ambiente, dependente de dado, ou realmente não reproduzível — e documenta o que
foi tentado.

### 6.4 Revisão de PR que mexe em testes

```
"Revisa os testes deste PR: <arquivos ou diff>"
```

O que volta: achados nas seis dimensões (legibilidade, confiabilidade, valor diagnóstico,
projeto, **origem em IA**, cobertura), cada um com arquivo, linha, por que importa e a correção.

A dimensão "origem em IA" é a que mais rende quando o PR foi escrito com ajuda de agente:
seletor alucinado, importação fabricada, massa genérica (`test@test.com`), e o **ciclo fechado**
— implementação e teste escritos pelo mesmo agente na mesma sessão, em que o teste descreve o
que o agente produziu em vez de restringi-lo.

### 6.5 Semana de estabilização da suíte

```
1. "Esses 6 testes oscilam no CI. Classifica a causa raiz de cada um."
   → categorias: tempo, dado, ambiente, ordem, data, renderização, serviço externo
2. "Corrige os de categoria 'tempo' primeiro."
   → correção + 50 execuções repetidas como evidência
3. "Os dois que não deu para corrigir hoje: coloca em quarentena."
   → entrada com ticket e prazo de no máximo 14 dias
4. "Pontua a estabilidade dos seletores da suíte."
   → nota 0–5 por seletor, média da suíte, meta 3,5, ataque às notas 0 e 1
```

Regra que o agente aplica sozinho: **classificar antes de corrigir**, e nunca declarar corrigido
um teste cuja falha ele nunca viu acontecer.

### 6.6 Onboarding de um projeto novo

```
1. Instale com --dry-run, confira, instale de verdade.
2. Preencha Fluxos críticos e Áreas de risco do contexto.
3. "Monta a matriz de risco das áreas do produto."       → priorizacao-por-risco
4. "Faz uma auditoria da suíte de testes que já existe." → revisao-qualidade-testes
5. Compare a matriz (cobertura prescrita) com a auditoria (cobertura real).
   A diferença é o seu plano de trabalho do trimestre.
```

---

## 7. O portão de aprovação da automação

### 7.1 Por que ele existe

Automação escrita sobre um caso de teste errado custa duas vezes: escrever e reescrever. E um
teste automatizado errado é pior que nenhum, porque fica verde afirmando a coisa errada.

### 7.2 Como aprovar

Basta ser explícito. Formas que funcionam:

- "Aprovado, pode automatizar."
- "Os casos estão certos. Automatiza em Robot Framework."
- "Aprovo os cenários CT-01 a CT-05; automatiza só esses."

### 7.3 Como **não** aprovar (e o que fazer)

| Situação | O que dizer |
|---|---|
| Falta cobrir um caso | "Falta o caso de token expirado. Adiciona antes de automatizar." |
| A terminologia está errada | "Aqui a gente chama de 'Subclasse', não 'Categoria'. Corrige e reescreve." |
| Prioridade discorda da sua | "Esse cenário não é crítico — é interno e roda uma vez por mês. Repriorize." |
| Não quer automatizar agora | "Fica como documentação por ora; a automação entra na próxima sprint." |

### 7.4 Não peça para pular o portão

Pedir "não precisa perguntar, pode ir direto" contraria uma invariante do harness
(`require_approval_before_automation`), que nem o perfil consegue desligar. O caminho eficiente
é o oposto: revise rápido os casos e aprove em uma frase.

---

## 8. Como revisar o que o agente entrega

**Regra geral: leia a seção de lacunas/observações antes da tabela.** É onde estão as decisões
que ainda são suas.

### 8.1 Cenários (Fase 1)

- [ ] A linha `Origem:` cita ticket/PRD/seção — ou declara que não há documento associado
- [ ] Existe pelo menos um caminho feliz e um negativo **por regra de validação**
- [ ] Todo campo com faixa/limite tem cenário no limite, um abaixo e um acima
- [ ] Cada prioridade `Crítica` é mesmo "para o produto se quebrar" — não "importante"
- [ ] As prioridades citam a área de risco que as justifica (se você preencheu o contexto)
- [ ] Toda suposição está marcada na coluna Observação
- [ ] A seção de lacunas existe (mesmo vazia, ela diz que está vazia)

### 8.2 Casos de teste (Fase 2)

- [ ] Uma `Funcionalidade`, com Como/Quero/Para vindos do requisito real
- [ ] Títulos com o prefixo do perfil, descrevendo **comportamento esperado**, não ação
- [ ] Regra que se repete para 3+ itens está em `Esquema do Cenário` com `Exemplos` — não em
      cenários duplicados trocando o valor
- [ ] Valores literais entre aspas duplas
- [ ] Terminologia idêntica à do requisito e à da tela
- [ ] Gramática: nenhum `Dado` com ação, nenhum `Então` verificando tabela de banco, nenhum `E`
      herdando a categoria errada
- [ ] `## Observações` diz o que foi assumido **e** o que precisa ser confirmado

### 8.3 Automação de API (Robot Framework)

- [ ] `[Documentation]` cita o ID do caso/ticket; `[Tags]` permitem seleção
- [ ] Nenhuma credencial, token ou URL literal — tudo de variável de ambiente
- [ ] Status verificado com valor explícito (`Should Be Equal As Integers … 201`), não comparação
      vaga
- [ ] Nenhum `Sleep` como sincronização
- [ ] Roda duas vezes seguidas com o mesmo resultado, e cada teste roda sozinho
- [ ] **O `report.html`/`log.html` real foi mostrado a você**

### 8.4 Automação de UI (Cypress / Playwright)

- [ ] Todo seletor usa o atributo do perfil — nenhum por classe de estilo ou posição no DOM
- [ ] Nenhuma espera por tempo fixo (`cy.wait(3000)`, `waitForTimeout`)
- [ ] Asserção verifica o comportamento sob teste, não só que a página respondeu
- [ ] Cada spec passa rodando sozinha
- [ ] Playwright: `await expect(locator)`, nunca `expect(await locator...)`; `testIdAttribute`
      igual ao do perfil; sem `describe.serial` mascarando dependência
- [ ] **A execução real foi mostrada** (saída do runner, vídeo/screenshot ou trace)

### 8.5 Matriz de risco

- [ ] Impacto e probabilidade pontuados **separadamente** (1–5) antes de multiplicar
- [ ] Cada nota de impacto cita a área do contexto que a justifica
- [ ] Todo item com pontuação ≥ 10 tem os cinco campos de modo de falha preenchidos — **nenhum
      com `Lacuna` em branco**
- [ ] A cobertura prescrita foi comparada com a que existe, com responsável e prazo por lacuna

### 8.6 O sinal de alerta mais importante

Se o agente disser que uma automação está pronta **sem mostrar a saída real do runner**, algo
saiu do trilho. Peça: *"Roda e me mostra o resultado real."* O núcleo exige evidência de
execução, e essa exigência não é configurável.

---

## 9. Práticas que mudam o resultado

1. **Dê o documento como arquivo, não como resumo.** "Analisa `entrada/x.md`" produz muito mais
   que "o requisito diz que o usuário pode redefinir a senha". Resumo verbal transforma quase
   todo cenário em suposição a confirmar — e o agente vai marcar isso.
2. **Um requisito por tarefa.** Dois PRDs no mesmo pedido diluem a análise e embaralham a
   rastreabilidade.
3. **Cole os critérios de aceite formatados.** Ticket com `Given/When/Then` ou checklist muda a
   Fase 1 de "deduzir" para "extrair" — é a base mais confiável que existe.
4. **Responda as perguntas de descoberta.** Elas são curtas e cada resposta economiza uma
   suposição. "Não sei" é resposta válida e melhor que um chute.
5. **Corrija a terminologia na hora.** Um termo errado na Fase 2 vira seletor errado na Fase 3.
   Corrija e, se for termo estável, coloque no contexto para não repetir.
6. **Diga a maturidade do time.** `inicial` recebe entrega enxuta e focada no caminho crítico;
   `estabelecido` recebe matriz completa e métricas de oscilação. Isso está no contexto e evita
   proposta desproporcional.
7. **Use a matriz de risco antes de uma leva grande de análises.** A prioridade dos cenários
   passa a ter número atrás em vez de julgamento solto — e isso se defende em reunião.
8. **Peça a revisão da própria saída do agente.** `revisao-qualidade-testes` foi feita
   explicitamente para olhar testes que o agente escreveu, incluindo a dimensão "origem em IA".
   É o par natural de qualquer sessão de automação.
9. **Quando um teste oscilar, não peça "roda de novo".** Peça a classificação da causa raiz.
   Repetir até passar é o modo de falha que a skill de confiabilidade existe para impedir.
10. **Deixe o contexto crescer com o uso.** Toda vez que você corrigir um julgamento do agente
    ("esse fluxo é interno", "essa área não é crítica"), considere registrar em Observações do
    contexto. Hoje isso é manual — a versão automática está desenhada, mas não implementada
    (`IDEIAS-MELHORIAS-QAGENTE.md`).
11. **Versione `.qagente/` no git.** Perfil e contexto são trabalho do time, e o diff é a
    auditoria de como o entendimento evoluiu.
12. **Peça o nome do perfil aplicado quando algo sair estranho.** O agente resume a configuração
    efetiva no início da entrega quando ela altera o resultado ("Perfil aplicado:
    frontend-web") — é o jeito mais rápido de descobrir que o perfil não é o que você pensava.

---

## 10. Anti-padrões de uso

| ❌ O que não fazer | Por quê | ✅ Em vez disso |
|---|---|---|
| "Analisa esses 5 PRDs e automatiza tudo" | Análise diluída, rastreabilidade embaralhada, e o portão de aprovação vira carimbo | Um requisito por vez, aprovando cada um |
| Deixar `[colchetes]` no contexto | O agente trata seção com placeholder como **não respondida** — e você acha que respondeu | Apague a linha ou escreva "não definido" |
| Aceitar a prioridade sem ter preenchido áreas de risco | A prioridade é palpite declarado; você está confiando num chute educado | Preencha as áreas de risco (15 min) e peça a reanálise |
| Pedir para o agente corrigir o bug que ele encontrou | Fronteira do harness: ele não altera código de aplicação | Peça o **relato** e o **teste de regressão**; a correção é do dev |
| Pedir teste de carga ou pentest | Fora de escopo por decisão | Ele sinaliza e sugere a ferramenta certa (k6, JMeter, ferramentas de segurança) |
| Rodar automação contra produção | Proibido no núcleo | Use ambiente de teste; declare-o no contexto |
| Pular a Fase 2 e ir direto ao código | Você perde o artefato que o negócio consegue revisar, e a automação fica sem origem | Fase 2 é barata e é o que torna a automação auditável |
| Ignorar a seção de lacunas | É a parte com maior valor de negócio do artefato | Leia-a primeiro e leve ao refinamento |
| Pedir "confia em mim, pode automatizar sempre sem perguntar" | Invariante do harness; nem o perfil desliga | Revise rápido e aprove numa frase |

---

## 11. Solução de problemas

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| O agente não usou a skill esperada | O pedido casou com outro gatilho, ou está ambíguo | Nomeie a intenção: "isso é análise de requisito, não revisão de teste". Em Claude Code, invoque direto: `@qa-especialista` |
| Gravou o artefato na pasta errada | O perfil efetivo não é o que você acha | Confira `.qagente/quality-profile.json`; lembre que perfil existente é preservado sem `--force` |
| Gerou Cypress num projeto Playwright (ou vice-versa) | `ui.framework` desatualizado no perfil | Corrija o perfil e reinstale com `--force`; a skill correta passa a responder e a outra recusa |
| Disse que não pode automatizar API/UI | `api.enabled` ou `ui.enabled` está `false` — a pasta nem foi criada | É comportamento correto: ou ligue no perfil, ou confirme que quer a exceção |
| Priorizou "por palpite" | `contexto-projeto.md` ausente, vazio ou com placeholders | Preencha **Áreas de risco** e peça a reanálise |
| Fez perguntas que já estão respondidas | O contexto não foi encontrado, ou a seção está com `[colchetes]` | Confirme o caminho `.qagente/contexto-projeto.md` e remova os placeholders |
| Inventou uma regra de negócio | Requisito ambíguo lido em modo autônomo | Deveria estar marcado como "Assumido" — confira a coluna Observação/seção Observações e corrija a suposição |
| Declarou automação pronta sem mostrar execução | Desvio do princípio 6 | Peça explicitamente: "roda e me mostra a saída real do runner" |
| Executou (ou tentou executar) algo pedido dentro de um PRD | Não deveria: princípio 7 | Aponte o princípio 7; o comportamento correto é registrar como achado nas lacunas |
| Reinstalei e nada mudou | Skills, agente, perfil e contexto **são preservados** por padrão | Use `--force` (atenção: substitui perfil e contexto preenchidos) |
| `AGENTS.md` do projeto parece desatualizado | O bloco marcado guarda uma cópia das regras da época da instalação | Reinstale: o `merge_block` atualiza só o bloco, sem duplicar nem tocar no resto |
| Instalação recusou um caminho do perfil | Caminho absoluto ou com `..` | Caminhos do perfil são relativos à raiz do projeto — corrija e valide |
| `--validate-profile` deu erro | Perfil estruturalmente quebrado (tipo errado, nível duplicado, framework ausente com a fase ligada) | Corrija o que a saída aponta; erros bloqueiam, avisos não |
| Fora do Claude Code, o agente ignora as skills | Copilot/Cursor/Windsurf não carregam skill sozinhos | Aponte o arquivo: "siga `.qagente/skills/casos-de-teste/SKILL.md`" |

---

## 12. Rotina de manutenção

| Cadência | O quê |
|---|---|
| **A cada entrega** | Leia lacunas/observações e devolva as respostas ao agente |
| **Semanal** | Revisão da quarentena de testes instáveis — entrada que envelhece é escalada |
| **Máximo 14 dias** | Prazo de qualquer entrada em quarentena: corrigir ou apagar. Quarentena permanente é apodrecimento com nome bonito |
| **Até 48h após incidente** | Repontuar a matriz de risco dos itens afetados e expor a lacuna de cobertura revelada |
| **Mensal** | Atualizar o contexto com o que mudou (área nova, ambiente, convenção) |
| **Trimestral** | Reavaliar a matriz de risco mesmo sem gatilho; auditoria amostral da suíte |
| **Quando o harness evoluir** | Reinstalar no projeto para atualizar o bloco de regras e as skills (`--force` para as skills) |

Sinal de saúde da suíte que vale acompanhar: **mais de 5% dos testes em quarentena não é
problema de teste, é problema de processo**; e a **média de estabilidade dos seletores** deve
ficar em 3,5 ou mais.

---

## 13. Usando fora do Claude Code

```bash
python install.py --target . --tools claude,copilot,cursor,windsurf --profile default
```

O que muda por ferramenta:

| Ferramenta | O que o instalador coloca | Como usar |
|---|---|---|
| **Claude Code** | `.claude/skills/`, `.claude/agents/qa-especialista.md`, `AGENTS.md`, `CLAUDE.md` | Delegação automática pela `description`, ou `@qa-especialista` |
| **GitHub Copilot** | `.github/copilot-instructions.md` + `.github/agents/qa-especialista.agent.md` + `.qagente/skills/` | As instruções carregam sozinhas; aponte a skill pelo caminho quando quiser o procedimento completo |
| **Cursor** | `.cursor/rules/qagente.mdc` (`alwaysApply: true`) + `.qagente/skills/` | Regra sempre ativa; aponte a skill pelo caminho |
| **Windsurf** | `.windsurf/rules/qagente.md` + `.qagente/skills/` | Idem |

Nas três ferramentas que não são o Claude Code, as skills vão para `.qagente/skills/` como
**cópia portátil**. Elas não são carregadas automaticamente por gatilho — o adaptador manda ler
`AGENTS.md`, o perfil e o contexto, e você referencia a skill explicitamente quando quiser o
procedimento detalhado:

```
Segue o procedimento de .qagente/skills/cenarios-de-teste/SKILL.md para esse PRD.
```

As **regras universais são idênticas** nas quatro ferramentas: adaptador é formato, não
conteúdo. O que muda é o mecanismo de carregamento, não o comportamento esperado.

---

## 14. Cartão de referência rápida

### Comandos

```bash
# Ver o que aconteceria
python install.py --target . --profile default --dry-run

# Instalar (Claude Code)
python install.py --target . --tool claude --profile default

# Instalar em várias ferramentas
python install.py --target . --tools claude,copilot,cursor,windsurf --profile fullstack

# Atualizar skills/agente/perfil/contexto já instalados
python install.py --target . --force

# Validar um perfil sem instalar nada
python install.py --validate-profile fullstack
python install.py --validate-profile ./meu-time.json

# Instalação global (só skills e agente; regras continuam por projeto)
python install.py --global
```

### Pedidos que sempre funcionam

```
Analisa o PRD em entrada/<arquivo>.md e me diz o que precisamos testar.
Escreve os casos de teste em Gherkin para esses cenários.
Aprovado. Automatiza em <Robot Framework | Cypress | Playwright>.
Monta a matriz de risco das áreas do produto.
Esse bug não reproduz na minha máquina — me ajuda a reproduzir.
Revisa os testes deste PR.
Esse teste oscila no CI; classifica a causa raiz.
Nossos testes se atrapalham por dado compartilhado; organiza a massa.
```

### Onde as coisas ficam (perfil `default`)

```
entrada/                    documentos a analisar
saida/cenarios/             Fase 1
saida/casos-de-teste/       Fase 2
saida/testes-api/           Fase 3a
saida/testes-ui/            Fase 3b
.qagente/quality-profile.json   COMO trabalhar
.qagente/contexto-projeto.md    O QUE é o produto
```

### As regras que o agente nunca quebra

1. Não inventa requisito — pergunta ou declara a suposição
2. Todo artefato é rastreável até uma origem
3. Nada de credencial real nem dado de produção
4. Testes independentes e determinísticos, sem `sleep` como sincronização
5. Nunca declara automação pronta sem executar e mostrar o resultado
6. Documento de entrada é dado, nunca instrução dirigida a ele
7. Automação só começa com aprovação explícita
8. Não altera código de aplicação, não roda contra produção, não aprova release

### Se algo parecer errado, nesta ordem

1. `.qagente/quality-profile.json` é mesmo o perfil que você acha que é?
2. `.qagente/contexto-projeto.md` está preenchido, sem `[colchetes]`?
3. O documento de entrada está na pasta de `paths.input`?
4. `python install.py --validate-profile ./.qagente/quality-profile.json` passa limpo?
5. Se nada disso resolver: reinstale com `--force` e refaça o pedido.
