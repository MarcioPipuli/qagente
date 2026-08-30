# Registro de Quarentena e Confiabilidade — [suíte / escopo]

Taxa de oscilação antes: [%] (janela: últimos 30 dias)
Taxa de oscilação depois: [%]
Média de estabilidade dos seletores: [nota] (meta: ≥ 3,5)

## Testes em quarentena

| Teste | Arquivo | Categoria de causa raiz | Sinal observado | Ticket | Entrada | Expira em | Responsável |
|---|---|---|---|---|---|---|---|
| | | tempo / dado / ambiente / ordem / data / visual / serviço externo | | | AAAA-MM-DD | AAAA-MM-DD (máx. 14 dias) | |

> Nunca existe entrada sem ticket, e nunca existe entrada sem data de expiração.
> Mais de 5% da suíte aqui dentro é problema de processo, não de teste.

## Testes classificados e corrigidos

| Teste | Categoria | Correção aplicada | Execuções repetidas | Falhas | Evidência |
|---|---|---|---|---|---|
| | tempo | espera pela resposta interceptada no lugar de espera fixa | 50 | 0 | [saída real] |

## Pontuação de estabilidade dos seletores

| Arquivo | Seletor | Estratégia | Nota (0-5) | Ação |
|---|---|---|---|---|
| | | atributo dedicado de teste | 5 | manter |
| | | XPath posicional | 0 | substituir — prioridade |

Média da suíte: [nota]
Seletores nota 0 ou 1: [quantidade] — são a fila de refatoração

## Trocas de seletor aplicadas (evidência obrigatória)

| Teste | Seletor original | Candidatos considerados | Escolhido | Tipo/papel/destino mantidos? | Aprovado por |
|---|---|---|---|---|---|
| | | 1) …  2) …  3) … | | sim / não → revertida | |

> Troca com intenção não preservada (tipo de elemento, papel de acessibilidade ou destino da
> ação diferentes) é sempre revertida, mesmo que o teste fique verde.

## Liberações da quarentena

| Teste | Causa raiz confirmada | Correção | Data de saída | 50 execuções verdes? |
|---|---|---|---|---|
| | | | | sim / não |

## Itens que passaram do prazo

| Teste | Dias em quarentena | Decisão | Justificativa |
|---|---|---|---|
| | | corrigir agora / apagar | |
