// cypress/support/pages/[nome]Page.js
// Use este padrão só quando a mesma tela/fluxo é reutilizada por várias specs
// (3+ usos) — para casos menores, prefira comandos customizados simples.
class NomePage {
  visit() {
    cy.visit('/[rota]')
    return this
  }

  preencherCampo(valor) {
    cy.get('[data-cy=campo-1]').type(valor)
    return this
  }

  confirmar() {
    cy.get('[data-cy=confirmar]').click()
    return this
  }

  resultadoDeveSerVisivel() {
    cy.get('[data-cy=resultado]').should('be.visible')
    return this
  }
}

export default new NomePage()
