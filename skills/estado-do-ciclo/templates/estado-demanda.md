# Estado — [nome-base do documento de origem]

Origem: [caminho do documento de entrada] · lido em [AAAA-MM-DD]
Gate atual: **[G0 | G1 | G2 | G3 | G4 | G5]** — [nome do gate]
Falta para o próximo: [o que precisa acontecer, em uma linha]
Reconciliado com o disco em: [AAAA-MM-DD HH:MM] — [tudo conferido | divergências abaixo]

> Registro não conferido contra o disco não vale: ele afirma com autoridade um estado que pode
> não existir mais. Reconcilie antes de usar.

## Artefatos

Um por gate fechado. O caminho é conferido em disco, não copiado deste template.

| Gate | Artefato | Caminho | Data | Confere em disco? |
|---|---|---|---|---|
| G2 | Cenários | `saida/cenarios/[nome].cenarios.md` | | [sim / NÃO — ver Divergências] |
| G3 | Casos de teste | `saida/casos-de-teste/[nome].casos.md` | | |
| G4 | Automação | `saida/testes-api/` ou `saida/testes-ui/` | | |
| G5 | Veredito de smoke | | | |

## Aprovações

**Toda linha carrega a fala literal do usuário.** Coluna vazia significa que não houve aprovação
— e é para ela ficar visível que a linha existe mesmo vazia.

| Gate | Fala do usuário, literal | Data |
|---|---|---|
| G2 | "[transcreva exatamente o que o usuário disse]" | |
| G3 | | |

> O agente nunca preenche esta tabela por dedução, por alta confiança, ou por interpretar
> silêncio. Aprovação sem fala citada é entrada inválida.
>
> **G3 é reconfirmado a cada sessão, mesmo preenchido aqui.** Esta linha serve para não repetir
> a Fase 2; não serve para iniciar a automação sem perguntar.

## Divergências encontradas na reconciliação

| O registro dizia | O disco diz | Perguntado ao usuário? |
|---|---|---|

> Divergência nunca é resolvida em silêncio. O disco vence quando há artefato mais novo;
> quando falta artefato de um gate dito aprovado, a saída é perguntar — nunca regerar.

## Lacunas abertas

Herdadas da Fase 1 e ainda sem resposta. Lacuna já respondida no contexto do projeto sai daqui.

- [pergunta que o requisito não respondeu]

## Hipóteses assumidas e não confirmadas

- [o que foi assumido para seguir, e o que muda se estiver errado]

## Histórico

| Data | Gate | O que aconteceu |
|---|---|---|
