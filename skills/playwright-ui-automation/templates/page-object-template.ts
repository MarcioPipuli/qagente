// tests/pages/[Nome]Page.ts
// Use este padrão só quando a mesma tela/fluxo é reutilizada por 3+ specs.
// Para casos menores, locators direto na spec são mais legíveis.
import { expect, type Locator, type Page } from '@playwright/test'

export class NomePage {
  readonly page: Page

  // Locators são lazy: declarar no construtor não busca nada e não guarda
  // referência velha — a busca acontece na ação ou na asserção.
  readonly campoPrincipal: Locator
  readonly botaoConfirmar: Locator
  readonly resultado: Locator
  readonly mensagemErro: Locator

  constructor(page: Page) {
    this.page = page
    this.campoPrincipal = page.getByLabel('[Rótulo do campo]')
    this.botaoConfirmar = page.getByRole('button', { name: '[Confirmar]' })
    this.resultado = page.getByRole('heading', { name: '[Resultado esperado]' })
    this.mensagemErro = page.getByTestId('[identificador-da-mensagem]')
  }

  async abrir() {
    await this.page.goto('/[rota]')
  }

  async preencherEConfirmar(valor: string) {
    await this.campoPrincipal.fill(valor)
    await this.botaoConfirmar.click()
  }

  // A asserção fica aqui só quando ela É o contrato da página. Verificações
  // específicas de um cenário pertencem à spec, onde a falha é mais legível.
  async deveMostrarResultado() {
    await expect(this.resultado).toBeVisible()
  }
}
