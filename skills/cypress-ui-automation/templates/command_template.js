// cypress/support/commands.js
// Adicione aqui ações repetidas em 2+ specs (login, navegação padrão, etc.)

Cypress.Commands.add('login', (email, senha) => {
  cy.session([email, senha], () => {
    cy.visit('/login')
    cy.get('[data-cy=email]').type(email)
    cy.get('[data-cy=senha]').type(senha, { log: false })
    cy.get('[data-cy=entrar]').click()
    cy.url().should('include', '/dashboard')
  })
})

// Exemplo de comando que encapsula setup de dados via API (mais rápido que via UI)
Cypress.Commands.add('criarRecursoViaApi', (payload) => {
  cy.request('POST', `${Cypress.env('apiUrl')}/[recurso]`, payload).then((response) => {
    expect(response.status).to.eq(201)
    return response.body
  })
})
