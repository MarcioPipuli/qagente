// cypress/e2e/[dominio]/[funcionalidade].cy.js
// Rastreabilidade: [ticket/PRD de origem]
describe('[Nome da funcionalidade]', () => {
  beforeEach(() => {
    cy.fixture('[dominio]').then((dados) => {
      cy.wrap(dados).as('dados')
    })
    cy.visit('/[rota-inicial]')
  })

  it('[CT-ID] [Descrição específica do cenário — caminho feliz]', function () {
    cy.intercept('POST', '/api/[recurso]').as('acaoPrincipal')
    cy.get('[data-cy=campo-1]').type(this.dados.valorValido)
    cy.get('[data-cy=confirmar]').click()
    cy.wait('@acaoPrincipal').its('response.statusCode').should('eq', 200)
    cy.get('[data-cy=resultado]').should('be.visible')
  })

  it('[CT-ID] [Descrição específica do cenário — negativo]', () => {
    cy.intercept('POST', '/api/[recurso]', { statusCode: 400, body: { erro: '[mensagem]' } }).as('acaoInvalida')
    cy.get('[data-cy=campo-1]').type('[valor inválido]')
    cy.get('[data-cy=confirmar]').click()
    cy.wait('@acaoInvalida')
    cy.get('[data-cy=mensagem-erro]').should('contain', '[mensagem]')
  })
})
