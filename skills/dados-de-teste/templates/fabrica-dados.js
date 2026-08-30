/**
 * Fábrica de dados de teste — esqueleto para Cypress e Playwright.
 *
 * Adapte ao `ui.language` do perfil (converta para TypeScript quando for o caso) e à
 * terminologia do domínio declarada em `.qagente/contexto-projeto.md`.
 *
 * Regras que este arquivo materializa:
 *   - padrões sensatos + sobrescrita por teste (massa mínima, sinal máximo);
 *   - sequência para todo campo único, para não colidir em execução paralela;
 *   - variantes nomeadas no lugar de um arquivo de fixture por combinação;
 *   - associação entre entidades, para a estrutura referencial sair correta;
 *   - determinismo: nada de valor sorteado sem semente nem data corrente na massa.
 *
 * NUNCA coloque credencial aqui. Usuário e senha vêm das variáveis de ambiente
 * declaradas em `api.user_env` / `api.password_env` no perfil do projeto.
 */

// ---------------------------------------------------------------------------
// Sequência e determinismo
// ---------------------------------------------------------------------------

/** Sufixo único por execução: evita colisão de campo único entre trabalhadores paralelos. */
const EXECUCAO = process.env.TEST_RUN_ID || `${Date.now()}`;

let contador = 0;
const proximo = () => ++contador;

/**
 * Data fixa da massa. Congelar aqui é o que torna a asserção repetível.
 * ❌ Nunca use `new Date()` ou `Date.now()` dentro de um valor sobre o qual o teste afirma.
 */
const DATA_BASE = new Date('2026-01-15T12:00:00.000Z');

// ---------------------------------------------------------------------------
// Fábricas
// ---------------------------------------------------------------------------

/**
 * @param {object} [sobrescritas] apenas os campos que o cenário investiga
 */
export function criarUsuario(sobrescritas = {}) {
  const n = proximo();
  return {
    // Sequência + sufixo de execução: único dentro e entre execuções paralelas.
    email: `usuario-${n}-${EXECUCAO}@teste.exemplo.com`,
    nome: `Usuário de Teste ${n}`,
    perfil: 'comum',
    ativo: true,
    criadoEm: DATA_BASE.toISOString(),
    ...sobrescritas,
  };
}

/** Variantes nomeadas — usadas em vez de ❌ uma explosão de arquivos de fixture por combinação. */
export const usuarioAdmin = (sobrescritas = {}) =>
  criarUsuario({ perfil: 'admin', ...sobrescritas });

export const usuarioInativo = (sobrescritas = {}) =>
  criarUsuario({ ativo: false, ...sobrescritas });

/** Associação: o pedido constrói o próprio usuário quando o teste não fornece um. */
export function criarPedido(sobrescritas = {}) {
  const n = proximo();
  return {
    codigo: `PED-${EXECUCAO}-${String(n).padStart(4, '0')}`,
    usuario: criarUsuario(),
    itens: [criarItem()],
    status: 'pendente',
    criadoEm: DATA_BASE.toISOString(),
    ...sobrescritas,
  };
}

export function criarItem(sobrescritas = {}) {
  const n = proximo();
  return {
    sku: `SKU-${EXECUCAO}-${n}`,
    descricao: `Produto ${n}`,
    quantidade: 1,
    precoUnitario: 100.0,
    ...sobrescritas,
  };
}

export const criarVarios = (fabrica, quantidade, sobrescritas = {}) =>
  Array.from({ length: quantidade }, () => fabrica(sobrescritas));

// ---------------------------------------------------------------------------
// Massa de borda — alimenta os cenários de valor limite levantados na Fase 1
// ---------------------------------------------------------------------------

export const textosDeBorda = [
  '',
  '   ',
  'a'.repeat(256),
  'Ação, çedilha e acentuação',
  '🙂 emoji no meio',
  '<script>alert(1)</script>',
  "' OR 1=1 --",
];

export const datasDeBorda = [
  '2026-01-01T00:00:00.000Z', // virada de ano
  '2026-01-31T23:59:59.999Z', // fim de mês
  '2028-02-29T12:00:00.000Z', // ano bissexto
  '1970-01-01T00:00:00.000Z', // data muito antiga
];

export const limites = (minimo, maximo) => [
  minimo - 1,
  minimo,
  minimo + 1,
  maximo - 1,
  maximo,
  maximo + 1,
];

// ---------------------------------------------------------------------------
// Ciclo de vida — criação e limpeza garantidas
// ---------------------------------------------------------------------------

/**
 * Cypress: crie a massa no `beforeEach` via `cy.request` e remova no `afterEach`,
 * na ordem inversa da criação.
 *
 *   beforeEach(() => {
 *     cy.request('POST', '/api/usuarios', criarUsuario()).then((r) => {
 *       cy.wrap(r.body.id).as('usuarioId');
 *     });
 *   });
 *   afterEach(function () {
 *     if (this.usuarioId) cy.request('DELETE', `/api/usuarios/${this.usuarioId}`);
 *   });
 *
 * Playwright: use `test.extend`. A limpeza fica DEPOIS do `await use(...)`, que roda
 * mesmo quando o teste falha — diferente de um passo final solto, que a falha pula.
 *
 *   export const test = base.extend({
 *     usuario: async ({ request }, use) => {
 *       const resposta = await request.post('/api/usuarios', { data: criarUsuario() });
 *       const usuario = await resposta.json();
 *       await use(usuario);
 *       await request.delete(`/api/usuarios/${usuario.id}`);
 *     },
 *   });
 */
