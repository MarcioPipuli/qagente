# Smoke Test — [build / versão]

Veredito: **[GO | NO-GO]**

Build/versão: [identificador exato — tag, commit, número de build]
Ambiente: [nome e URL do ambiente onde a suíte rodou]
Data e hora: [AAAA-MM-DD HH:MM]
Framework(s): [api.framework / ui.framework]
Contexto do projeto disponível: [sim — fluxos críticos vieram da tabela de áreas de risco | não — seleção proposta como palpite, ver Lacunas]

> Veredito sem build e ambiente identificados não autoriza nada: "passou" não diz onde.

## Duração

| | Valor |
|---|---|
| Teto efetivo (`conventions.smoke_max_minutes`) | [valor do perfil] min |
| Duração medida | [valor] min |
| Situação | [dentro do teto | estourou — ver Cortes propostos] |

## Casos da suíte

| Caso | Rastreio | Tipo (do índice de cenários) | Camada | Fluxo crítico coberto | O que fica inválido se falhar | Resultado |
|---|---|---|---|---|---|---|
| | `@CT-01` | Caminho feliz | `[API]` / `[INTERFACE]` | | | [verde / vermelho] |

> A coluna `Tipo` é **lida** do índice do documento de cenários pelo rastreio, nunca decidida aqui. Valor diferente de `Caminho feliz` não entra no smoke.

> Caso cuja coluna "o que fica inválido" for "nada em especial" não é smoke — é regressão, e sai da suíte.

## Evidência de execução

```
[saída real da execução — colada, não descrita]
```

## Classificação das falhas

Preencher só quando o veredito for NO-GO. Uma linha por caso vermelho.

| Caso | Leitura | Sinal que levou à classificação | Encaminhado para |
|---|---|---|---|
| | [defeito no build / ambiente quebrado / teste instável] | | [reproducao-bugs / correção de ambiente / confiabilidade-testes] |

> Repetir a execução até passar não é uma das leituras. Smoke que precisou de três tentativas é NO-GO com problema de confiabilidade em cima.

## Cortes propostos

Preencher só quando a duração estourar o teto. A correção é cortar casos, nunca aumentar o teto.

| Caso | Por que sai | Cobertura que fica descoberta |
|---|---|---|

## Lacunas

- [fluxo crítico sem caso de teste escrito — a Fase 2 é quem preenche]
- [caso retirado por instabilidade e a cobertura que ele deixou em aberto]
- [tabela de áreas de risco ausente ou desatualizada no contexto do projeto]

## Decisão

[GO — a regressão pode começar. | NO-GO — a regressão está bloqueada até o veredito virar GO.]
