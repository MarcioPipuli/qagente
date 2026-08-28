---
name: escrita-casos-teste
description: Escreve casos de teste em Gherkin/BDD (português), organizados em Funcionalidade + Tópicos + Cenários, seguindo o padrão consolidado do time — inclui quando usar Esquema do Cenário com Exemplos, convenções de nomenclatura e citação explícita de suposições/lacunas do requisito original em uma seção de Observações. Use quando o usuário pedir para escrever, gerar ou padronizar casos de teste/cenários BDD a partir de um requisito, ticket, história de usuário ou lista de cenários já levantada. Do NOT use para identificar quais cenários testar a partir de documentação bruta (use `analise-documentacao-testes` primeiro) ou para automatizar os casos em código (use `robot-framework-api` ou `cypress-ui-automation`). Depende de `gherkin-palavras-chave` para a gramática de Dado/Quando/Então/E/Mas — não duplica essas regras aqui.
license: CC-BY-4.0
metadata:
  author: QAGente
  version: '2.0.0'
---

# Escrita de Casos de Teste (BDD/Gherkin, pt)

Transforma cenários de teste (da skill `analise-documentacao-testes`, ou fornecidos diretamente) em um documento de cenários BDD formal, no formato Gherkin em português. Segunda fase do fluxo QA — ver `../../AGENTS.md`. Esta skill define a **estrutura do documento**; para a gramática de cada passo individual (Dado/Quando/Então/E/Mas), use `gherkin-palavras-chave` em conjunto.

## Quando usar

- O usuário já tem uma lista de cenários (própria ou gerada por `analise-documentacao-testes`) e quer o documento de cenários BDD formal.
- O usuário pede cenários "em Gherkin", "em BDD" ou "no padrão de sempre" a partir de um requisito/ticket.
- O usuário quer revisar ou padronizar um arquivo de cenários existente para bater com o formato do time.

## Estrutura do documento

Todo documento de cenários é salvo como arquivo Markdown (`.md`) — o Gherkin fica em um bloco de código dentro dele, nunca como `.feature` solto (ver convenção de pastas em `AGENTS.md`). A estrutura segue esta ordem:

### 1. Cabeçalho

```markdown
# Cenários de Teste BDD – <Nome do Requisito/Funcionalidade>
```

Use o nome descritivo do requisito. Se houver um ticket de origem (Jira, Azure DevOps etc.), cite-o — no nome do arquivo e/ou logo abaixo do cabeçalho — para manter a rastreabilidade exigida pelo princípio 1 de `AGENTS.md`.

### 2. Bloco de código Gherkin

Abre com:

````markdown
```gherkin
# language: pt
````

E fecha com ` ``` ` ao final de todos os cenários do documento.

### 3. Bloco `Funcionalidade`

```gherkin
Funcionalidade: <nome objetivo da funcionalidade>
  Como <ator: Instituição / Autorregulador / Usuário / ...>
  Quero <ação/objetivo>
  Para <benefício/motivo de negócio>
```

O ator, a ação e o benefício vêm do requisito de origem — nunca invente um motivo de negócio que não esteja explícito ou razoavelmente implícito no texto original (princípio 2 de `AGENTS.md`).

### 4. Organização em Tópicos

Cada bloco temático de cenários é precedido por um comentário Gherkin:

```gherkin
  # Tópico N - <descrição curta do tópico/campo/regra tratada>
```

Um tópico por campo, regra, tela ou fluxo, na ordem lógica em que aparecem no requisito original. Isso mantém o documento navegável mesmo quando há dezenas de cenários.

### 5. Cenário simples vs. Esquema do Cenário

**Cenário simples** — quando a regra não varia por parâmetro:

```gherkin
  Cenário: Validar que <descrição objetiva do comportamento esperado>
    Dado que <contexto>
    Quando <ação>
    Então <resultado>
    E <complemento, se necessário>
```

**Esquema do Cenário (Scenario Outline)** — quando a MESMA regra se repete para uma lista de campos/valores/status/etapas (3 ou mais itens):

```gherkin
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

### 6. Nomenclatura dos títulos

Todo título de `Cenário:` ou `Esquema do Cenário:` começa com **"Validar que..."** e descreve o comportamento esperado de forma afirmativa e específica. Nunca use títulos genéricos como "Teste 1" ou "Cenário de erro".

### 7. Convenções de escrita dentro dos passos

- Valores/labels literais sempre entre aspas duplas: `"Sim"`, `"Não se aplica"`, `"FIDC"`, `"Enviar para análise Anbima"`.
- Terminologia do domínio é copiada exatamente como aparece no requisito original (nomes de campos, telas, botões, atores) — não parafraseie.
- Cobertura sistemática de pares positivo/negativo dentro do mesmo tópico: obrigatório vs. não obrigatório, habilitado vs. desabilitado, campo aparece vs. não aparece (reflete o princípio 3 — pensar em risco — de `AGENTS.md`).
- Indentação de 2 espaços por nível: `Funcionalidade` → `Cenário`/`Esquema do Cenário` → passos → `Exemplos` → linhas da tabela.
- Gramática de cada passo (Dado/Quando/Então/E/Mas) segue `gherkin-palavras-chave`.

### 8. Seção de Observações

Fora do bloco de código, ao final do documento:

```markdown
## Observações
```

(ou `## Observação`, no singular, se houver apenas uma). Use SEMPRE que um cenário tiver sido:

- **deduzido por complementaridade lógica** — a regra original só descreve um dos lados (ex.: só o caso positivo), e o cenário do lado oposto foi inferido;
- **montado com base em informação de outro requisito ou conversa anterior** porque o texto original não trouxe todos os dados necessários (ex.: lista de campos que deveria aparecer em uma tela);
- **escrito a partir de um trecho ambíguo, incompleto ou truncado** do requisito original.

Cada observação deve: (a) explicar o que foi assumido/deduzido e por quê, (b) indicar explicitamente que precisa ser confirmado com o time antes de considerar definitivo. Isto implementa o princípio 2 de `AGENTS.md` ("documentação ambígua gera pergunta, não suposição silenciosa") em modo autônomo — nunca omita uma suposição em silêncio.

## Passo a passo para gerar cenários a partir de um requisito novo

1. Ler o requisito e identificar ator, objetivo e benefício (para o cabeçalho `Funcionalidade`).
2. Quebrar o requisito em tópicos lógicos (um por campo/regra/tela/fluxo).
3. Para cada tópico, decidir entre Cenário simples ou Esquema do Cenário (regra da seção 5).
4. Escrever os títulos no padrão "Validar que...".
5. Aplicar a gramática Dado/Quando/Então/E/Mas de `gherkin-palavras-chave` em cada passo.
6. Cobrir explicitamente os pares positivo/negativo e casos de borda mencionados ou implícitos no requisito.
7. Registrar em `## Observações` qualquer suposição, dedução ou lacuna do requisito original.
8. Revisar: valores literais entre aspas, terminologia batendo com o requisito original, indentação consistente.

## Revisão de qualidade antes de entregar

- [ ] Todo título de Cenário/Esquema do Cenário começa com "Validar que..." e é específico.
- [ ] Esquema do Cenário foi usado (não Cenários repetidos) sempre que 3+ itens compartilham a mesma regra.
- [ ] Valores literais estão entre aspas duplas.
- [ ] Terminologia bate exatamente com o requisito original (nomes de campo, tela, botão).
- [ ] Pares positivo/negativo relevantes estão cobertos dentro de cada tópico.
- [ ] Toda suposição/dedução/lacuna está registrada em `## Observações`, não escondida no meio dos cenários.
- [ ] Origem do requisito (ticket, PRD, seção) está identificável a partir do cabeçalho.

## Exemplo completo

Ver `templates/cenario.md` para um exemplo completo (cabeçalho + `Funcionalidade` + um `Cenário` simples + um `Esquema do Cenário` com `Exemplos` + seção de `Observações`).

## Ao encadear com a próxima fase

A automação (Robot Framework para API → `robot-framework-api`; Cypress para UI → `cypress-ui-automation`) é opcional e nunca começa automaticamente. Após entregar o documento de casos de teste, pergunte explicitamente ao usuário se ele aprova seguir para automação agora ou se os casos ficam como documentação para execução manual por ora — mesmo que o pedido original já tenha pedido automação de ponta a ponta, aguarde essa confirmação antes de acionar `robot-framework-api` ou `cypress-ui-automation`.
