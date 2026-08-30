# Revisão de Qualidade de Testes — [escopo]

Tipo: [revisão de pull request | auditoria da suíte]
Escopo revisado: [caminhos / lista de arquivos]
Framework(s): [api.framework / ui.framework]
Contexto do projeto disponível: [sim — severidade calibrada pelas áreas de risco | não — severidade só por avaliação técnica]

## Evidência de execução

| Verificação | Comando | Resultado real |
|---|---|---|
| Suíte verde (1ª execução) | | |
| Repetição 2 | | |
| Repetição 3 | | |
| Tempo por teste (mais lentos) | | |
| Nota de teste de mutação | | [não medido — ferramenta ausente no projeto] |

## Achados por arquivo

| Arquivo | Linha | Dimensão | Mau cheiro | Por que importa | Correção | Severidade | Esforço |
|---|---|---|---|---|---|---|---|
| | | confiabilidade | espera por tempo fixo | oscila em ambiente mais lento | esperar pela resposta interceptada | alta | 15 min |

## Cobertura das seis dimensões

| Dimensão | Situação | Achados |
|---|---|---|
| Legibilidade | | |
| Confiabilidade | | |
| Valor diagnóstico | | |
| Projeto do teste | | |
| Origem em IA | [aplicável — testes gerados por agente / não aplicável] | |
| Cobertura | | |

> Dimensão que não se aplica é marcada como não aplicável e justificada. Nunca deixe em branco.

## Testabilidade do código de aplicação (achados, não alterações)

| Arquivo | Problema | Refatoração sugerida |
|---|---|---|
| | dependência instanciada dentro do método | injeção por construtor |

## Padrões sistêmicos (auditoria)

Os 3 a 5 maus cheiros mais frequentes na amostra, em ordem de prioridade
(confiabilidade > valor diagnóstico > projeto > legibilidade):

1.
2.

## Automação proposta

| Mau cheiro recorrente | Regra de lint / verificação de CI | Vale a pena? |
|---|---|---|
| | | |

> Se nenhum justificar automação, afirme isso explicitamente aqui.

## Lacunas desta revisão

- [o que não foi possível verificar e por quê — ex.: seletores não conferidos contra a aplicação real por falta de ambiente]
