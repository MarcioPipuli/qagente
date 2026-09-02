# Casos de Teste — [Nome do Requisito/Funcionalidade]
Origem: [ticket/PRD/seção] | Cenários de origem: [caminho do documento de cenários, se houver]

<!-- Layout do formato `markdown-palavras-chave`: os passos usam as palavras-chave
     (DADO/QUANDO/ENTÃO/E/MAS, gramática em `gherkin-palavras-chave`) e os metadados moram em
     campos rotulados, como em ferramenta de gestão de caso de teste. O outro formato do
     harness é `markdown-gherkin`, em `templates/casos-de-teste.md`. Quem decide é
     `artifact_format` no perfil.

     Três âncoras são obrigatórias em cada caso, e é por elas que o validador confere o
     documento. O rótulo é fixo; o resto do layout é do time:
       - `Rastreio:`          o ID do cenário de origem (ou do requisito, se não houver fase 1)
       - `[API]` / `[INTERFACE]`  a camada, em qualquer lugar do bloco do caso
       - `Tipo de Execução:`  `Pendente de Automacao` ou `Nao Automatizavel` -->

---

## [Título do caso — específico e afirmativo, no prefixo de `conventions.scenario_title_prefix`]

Rastreio: [ID do cenário de origem — ex.: CT-01]

Summary:
[API|INTERFACE] [descrição curta do caso]

Description:
Valida que [o que o caso verifica]. Cobre [RNs/CAs cobertos]. Referência: [cenário de origem]

Action:
*DADO* que [pré-condição específica, no presente]
*E* [pré-condição adicional, se houver]
*QUANDO* [a ação — UMA por caso, com o rótulo exato do requisito]

Data:
- [item de massa — placeholder descritivo, nunca dado real de produção]

Expected Result:
*ENTÃO* o sistema deve [resultado esperado exato — valor, mensagem ou estado verificável]
*E* [resultado complementar, se houver]

Tipo de Execução:
Pendente de Automacao

## [Título do segundo caso — caso negativo do mesmo tópico]

Rastreio: [ID do cenário de origem]

Summary:
[API|INTERFACE] [descrição curta]

Description:
Valida que [o que o caso verifica]. Cobre [RN/CA].

Action:
*DADO* que [pré-condição]
*MAS* [pré-condição negativa, se houver — nunca "E"]
*QUANDO* [a ação]

Expected Result:
*ENTÃO* o sistema deve [resultado esperado]
*MAS* [condição restritiva, se houver]

Tipo de Execução:
Nao Automatizavel

## Resumo dos Casos de Teste

**Total de casos:** [N]
**Por camada:** [API] [N] · [INTERFACE] [N]
**Por tipo de execução:** Pendente de Automacao [N] · Nao Automatizavel [N]
**Por prioridade herdada:** [Alta N · Média N · Baixa N — níveis de `risk_levels`, no idioma de `language`]
**Aderência ao contrato:** [N casos sugeridos, N escritos — e o motivo de cada divergência, se houver]

<!-- Escreva o resumo por último, com o corpo já fechado, e confira que os totais batem.
     Cada caso `Nao Automatizavel` entra aqui com o motivo. Os rótulos `**Total de casos:**` e
     `**Aderência ao contrato:**` são lidos pelo validador — mudá-los desliga a checagem. -->

## Observações

- [Só quando NÃO existe documento de cenários para segurar as lacunas. Explique aqui qualquer
  suposição, dedução por complementaridade lógica, ou trecho ambíguo do requisito que precise
  ser confirmado com o time antes de considerar os casos definitivos. Havendo documento de
  cenários, cite-o e remova esta seção — a lacuna mora lá.]
