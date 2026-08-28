---
name: cypress-ui-automation
description: Escreve e organiza testes automatizados de interface web (E2E) em Cypress, usando seletores estáveis, comandos customizados, fixtures de dados e interceptação de rede, evitando esperas fixas e testes frágeis. Use quando o usuário pedir para automatizar testes de tela/UI, escrever testes em Cypress, criar uma spec .cy.js/.cy.ts, testar um fluxo de formulário/navegação/checkout, validar comportamento visual/UX via automação, ou revisar/corrigir testes Cypress existentes (flaky, seletor quebrado). Do NOT use for automação de API pura sem interface (use robot-framework-api), testes de carga/performance, ou para escrever os casos de teste em si antes de automatizar (use escrita-casos-teste).
license: CC-BY-4.0
metadata:
  author: QAGente
  version: '1.0.0'
---

# Automação de UI com Cypress

Escreve specs Cypress executáveis a partir de casos de teste já definidos (skill `escrita-casos-teste`) ou diretamente de um fluxo de tela descrito pelo usuário. Terceira fase (ramo UI) do fluxo QA — ver `../../AGENTS.md`.

## Quando usar

- Casos de teste envolvem navegação, formulários, cliques, ou verificação visual de estado na aplicação web.
- Usuário pede para "automatizar o fluxo de checkout em Cypress".
- Usuário reporta um teste Cypress "flaky" (intermitente) e pede correção.

Esta skill é opcional e não é a função principal do agente (que é análise + escrita de cenários/casos de teste). Se os casos de teste ainda não existem, escreva-os primeiro (`escrita-casos-teste`) e só inicie a automação depois que o usuário aprovar explicitamente esse documento — mesmo que o pedido original já peça a automação diretamente, confirme antes de começar.

## Estrutura de arquivos

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

1. `data-cy`/`data-testid` dedicado a teste — `cy.get('[data-cy=submit-button]')`.
2. Atributo semântico estável (`role`, `name`, `aria-label`) — `cy.get('[role=dialog]')`, `cy.findByRole('button', { name: /enviar/i })` se `@testing-library/cypress` estiver disponível.
3. **Nunca** classe CSS de estilo (`.btn-primary-v2`) ou seletor posicional (`div > div:nth-child(3)`) — quebram a cada mudança visual sem relação com o comportamento testado.

Se o projeto não tiver `data-cy` nos componentes ainda, sinalize isso ao usuário como recomendação (adicionar o atributo é responsabilidade do time de desenvolvimento, não algo para o teste "contornar" com seletor frágil).

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
