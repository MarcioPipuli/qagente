# Casos de Teste BDD – [Nome do Requisito/Funcionalidade]
<!-- Origem: [ticket/PRD/seção] · Cenários: [caminho do documento de cenários, se houver] -->

```gherkin
# language: pt

Funcionalidade: [nome objetivo da funcionalidade]
  Como [ator/persona]
  Quero [ação/objetivo]
  Para [benefício/motivo de negócio]

  # Tópico 1 - [cenário de origem ou campo/regra/tela tratada]

  @CT-01 @api @pendente-de-automacao
  Cenário: Validar que [descrição objetiva do comportamento esperado — caminho feliz]
    Dado que [estado inicial, descrito pelo que o dado é, não pelo valor literal]
    Quando [uma única ação]
    Então [resultado observável e verificável, vindo dos Resultados Esperados do cenário]
    E [resultado adicional, se houver]

  @CT-01 @interface @pendente-de-automacao
  Cenário: Validar que [descrição objetiva do comportamento esperado — caso negativo]
    Dado que [estado inicial]
    Quando [uma única ação inválida]
    Então [erro/comportamento esperado, específico]

  # Tópico 2 - [próximo cenário de origem]

  @CT-02 @interface @pendente-de-automacao
  Esquema do Cenário: Validar que [descrição usando placeholder entre <>]
    Dado que [contexto usando "<parametro>"]
    Quando [ação]
    Então o campo "<parametro>" [resultado esperado]

    Exemplos:
      | parametro           |
      | [valor 1]           |
      | [valor 2]           |
      | [valor 3]           |
```

## Resumo dos Casos de Teste

**Total de casos:** [N] ([N] Cenário + [N] Esquema do Cenário com [N] Exemplos)
**Por camada:** @api [N] · @interface [N]
**Por tipo de execução:** @pendente-de-automacao [N] · @nao-automatizavel [N]
**Por prioridade herdada:** [Alta N · Média N · Baixa N — níveis de `risk_levels`, no idioma de `language`]
**Aderência ao contrato:** [N casos sugeridos, N escritos — e o motivo de cada divergência, se houver]

<!-- Escreva o resumo por último, com o corpo já fechado, e confira que os totais batem.
     Cada caso @nao-automatizavel entra aqui com o motivo. -->

## Observações

- [Só quando NÃO existe documento de cenários para segurar as lacunas. Explique aqui qualquer
  suposição, dedução por complementaridade lógica, ou trecho ambíguo do requisito que precise
  ser confirmado com o time antes de considerar os casos definitivos. Havendo documento de
  cenários, cite-o e remova esta seção — a lacuna mora lá.]
