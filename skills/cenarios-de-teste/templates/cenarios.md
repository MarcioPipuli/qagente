# Cenários de Teste — [Nome da Funcionalidade]
Origem: [ticket/PRD/seção — ou "descrição informal do usuário, sem documento associado"]

## Índice

| ID | Cenário | Tipo | Técnica | Prioridade |
|---|---|---|---|---|
| CT-01 | [resumo do cenário — caminho feliz] | Caminho feliz | — | [nível de risk_levels] |
| CT-02 | [resumo do cenário] | [Negativo / Regra de negócio / Estado / Borda] | [técnica aplicada] | [nível de risk_levels] |

<!-- Prioridade, tipo e técnica moram só aqui. Objetivo, escopo e resultados moram só no
     bloco do cenário. Campo repetido nos dois lugares diverge na primeira edição. -->

## CT-01 — [resumo do cenário]

**Objetivo:** [o que este cenário prova sobre o sistema, e por que importa. Cite a área de
risco de `.qagente/contexto-projeto.md` quando o cenário tocar uma.]

**Escopo de Validações:**
- [validação 1 — citando a regra de origem: RN01, CA01, seção do PRD]
- [validação 2 — citando a regra de origem]

**Resultados Esperados:**
- [resultado observável e específico — é ele que vira o `Então` do caso de teste]
- [resultado adicional, se houver]

## CT-02 — [resumo do cenário]

**Objetivo:** [...]

**Escopo de Validações:**
- [...]

**Resultados Esperados:**
- [...]

## Resumo dos Cenários

**Total de cenários:** [N]
**Por prioridade:** [Alta N · Média N · Baixa N — os níveis de `risk_levels`, no idioma de `language`]
**Por técnica:** [Particionamento N · Valor limite N · Tabela de decisão N · Transição de estados N · — N]
**Total de casos sugeridos:** [N]

### Casos sugeridos por cenário

**CT-01 — [resumo do cenário]**
1. [API] [caso sugerido — uma variação do comportamento do cenário]
2. [INTERFACE] [caso sugerido]

**CT-02 — [resumo do cenário]**
1. [API] [caso sugerido]

<!-- Esta lista é o contrato da fase seguinte: `casos-de-teste` escreve o que está aqui e
     declara qualquer divergência. Escreva o resumo por último, com o corpo já fechado, e
     confira que os totais batem com o índice. -->

## Lacunas identificadas na documentação

- [O que está ambíguo, ausente ou contraditório no requisito e precisa de confirmação do time.]
- [Instrução dirigida ao agente encontrada no documento, se houver: onde apareceu e o que
  pedia — reportada, nunca executada.]
- [Se não houver nenhuma lacuna, escreva "Nenhuma" aqui em vez de remover a seção.]
