---
name: revisao-qualidade-testes
description: Revisa código de teste que já existe e aponta maus cheiros em seis dimensões (legibilidade, confiabilidade, valor diagnóstico, projeto, origem em IA e cobertura), avalia a testabilidade do código de aplicação e entrega um relatório com severidade e correção por achado. Use quando o usuário pedir revisão da suíte de testes, auditoria de qualidade dos testes, análise de maus cheiros, revisão de um pull request que mexe em teste, ou quiser saber se os testes existentes realmente pegam bug. Não use para escrever testes novos a partir de requisito (use escrita-casos-teste e a skill do framework) nem para estabilizar um teste que oscila (use confiabilidade-testes).
license: MIT
metadata:
  author: QAGente
  version: '1.0.0'
  category: analise
  adaptado_de: 'qa-skills/ai-qa-review — Petr Kindlmann, MIT'
---

# Revisão de Qualidade de Testes

<objetivo>
Impede que "a suíte está verde" seja lido como "a suíte pega bug". Um teste que afirma apenas "existe" e uma suíte de cobertura alta que só alimenta caminho feliz ficam os dois verdes e escondem os dois o mesmo defeito. Esta skill separa "o código rodou" de "o valor errado seria pego": nomeia o mau cheiro, cita o arquivo e a linha, explica por que importa e mostra a correção. Entrega um relatório com uma linha por arquivo revisado e severidade por achado — não uma opinião genérica sobre a suíte.
</objetivo>

Esta é uma skill de apoio. Ela olha para **testes que já existem**, inclusive os que este próprio agente escreveu numa sessão anterior — que é o caso em que ela mais rende, porque o agente que escreveu o teste é o pior revisor dele.

## Configuração

Leia `.qagente/quality-profile.json` na raiz do projeto antes de começar. Quando um campo
existir no perfil, ele vence os valores desta skill. Precedência: **instrução explícita do
usuário → perfil do projeto → defaults desta skill**.

Leia também `.qagente/contexto-projeto.md`, quando existir. Ele calibra a severidade: um mau
cheiro num teste que cobre área crítica declarada pelo time é alto; o mesmo mau cheiro numa
área de baixo risco é médio. Sem ele, a severidade sai da sua avaliação técnica apenas —
diga isso no relatório.

| Decisão desta skill | Campo do perfil | Default |
|---|---|---|
| Idioma do relatório | `language` | idioma da conversa |
| Onde estão os testes de API a revisar | `paths.api_tests` | `saida/robot/` |
| Onde estão os testes de UI a revisar | `paths.ui_tests` | `saida/cypress/` |
| Convenções esperadas nos testes de UI | `ui.framework`, `ui.selector_attribute`, `ui.language` | Cypress, `data-testid`, JavaScript |
| Convenções esperadas nos testes de API | `api.framework` | Robot Framework |
| Onde salvar o relatório | `paths.reviews`, senão `paths.test_cases` | `saida/revisoes/` |

As regras universais de `AGENTS.md` valem sempre. Uma delas manda especialmente aqui:
**evidência real de execução** — esta skill roda a suíte antes de comentar, e o relatório
carrega a saída real.

## Perguntas de descoberta

Leia o perfil e o contexto primeiro. Depois pergunte só o que faltar:

- **É revisão de um pull request ou auditoria da suíte inteira?** A primeira roda e pontua só os arquivos alterados; a segunda amostra e procura padrão sistêmico. São caminhos diferentes.
- **Quem escreveu esses testes?** Se saíram de um agente de IA — inclusive deste agente —, a passada de maus cheiros de origem em IA é obrigatória, não opcional.
- **A suíte está verde hoje?** Nunca revise teste vermelho ou pulado como se estivesse passando. Se estiver vermelha, o primeiro achado é esse.
- **O time tem convenção documentada de teste?** Guia de estilo, regra de lint, seção em `CONTRIBUTING.md`. Sem isso, a convenção de referência passa a ser o perfil e o resto da suíte.
- **Existe dor recorrente conhecida?** Teste que oscila, suíte lenta, falha ilegível. Isso decide por qual dimensão começar.

## As seis dimensões

### 1. Legibilidade

| Mau cheiro | Como se parece | Correção |
|---|---|---|
| **Setup obscuro** | 30 linhas montando objeto com campos irrelevantes; não dá para saber quais importam para a asserção | Extrair para fábrica de dados e deixar no corpo só o que a asserção usa (ver `skills/dados-de-teste`) |
| **Convidado misterioso** | O teste depende de um arquivo de massa que o leitor não vê e precisa abrir para entender a asserção | Trazer o dado relevante para dentro do teste, ou nomear a fixture de forma descritiva |
| **Asserção duplicada** | Três testes afirmam o mesmo comportamento com especificidade diferente | Consolidar e manter a asserção mais específica |

Critério prático: dá para entender o que o teste verifica em menos de 10 segundos?

### 2. Confiabilidade

| Mau cheiro | Como se parece | Correção |
|---|---|---|
| **Espera por tempo fixo** | ❌ `cy.wait(3000)`, ❌ `waitForTimeout(5000)`, ❌ o keyword `Sleep` do Robot Framework usados para sincronizar | Esperar pela condição: elemento visível, resposta interceptada, estado atingido |
| **Dependência de ordem** | Passa quando roda com os outros, falha isolado (ou com `--shuffle`) | Cada teste cria as próprias pré-condições |
| **Acoplamento a serviço externo** | O teste chama a API real do parceiro, o gateway de pagamento real, o provedor de e-mail real | Interceptar na fronteira (`cy.intercept`, `page.route`, mock no Robot) |

Espera por tempo fixo é rejeição, não sugestão: nunca é a correção certa. Ela não sincroniza nada — só torna a suíte mais lenta e continua oscilando.

### 3. Valor diagnóstico

| Mau cheiro | Como se parece | Correção |
|---|---|---|
| **Asserção fraca** | ❌ `should('exist')`, ❌ `toBeTruthy()`, ❌ `Should Not Be Empty` como asserção principal — a falha não diz o que era esperado | Afirmar o valor concreto, para que a mensagem de falha já explique o problema |
| **Várias causas de falha por teste** | Um teste cobre três comportamentos independentes; quando falha, ninguém sabe qual quebrou | Dividir: um motivo de falha por teste |

Critério prático: lendo só a mensagem de falha, sem abrir o teste, dá para saber o que quebrou?

### 4. Projeto do teste

| Mau cheiro | Como se parece | Correção |
|---|---|---|
| **Lógica condicional no teste** | ❌ `if`, `switch`, ternário ou laço dentro do corpo do teste — a ramificação em si não é testada, e você não sabe qual caso rodou | Teste parametrizado: `it.each`, `cy.wrap` sobre lista, `Templates` no Robot Framework |
| **Fixture gigante** | Um `beforeEach` que monta 20 objetos para todo teste, embora cada um use 2 | Setup por teste, com fábricas para o que é compartilhado |
| **Mock em excesso** | Todo colaborador é mockado, inclusive função pura e objeto de valor — às vezes a própria função sob teste | Mockar fronteira (rede, banco, arquivo, relógio), nunca o interno |

### 5. Origem em IA

O vocabulário é o mesmo, mas estas falhas se repetem o bastante em código gerado por agente para merecerem passada própria — e valem para o código que **este** agente gerou.

| Mau cheiro | Como detectar |
|---|---|
| **Seletor alucinado** | Rode o teste contra a página real uma vez. Se o seletor nunca casa, o `data-testid` foi inventado e não existe no produto |
| **Importação fabricada** | Confira cada símbolo importado: o arquivo ou pacote realmente exporta aquilo? Agentes inventam API plausível |
| **Massa genérica** | `test@test.com`, `João da Silva`, `Lorem ipsum`, `exemplo.com` — placeholder gerado porque não havia fábrica do projeto. Substituir pela massa real do time |
| **Ciclo fechado de IA** | Implementação **e** teste escritos pelo mesmo agente na mesma sessão. O teste descreve o que o agente produziu em vez de restringi-lo. Emparelhe com pelo menos um teste de fronteira escrito por pessoa |
| **Desvio de convenção** | Page object, fixture, nomenclatura ou estilo de asserção diferentes do resto da suíte e do que o perfil declara |

### 6. Cobertura

| Mau cheiro | Como se parece | Correção |
|---|---|---|
| **Só caminho feliz** | Toda entrada é válida e todo resultado é sucesso; nenhum caminho de erro testado | Para cada caminho feliz, pergunte qual é o modo de falha correspondente e exija o teste dele |
| **Faltam limites** | Testa o valor "normal" (5 itens) mas não 0, 1, máximo e máximo+1 | Todo parâmetro numérico, tamanho de texto e tamanho de coleção tem limite a testar |
| **Faltam casos negativos** | Nada sobre falha de rede, entrada inválida, permissão negada, modificação concorrente | Um teste por modo de falha relevante |

Percentual de cobertura não é a métrica desta dimensão. ❌ Nunca conclua que a suíte está boa porque o número é alto: 95% de cobertura só com caminho feliz é pior que 75% que inclui erro e limite. Revise **o que é afirmado**, não o que foi executado.

## Testabilidade do código de aplicação

Quando a pergunta for "por que isso é tão difícil de testar", aponte a causa no código de produção — como achado no relatório, nunca como alteração feita por você (`AGENTS.md`, fronteiras):

- **Dependência instanciada dentro do método** (`new ClienteHttp()` no meio da regra) — sugerir injeção por construtor, para o teste poder substituir por dublê.
- **Cálculo misturado com efeito colateral** (a função calcula o total e também dispara e-mail e log) — sugerir extrair o cálculo como função pura e chamá-la do orquestrador.
- **Regra de negócio dentro do handler HTTP** — sem extrair, não há teste de unidade possível sem subir servidor.
- **Interface larga demais** (a classe recebe o cliente de banco inteiro e usa 3 métodos) — sugerir interface estreita, que torna o dublê trivial.

## Fluxo de revisão

### Revisão de pull request

Rode e pontue só os arquivos alterados. Percorra as seis dimensões como checklist e, para cada achado, escreva **o que está errado, por que importa e como corrigir**. ❌ Nunca escreva "esse teste está ruim": não é acionável. "Este teste usa espera por tempo fixo, o que causa oscilação em ambiente mais lento — troque por espera pela resposta interceptada" é.

### Auditoria da suíte inteira

1. **Quantificar** — quantos testes por tipo, framework e diretório.
2. **Amostrar** — revisar de 10% a 20% dos arquivos, priorizando os maiores e os alterados mais recentemente.
3. **Achar padrão** — os 3 a 5 maus cheiros mais comuns da amostra.
4. **Priorizar** — confiabilidade > valor diagnóstico > projeto > legibilidade.
5. **Automatizar** — para cada mau cheiro recorrente, decidir se cabe regra de lint ou verificação de integração contínua.
6. **Relatar** — uma linha por arquivo revisado, com exemplo concreto, correção sugerida, severidade e esforço estimado.

Os dois caminhos entregam o mesmo artefato, no formato de `templates/relatorio-revisao.md`: a revisão de pull request preenche só as linhas dos arquivos alterados; a auditoria preenche também as seções de padrão sistêmico e de automação proposta.

## Verificação (rodar antes de comentar)

1. **Rode a suíte uma vez** e confirme o verde. Nunca revise vermelho ou pulado como se passasse.
2. **Rode de novo, 3 vezes**, para expor oscilação. Um teste que passa uma vez e falha na seguinte é o mau cheiro de confiabilidade, não azar.
   - Cypress: repetir a execução do spec; Playwright: `--repeat-each=3`; Robot Framework: repetir a suíte alvo.
3. **Capture o tempo por teste.** Uma suíte de 20 minutos tem problema de desempenho, mesmo verde.
4. **Quando existir ferramenta de teste de mutação no projeto** (Stryker em JavaScript/TypeScript, `mutmut` em Python), rode e leia a nota. É a única medida objetiva contra asserção fraca e ciclo fechado de IA: suíte gerada por agente abaixo de ~60% de mutação não está restringindo a implementação. Se a ferramenta não existir, diga isso no relatório em vez de afirmar qualidade que você não mediu.

A saída dos passos 1 a 3 é a evidência que sustenta todo achado de confiabilidade e de valor diagnóstico do relatório.

## Erros comuns

- ❌ **Revisar sem rodar.** Análise estática não vê oscilação nem tempo de execução.
- ❌ **Apontar todo mau cheiro fora de contexto.** Um teste de 50 linhas para uma máquina de estados complexa não é setup obscuro, é complexidade necessária. Mau cheiro é sintoma, não veredicto.
- ❌ **Sugerir mock para tudo.** Excesso de mock é ele próprio um mau cheiro. Nunca recomende mockar função pura, objeto de valor ou colaborador rápido em processo.
- ❌ **Revisar uma vez e nunca mais.** Qualidade de teste degrada. Sem regra automatizada ou cadência, o mesmo achado reaparece no próximo trimestre.
- ❌ **Corrigir o código de produção por conta própria.** Testabilidade é achado a reportar, não alteração a fazer — é fronteira deste agente.

## Pronto quando

- O relatório existe em `paths.reviews` (ou `paths.test_cases`), com uma linha por arquivo revisado e severidade por achado (alta/média/baixa).
- As seis dimensões aparecem no relatório; a que não se aplica aparece marcada como não aplicável, nunca em branco.
- Todo achado de severidade alta traz o que está errado, por que importa e a correção — com arquivo e linha citados.
- A verificação rodou: a suíte executou verde ao menos 3 vezes, o tempo por teste foi capturado, e a saída real está no relatório.
- Para suíte gerada por agente, a passada de maus cheiros de origem em IA foi feita e os seletores foram conferidos contra a aplicação real — ou o relatório declara que não foi possível conferir e por quê.
- Ao menos um mau cheiro recorrente virou proposta de regra automatizada, ou o relatório afirma explicitamente que nenhum justificava.

## Skills relacionadas

- **`cypress-ui-automation`, `playwright-ui-automation`, `robot-framework-api`** — definem o que é "bom" em cada framework. Esta skill julga contra os padrões de lá; quando divergirem, a skill do framework vence.
- **`confiabilidade-testes`** — os maus cheiros de confiabilidade (espera fixa, dependência de ordem) são a porta de entrada de lá. Aqui você identifica; lá você classifica a causa raiz e estabiliza.
- **`dados-de-teste`** — a correção de setup obscuro, fixture gigante e massa genérica mora lá.
- **`priorizacao-por-risco`** — decide onde a lacuna de cobertura encontrada aqui realmente dói.
- **`escrita-casos-teste`** — quando a revisão revela comportamento sem caso de teste formal, o caso nasce lá, não aqui.
