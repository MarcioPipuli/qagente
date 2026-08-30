---
name: dados-de-teste
description: Projeta a massa de teste da suíte com fábricas, fixtures, sementes idempotentes, isolamento por teste, limpeza garantida e anonimização de dado de produção. Use quando o usuário pedir para organizar a massa de teste, criar fábrica ou fixture de dados, resolver testes que se atrapalham por dado compartilhado, tornar a massa determinística, semear banco de teste, ou usar dado parecido com o de produção sem expor informação pessoal. Não use para estabilizar um teste que oscila por outra causa que não dado (use confiabilidade-testes) nem para escrever os casos de teste em si (use escrita-casos-teste).
license: MIT
metadata:
  author: QAGente
  version: '1.0.0'
  category: automacao
  adaptado_de: 'qa-skills/test-data-management — Petr Kindlmann, MIT'
---

# Dados de Teste

<objetivo>
Impede que a camada de dados vire a causa raiz invisível da suíte. Massa malfeita produz três falhas que parecem problemas diferentes e são o mesmo problema: teste que oscila porque dois testes disputam a mesma linha do banco, teste que não prova nada porque a massa é irreal, e risco jurídico porque alguém copiou o banco de produção para homologação. Esta skill entrega massa determinística, isolada por teste, realista o suficiente e livre de dado pessoal real — com limpeza que roda mesmo quando o teste falha.
</objetivo>

Esta é uma skill de apoio às Fases 3a e 3b. Ela não escreve testes; escreve a camada de dados de que os testes dependem. É também a resposta concreta ao princípio 4 de `AGENTS.md` — testes independentes e determinísticos.

## Configuração

Leia `.qagente/quality-profile.json` na raiz do projeto antes de começar. Quando um campo
existir no perfil, ele vence os valores desta skill. Precedência: **instrução explícita do
usuário → perfil do projeto → defaults desta skill**.

Leia também `.qagente/contexto-projeto.md`, quando existir. Dele saem a terminologia do
domínio (que dá nome aos campos da fábrica), os ambientes do time e a informação de quais
dados são sensíveis no produto. Sem ele, a fábrica sai com nomes genéricos e você não sabe o
que precisa ser anonimizado — diga isso ao usuário.

| Decisão desta skill | Campo do perfil | Default |
|---|---|---|
| Idioma dos identificadores e comentários | `language`, `ui.language` | pt-BR nos comentários, inglês nos nomes técnicos |
| Onde vive a massa de UI | `paths.ui_tests` | `saida/cypress/` |
| Onde vive a massa de API | `paths.api_tests` | `saida/robot/` |
| Framework de UI (formato da fábrica) | `ui.framework` | Cypress |
| Framework de API (formato do recurso) | `api.framework` | Robot Framework |
| Nomes das variáveis de credencial | `api.user_env`, `api.password_env`, `api.base_url_env` | `QA_API_USER`, `QA_API_PASSWORD`, `API_BASE_URL` |

As regras universais de `AGENTS.md` valem sempre, e duas são inegociáveis nesta skill:
**proteção de segredos** — credencial nunca entra em arquivo de massa, sempre vem das
variáveis declaradas no perfil — e **independência dos testes**.

## Perguntas de descoberta

Leia o perfil e o contexto primeiro. Depois pergunte só o que faltar:

- **Como a massa é criada hoje?** Manualmente, por script, por cópia de produção, ou não existe? Cópia de produção muda a pauta: a anonimização vira o primeiro assunto.
- **Os testes compartilham dado ou cada um cria o seu?** Compartilhamento é a causa raiz mais comum de falha que só aparece em paralelo.
- **Como a massa é limpa?** Rollback, truncate, chamada de API, ou nunca? "Nunca" significa que o banco de teste cresce até virar problema.
- **O produto trata dado pessoal?** Nome, e-mail, telefone, CPF, endereço, dado financeiro ou de saúde. Isso decide se a seção de anonimização se aplica.
- **Qual o tamanho e a complexidade da massa?** Dezenas de registros com relação simples é um problema; hierarquia profunda entre serviços é outro.
- **Os testes rodam em paralelo?** Se sim, identificador único por execução deixa de ser recomendação e vira requisito.

## Princípios

### 1. Cada teste é dono da própria massa

Teste que depende de dado preexistente é frágil: quando o teste A altera o registro compartilhado, o teste B quebra — e quebra de forma intermitente, o que é pior, porque some quando você investiga. Cada teste cria exatamente o que precisa, verifica contra o que criou e limpa depois. É isso que permite paralelismo e elimina dependência de ordem.

### 2. Fábrica para dado com ciclo de vida, fixture para dado de referência

Arquivo estático (JSON, YAML, `.resource`) serve para dado que não muda: lista de países, moedas, tabela de configuração, resposta mockada de API, arquivo de comparação. Para entidade que o teste cria e altera — usuário, pedido, produto —, use **função de fábrica** com valores padrão sensatos e sobrescrita por teste.

**Regra de decisão:** se o dado tem ciclo de vida (criado, alterado, apagado durante o teste), é fábrica. Se é material de referência só de leitura, é fixture.

### 3. Nunca leve dado de produção para outro ambiente sem anonimizar

O banco de produção tem a massa mais realista que existe — e também dado pessoal de gente real. Copiá-lo para homologação viola LGPD (e GDPR, quando houver usuário na Europa), espalha risco para um ambiente menos protegido e cria passivo jurídico. Substitua o dado pessoal por equivalente sintético preservando o formato e a distribuição.

### 4. Massa determinística

O teste precisa dar o mesmo resultado independentemente de quando e onde roda. ❌ Nunca use `Math.random()` sem semente, `Date.now()` ou `Get Current Date` dentro de uma asserção. Use gerador com semente fixa, data fixa e sequência de fábrica.

### 5. Massa mínima, sinal máximo

Um teste de busca de usuário não precisa de perfil completo com endereço de cobrança, meio de pagamento e histórico de pedidos. ❌ Massa superespecificada esconde a intenção do teste e aumenta o custo de manutenção. A fábrica traz o padrão; o teste sobrescreve só o campo que ele investiga.

## Fábricas

A forma que toda fábrica segue, independentemente da linguagem:

- **Padrões mais sobrescrita** — a fábrica devolve um objeto completo e válido; o teste passa só o campo que importa para o cenário (`criarUsuario({ perfil: 'admin' })`).
- **Sequência para campo único** — e-mail, documento e código nunca são fixos. Um contador ou sufixo por execução evita colisão em paralelo.
- **Variantes nomeadas** — em vez de um arquivo por combinação, dê nome aos estados recorrentes: `admin`, `inativo`, `semEstoque`, `comDesconto`.
- **Associação** — a fábrica de pedido constrói o usuário dele. Assim a estrutura referencial sai correta sem fiação manual em cada teste.

O esqueleto para Cypress e Playwright está em `templates/fabrica-dados.js`; o equivalente em Robot Framework, com keywords de criação e limpeza, está em `templates/massa_template.resource`. Adapte ao `ui.language` do perfil (TypeScript quando for o caso).

### Fábrica ou fixture?

| Situação | Fábrica | Fixture estática |
|---|---|---|
| Entidade que o teste cria ou altera | sim | não |
| Dado de referência (países, moedas, configuração) | não | sim |
| Muitas variações por teste | sim | não — vira explosão de arquivos |
| Relações complexas entre entidades | sim, por associação | não — difícil de manter |
| Resposta mockada de API | não | sim |
| Arquivo de comparação (snapshot) | não | sim |

## Semeadura do banco

Um script de semeadura precisa ser seguro para rodar mais de uma vez sem duplicar dado. Use inserção com resolução de conflito (`INSERT ... ON CONFLICT (chave_natural) DO UPDATE ...`) ancorada numa **chave natural** — código do país, sigla da moeda —, nunca na chave primária.

❌ Apagar tudo e inserir de novo não é idempotente: quebra chave estrangeira e reatribui identificadores sequenciais, então o teste que guardou um ID passa a apontar para outro registro.

| Estratégia | Quando usar | Vantagem | Custo |
|---|---|---|---|
| Setup e teardown por teste | Testes que alteram dado | Isolamento total, seguro em paralelo | Mais lento, mais código |
| Semeadura por suíte | Dado de referência só de leitura | Rápido e simples | Não pode ser alterado pelos testes |
| Semeadura por processo paralelo | Execução paralela com massa por trabalhador | Equilíbrio entre velocidade e isolamento | Exige fixture com escopo de trabalhador |
| Semeadura global | Preparação do ambiente | Roda uma vez | Precisa ser idempotente; estado compartilhado é risco |

## Limpeza

| Estratégia | Quando usar | Velocidade |
|---|---|---|
| **Rollback de transação** | Teste com acesso direto ao banco | mais rápida |
| **Truncate em cascata** | Reset de tabelas entre suítes | intermediária |
| **Limpeza por API** | Teste de ponta a ponta sem acesso ao banco | mais lenta |

Rollback de transação **não** limpa teste de ponta a ponta: a aplicação abre as próprias conexões, e a transação do lado do teste não desfaz a escrita feita pela aplicação. Nesses casos, apague pela API, na ordem inversa da criação.

A limpeza vai no bloco pós-uso da fixture, que roda mesmo quando o teste falha — nunca só num passo final que a falha pula.

## Anonimização

Quando o time precisar de massa realista vinda de produção, aplique a substituição antes de qualquer cópia sair do ambiente de origem.

| Tipo de dado | Substituição | Exemplo |
|---|---|---|
| E-mail | Gerado, mantendo o padrão de domínio | `joana.silva@empresa.com.br` → `usuario-7291@teste.exemplo.com` |
| Nome completo | Gerado | `Joana Silva` → `Alice Martins` |
| Telefone | Gerado, formato preservado | `+55 11 91234-5678` → `+55 11 99876-5432` |
| Endereço | Gerado, mantendo cidade e estado | `Rua A, 123, São Paulo` → `Rua B, 456, São Paulo` |
| CPF / documento | Padrão reservado a teste | usar faixa de teste, nunca documento real |
| Cartão | Cartão de teste do provedor | nunca número real |
| Data de nascimento | Deslocada por um mesmo intervalo fixo | `1990-03-15` → `1987-07-22` |

Cuidados que fazem a diferença entre anonimizar e parecer que anonimizou:

- Use gerador **com semente fixa** e uma tabela de correspondência em memória, para que o mesmo e-mail vire sempre o mesmo substituto dentro daquela execução — senão a integridade referencial quebra.
- Processe **primeiro os registros pais, depois os filhos**, dentro de **uma transação**: anonimizar o e-mail do usuário exige atualizar o mesmo e-mail em pedidos, comentários e trilha de auditoria.
- ❌ Nunca guarde a tabela de correspondência depois do processo. Se ela sobrevive, a anonimização é reversível e não vale nada.
- Verifique se o dado não pode ser reidentificado pela combinação de campos que sobraram (CEP + data de nascimento + gênero costuma bastar).
- A política de retenção do ambiente de teste também se aplica: massa anonimizada não fica lá para sempre.

## Massa de borda

A fábrica deve facilitar gerar caso de borda sem escrevê-lo à mão em cada teste. Mantenha listas reutilizáveis:

- **Textos**: vazio, só espaços, muito longo, com acento e cedilha, com emoji, com tentativa de injeção (`<script>`, `' OR 1=1`), com caractere de controle, com inversão de direção.
- **Datas**: início e fim de mês, ano bissexto, virada de ano, data futura, data muito antiga, fuso diferente.
- **Números**: mínimo, mínimo−1, máximo, máximo+1, zero, negativo, com muitas casas decimais.

São eles que alimentam a análise de valor limite da Fase 1 (`skills/analise-documentacao-testes`) quando ela vira teste automatizado.

## Erros comuns

- ❌ **Dado compartilhado e mutável.** Vários testes lendo e escrevendo as mesmas linhas. O teste A cria o usuário, o B altera, o C afirma sobre o estado original e falha — só às vezes. Cada teste cria o seu.
- ❌ **Dado de produção sem anonimização.** Copiar o banco para homologação "para testar com dado realista". Nunca faça isso: é violação de LGPD e risco de vazamento num ambiente menos protegido.
- ❌ **Massa não determinística.** Valor sorteado sem semente ou data corrente dentro da asserção. O teste passa na segunda e falha na terça porque o nome gerado estourou o limite do campo.
- ❌ **Sem estratégia de limpeza.** Toda criação de dado precisa de uma remoção correspondente. Sem isso, o banco de teste cresce até afetar o desempenho e a massa velha gera falso positivo.
- ❌ **Explosão de arquivos de fixture.** `usuario-admin.json`, `usuario-inativo.json`, `usuario-admin-inativo.json`. Evite: use uma fábrica com variantes nomeadas.
- ❌ **Identificador fixo no teste.** `id: 1` acopla o teste ao estado do banco e colide em paralelo. Use sequência de fábrica ou identificador gerado com semente.
- ❌ **Credencial dentro do arquivo de massa.** Usuário e senha nunca são literais no repositório; eles vêm das variáveis de ambiente declaradas em `api.user_env` e `api.password_env`.

## Pronto quando

- Toda entidade que a suíte cria tem fábrica ou fixture — nenhum objeto montado à mão dentro do corpo do teste para entidade compartilhada.
- A massa é isolada por teste: a suíte passa com paralelismo ligado **e** com ordem embaralhada, e a saída real das duas execuções foi mostrada.
- O script de semeadura é idempotente: rodar duas vezes seguidas produz a mesma contagem de registros e termina sem erro.
- Nenhum dado pessoal real existe na massa de teste — e-mail, documento e telefone conferidos, com o resultado da verificação registrado.
- Nenhuma credencial aparece literal em arquivo de massa; todas vêm das variáveis declaradas no perfil.
- A limpeza devolve o ambiente à linha de base: a contagem de registros antes e depois da suíte é a mesma, sem órfãos.
- As listas de massa de borda existem e estão ligadas aos cenários de valor limite levantados na Fase 1.

## Skills relacionadas

- **`robot-framework-api`, `cypress-ui-automation`, `playwright-ui-automation`** — consomem esta camada. O formato concreto da fábrica segue as convenções da skill do framework escolhido no perfil.
- **`confiabilidade-testes`** — dependência de dado e de ordem é uma das categorias de causa raiz de lá; a correção é o que esta skill descreve.
- **`revisao-qualidade-testes`** — os maus cheiros de setup obscuro, fixture gigante e massa genérica apontam para cá.
- **`analise-documentacao-testes`** — a análise de valor limite da Fase 1 define quais casos de borda a massa precisa cobrir.
- **`reproducao-bugs`** — a reprodução determinística depende de massa fixa; as fábricas daqui são o que a torna repetível.
