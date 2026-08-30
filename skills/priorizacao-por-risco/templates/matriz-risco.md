# Matriz de Risco — [escopo analisado]

Origem do impacto: `.qagente/contexto-projeto.md` (seção Áreas de risco)
Método: impacto × probabilidade (`risk_method`)
Data desta avaliação: [AAAA-MM-DD]
Próxima reavaliação: [AAAA-MM-DD — trimestral, ou 48h após incidente]

## Itens pontuados

| ID | Item de risco | Consequência se falhar | Impacto (1-5) | Área de risco citada | Probabilidade (1-5) | Justificativa da probabilidade | Composto | Zona |
|---|---|---|---|---|---|---|---|---|
| R-01 | [o que pode falhar] | [consequência] | 5 | Pagamento | 4 | Alterado 31× em 3 meses | 20 | critical |
| R-02 | | | | | | | | |

> Item sem área de risco correspondente no contexto do projeto: registre `— (sem área declarada)`
> na coluna, nunca deixe em branco nem atribua o impacto como se ele viesse do contexto.

## Modos de falha (obrigatório para composto ≥ 10)

### R-01 — [nome do componente] (composto 20)

```
Modo de falha 1: [o que especificamente pode falhar]
  Gatilho:            [o que causa essa falha]
  Raio de impacto:    [usuários, sistemas e dados afetados]
  Forma de detecção:  [monitoramento, teste, reclamação de usuário]
  Mitigação atual:    [testes, alertas, feature flag, fallback existentes]
  Lacuna:             [o que falta — este campo vira cenário de teste na Fase 1]
```

## Alinhamento de cobertura

| ID | Zona | Cobertura prescrita | Cobertura atual | Lacuna | Responsável | Prazo |
|---|---|---|---|---|---|---|
| R-01 | critical | API: todos os contratos; UI: jornada + erros; unidade 90% ramos | UI só caminho feliz | Sem teste de erro de pagamento | | |

## Quase-incidentes desde a última avaliação

| Data | O que quase escapou | Onde foi pego | Item repontuado |
|---|---|---|---|
| | | | |

## Gatilhos de reavaliação

- Incidente em produção → repontuar os itens afetados em até 48h
- Nova área de funcionalidade
- Mudança de dependência crítica (versão de API, troca de fornecedor)
- Mudança relevante na composição do time
- Trimestral, mesmo sem gatilho
