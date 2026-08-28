# Cenários de Teste BDD – [Nome do Requisito/Funcionalidade]
<!-- Origem: [ticket/PRD/seção de referência] -->

```gherkin
# language: pt

Funcionalidade: [nome objetivo da funcionalidade]
  Como [ator/persona]
  Quero [ação/objetivo]
  Para [benefício/motivo de negócio]

  # Tópico 1 - [descrição curta do tópico/campo/regra tratada]

  Cenário: Validar que [descrição objetiva do comportamento esperado — caminho feliz]
    Dado que [estado inicial]
    Quando [uma ação]
    Então [resultado observável e verificável]
    E [resultado adicional, se houver]

  Cenário: Validar que [descrição objetiva do comportamento esperado — caso negativo]
    Dado que [estado inicial]
    Quando [ação inválida]
    Então [erro/comportamento esperado, específico]

  # Tópico 2 - [descrição curta do próximo tópico]

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

## Observações

- [Explique aqui qualquer suposição, dedução por complementaridade lógica, ou lacuna do
  requisito original que precise ser confirmada com o time antes de considerar os cenários
  definitivos. Remova esta seção apenas se nenhum cenário acima depender de suposição.]
