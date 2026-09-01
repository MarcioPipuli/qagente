---
name: confiabilidade-testes
description: Classifica testes que oscilam por causa raiz (tempo, dado, ambiente, ordem, data, renderização, serviço externo), pontua a estabilidade dos seletores, aplica a correção correspondente a cada categoria e gerencia quarentena com prazo e ticket. Use quando o usuário disser que um teste falha de forma intermitente, que a suíte não é confiável, que estão repetindo execução até passar, ou pedir para estabilizar, pontuar seletores ou colocar teste em quarentena. Não use para reproduzir um bug de produto a partir de um relato (use reproducao-bugs) nem para revisar a qualidade geral de uma suíte verde (use revisao-qualidade-testes).
license: MIT
metadata:
  author: QAGente
  version: '1.0.0'
  category: automacao
  adaptado_de: 'qa-skills/test-reliability — Petr Kindlmann, MIT'
---

# Confiabilidade de Testes

<objetivo>
Impede as duas saídas fáceis diante de um teste instável, que são as duas que custam caro depois: repetir a execução até passar — o teste que precisa de 2 de 3 acaba falhando 3 de 3 no release mais crítico — e trocar o seletor em silêncio, deixando o teste verde verificando outro elemento sem ninguém perceber. No lugar delas, obriga a **classificar a causa raiz antes de corrigir**, porque a correção de um problema de tempo não tem nada a ver com a de uma dependência de dado, e obriga toda estabilização a deixar evidência revisável. Entrega a categoria de causa raiz de cada teste que oscila, a correção aplicada, a pontuação de estabilidade dos seletores e uma quarentena com prazo.
</objetivo>

Esta é uma skill de apoio, aplicada a testes que já existem — normalmente os produzidos pelas Fases 3a e 3b.

## Configuração

Leia `.qagente/quality-profile.json` na raiz do projeto antes de começar. Quando um campo
existir no perfil, ele vence os valores desta skill. Precedência: **instrução explícita do
usuário → perfil do projeto → defaults desta skill**.

Leia também `.qagente/contexto-projeto.md`, quando existir. Dele saem os ambientes de
execução do time e as áreas de risco — que decidem se um teste que oscila entra em quarentena
ou vira prioridade de correção imediata. Um teste instável que cobre área crítica não vai para
a quarentena e espera; ele é corrigido primeiro.

| Decisão desta skill | Campo do perfil | Default |
|---|---|---|
| Idioma do relatório | `language` | idioma da conversa |
| Framework de UI e seus seletores | `ui.framework`, `ui.selector_attribute` | Cypress, `data-testid` |
| Framework de API | `api.framework` | Robot Framework |
| Onde estão os testes | `paths.ui_tests`, `paths.api_tests` | `saida/testes-ui/`, `saida/testes-api/` |
| Onde salvar o relatório e o registro de quarentena | `paths.reviews`, senão `paths.test_cases` | `saida/confiabilidade/` |
| Execuções para dar uma correção como verificada | `conventions.stability_runs` | `50` |
| Prazo máximo de quarentena | `conventions.quarantine_max_days` | `14` dias |

Os dois números acima são política do time, não constante: escreva no relatório e no registro
de quarentena o valor **efetivo** do perfil, nunca o default citado nos exemplos desta skill.
E `stability_runs` é prova de correção — não é a contagem da reprodução de defeito nem a
amostragem da revisão de suíte; ver `AGENTS.md`, "Perfil de qualidade do time".

As regras universais de `AGENTS.md` valem sempre. Duas mandam aqui: **independência e
determinismo dos testes** — que é literalmente o assunto desta skill — e **evidência real de
execução**: nenhuma correção é dada como boa sem a saída das execuções repetidas.

## Perguntas de descoberta

Leia o perfil e o contexto primeiro. Depois pergunte só o que faltar:

- **Qual é a taxa atual de oscilação?** Percentual de testes que passam na repetição, nos últimos 30 dias. Abaixo de 2% é saudável; de 2% a 5% pede atenção; acima de 5% a equipe já parou de confiar na suíte.
- **Onde a dor se concentra?** Seletor quebrando, tempo, massa, ambiente? Se não se sabe, instrumente antes de corrigir.
- **Qual é a estratégia de seletores hoje?** `data-testid` em tudo, mistura de CSS com papel, ou "o que funcionar"? Define a linha de base da pontuação.
- **Como o time trata teste instável hoje?** Repetir e torcer, pular e esquecer, ou algo estruturado? Decide quanto processo precisa entrar.
- **A integração contínua roda sempre na mesma máquina?** Recursos variáveis mudam o diagnóstico de ambiente.
- **Qual é a estratégia de massa de teste?** Banco compartilhado, massa por teste, fábrica? Decide se a cura de dado se aplica.

## Passo 1 — Classificar antes de corrigir

Todo teste que oscila tem uma categoria de causa raiz. Classificar errado desperdiça esforço e às vezes piora a situação.

| Categoria | Sinal | Causa raiz | Direção da correção |
|---|---|---|---|
| **Tempo** | Erro de timeout, passa na repetição, pior na integração contínua | Condição de corrida, animação, operação assíncrona | Esperar pela condição, nunca por tempo |
| **Dependência de dado** | Falha junto com os outros, passa sozinho | Estado compartilhado, limpeza ausente | Isolar por teste, limpar na própria fixture |
| **Ambiente** | Falha em uma máquina específica, correlaciona com carga | Disputa de recurso, latência de rede | Interceptar externos, aumentar recurso |
| **Dependência de ordem** | Falha com paralelismo ou execução embaralhada | Depende do efeito colateral de outro teste | Pré-condições próprias e completas |
| **Sensibilidade a data** | Falha em horários específicos (meia-noite, virada de mês) | Usa o relógio real, cruza limite de data | Congelar o relógio, comparar de forma relativa |
| **Renderização visual** | Diferença de captura oscila, subpixel | Fonte, antisserrilhamento, quadro de animação | Aumentar tolerância, mascarar região dinâmica |
| **Serviço externo** | Correlaciona com o status do terceiro | Chamada HTTP real dentro do teste | Interceptar a API externa |

### Árvore de decisão

```
Teste oscila
│
├── Passa quando roda sozinho?
│   ├── SIM → DEPENDÊNCIA DE ORDEM ou DE DADO
│   │   ├── Outro teste cria/altera o dado que ele usa? → ORDEM
│   │   └── Compartilha banco, arquivo ou cache? → DADO
│   └── NÃO → siga abaixo
│
├── Falha mais na integração contínua que no local?
│   ├── SIM → TEMPO ou AMBIENTE
│   │   ├── Erro de timeout? → TEMPO (a máquina de CI é mais lenta)
│   │   ├── Erro de conexão? → AMBIENTE (latência ou serviço fora)
│   │   └── Erro de recurso (memória, disco)? → AMBIENTE (disputa)
│   └── NÃO → siga abaixo
│
├── Falha em horários específicos?
│   ├── SIM → SENSIBILIDADE A DATA (virada de dia, de mês, fuso)
│   └── NÃO → siga abaixo
│
├── Envolve captura de tela ou comparação visual? → RENDERIZAÇÃO VISUAL
├── Chama API HTTP externa?                       → SERVIÇO EXTERNO
└── Nenhum acima → TEMPO (classificação padrão)
    └── Investigue: qual operação assíncrona não está sendo aguardada?
```

Antes de classificar, **reproduza a oscilação**: repita a execução do teste alvo muitas vezes num único ambiente (Playwright `--repeat-each=20`; Cypress, repetir o spec em laço; Robot Framework, repetir a suíte alvo). Se ele não falhar nenhuma vez, você ainda não tem o que corrigir — e nunca declare corrigido um teste cuja falha você nunca viu.

## Passo 2 — Pontuar a estabilidade dos seletores

Todo seletor recebe nota de 0 a 5. É o que transforma "nossos seletores são frágeis" em número que dá para acompanhar.

| Nota | Estratégia | Sobrevive a |
|---|---|---|
| 5 | Atributo dedicado de teste (`ui.selector_attribute`, por padrão `data-testid`) | Mudança de CSS, de texto e de estrutura |
| 4 | Papel + nome acessível (`getByRole`, `findByRole`, `role=` no Robot) | Mudança de CSS e de estrutura |
| 3 | Rótulo associado ao campo | Mudança de CSS; quebra se o rótulo for reescrito |
| 2 | Texto visível | Quebra a qualquer mudança de texto |
| 1 | Classe CSS (`.btn-primary.enviar`) | Quebra a qualquer mudança de CSS ou estrutura |
| 0 | XPath posicional (`//div[3]/button[1]`) | Quebra a qualquer mudança de DOM |

**Meta: média 3,5 ou mais na suíte.** Audite periodicamente e ataque primeiro as notas 0 e 1. Emita uma nota por seletor e a média da suíte num arquivo do relatório, para que a meta seja verificável em vez de afirmada.

Quando um seletor quebra, o elemento em geral ainda existe com atributos diferentes. Candidatos de substituição, em ordem de confiança: contêiner conhecido + tag e tipo dentro dele; rótulo vizinho + campo adjacente; texto próximo + tipo de elemento no mesmo pai. São **candidatos a revisar**, nunca substituições automáticas silenciosas.

## Passo 3 — Aplicar a correção da categoria

- **Tempo** — troque toda espera fixa por espera pela condição real: elemento visível, resposta interceptada com status esperado, estado atingido. ❌ Nunca use `cy.wait(3000)`, `waitForTimeout(5000)` ou o keyword `Sleep` do Robot Framework como correção de estabilidade; eles não sincronizam nada.
- **Dependência de dado e de ordem** — cada teste cria e destrói a própria massa. A limpeza vai na fixture (que garante execução mesmo em falha), nunca só num `afterEach` que pode não rodar. Ver `skills/dados-de-teste`.
- **Ambiente** — antes de culpar o teste, confirme a saúde do ambiente: se a aplicação ou a API responde muito acima do normal, a falha é de disputa de recurso e não deve contar como oscilação do teste. Registre o diagnóstico em vez de repetir a execução.
- **Sensibilidade a data** — congele o relógio (`cy.clock`, `page.clock.install`, data fixa nas variáveis do Robot) e compare de forma relativa.
- **Renderização visual** — mascare região dinâmica (data, avatar, contador) e ajuste a tolerância, em vez de aceitar a diferença.
- **Serviço externo** — intercepte na fronteira (`cy.intercept`, `page.route`, mock no Robot). Chamada real a terceiro dentro de teste automatizado é fonte permanente de oscilação.

### Cura de massa expirada

Massa de teste vence, é limpa ou fica inválida. Padrões comuns e a correção:

| Sintoma | Causa | Correção |
|---|---|---|
| 401 no meio do teste | Token de autenticação expirado | Regenerar na fixture antes de usar |
| 404 ao acessar registro semeado | Registro de teste apagado | Recriar antes do teste |
| 409 ou violação de restrição | Colisão de valor único | Gerar identificador único por execução |
| Dado errado retornado | Cache velho | Limpar cache no setup |
| 429 | Cota estourada | Conta de teste dedicada ou reset de cota |

A fixture verifica se a massa existe e está válida, recria se não estiver, **anota que curou** para ficar observável, e limpa no fim — sempre no bloco pós-uso da fixture, nunca fora dela.

## Passo 4 — Quarentena com prazo

Quarentena isola o teste instável: ele continua rodando, mas não bloqueia a integração contínua. Não é um lugar para o teste morar.

**Ciclo:**

1. **Detectar** — identificado como instável pelo relatório de CI ou por triagem.
2. **Marcar** — etiqueta de quarentena com link do ticket e data de entrada.
3. **Isolar** — projeto/execução separada, que não bloqueia o pipeline.
4. **Diagnosticar** — classificar pela árvore do Passo 1.
5. **Corrigir** — aplicar a correção da categoria.
6. **Verificar** — `conventions.stability_runs` execuções repetidas (50 execuções por default), zero falhas.
7. **Liberar** — remover a etiqueta e registrar no histórico qual era a causa e qual foi a correção.

**Regras de higiene:**

- **Prazo máximo de `conventions.quarantine_max_days`** — 14 dias por default. Depois disso, corrija ou apague. ❌ Quarentena permanente é apodrecimento com nome bonito.
- **Toda entrada tem ticket.** Nunca existe quarentena anônima.
- **Revisão semanal.** Entrada que envelhece é escalada.
- **Acompanhe o tamanho.** Mais de 5% da suíte em quarentena não é problema de teste, é problema de processo.

❌ Nunca use `test.skip('instável, corrijo depois')` nem o equivalente do framework: "depois" não chega, e teste pulado sem ticket é código morto que dá falsa sensação de cobertura.

Registre cada entrada em `templates/registro-quarentena.md`.

## Passo 5 — Toda correção deixa evidência

Quando a correção for automática ou semiautomática — em especial troca de seletor —, ela precisa produzir registro revisável: o que quebrou, quais candidatos foram considerados, qual foi escolhido, e por quê.

Antes de aceitar a troca, faça a **checagem de intenção**: o teste continua verificando a mesma coisa?

- Tipo de elemento mudou (botão virou link) → intenção **não** preservada, reverta.
- Papel de acessibilidade mudou → intenção **não** preservada, reverta.
- Destino da ação mudou (outro endpoint, outro formulário) → intenção **não** preservada, reverta.
- Mesma tag, mesmo papel, mesmo destino → intenção preservada, mantenha.

Uma correção que muda **o que** o teste verifica, e não apenas **como** ele encontra o elemento, é sempre revertida.

## Erros comuns

- ❌ **Troca silenciosa de seletor.** Substituir sem registro, sem revisão e sem checagem de intenção. O teste pode ter passado a verificar outro elemento e ninguém saberia.
- ❌ **"Só repete" como correção.** Repetição é mecanismo de detecção, nunca correção. Um teste que precisa de 2 de 3 vai falhar 3 de 3 exatamente no release que importa.
- ❌ **Desativar o teste instável para sempre.** Ou quarentena com prazo e ticket, ou apagar. Nunca a terceira via.
- ❌ **Tratar toda oscilação igual.** Adicionar espera fixa num problema de dependência de dado deixa a suíte mais lenta e igualmente instável.
- ❌ **Construir automação de cura antes de ter teste estável.** Comece por seletor resiliente e espera correta. Infraestrutura de cura automática só depois que os dados mostrarem onde a quebra acontece.
- ❌ **Contar falha de ambiente como oscilação do teste.** Isso polui a métrica e faz o time perseguir o problema errado.
- ❌ **Declarar corrigido sem repetir a execução.** Sem as 50 execuções verdes do perfil (`conventions.stability_runs`), você tem esperança, não evidência.

## Pronto quando

- Todo teste instável do escopo está classificado por causa raiz, com o sinal que levou à classificação registrado.
- Cada um foi corrigido ou colocado em quarentena — nenhum ficou sendo repetido em silêncio sem plano e sem ticket.
- A correção foi verificada com o número de execuções repetidas de `conventions.stability_runs` (50 execuções, zero falhas, por default) e a saída real foi mostrada ao usuário.
- O relatório lista uma nota de estabilidade por seletor e a média da suíte, com a meta de 3,5 explicitada e o resultado comparado a ela.
- Toda entrada de quarentena tem ticket e data de expiração dentro de `conventions.quarantine_max_days` (14 dias por default).
- Nenhuma troca de seletor foi aplicada sem registro de candidatos e sem checagem de intenção.
- A taxa de oscilação da suíte foi medida antes e depois, ou o relatório diz por que não foi possível medir.

## Skills relacionadas

- **`cypress-ui-automation`, `playwright-ui-automation`, `robot-framework-api`** — os padrões de espera, seletor e fixture que esta skill cobra vêm de lá. Aqui você corrige o que já existe; lá você escreve certo desde o começo.
- **`reproducao-bugs`** — quando a investigação mostra que a oscilação é bug real do produto, e não do teste, o caminho é lá: reproduzir, isolar e escrever o teste de regressão.
- **`dados-de-teste`** — a correção de dependência de dado e de ordem mora lá: fábricas, isolamento por teste e limpeza garantida.
- **`revisao-qualidade-testes`** — identifica os maus cheiros de confiabilidade numa revisão ampla; esta skill os classifica e corrige.
- **`priorizacao-por-risco`** — decide qual teste instável é corrigido agora e qual pode esperar na quarentena.
