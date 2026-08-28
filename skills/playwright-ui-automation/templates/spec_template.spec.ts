// tests/e2e/[dominio]/[funcionalidade].spec.ts
// Rastreabilidade: [ticket/PRD de origem]
import { test, expect } from '@playwright/test'

test.describe('[Nome da funcionalidade]', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/[rota-inicial]')
  })

  test('[TC-ID] [Descrição específica do cenário — caminho feliz]', async ({ page }) => {
    // Espera a resposta real: é ela que sinaliza a conclusão, não um tempo fixo.
    const resposta = page.waitForResponse((r) => r.url().includes('/api/[recurso]') && r.ok())

    await page.getByLabel('[Rótulo do campo]').fill('[valor válido]')
    await page.getByRole('button', { name: '[Confirmar]' }).click()
    await resposta

    // expect(locator) tem auto-retry; expect(await locator.isVisible()) NÃO tem.
    await expect(page.getByRole('heading', { name: '[Resultado esperado]' })).toBeVisible()
    await expect(page.getByTestId('[identificador-do-resultado]')).not.toBeEmpty()
  })

  test('[TC-ID] [Descrição específica do cenário — negativo]', async ({ page }) => {
    // Força um cenário que seria difícil de reproduzir de verdade.
    await page.route('**/api/[recurso]', (route) =>
      route.fulfill({ status: 400, json: { erro: '[mensagem de erro]' } }),
    )

    await page.getByLabel('[Rótulo do campo]').fill('[valor inválido]')
    await page.getByRole('button', { name: '[Confirmar]' }).click()

    await expect(page.getByText('[mensagem de erro]')).toBeVisible()
    // O usuário não pode perder o que já preencheu por causa de um erro do servidor.
    await expect(page.getByLabel('[Rótulo do campo]')).toHaveValue('[valor inválido]')
  })
})
