---
name: regressao
description: Seleciona e executa a suíte de regressão de uma release por impacto de mudança e risco, com o critério de entrada registrado caso a caso e o que ficou de fora declarado com o risco assumido. Use quando o usuário precisar decidir o que rodar antes de liberar uma versão, justificar a seleção feita, montar a suíte de regressão a partir dos casos existentes, ou quando a suíte completa deixou de caber na janela de release. Não use para o portão de build antes da bateria (use smoke-test), para escrever casos novos (use casos-de-teste) nem para construir a matriz de risco do produto (use priorizacao-por-risco).
license: CC-BY-4.0
metadata:
  author: QAGente
  version: '1.0.0'
  category: automacao
---

# Regressão

<objetivo>
Impede os dois extremos que todo time alterna quando a suíte cresce: **rodar tudo sempre** — que funciona até a suíte não caber mais na janela e ser abandonada no primeiro prazo apertado, sem ninguém decidir isso — e **escolher na véspera por intuição**, que é como a regressão de uma área crítica fica de fora e o incidente aparece três dias depois do deploy. Entrega um conjunto selecionado por critério derivado da mudança e do risco, com a justificativa de cada caso que entrou, a lista explícita do que ficou de fora com o risco assumido, e a execução real.
</objetivo>

Esta é uma skill de apoio, aplicada a testes que já existem — normalmente os produzidos pelas
Fases 3a e 3b. Ela não escreve casos novos nem redecide prioridade: seleciona entre o que já
existe, usando decisões que já foram tomadas.

## Configuração

Leia `.qagente/quality-profile.json` na raiz do projeto antes de começar. Quando um campo
existir no perfil, ele vence os valores desta skill. Precedência: **instrução explícita do
usuário → perfil do projeto → defaults desta skill**.

Leia também `.qagente/contexto-projeto.md`, quando existir. Dele saem as **áreas de risco com
impacto de negócio**, que são a segunda das quatro entradas da seleção (Passo 1). Sem elas, a
seleção fica reduzida ao diff — ou seja, cobre o que mudou e ignora o que é caro quebrar mesmo
sem ter mudado. Se o arquivo não existir, diga explicitamente que a seleção está cega para
impacto e o que mudaria com ele preenchido.

| Decisão desta skill | Campo do perfil | Default |
|---|---|---|
| Idioma do relatório | `language` | idioma da conversa |
| Escala de prioridade herdada | `risk_levels` | `critical`, `high`, `medium`, `low` |
| Onde estão os testes | `paths.api_tests`, `paths.ui_tests` | `saida/testes-api/`, `saida/testes-ui/` |
| Onde estão os casos de origem | `paths.test_cases` | `saida/casos-de-teste/` |
| Onde salvar o relatório | `paths.regression_results`, senão `paths.reviews`, senão `paths.test_cases` | `saida/regressao/` |
| Framework de API e de UI | `api.framework`, `ui.framework` | Robot Framework, Cypress |

Os dois níveis mais altos de `risk_levels` entram na seleção sempre, por default — e esse
"sempre" é o único automatismo da skill. Todo o resto é justificado caso a caso.

As regras universais de `AGENTS.md` valem sempre. Três mandam aqui: **evidência real de
execução**, **rastreabilidade** — cada caso selecionado aponta para o que o puxou — e a
fronteira de que este agente **não altera código de aplicação**: defeito encontrado é achado
a relatar, nunca conserto aplicado de passagem.

## Perguntas de descoberta

Leia o perfil e o contexto primeiro, e pule tudo que eles já responderem. Depois pergunte só
o que faltar:

- **O que entrou nesta release?** Diff, changelog, lista de pull requests ou de tickets. Sem isso a primeira das quatro entradas não existe e a seleção começa manca.
- **Qual é a janela disponível?** Horas até o deploy, e se a execução é paralela. Decide se a seleção precisa cortar ou se a suíte inteira cabe.
- **O smoke já rodou nesta build?** Se não rodou, ou reprovou, esta skill não começa — ver Passo 3.
- **Houve incidente em produção desde a última release?** Área que quebrou volta para a seleção mesmo sem mudança nesta.
- **A suíte roda em ambiente igual ao de produção?** Diferença relevante vira ressalva no relatório, não nota de rodapé.
- **Existe seleção de regressão hoje?** Se existe, o trabalho pode ser auditar o critério dela, não montar do zero.

## Passo 1 — As quatro entradas da seleção

A seleção é **derivada**, nunca opinada. Quatro entradas, aplicadas nesta ordem. Cada caso que
entra na suíte carrega qual delas o puxou — é isso que separa uma seleção de uma lista.

1. **O que mudou na release.** O diff, o changelog, os tickets fechados. Caso que cobre código tocado entra, sempre, sem discussão de prioridade. Esta entrada é objetiva e é a única que não depende de julgamento.
2. **Áreas de risco do contexto do projeto.** Caso que toca área de impacto alto entra **mesmo sem mudança nesta release**, porque o custo de errar ali foi declarado pelo time. É a entrada que cobre o efeito colateral: o módulo que ninguém mexeu e que quebrou porque uma dependência mudou embaixo dele.
3. **Histórico de defeito.** Módulo que já quebrou volta a ser coberto. A origem são os testes de regressão que `skills/reproducao-bugs` deixou junto de cada relato — eles existem exatamente para isto, e a regressão é o momento em que são cobrados.
4. **Prioridade herdada.** A coluna que `skills/priorizacao-por-risco` e a Fase 1 já preencheram. Os dois níveis mais altos de `risk_levels` entram por default.

> **Esta skill não redecide prioridade.** Pelo mesmo motivo que a Fase 2 não redecide
> granularidade: a decisão já foi tomada com mais informação e mais tempo do que a véspera de
> uma release tem. Se durante a seleção aparecer um caso cuja prioridade parece errada, isso é
> análise, e o lugar dela é a Fase 1 — registre como achado e siga com a prioridade vigente.

## Passo 2 — Declarar o que ficou de fora

A metade que os times pulam, e a que decide se a seleção serve para alguma coisa.

Uma lista do que entrou responde "o que vamos rodar". Só a lista do que **não** entrou responde
a pergunta que o responsável pela release precisa responder de verdade:
**o que estamos aceitando não saber?**
Sem ela, escopo e omissão ficam indistinguíveis — e a diferença entre os dois é justamente
alguém ter decidido.

Cada caso fora da seleção entra numa tabela com o risco assumido em uma linha:

| Caso | Por que ficou de fora | Risco assumido |
|---|---|---|
| CT-32 | Área não tocada, prioridade baixa | Falha em relatório mensal passaria despercebida até o fechamento |

Quando a suíte inteira cabe na janela e nada fica de fora, diga isso explicitamente. Tabela
vazia sem explicação lê-se como esquecimento.

## Passo 3 — O smoke vem antes

A regressão só começa com veredito GO de `skills/smoke-test` na mesma build e no mesmo
ambiente.

Não é hierarquia burocrática: regressão sobre build reprovado gasta a janela inteira
depurando ambiente e produz um relatório de dezenas de falhas em cascata, todas com a mesma
causa raiz, que alguém vai levar horas para reconciliar. O portão existe para que o vermelho
da regressão signifique alguma coisa.

❌ Nunca comece a regressão com smoke vermelho ou não executado porque "não deu tempo". O
tempo que se ganha pulando o portão é o mesmo que se perde triando falhas em cascata,
com a diferença de que agora a janela já foi consumida.

## Passo 4 — Executar e relatar

A suíte selecionada é executada com o framework do perfil, e a saída real vai na entrega —
princípio 6 de `AGENTS.md`.

Registre em `templates/relatorio-regressao.md`: release e ambiente identificados, a tabela de
casos com o critério de entrada de cada um, a tabela do que ficou de fora com o risco assumido,
a evidência de execução e os defeitos encontrados.

**Defeito encontrado vira relato, não conserto.** Esta skill não altera código de aplicação —
é fronteira de `AGENTS.md`, e vale mesmo quando a correção parece óbvia e a release está
apertada. Cada falha vai para `skills/reproducao-bugs`: reproduzir, isolar, registrar. O
relatório da regressão cita o relato, não a correção.

Falha que se revele instabilidade do teste, e não defeito do produto, vai para
`skills/confiabilidade-testes` e **não entra na contagem de defeitos da release**.
Contar oscilação como defeito polui a métrica e faz o time perseguir o problema errado.

## Erros comuns

- ❌ **"Rodar tudo" como estratégia.** Funciona até não caber, e aí é abandonado sem decisão. Se a suíte inteira cabe na janela, ótimo — mas a seleção continua sendo declarada, porque no trimestre que vem ela não vai caber.
- ❌ **Selecionar na véspera, sem critério registrado.** Seleção que ninguém consegue reconstruir depois não pode ser auditada quando o incidente acontecer, e a lição do incidente se perde.
- ❌ **Omitir o que ficou de fora.** Sem essa tabela, o responsável pela release não tem como decidir nada — está aprovando o que não sabe que não sabe.
- ❌ **Selecionar só pelo diff.** Cobre o que mudou e ignora o que é caro quebrar. O efeito colateral em módulo intocado é exatamente o que a entrada 2 existe para pegar.
- ❌ **Redecidir prioridade durante a seleção.** A véspera da release é o pior momento e o pior contexto para refazer análise de risco. Registre o achado e devolva à Fase 1.
- ❌ **Corrigir o código de aplicação ao achar defeito.** Fronteira de `AGENTS.md`, sem exceção de prazo.
- ❌ **Contar teste instável como defeito da release.** Polui a métrica e esconde a saúde real da suíte.
- ❌ **Declarar a regressão concluída sem a saída real.** Vale aqui o mesmo que em toda automação do harness.

## Pronto quando

- Cada caso selecionado tem, na tabela, qual das quatro entradas do Passo 1 o puxou — nenhum entrou sem justificativa.
- A tabela do que ficou de fora existe, com o risco assumido de cada item, ou o relatório diz explicitamente que nada ficou de fora e por quê.
- O smoke desta build e deste ambiente está com veredito GO, citado no relatório.
- As áreas de risco vieram de `.qagente/contexto-projeto.md`, ou o relatório declara que a seleção está cega para impacto e o que mudaria com o arquivo preenchido.
- Nenhuma prioridade foi redecidida aqui; divergências viraram achado para a Fase 1.
- A execução aconteceu de verdade e a saída real foi mostrada ao usuário.
- Cada defeito encontrado virou relato encaminhado, e nenhum código de aplicação foi alterado.
- Falhas por instabilidade estão separadas da contagem de defeitos da release.

## Skills relacionadas

- **`smoke-test`** — o portão que precede esta skill. GO de lá é pré-condição daqui, na mesma build e no mesmo ambiente. A classificação de cada caso como smoke, regressão, ambos ou nenhum é decidida em conjunto pelas duas.
- **`priorizacao-por-risco`** — dona da matriz de risco que alimenta a entrada 4 e da tabela de áreas de risco quando o contexto do projeto precisa ser construído ou recalibrado após um incidente.
- **`reproducao-bugs`** — para onde vai todo defeito que a regressão encontrar, e de onde vêm os testes de regressão que a entrada 3 cobra.
- **`confiabilidade-testes`** — dona das falhas que se revelarem instabilidade do teste, que saem da contagem de defeitos da release.
- **`casos-de-teste`** — de onde vêm os casos que esta skill seleciona. Fluxo relevante sem caso escrito é lacuna a registrar; preenchê-la é trabalho da Fase 2.
- **`revisao-qualidade-testes`** — quando a regressão expõe que a suíte é grande mas rasa, o diagnóstico de qualidade é lá.
