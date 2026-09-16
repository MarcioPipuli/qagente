# Regressão — [release / versão]

Release: [identificador exato — tag, versão, número de build]
Ambiente: [nome e URL do ambiente onde a suíte rodou]
Data e hora: [AAAA-MM-DD HH:MM]
Framework(s): [api.framework / ui.framework]
Janela disponível: [horas] — execução [sequencial | paralela]
Smoke desta build: **[GO — relatório em <caminho> | NÃO EXECUTADO — a regressão não deveria ter começado]**
Contexto do projeto disponível: [sim — áreas de risco alimentaram a entrada 2 | não — seleção cega para impacto, ver Ressalvas]

> Sem veredito GO do smoke na mesma build e no mesmo ambiente, este relatório não vale: as falhas abaixo podem ser todas a mesma causa raiz de ambiente.

## Casos selecionados

| Caso | Rastreio | Camada | Entrada que puxou | Detalhe da justificativa | Resultado |
|---|---|---|---|---|---|
| | `@CT-01` | `[API]` / `[INTERFACE]` | [1 mudança / 2 área de risco / 3 histórico / 4 prioridade] | [qual arquivo mudou, qual área, qual defeito anterior, qual nível] | [verde / vermelho] |

> A prioridade da entrada 4 é **lida** da coluna `Prioridade` do índice de cenários pelo rastreio. Sem documento de cenários, registre em Ressalvas — nunca arbitre uma.

> Nunca deixe a coluna vazia: caso sem entrada declarada não é seleção, é intuição com formatação. Toda linha tem uma das quatro.

## Fora da seleção

| Caso | Por que ficou de fora | Risco assumido |
|---|---|---|

> Se nada ficou de fora, escreva aqui por que a suíte inteira coube. Tabela vazia sem explicação lê-se como esquecimento.

## Evidência de execução

```
[saída real da execução — colada, não descrita]
```

| | Valor |
|---|---|
| Casos executados | |
| Verdes | |
| Vermelhos | |
| Duração total | |

## Defeitos encontrados

Uma linha por falha que é defeito do produto. A correção **não** entra aqui: esta skill não altera código de aplicação.

| Caso | O que falhou | Relato de reprodução | Área de risco atingida |
|---|---|---|---|
| | | [caminho do relato em reproducao-bugs] | |

## Falhas por instabilidade

Separadas de propósito: não entram na contagem de defeitos da release.

| Caso | Sinal de instabilidade | Encaminhado para |
|---|---|---|
| | [passa na repetição / falha só em paralelo / correlaciona com serviço externo] | confiabilidade-testes |

## Achados para a Fase 1

Prioridade que parece errada não é redecidida aqui — vira achado.

| Caso | Prioridade vigente | O que a regressão sugere | Por quê |
|---|---|---|---|

## Ressalvas

- [diferença relevante entre o ambiente de teste e o de produção]
- [fluxo relevante sem caso de teste escrito — lacuna para a Fase 2]
- [áreas de risco ausentes ou desatualizadas no contexto do projeto]

## Recomendação

[A release pode seguir. | A release não deve seguir: <defeitos bloqueantes>.]
