# Reprodução — [título curto do defeito]

Origem: [ticket/ID do bug — ou "relato informal do usuário na conversa, sem ticket associado"]
Status da reprodução: [reproduzido | oscilação | específico de ambiente | dependente de dado | não reproduzível]

## 1. Dimensões extraídas do relato

| Dimensão | Valor | Origem |
|---|---|---|
| Passos exatos | | relato / perguntado ao relator |
| Build / versão / commit | | |
| Ambiente (SO, navegador+versão, dispositivo) | | |
| Dados de entrada (conta, massa, cupom) | | |
| Esperado × obtido | esperado `[valor]`, obtido `[valor]` | |
| Frequência | [toda vez / intermitente] | |
| Fuso, idioma, moeda | | |
| Momento da ocorrência | | |

> Linha em branco não é lacuna aceita: é a próxima pergunta ao relator. Registre aqui o que
> foi perguntado e ainda não respondido, em vez de preencher por suposição.

## 2. Reprodução mínima

Passos após o ciclo reproduzir → minimizar → isolar (não é a caminhada original):

1.
2.

Ou comando único:

```
[comando]
```

Camada isolada: [UI / API / unidade]

### Cortes testados durante a minimização

| Elemento removido | Ainda reproduz? | Conclusão |
|---|---|---|
| | sim / não | corte mantido / elemento necessário, devolvido |

## 3. Determinismo

| Fonte | Como foi fixada |
|---|---|
| Tempo | |
| Aleatoriedade / massa | |
| Rede externa | |
| Fuso e idioma | |

Execuções consecutivas com falha idêntica: [n/10]

## 4. Commit que introduziu (quando for regressão)

```
git bisect start
git bisect bad HEAD
git bisect good [tag do último release limpo]
git bisect run [comando de UM teste alvo]
git bisect reset
```

Primeiro commit ruim: `[sha]` — [assunto do commit]

## 5. Teste de regressão

Caminho: `[paths.api_tests ou paths.ui_tests]/[arquivo]`
Framework: [api.framework / ui.framework]

| Verificação | Resultado real |
|---|---|
| Falha antes da correção (vermelho) | [saída da execução] |
| Passa depois da correção (verde) | [saída da execução] |
| Volta a falhar com a correção revertida | [saída da execução] |

## 6. Evidência

- [log / print / trace / artefato de execução]

## 7. Bloco para colar no ticket

```markdown
**Reprodução mínima:** [passos ou comando]
**Ambiente e build:** [ambiente] — commit `[sha]`
**Esperado × obtido:** esperado `[valor]`, obtido `[valor]`
**Commit introdutor:** `[sha]`
**Teste de regressão:** `[caminho do arquivo]`
**Evidência:** [link ou anexo]
**Determinismo:** [massa fixa, tempo congelado, interceptações usadas]
```

## Se não reproduziu

| O que foi tentado | Resultado |
|---|---|
| Ambientes replicados | |
| Número de execuções repetidas | |
| Massa do relator replicada | |

Diagnóstico e evidência que levou a ele: [texto]
