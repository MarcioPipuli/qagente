// playwright.config.ts — raiz do projeto
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e', // = paths.ui_tests do perfil

  // Falha o build se alguém esquecer um test.only commitado.
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  fullyParallel: true, // exige testes independentes — ver princípio 4 de AGENTS.md

  reporter: [['html', { open: 'never' }], ['list']],

  use: {
    // URL base por ambiente; o nome da variável vem de ui.base_url_env no perfil.
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:3000',

    // PRECISA bater com ui.selector_attribute do perfil. Sem isto, getByTestId()
    // procura data-testid e ignora silenciosamente o atributo do time.
    testIdAttribute: 'data-testid',

    // Evidência de execução: trace guarda DOM, rede, console e screenshots.
    // 'on-first-retry' dá evidência em toda falha sem custo no caminho feliz.
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    // Autentica uma vez e grava a sessão; os demais projetos reaproveitam.
    { name: 'setup', testMatch: /auth\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'tests/.auth/usuario.json' },
      dependencies: ['setup'],
    },
  ],
})
