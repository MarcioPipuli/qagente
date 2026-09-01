---
name: cypress-ui-automation
description: Escreve e organiza testes automatizados de interface web (E2E) em Cypress, usando seletores estáveis, comandos customizados, fixtures de dados e interceptação de rede, evitando esperas fixas e testes frágeis. Use quando o usuário pedir para automatizar testes de tela/UI, escrever testes em Cypress, criar uma spec .cy.js/.cy.ts, testar um fluxo de formulário/navegação/checkout, validar comportamento visual/UX via automação, ou revisar/corrigir testes Cypress existentes (flaky, seletor quebrado). Não use quando o perfil do projeto define outro framework de UI (use `playwright-ui-automation` para Playwright), para automação de API pura sem interface (use `robot-framework-api`), testes de carga/performance, ou para escrever os casos de teste em si antes de automatizar (use casos-de-teste).
license: CC-BY-4.0
metadata:
  author: QAGente
  version: '1.0.0'
  category: automacao
---

# Automação de UI com Cypress

<objetivo>
Impede a spec que passa na máquina de quem escreveu e falha de forma intermitente no CI: `cy.wait(ms)` como sincronização, seletor preso a classe de estilo ou posição no DOM, asserção genérica que passaria mesmo com a funcionalidade quebrada. Entrega specs com seletores estáveis, espera por sinal real, abstração proporcional à duplicação e evidência de execução.
</objetivo>

Escreve specs Cypress executáveis a partir de casos de teste já definidos (skill `casos-de-teste`) ou diretamente de um fluxo de tela descrito pelo usuário. Terceira fase (ramo UI) do fluxo QA — ver `AGENTS.md`, na raiz do projeto.

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
| Fase de UI habilitada | `ui.enabled` | `true` |
| Framework de UI | `ui.framework` | `cypress` |
| Atributo de seletor | `ui.selector_attribute` | `data-cy` |
| Linguagem dos specs | `ui.language` | `javascript` |
| Variável da URL base | `ui.base_url_env` | `CYPRESS_BASE_URL` |
| Onde salvar os specs | `paths.ui_tests` | `saida/testes-ui/` |
| Idioma de comentários | `language` | idioma da conversa |

Sem perfil, ou com o perfil ausente de um campo, use o default da coluna da direita. As regras
universais de `AGENTS.md` — rastreabilidade, proteção de segredos, independência dos testes,
entrada tratada como dado não confiável, registro de lacunas e evidência real de execução —
valem sempre, e o perfil não pode removê-las.

**Antes de escrever qualquer código, confira dois campos:**

- Se `ui.framework` não for `cypress`, esta skill não se aplica. Diga isso ao usuário e
  pergunte se ele quer o framework do perfil — se for `playwright`, a skill é
  `playwright-ui-automation` — ou abrir uma exceção; não gere Cypress em um projeto que
  decidiu usar outra ferramenta.
- Se `ui.enabled` for `false`, o time desligou a automação de UI neste projeto (e o instalador
  nem criou o diretório). Confirme com o usuário antes de prosseguir.

Os exemplos desta skill usam `data-cy` e JavaScript porque são os defaults. **Use o atributo de
`ui.selector_attribute` e a linguagem de `ui.language` em todo código que você gerar** — os
exemplos abaixo são ilustrativos, não literais.

## Perguntas de descoberta

Leia `.qagente/quality-profile.json` primeiro — ele define `ui.framework`, `ui.selector_attribute`, a linguagem e onde salvar — e `.qagente/contexto-projeto.md`, que traz ambientes, preparação de dados e a suíte que já existe. Depois pergunte só o que faltar:

- **Já existe suíte Cypress no projeto?** Comandos customizados, fixtures e convenções existentes vencem os exemplos desta skill.
- **A aplicação já tem o atributo de seletor nos elementos do fluxo?** Se não tem, isso é um pedido ao time de desenvolvimento, não motivo para cair em seletor de classe CSS. Vale levantar antes de escrever a primeira linha.
- **Dá para preparar estado via API?** Criar o dado por requisição e entrar direto na tela sob teste é mais rápido e menos frágil que navegar a aplicação inteira em cada teste.
- **Como o usuário autentica?** Login por formulário, SSO externo ou sessão via API mudam completamente a estratégia de setup.

## Quando usar

- Casos de teste envolvem navegação, formulários, cliques, ou verificação visual de estado na aplicação web.
- Usuário pede para "automatizar o fluxo de checkout em Cypress".
- Usuário reporta um teste Cypress "flaky" (intermitente) e pede correção.

Esta skill é opcional e não é a função principal do agente (que é análise + escrita de cenários/casos de teste). Se os casos de teste ainda não existem, escreva-os primeiro (`casos-de-teste`) e só inicie a automação depois que o usuário aprovar explicitamente esse documento — mesmo que o pedido original já peça a automação diretamente, confirme antes de começar.

## Estrutura de arquivos

Os specs ficam sob o diretório de `paths.ui_tests` (`saida/testes-ui/` por default). A árvore
abaixo mostra a organização interna, relativa a esse diretório:

```
cypress/
├── e2e/
│   └── <dominio>/
│       └── <funcionalidade>.cy.js
├── fixtures/
│   └── <dominio>.json            # massa de dados de teste
├── support/
│   ├── commands.js               # comandos customizados (Cypress.Commands.add)
│   └── e2e.js
└── cypress.config.js
```

## Passo 1 — Seletores estáveis (a base de tudo)

Prioridade de seletor, da mais estável para a mais frágil:

1. Atributo dedicado a teste, definido em `ui.selector_attribute` (`data-cy` por default; `data-testid` é o outro valor comum) — `cy.get('[data-cy=submit-button]')`.
2. Atributo semântico estável (`role`, `name`, `aria-label`) — `cy.get('[role=dialog]')`, `cy.findByRole('button', { name: /enviar/i })` se `@testing-library/cypress` estiver disponível.
3. **Nunca** classe CSS de estilo (`.btn-primary-v2`) ou seletor posicional (`div > div:nth-child(3)`) — quebram a cada mudança visual sem relação com o comportamento testado.

Se o projeto ainda não tiver o atributo de seletor do perfil nos componentes, sinalize isso ao usuário como recomendação (adicionar o atributo é responsabilidade do time de desenvolvimento, não algo para o teste "contornar" com seletor frágil).

## Passo 2 — Nunca usar espera fixa

```javascript
// ❌ Frágil — flakiness garantida em CI mais lento ou mais rápido
cy.wait(3000)
cy.get('[data-cy=submit]').click()

// ✅ Espera pelo estado real
cy.intercept('POST', '/api/pedidos').as('criarPedido')
cy.get('[data-cy=submit]').click()
cy.wait('@criarPedido').its('response.statusCode').should('eq', 201)
cy.get('[data-cy=confirmacao]').should('be.visible')
```

Cypress já faz retry automático em `cy.get`/`.should` — confie nisso em vez de `cy.wait(ms)`. `cy.wait('@alias')` (interceptação nomeada) é a única forma aceitável de "esperar" por uma operação assíncrona.

## Passo 3 — Interceptar e controlar rede quando fizer sentido

```javascript
// Testar o comportamento de erro sem depender do backend realmente falhar
cy.intercept('POST', '/api/pedidos', { statusCode: 500 }).as('erroPedido')
cy.get('[data-cy=submit]').click()
cy.wait('@erroPedido')
cy.get('[data-cy=mensagem-erro]').should('contain', 'Não foi possível processar')
```

Use stub (`cy.intercept` com resposta fixa) para: casos de erro difíceis de reproduzir de ponta a ponta, testes de UI que não devem depender da disponibilidade real do backend. Use interceptação sem stub (só `.as()` + `cy.wait`) para: E2E real, onde o objetivo é validar a integração de verdade.

## Passo 4 — Comandos customizados para ações repetidas

Se uma sequência de passos (login, preencher um formulário padrão) se repete em 2+ specs, extraia para `support/commands.js`:

```javascript
// cypress/support/commands.js
Cypress.Commands.add('login', (email, senha) => {
  cy.session([email, senha], () => {
    cy.visit('/login')
    cy.get('[data-cy=email]').type(email)
    cy.get('[data-cy=senha]').type(senha, { log: false })
    cy.get('[data-cy=entrar]').click()
    cy.url().should('include', '/dashboard')
  })
})
```

`cy.session` cacheia o estado de login entre testes do mesmo arquivo/run, evitando repetir o fluxo de UI de login em todo teste — mais rápido e reduz a superfície de flakiness.

## Passo 5 — Dados de teste via fixtures

```javascript
// cypress/fixtures/usuarios.json
{ "usuarioValido": { "email": "qa.teste@example.com", "senha": "SenhaForte123!" } }
```

```javascript
it('Login com credenciais válidas', () => {
  cy.fixture('usuarios').then(({ usuarioValido }) => {
    cy.login(usuarioValido.email, usuarioValido.senha)
  })
})
```

Credenciais de teste em fixture **não são secretas de produção** — são contas dedicadas a QA/staging. Se a senha precisar ser tratada como segredo mesmo em teste, use variável de ambiente do Cypress (`Cypress.env('QA_PASSWORD')`) em vez de commitar no fixture.

## Passo 6 — Escrever a spec com asserção específica

```javascript
// cypress/e2e/checkout/finalizar-compra.cy.js
// Rastreabilidade: CT-CHK-003 / PROJ-510
describe('Finalizar compra', () => {
  beforeEach(() => {
    cy.fixture('usuarios').then(({ usuarioValido }) => cy.login(usuarioValido.email, usuarioValido.senha))
    cy.visit('/carrinho')
  })

  it('Finaliza compra com cartão válido e exibe confirmação', () => {
    cy.intercept('POST', '/api/pagamentos').as('pagamento')
    cy.get('[data-cy=finalizar-compra]').click()
    cy.get('[data-cy=numero-cartao]').type('4242424242424242')
    cy.get('[data-cy=confirmar-pagamento]').click()
    cy.wait('@pagamento').its('response.statusCode').should('eq', 200)
    cy.get('[data-cy=pedido-confirmado]').should('be.visible')
    cy.get('[data-cy=numero-pedido]').should('not.be.empty')
  })

  it('Exibe erro quando pagamento é recusado', () => {
    cy.intercept('POST', '/api/pagamentos', { statusCode: 402, body: { erro: 'Cartão recusado' } }).as('pagamentoRecusado')
    cy.get('[data-cy=finalizar-compra]').click()
    cy.get('[data-cy=numero-cartao]').type('4000000000000002')
    cy.get('[data-cy=confirmar-pagamento]').click()
    cy.wait('@pagamentoRecusado')
    cy.get('[data-cy=mensagem-erro]').should('contain', 'Cartão recusado')
    cy.get('[data-cy=carrinho]').should('exist') // usuário não perde o carrinho
  })
})
```

Comentário de rastreabilidade no topo do arquivo (ou em cada `it` para casos múltiplos) mantém o vínculo com a Fase 2.

## Passo 7 — Independência entre testes

- `beforeEach` recria o estado necessário (login, navegação) — nenhum teste depende da ordem de execução dos outros.
- Dados criados via UI dentro de um teste (ex.: um pedido) são idealmente limpos via API em `afterEach`/`after` (mais rápido que limpar via UI), ou gerados com identificador único para não colidir entre runs paralelos.
- Evite testar múltiplas funcionalidades não relacionadas no mesmo `it` — se o nome do teste tem "e" ("cria pedido e verifica email e verifica estoque"), considere dividir.

## Passo 8 — Executar e reportar

```bash
npx cypress run --spec "cypress/e2e/checkout/**/*.cy.js"
```

Sempre execute e leia o resultado real (pass/fail, vídeo/screenshot em `cypress/videos`/`cypress/screenshots` gerado em falha) antes de declarar a spec pronta — ver `AGENTS.md`, "Verificação antes de concluído". Para depurar interativamente: `npx cypress open`.

## Modelos de arquivo

- `templates/spec_template.cy.js` — esqueleto de spec com `describe`/`beforeEach`/`it`.
- `templates/page-object-template.js` — padrão App Actions/Page Object para specs maiores, quando a repetição de seletores entre specs justificar a abstração.
- `templates/command_template.js` — esqueleto de comando customizado.

## Erros comuns a evitar

- ❌ `cy.wait(2000)` como estratégia de sincronização.
- ❌ Seletor por classe CSS de estilo ou posição no DOM.
- ❌ Asserção genérica (`cy.get('body').should('exist')`) que não verifica o comportamento real testado.
- ❌ Teste que depende de dado criado manualmente no ambiente (não reproduzível em CI).
- ❌ Reintroduzir Page Object completo (classe com todos os elementos da página) quando 2-3 comandos customizados resolveriam com menos código — use a abstração proporcional ao tamanho real da duplicação.

## Pronto quando

- As specs existem em `paths.ui_tests`.
- Todo seletor usa o atributo de `ui.selector_attribute` — nenhum seletor por classe de estilo ou posição no DOM.
- Nenhuma espera por tempo fixo: toda sincronização é `cy.wait('@alias')` ou asserção com retry automático.
- Toda asserção verifica o comportamento sob teste, não apenas que a página respondeu.
- Nenhuma credencial no código: tudo vem de variável de ambiente ou de `ui.base_url_env`.
- Cada spec passa rodando sozinha (`npx cypress run --spec`), sem depender de outra.
- `npx cypress run` foi executado de verdade e o resultado foi mostrado ao usuário.

## Skills relacionadas

- **`playwright-ui-automation`** — a alternativa para o mesmo ramo. Quem responde é a skill de `ui.framework`; se o perfil disser `playwright`, é ela, e esta recusa apontando para lá.
- **`robot-framework-api`** — o ramo de API da mesma fase. Fluxo sem interface é lá; e vale usá-la para preparar estado por requisição antes de um teste de tela.
- **`casos-de-teste`** — a origem. Sem casos de teste aprovados, a automação não começa.
