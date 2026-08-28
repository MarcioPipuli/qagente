---
name: analise-documentacao-testes
description: Analisa documentação de requisitos (PRD, user story, ticket, especificação técnica, ADR) e extrai cenários de teste priorizados aplicando técnicas de design de testes (particionamento de equivalência, valor limite, tabela de decisão, transição de estados). Use quando o usuário pedir para analisar uma especificação e levantar o que testar, mapear cenários de teste a partir de um requisito, identificar casos de borda ou regras de negócio implícitas, ou fazer uma análise de risco de qualidade antes de escrever testes. Do NOT use for já escrever os casos de teste formais (use escrita-casos-teste) ou para automatizar testes (use robot-framework-api ou cypress-ui-automation).
license: CC-BY-4.0
metadata:
  author: QAGente
  version: '1.0.0'
---

# Análise de Documentação para Testes

Lê documentação de requisitos e a transforma em uma lista de cenários de teste rastreáveis e priorizados por risco. É a primeira fase do fluxo QA (ver `AGENTS.md`, na raiz do projeto) — a saída desta skill alimenta `escrita-casos-teste`.

## Configuração

Leia `.qagente/quality-profile.json` na raiz do projeto antes de começar. Quando um campo
existir no perfil, ele vence os valores desta skill. Precedência: **instrução explícita do
usuário → perfil do projeto → defaults desta skill**.

| Decisão desta skill | Campo do perfil | Default |
|---|---|---|
| Idioma dos artefatos | `language` | idioma da documentação de origem |
| Níveis de prioridade | `risk_levels` | Alta / Média / Baixa |
| Método de priorização | `risk_method` | probabilidade × impacto |
| Padrão de ID dos cenários | `conventions.test_id_pattern` | `CT-01`, `CT-02`, ... |
| Onde salvar a saída | `paths.scenarios` | `saida/cenarios/` |

Sem perfil, ou com o perfil ausente de um campo, use o default da coluna da direita. As regras
universais de `AGENTS.md` — rastreabilidade, proteção de segredos, independência dos testes,
registro de lacunas e evidência real de execução — valem sempre, e o perfil não pode removê-las.

Os `risk_levels` são declarados no perfil em inglês (`critical`, `high`, `medium`, `low`),
mas devem ser **escritos no idioma dos artefatos**. Com quatro níveis, use a escala completa —
não colapse para três só porque os exemplos desta skill mostram três.

## Quando usar

- Usuário cola/aponta um PRD, user story, ticket (Jira/Linear/GitHub Issue), especificação de API (OpenAPI/Swagger) ou ADR e pede "o que precisamos testar aqui".
- Usuário pede uma "análise de risco de qualidade" ou "cobertura de testes" antes de codificar.
- Usuário descreve uma funcionalidade informalmente e quer ajuda para pensar nos cenários.

## Passo 1 — Localizar e ler a fonte

1. Se o usuário forneceu um caminho de arquivo, URL ou colou o texto, leia-o por completo antes de prosseguir. Nunca gere cenários a partir do título/resumo apenas.
2. Se a fonte for um ticket com critérios de aceite formatados (`Given/When/Then`, checklist, "Acceptance Criteria"), extraia-os literalmente primeiro — eles são a base mais confiável.
3. Se a fonte for uma especificação de API (OpenAPI/Swagger, contrato GraphQL), identifique: endpoints/operações, parâmetros obrigatórios vs. opcionais, tipos e formatos, códigos de resposta documentados (2xx, 4xx, 5xx), regras de autenticação/autorização.
4. Se a documentação for informal ou incompleta, diga isso explicitamente ao usuário antes de prosseguir — não preencha lacunas de regra de negócio por conta própria (ver `AGENTS.md`, princípio 2).

## Passo 2 — Extrair os elementos testáveis

Para cada funcionalidade/regra encontrada, identifique:

- **Entradas** e seus tipos/formatos/domínios de valor válido.
- **Regras de negócio** (validações, cálculos, condições de habilitação/desabilitação).
- **Estados e transições** (ex.: pedido `pendente → pago → enviado → entregue`; o que é uma transição inválida?).
- **Atores e permissões** (o que cada perfil de usuário pode/não pode fazer).
- **Integrações externas** (o que acontece se a dependência falhar, atrasar, ou retornar dado inesperado?).
- **Mensagens e feedback ao usuário** (o que deve ser exibido em cada caso, incluindo erro).

## Passo 3 — Aplicar técnicas de design de testes

Escolha a(s) técnica(s) adequada(s) a cada elemento — não force todas em tudo:

| Técnica | Quando aplicar | O que produz |
|---|---|---|
| **Particionamento de equivalência** | Campo com domínio de valores (enum, faixa, formato) | Uma classe válida representativa + uma classe inválida por tipo de violação |
| **Análise de valor limite** | Campo numérico/data com limite (mín/máx, idade, quantidade) | Testes no limite, um abaixo, um acima |
| **Tabela de decisão** | Regra de negócio com múltiplas condições combinadas (ex.: desconto = f(cliente VIP, cupom, valor do carrinho)) | Uma linha por combinação relevante de condições |
| **Transição de estados** | Entidade com ciclo de vida (pedido, assinatura, ticket) | Um teste por transição válida + um por transição inválida |
| **Análise de risco** | Priorização final de tudo acima | Uma prioridade por cenário, na escala de `risk_levels` e pelo método de `risk_method` |

Sempre cubra, no mínimo: 1 caminho feliz, 1+ cenário negativo por regra de validação, e os limites de qualquer valor com faixa/limite definido.

## Passo 4 — Produzir a lista de cenários

Salve o resultado como arquivo Markdown (`.md`) no diretório de `paths.scenarios` — sem perfil, `saida/cenarios/` (ver convenção de pastas em `AGENTS.md`). Formato de saída (ajuste a granularidade ao tamanho do requisito — uma funcionalidade pequena não precisa de 20 cenários):

```markdown
## Cenários de Teste — [Nome da Funcionalidade]
Origem: [ticket/PRD/seção — ou "descrição informal do usuário, sem documento associado"]

| ID | Cenário | Tipo | Técnica | Prioridade | Observação |
|---|---|---|---|---|---|
| CT-01 | Login com credenciais válidas | Caminho feliz | — | Alta | |
| CT-02 | Login com senha incorreta | Negativo | Particionamento | Alta | |
| CT-03 | Bloqueio após 5 tentativas falhas | Regra de negócio | Tabela de decisão | Alta | Limite "5" não confirmado no doc — assumido |
| CT-04 | Campo email vazio | Negativo | Particionamento | Média | |
| CT-05 | Sessão expira após 30 min de inatividade | Estado | Transição de estados | Média | |

### Lacunas identificadas na documentação
- [O que está ambíguo/ausente e precisa de confirmação do usuário]
```

Marque toda suposição assumida na coluna "Observação" — nunca a apresente como se estivesse confirmada pela documentação.

## Passo 5 — Priorizar por risco

Use a escala de `risk_levels` e o método de `risk_method` do perfil. Com o método padrão
(`probability-impact`), a prioridade é a probabilidade de o cenário falhar × o impacto no
negócio se ele falhar em produção.

Na escala padrão de três níveis:

- **Alta**: fluxo core do produto, envolve dinheiro/dados sensíveis, ou alta probabilidade de regressão.
- **Média**: funcionalidade secundária, mas com uso real.
- **Baixa**: caso de borda raro ou cosmético.

Quando o perfil declarar um nível acima do mais alto (ex.: `critical`), reserve-o para o que
para o produto inteiro se quebrar — não o use como sinônimo de "importante", senão a escala
perde poder de discriminação e volta a ser de três níveis na prática.

## Exemplo

**Usuário**: "Aqui está o ticket PROJ-482 sobre recuperação de senha, me diz o que precisamos testar."

**Ação**: ler o ticket completo → identificar entradas (email), regras (token expira em 15min, só um token ativo por vez, rate limit de 3 solicitações/hora) → aplicar valor limite no tempo de expiração e no rate limit, particionamento no formato de email → gerar tabela de cenários com CT-01 a CT-08, priorizados, citando PROJ-482 como origem → sinalizar que o ticket não especifica o comportamento quando o usuário solicita novo token com um token anterior ainda válido (lacuna a confirmar).

## Ao encadear com a próxima fase

Ao final, pergunte se o usuário quer seguir para `escrita-casos-teste` com esses cenários, ou revisar a lista primeiro.
