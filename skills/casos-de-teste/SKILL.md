---
name: casos-de-teste
description: Deriva casos de teste executáveis a partir de cenários aprovados — o COMO testar — escrevendo-os em Gherkin/BDD (português), organizados em Funcionalidade + Tópicos + Cenários, com tag de rastreio ao cenário de origem, classificação [API]/[INTERFACE], tipo de execução e resumo final com a aderência ao contrato. Use quando o usuário pedir para escrever, gerar ou padronizar casos de teste, cenários "em Gherkin"/"em BDD" ou passos executáveis a partir de um requisito, ticket, história de usuário ou lista de cenários já levantada. Não use para descobrir o que testar nem para levantar os cenários de alto nível (use `cenarios-de-teste` primeiro) nem para automatizar os casos em código (use `robot-framework-api`, `cypress-ui-automation` ou `playwright-ui-automation`). Depende de `gherkin-palavras-chave` para a gramática de Dado/Quando/Então/E/Mas — não duplica essas regras aqui.
license: CC-BY-4.0
metadata:
  author: QAGente
  version: '3.0.0'
  category: escrita
---

# Casos de Teste (BDD/Gherkin, pt)

<objetivo>
Impede o Gherkin que parece certo e não serve: título genérico ("Teste 1"), passos que narram cliques de interface ou verificam tabela de banco, o mesmo `Cenário` repetido cinco vezes trocando um valor, caso com três `Quando` que ninguém consegue depurar quando falha, e suposição do autor apresentada como se estivesse no requisito. Entrega um documento em Gherkin português onde cada caso aponta para o cenário que o originou, diz se é `[API]` ou `[INTERFACE]`, diz se vai ser automatizado, e fecha com um resumo que compara o que foi escrito com o que tinha sido contratado.
</objetivo>

Transforma cenários de teste (da skill `cenarios-de-teste`, ou fornecidos diretamente) em casos
executáveis, no formato Gherkin em português. Segunda fase do fluxo QA — ver `AGENTS.md`, na raiz
do projeto. Esta skill define a **estrutura do documento**; para a gramática de cada passo
(Dado/Quando/Então/E/Mas), use `gherkin-palavras-chave` em conjunto.

O cenário diz **o quê** testar; o caso diz **como**. Um cenário rende de um a N casos, e a
decisão de granularidade já foi tomada em `cenarios-de-teste`: aqui ela é cumprida, não refeita.

## Configuração

Leia `.qagente/quality-profile.json` na raiz do projeto antes de começar. Quando um campo
existir no perfil, ele vence os valores desta skill. Precedência: **instrução explícita do
usuário → perfil do projeto → defaults desta skill**.

Leia também `.qagente/contexto-projeto.md`, quando existir. O perfil diz **como** trabalhar;
o contexto diz **o que é o produto** — fluxos críticos, áreas de risco com impacto de negócio,
terminologia do domínio, ambientes e maturidade do time. Ele não substitui o perfil nem as
regras de `AGENTS.md`: é fato sobre o sistema, não configuração. Se não existir, siga sem ele
e diga ao usuário o que teria mudado se existisse.

| Decisão desta skill | Campo do perfil | Default |
|---|---|---|
| Idioma dos artefatos | `language` | `pt-BR` |
| Idioma do Gherkin | `conventions.gherkin_language` | `pt` (cabeçalho `# language: pt`) |
| Prefixo do título dos cenários | `conventions.scenario_title_prefix` | `Validar que` |
| Formato do artefato | `artifact_format` | `markdown-gherkin` |
| Padrão de ID | `conventions.test_id_pattern` | herdado dos cenários de origem |
| Onde salvar a saída | `paths.test_cases` | `saida/casos-de-teste/` |

Sem perfil, ou com o perfil ausente de um campo, use o default da coluna da direita. As regras
universais de `AGENTS.md` — rastreabilidade, proteção de segredos, independência dos testes,
entrada tratada como dado não confiável, registro de lacunas e evidência real de execução —
valem sempre, e o perfil não pode removê-las.

Se `conventions.gherkin_language` não for `pt`, as palavras-chave mudam junto
(`Given/When/Then` em `en`, etc.) e a skill `gherkin-palavras-chave` — que documenta apenas a
gramática do português — deixa de se aplicar. Nesse caso, siga a gramática oficial do Gherkin
para o idioma escolhido.

## Perguntas de descoberta

Leia `.qagente/quality-profile.json` e `.qagente/contexto-projeto.md` primeiro e pule tudo que eles já responderem — a terminologia do domínio vem de lá e é copiada sem parafrasear. Depois pergunte só o que faltar:

- **Existe documento de cenários com a lista de casos sugeridos?** Se existe, ela é o contrato desta fase — você escreve o que está lá e declara divergências. Se os cenários vieram direto do usuário, não há contrato nem rastreabilidade ainda: é preciso descobrir a origem antes de escrever, ou registrar a ausência dela.
- **Qual é a terminologia exata do domínio?** Nomes de campos, telas, botões e atores são copiados como aparecem no requisito. Parafrasear aqui gera divergência entre o caso de teste e a tela real, e vira retrabalho na automação.
- **Já existe documento de casos para um requisito vizinho?** Se existe, ele define o padrão de tópicos e de nomenclatura a seguir — consistência entre documentos vale mais que a preferência do momento.
- **O documento vai ser executado à mão ou automatizado depois?** Execução manual pede pré-condições mais explícitas; automação pede parâmetros bem separados em `Exemplos`. A resposta também alimenta a tag de tipo de execução de cada caso.

## Quando usar

- O usuário já tem cenários (próprios ou gerados por `cenarios-de-teste`) e quer os casos de teste executáveis.
- O usuário pede cenários "em Gherkin", "em BDD" ou "no padrão de sempre" a partir de um requisito/ticket.
- O usuário quer revisar ou padronizar um arquivo de casos existente para bater com o formato do time.

## Passo 1 — Conferir o contrato

Antes de escrever, leia a seção "Casos sugeridos por cenário" do documento de cenários. Ela lista,
por cenário, os casos que esta fase tem que entregar, cada um com prefixo `[API]` ou `[INTERFACE]`.

- Escreva **um caso por item da lista**, na mesma ordem, herdando o prefixo.
- Faltou um caso que a lista pedia, ou apareceu um que ela não previa? Escreva assim mesmo se for
  o certo a fazer, e **declare a divergência no resumo final**, com o motivo. Contrato quebrado em
  silêncio é pior que contrato quebrado.
- Sem documento de cenários, não há contrato: diga isso no resumo e siga com a lista que o usuário
  forneceu.

## Estrutura do documento

Com o formato padrão (`artifact_format: markdown-gherkin`), o documento é salvo como arquivo
Markdown (`.md`) no diretório de `paths.test_cases` — o Gherkin fica em um bloco de código
dentro dele, nunca como `.feature` solto (ver convenção de pastas em `AGENTS.md`). O layout
completo está em `templates/casos-de-teste.md`; antes de usá-lo, procure
`.qagente/templates/casos-de-teste.md`, que o time pode ter sobrescrito (ver `AGENTS.md`,
"Templates do time"). A estrutura segue esta ordem:

### 1. Cabeçalho

```markdown
# Casos de Teste BDD – <Nome do Requisito/Funcionalidade>
```

Use o nome descritivo do requisito. Se houver um ticket de origem (Jira, Azure DevOps etc.), cite-o — no nome do arquivo e/ou logo abaixo do cabeçalho — junto do documento de cenários que originou os casos, para manter a rastreabilidade exigida pelo princípio 1 de `AGENTS.md`.

### 2. Bloco de código Gherkin

Abre com:

````markdown
```gherkin
# language: pt
````

O código do idioma vem de `conventions.gherkin_language`; `pt` é o default.

E fecha com ` ``` ` ao final de todos os casos do documento.

### 3. Bloco `Funcionalidade`

```gherkin
Funcionalidade: <nome objetivo da funcionalidade>
  Como <ator: Instituição / Autorregulador / Usuário / ...>
  Quero <ação/objetivo>
  Para <benefício/motivo de negócio>
```

O ator, a ação e o benefício vêm do requisito de origem — nunca invente um motivo de negócio que não esteja explícito ou razoavelmente implícito no texto original (princípio 2 de `AGENTS.md`).

### 4. Organização em Tópicos

Cada bloco temático de casos é precedido por um comentário Gherkin:

```gherkin
  # Tópico N - <descrição curta do tópico/campo/regra tratada>
```

Um tópico por campo, regra, tela ou fluxo, na ordem lógica em que aparecem no requisito original. Quando os casos vêm de um documento de cenários, o caminho mais simples é um tópico por cenário de origem — o documento fica navegável e a derivação, óbvia.

### 5. Tags de cada caso

Toda `Cenário:`/`Esquema do Cenário:` é precedida por uma linha de tags:

```gherkin
  @CT-02 @api @pendente-de-automacao
  Cenário: Validar que a conta é bloqueada ao atingir o limite de tentativas
```

| Tag | Valores | Para que serve |
|---|---|---|
| ID do cenário | `@CT-02` (padrão de `conventions.test_id_pattern`) | Rastreia o caso até o cenário que o originou. **Obrigatória.** |
| Camada | `@api` ou `@interface` | Herdada do prefixo `[API]`/`[INTERFACE]` do caso sugerido; decide se o caso vai para `api.framework` ou `ui.framework` na fase de automação. |
| Execução | `@pendente-de-automacao` ou `@nao-automatizavel` | Separa o que segue para automação do que fica como roteiro manual. |

Sem documento de cenários, a tag de ID aponta para o requisito de origem (`@PROJ-482`) — nunca fique sem nenhuma âncora de rastreio.

Marque `@nao-automatizavel` só com motivo declarado no resumo (depende de ambiente físico, de validação visual subjetiva, de terceiro sem ambiente de teste). "Difícil de automatizar" não é motivo.

### 6. Cenário simples vs. Esquema do Cenário

**Cenário simples** — quando a regra não varia por parâmetro:

```gherkin
  @CT-01 @api @pendente-de-automacao
  Cenário: Validar que <descrição objetiva do comportamento esperado>
    Dado que <contexto>
    Quando <ação>
    Então <resultado>
    E <complemento, se necessário>
```

**Esquema do Cenário (Scenario Outline)** — quando a MESMA regra se repete para uma lista de campos/valores/status/etapas (3 ou mais itens):

```gherkin
  @CT-03 @interface @pendente-de-automacao
  Esquema do Cenário: Validar que <descrição usando placeholder entre <>>
    Dado que <contexto usando "<parametro>">
    Quando <ação>
    Então o campo "<parametro>" <resultado esperado>

    Exemplos:
      | parametro   |
      | Valor 1     |
      | Valor 2     |
      | Valor 3     |
```

Regra de decisão: se a mesma verificação se aplica a 3+ itens de uma lista (campos, status, telas, fluxos, requisitos), use Esquema do Cenário — nunca repita o mesmo Cenário simples várias vezes trocando só o valor. Nomeie a coluna da tabela de Exemplos com o nome do parâmetro (`campo`, `etapa`, `fluxo`, `status`, `requisito` etc.) e alinhe as colunas com espaços para legibilidade.

**Como isso conversa com o contrato**: um caso sugerido = um `Cenário`. Quando 3+ casos sugeridos do mesmo cenário têm exatamente os mesmos passos e diferem só no valor, eles viram **linhas de `Exemplos`** dentro de um único `Esquema do Cenário`. A contagem do resumo conta linhas de `Exemplos`, não blocos, e diz como ficou: "11 casos: 6 `Cenário` + 1 `Esquema do Cenário` com 5 `Exemplos`".

### 7. Nomenclatura dos títulos

Todo título de `Cenário:` ou `Esquema do Cenário:` começa com o prefixo definido em
`conventions.scenario_title_prefix` — **"Validar que..."** é o default — e descreve o
comportamento esperado de forma afirmativa e específica. Nunca use títulos genéricos como
"Teste 1" ou "Cenário de erro". Se o perfil trouxer o prefixo vazio, escreva o título direto
no comportamento esperado, mantendo a forma afirmativa.

### 8. Convenções de escrita dentro dos passos

- **Uma ação por caso**: um único `Quando` relevante. Nunca escreva dois `Quando` no mesmo caso — quando ele falha, ninguém descobre qual das duas ações quebrou; são dois casos.
- **Sem lógica condicional**: nenhum passo carrega "se", "ou" ou "caso". Cada condição é um caso separado; a alternativa para variação é a tabela de `Exemplos`, nunca um "ou" no meio da linha.
- **Dado descritivo, não valor mágico**: prefira `Dado que existe um CNPJ válido de instituição cadastrada` a colar `"12.345.678/0001-90"` no passo. A exceção é quando o valor **é** o objeto do teste — formato inválido, valor no limite, código de status — e dentro da tabela de `Exemplos`, onde o valor é o parâmetro. A massa de verdade vem de `dados-de-teste`, não de constante escondida no passo.
- Valores/labels literais sempre entre aspas duplas: `"Sim"`, `"Não se aplica"`, `"FIDC"`, `"Enviar para análise Anbima"`.
- Terminologia do domínio é copiada exatamente como aparece no requisito original (nomes de campos, telas, botões, atores) — não parafraseie.
- Verbo fiel ao requisito: se o texto diz "clicar em 'Finalizar Preenchimento'", o passo aciona a opção `"Finalizar Preenchimento"`, com esse nome.
- Foco no comportamento, não na implementação: `Quando o usuário aciona "Confirmar"`, não `Quando o usuário clica no elemento com id "btn-submit"`.
- Cobertura sistemática de pares positivo/negativo dentro do mesmo tópico: obrigatório vs. não obrigatório, habilitado vs. desabilitado, campo aparece vs. não aparece (reflete o princípio 3 — pensar em risco — de `AGENTS.md`).
- Indentação de 2 espaços por nível: `Funcionalidade` → tags → `Cenário`/`Esquema do Cenário` → passos → `Exemplos` → linhas da tabela.
- Gramática de cada passo (Dado/Quando/Então/E/Mas) segue `gherkin-palavras-chave`.

### 9. Resumo dos Casos de Teste

Fora do bloco de código, ao final do documento, **escrito por último**:

```markdown
## Resumo dos Casos de Teste

**Total de casos:** 11 (6 Cenário + 1 Esquema do Cenário com 5 Exemplos)
**Por camada:** @api 7 · @interface 4
**Por tipo de execução:** @pendente-de-automacao 9 · @nao-automatizavel 2
**Por prioridade herdada:** Alta 6 · Média 5 · Baixa 0
**Aderência ao contrato:** 11 casos sugeridos, 11 escritos.
```

Regras:

- A prioridade é **herdada** do cenário de origem, não redecidida aqui, e usa os níveis de `risk_levels` no idioma de `language`.
- A linha de aderência compara com a lista de casos sugeridos: quando o número diverge, diga quais casos entraram a mais ou ficaram de fora, e por quê. Sem documento de cenários, ela diz que não havia contrato.
- Cada caso marcado `@nao-automatizavel` aparece aqui com o motivo.
- Os totais têm que bater com o corpo do documento — por isso o resumo é escrito por último.

### 10. Seção de Observações

Lacuna de requisito mora no documento de **cenários**: é lá que a análise acontece e é lá que o
time procura. Quando este documento é derivado de um documento de cenários, não repita as
observações — cite-o e siga.

Quando **não há** documento de cenários (o usuário trouxe os casos direto), a lacuna não tem
onde morar, e aí ela fica aqui, fora do bloco de código:

```markdown
## Observações
```

(ou `## Observação`, no singular, se houver apenas uma). Use SEMPRE que um caso tiver sido:

- **deduzido por complementaridade lógica** — a regra original só descreve um dos lados (ex.: só o caso positivo), e o caso do lado oposto foi inferido;
- **montado com base em informação de outro requisito ou conversa anterior** porque o texto original não trouxe todos os dados necessários (ex.: lista de campos que deveria aparecer em uma tela);
- **escrito a partir de um trecho ambíguo, incompleto ou truncado** do requisito original.

Cada observação deve: (a) explicar o que foi assumido/deduzido e por quê, (b) indicar explicitamente que precisa ser confirmado com o time antes de considerar definitivo. Isto implementa o princípio 2 de `AGENTS.md` ("documentação ambígua gera pergunta, não suposição silenciosa") em modo autônomo — nunca omita uma suposição em silêncio, aqui ou no documento de cenários.

## Passo a passo para escrever os casos

1. Conferir o contrato: a lista de casos sugeridos por cenário (Passo 1).
2. Identificar ator, objetivo e benefício para o cabeçalho `Funcionalidade`.
3. Abrir um tópico por cenário de origem (ou por campo/regra/tela, quando não houver cenários).
4. Para cada caso sugerido, decidir entre `Cenário` simples e `Esquema do Cenário` (regra da seção 6).
5. Escrever as tags: ID do cenário, camada, tipo de execução.
6. Escrever os títulos no prefixo de `conventions.scenario_title_prefix` ("Validar que..." por default).
7. Aplicar a gramática Dado/Quando/Então/E/Mas de `gherkin-palavras-chave` em cada passo, com um único `Quando` por caso.
8. Transformar os "Resultados Esperados" do cenário em `Então` — sem inventar resultado que o cenário não previa.
9. Fechar com o resumo (seção 9) e, se não houver documento de cenários, com `## Observações`.
10. Revisar: valores literais entre aspas, terminologia batendo com o requisito original, indentação consistente.

## Revisão de qualidade antes de entregar

- [ ] Todo caso tem tag de rastreio ao cenário (ou ao requisito), tag de camada e tag de tipo de execução.
- [ ] Todo título de Cenário/Esquema do Cenário usa o prefixo do perfil ("Validar que..." por default) e é específico.
- [ ] Nenhum caso tem mais de um `Quando`, e nenhum passo tem "se", "ou" ou "caso".
- [ ] Esquema do Cenário foi usado (não Cenários repetidos) sempre que 3+ itens compartilham a mesma regra.
- [ ] Valores literais estão entre aspas duplas, e nenhum valor concreto aparece onde um dado descritivo bastaria.
- [ ] Terminologia bate exatamente com o requisito original (nomes de campo, tela, botão).
- [ ] Pares positivo/negativo relevantes estão cobertos dentro de cada tópico.
- [ ] O resumo final existe, os totais batem com o corpo, e a aderência ao contrato está declarada.
- [ ] Toda suposição/dedução/lacuna está registrada — no documento de cenários, ou em `## Observações` quando ele não existe.
- [ ] Origem (ticket, PRD, documento de cenários) está identificável a partir do cabeçalho.

## Exemplo completo

Ver `templates/casos-de-teste.md` para um exemplo completo (cabeçalho + `Funcionalidade` + um `Cenário` simples com tags + um `Esquema do Cenário` com `Exemplos` + resumo final + seção de `Observações`).

## Pronto quando

- O arquivo `.md` existe em `paths.test_cases`, com o nome-base do documento de origem preservado.
- O bloco de código abre com `# language: pt` e tem exatamente uma `Funcionalidade`.
- Todo caso carrega tag de rastreio, tag de camada (`@api`/`@interface`) e tag de execução (`@pendente-de-automacao`/`@nao-automatizavel`).
- Todo título de cenário começa com o prefixo de `conventions.scenario_title_prefix` e descreve o comportamento esperado, não a ação.
- Cada caso tem um único `Quando`, e nenhum passo carrega condicional.
- Toda regra que se repete para três ou mais itens está em `Esquema do Cenário` com `Exemplos` — nenhum cenário simples duplicado trocando só o valor.
- Todo valor ou label literal está entre aspas duplas.
- Cada passo respeita a gramática de `gherkin-palavras-chave`: nenhum `Dado` com ação, nenhum `Então` com implementação interna, nenhum `E` herdando categoria errada.
- O resumo final existe, com totais que batem com o corpo e com a aderência ao contrato declarada.
- Toda dedução ou lacuna está registrada, dizendo o que foi assumido e o que precisa ser confirmado com o time.
- A origem (ticket, PRD, documento de cenários) está citada no documento.

## Ao encadear com a próxima fase

A automação é opcional e nunca começa automaticamente. A skill que a executa vem do perfil: `api.framework` para os casos `@api` (`robot-framework-api` sem perfil) e `ui.framework` para os `@interface` (`cypress-ui-automation` ou `playwright-ui-automation`; sem perfil, Cypress). Os casos `@nao-automatizavel` ficam de fora e seguem como roteiro manual. Após entregar o documento, pergunte explicitamente ao usuário se ele aprova seguir para automação agora ou se os casos ficam como documentação por ora — mesmo que o pedido original já tenha pedido automação de ponta a ponta, aguarde essa confirmação antes de acionar a skill de automação.

## Skills relacionadas

- **`cenarios-de-teste`** — a fase anterior. Volte para lá se os cenários ainda não existem, ou se ao escrever aparecer uma regra de negócio que ninguém levantou: isso é análise, não redação. É de lá que vêm a prioridade, a granularidade e o contrato de casos sugeridos.
- **`gherkin-palavras-chave`** — usada dentro desta, não no lugar dela. Esta skill define a estrutura do documento; aquela decide qual conector cabe em cada linha. Vá direto para lá quando a dúvida for só sobre um passo.
- **`dados-de-teste`** — dona da massa. Quando o caso precisar de dado real, fábrica ou limpeza, o passo aqui descreve o dado e a construção dele fica lá.
- **`robot-framework-api`, `cypress-ui-automation`, `playwright-ui-automation`** — a fase seguinte, e só com aprovação explícita do usuário. Qual delas responde vem de `api.framework` e `ui.framework`, e a tag de camada de cada caso diz qual dos dois se aplica.
