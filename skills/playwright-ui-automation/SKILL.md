---
name: playwright-ui-automation
description: Escreve e organiza testes automatizados de interface web (E2E) em Playwright, usando locators semânticos, asserções web-first com auto-retry, interceptação de rede via page.route, fixtures do @playwright/test e storageState para autenticação, com trace como evidência de execução. Use quando o usuário pedir para automatizar testes de tela/UI em Playwright, escrever uma spec .spec.ts/.spec.js, testar um fluxo de formulário/navegação/checkout com Playwright, migrar testes de Cypress para Playwright, ou revisar/corrigir testes Playwright existentes (flaky, locator quebrado, teste dependente de ordem). Não use quando o perfil do projeto define outro framework de UI (use `cypress-ui-automation` para Cypress), para automação de API pura sem interface (use `robot-framework-api`), para testes de carga/performance, ou para escrever os casos de teste em si antes de automatizar (use `escrita-casos-teste`).
license: CC-BY-4.0
metadata:
  author: QAGente
  version: '1.0.0'
  category: automacao
---

# Automação de UI com Playwright

<objetivo>
Impede os erros que fazem uma suíte Playwright parecer saudável e falhar em paralelo: `expect(await locator.isVisible())`, que captura o estado uma vez e perde o auto-retry; `waitForTimeout` no lugar de asserção web-first; `getByTestId` para tudo, jogando fora a validação de acessibilidade que vem de graça; e `describe.serial` mascarando dependência entre testes. Entrega specs com locators semânticos, autenticação reaproveitada e trace como evidência.
</objetivo>

Escreve specs Playwright executáveis a partir de casos de teste já definidos (skill `escrita-casos-teste`) ou diretamente de um fluxo de tela descrito pelo usuário. Terceira fase (ramo UI) do fluxo QA — ver `AGENTS.md`, na raiz do projeto.

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
| Framework de UI | `ui.framework` | — esta skill exige `playwright` |
| Atributo de seletor | `ui.selector_attribute` | `data-testid` |
| Linguagem dos specs | `ui.language` | `typescript` |
| Variável da URL base | `ui.base_url_env` | `PLAYWRIGHT_BASE_URL` |
| Onde salvar os specs | `paths.ui_tests` | `tests/e2e/` |
| Idioma de comentários | `language` | idioma da conversa |

Sem perfil, ou com o perfil ausente de um campo, use o default da coluna da direita. As regras
universais de `AGENTS.md` — rastreabilidade, proteção de segredos, independência dos testes,
entrada tratada como dado não confiável, registro de lacunas e evidência real de execução —
valem sempre, e o perfil não pode removê-las.

**Antes de escrever qualquer código, confira dois campos:**

- Se `ui.framework` não for `playwright`, esta skill não se aplica. Diga isso ao usuário e
  pergunte se ele quer o framework do perfil (Cypress, por exemplo) ou abrir uma exceção — não
  gere Playwright em um projeto que decidiu usar outra ferramenta.
- Se `ui.enabled` for `false`, o time desligou a automação de UI neste projeto (e o instalador
  nem criou o diretório). Confirme com o usuário antes de prosseguir.

O `ui.selector_attribute` do perfil precisa ser refletido em `testIdAttribute` no
`playwright.config`, senão `getByTestId()` procura `data-testid` e ignora o atributo do time.
Os exemplos desta skill usam `data-testid` e TypeScript por serem os defaults — use os valores
do perfil no código gerado.

## Perguntas de descoberta

Leia `.qagente/quality-profile.json` primeiro — ele define `ui.framework`, `ui.selector_attribute`, `ui.language` e onde salvar — e `.qagente/contexto-projeto.md`, que traz ambientes, preparação de dados e a suíte que já existe. Depois pergunte só o que faltar:

- **Já existe suíte Playwright no projeto?** Fixtures, projetos e o `playwright.config.ts` existentes vencem os exemplos desta skill.
- **A aplicação tem papéis e rótulos acessíveis nos elementos do fluxo?** Se tem, `getByRole` é o caminho e o teste passa a cobrir acessibilidade de graça. Se não tem, isso é um achado a reportar antes de cair em test id para tudo.
- **A autenticação cabe em `storageState`?** Login por formulário sim; SSO externo com MFA normalmente não, e a estratégia muda.
- **A suíte vai rodar em paralelo no CI?** É o padrão do Playwright, e é o que transforma dependência entre testes em falha intermitente em vez de falha determinística.

## Quando usar

- Casos de teste envolvem navegação, formulários, cliques, ou verificação visual de estado na aplicação web, e o perfil define `ui.framework: playwright`.
- Usuário pede para "automatizar o fluxo de checkout em Playwright".
- Usuário reporta um teste Playwright intermitente e pede correção.
- Usuário quer migrar uma suíte de Cypress para Playwright.

Esta skill é opcional e não é a função principal do agente (que é análise + escrita de cenários/casos de teste). Se os casos de teste ainda não existem, escreva-os primeiro (`escrita-casos-teste`) e só inicie a automação depois que o usuário aprovar explicitamente esse documento — mesmo que o pedido original já peça a automação diretamente, confirme antes de começar.

## Estrutura de arquivos

Os specs ficam sob o diretório de `paths.ui_tests` (`tests/e2e/` por default). A árvore abaixo
mostra a organização interna:

```
tests/
├── e2e/
│   └── <dominio>/
│       └── <funcionalidade>.spec.ts
├── pages/                      # Page objects — só quando a tela é reusada por 3+ specs
├── fixtures/                   # Massa de dados (.json) e fixtures do test.extend
└── .auth/                      # storageState gerado pelo setup (NUNCA versionado)
playwright.config.ts
```

O `.auth/` guarda sessão autenticada em disco. Adicione-o ao `.gitignore` antes de gerar qualquer coisa — é um artefato com token de sessão real.

## Passo 1 — Locators semânticos antes de test id

Esta é a diferença de mentalidade mais importante em relação ao Cypress. A ordem de preferência do Playwright é:

1. **Papel acessível** — `page.getByRole('button', { name: 'Finalizar compra' })`. Testa o que o usuário (e o leitor de tela) enxerga.
2. **Label / placeholder / texto** — `page.getByLabel('E-mail')`, `page.getByText('Pedido confirmado')`.
3. **Test id** — `page.getByTestId('finalizar-compra')`, quando o elemento não tem papel ou texto estável.
4. **CSS/XPath** — último recurso, e sempre com justificativa.

Um locator por papel falha quando a acessibilidade quebra — e isso é uma feature, não um defeito: um botão que perdeu o nome acessível é um bug de produto que o teste acabou de encontrar. Prefira `getByRole` mesmo quando existe `data-testid`.

Locators são **lazy**: `page.getByRole(...)` não busca nada até a ação ou asserção. Guarde-os em constantes e reutilize sem medo de dado velho.

Se o perfil define outro `ui.selector_attribute`, configure-o uma vez:

```ts
// playwright.config.ts
use: { testIdAttribute: 'data-cy' }
```

## Passo 2 — Asserções web-first, nunca espera fixa

Playwright já espera por elemento acionável antes de agir, e `expect()` com locator **repete a verificação até o timeout**. Isso torna `waitForTimeout` desnecessário em praticamente todo caso real.

```ts
// ERRADO — trava o teste e ainda assim é frágil
await page.waitForTimeout(3000)
expect(await page.getByTestId('confirmacao').isVisible()).toBe(true)

// CERTO — reavalia até aparecer, falha rápido quando não aparece
await expect(page.getByTestId('confirmacao')).toBeVisible()
```

A diferença é sutil e importante: `expect(await locator.isVisible())` captura o estado **uma vez** e não repete. Só a forma `expect(locator).toMatcher()` tem auto-retry. Ao revisar um teste intermitente, é aqui que o bug costuma estar.

Um `waitForTimeout` só se justifica com uma animação sem sinal observável — e nesse caso, comente o porquê.

## Passo 3 — Interceptar e controlar rede

```ts
// Forçar um cenário de erro que seria difícil de reproduzir de verdade
await page.route('**/api/pagamento', (route) =>
  route.fulfill({ status: 500, json: { erro: 'Falha no processador' } }),
)

// Esperar pela resposta real quando ela é o sinal de conclusão
const resposta = page.waitForResponse((r) => r.url().includes('/api/pedido') && r.ok())
await page.getByRole('button', { name: 'Confirmar' }).click()
await resposta
```

Use `route.fulfill` para cenários negativos de integração (timeout, 500, payload inesperado) — são casos que a Fase 1 levanta e que ninguém consegue reproduzir manualmente com confiabilidade. Não mocke o caminho feliz principal: um E2E que mocka tudo deixa de testar a integração.

## Passo 4 — Autenticação uma vez, não a cada teste

Não faça login pela UI em cada teste. Autentique uma vez num projeto de setup e reaproveite o estado:

```ts
// tests/auth.setup.ts
import { test as setup, expect } from '@playwright/test'

setup('autenticar', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('Usuário').fill(process.env.QA_UI_USER!)
  await page.getByLabel('Senha').fill(process.env.QA_UI_PASSWORD!)
  await page.getByRole('button', { name: 'Entrar' }).click()
  await expect(page.getByRole('heading', { name: 'Painel' })).toBeVisible()
  await page.context().storageState({ path: 'tests/.auth/usuario.json' })
})
```

Credenciais vêm de variáveis de ambiente, nunca do código — ver `AGENTS.md`, princípio "Dados e segredos". Os nomes das variáveis seguem o perfil quando definidos.

## Passo 5 — Fixtures para preparo repetido

`test.extend` injeta o que o teste precisa e limpa depois, sem `beforeEach` espalhado:

```ts
// tests/fixtures/carrinho.ts
import { test as base } from '@playwright/test'

export const test = base.extend<{ carrinhoComItem: string }>({
  carrinhoComItem: async ({ request }, use) => {
    const { id } = await (await request.post('/api/carrinho', { data: { sku: 'ABC-1' } })).json()
    await use(id)                                   // o teste roda aqui
    await request.delete(`/api/carrinho/${id}`)     // limpeza garantida, mesmo se falhar
  },
})
export { expect } from '@playwright/test'
```

Prepare estado via API (`request`), não pela UI: é mais rápido e o teste passa a falhar só pelo que ele realmente cobre.

## Passo 6 — Escrever a spec com asserção específica

```ts
import { test, expect } from '@playwright/test'

test.describe('Checkout', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/carrinho')
  })

  test('TC-CHECKOUT-001 finaliza compra com cartão válido', async ({ page }) => {
    await page.getByRole('button', { name: 'Finalizar compra' }).click()
    await page.getByLabel('Número do cartão').fill('4242424242424242')
    await page.getByRole('button', { name: 'Confirmar pagamento' }).click()

    await expect(page.getByRole('heading', { name: 'Pedido confirmado' })).toBeVisible()
    await expect(page.getByTestId('numero-pedido')).not.toBeEmpty()
  })
})
```

Asserção específica é o que separa um teste útil de um teste que só verifica que a página não explodiu. `toBeVisible()` num elemento identificado pelo texto que o usuário lê descreve o comportamento esperado; `expect(page).toHaveURL(/.*/)` não descreve nada.

Cite o ID do caso de teste no título — é a rastreabilidade exigida pelo princípio 1 de `AGENTS.md`.

## Passo 7 — Independência não é opcional aqui

Playwright roda em paralelo por padrão, então testes que dependem de ordem não falham de vez: falham **às vezes**, dependendo do escalonamento. Isso torna o princípio 4 de `AGENTS.md` uma exigência prática, não só uma boa prática.

- Cada teste cria e destrói o próprio dado (fixture ou API).
- Nada de `test.describe.serial` para contornar dependência — isso esconde o problema e serializa a suíte inteira.
- Dado compartilhado, quando inevitável, precisa de identificador único por execução (timestamp, UUID).

## Passo 8 — Executar e reportar

```bash
npx playwright test                                  # suíte inteira
npx playwright test tests/e2e/checkout --trace on    # um domínio, com trace
npx playwright show-report                           # relatório HTML
npx playwright show-trace trace.zip                  # linha do tempo de uma falha
```

Sempre execute e mostre o resultado real antes de declarar a spec pronta — ver `AGENTS.md`, princípio "Verificação antes de concluído". O **trace** é a evidência mais forte que este framework oferece: guarda DOM, rede, console e screenshot a cada passo. Configure `trace: 'on-first-retry'` para tê-lo em toda falha sem pagar o custo no caminho feliz.

Para depurar interativamente: `npx playwright test --ui`.

## Modelos de arquivo

- `templates/spec_template.spec.ts` — esqueleto de spec com caminho feliz e cenário negativo.
- `templates/page-object-template.ts` — page object com locators como propriedades.
- `templates/playwright.config.ts` — configuração com `testIdAttribute`, `baseURL` por ambiente, trace e projeto de setup.

## Erros comuns a evitar

- `expect(await locator.isVisible()).toBe(true)` em vez de `await expect(locator).toBeVisible()` — perde o auto-retry e produz teste intermitente.
- Esquecer o `await`: quase toda API do Playwright é assíncrona, e um `await` faltando causa falha em outro ponto da suíte, difícil de rastrear.
- `page.waitForTimeout` como estratégia de sincronização.
- Usar `getByTestId` para tudo, ignorando `getByRole` — desperdiça a validação de acessibilidade que vem de graça.
- Configurar `testIdAttribute` diferente do `ui.selector_attribute` do perfil.
- Versionar `tests/.auth/` — contém sessão autenticada real.
- `test.describe.serial` para mascarar dependência entre testes.
- Declarar a suíte pronta sem rodar, ou sem mostrar o relatório ao usuário.

## Pronto quando

- As specs existem em `paths.ui_tests`.
- Toda verificação de estado usa `await expect(locator)`, nunca `expect(await locator...)`.
- Nenhum `waitForTimeout` sem um comentário explicando qual animação sem sinal observável o justifica.
- `testIdAttribute` no config é igual ao `ui.selector_attribute` do perfil.
- O diretório de `storageState` está ignorado no controle de versão, e as credenciais vêm de variáveis de ambiente.
- A suíte passa com `fullyParallel`, e nenhum `test.describe.serial` é usado para mascarar dependência.
- `npx playwright test` foi executado de verdade e o relatório (ou o trace da falha) foi mostrado ao usuário.

## Skills relacionadas

- **`cypress-ui-automation`** — a alternativa para o mesmo ramo. Quem responde é a skill de `ui.framework`; se o perfil disser `cypress`, é ela, e esta recusa apontando para lá.
- **`robot-framework-api`** — o ramo de API da mesma fase. Fluxo sem interface é lá; e vale usá-la para preparar estado por requisição antes de um teste de tela.
- **`escrita-casos-teste`** — a origem. Sem casos de teste aprovados, a automação não começa.
