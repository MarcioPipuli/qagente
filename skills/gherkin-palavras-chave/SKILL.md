---
name: gherkin-palavras-chave
description: Explica e aplica corretamente as palavras-chave do Gherkin em português — Dado, Quando, Então, E, Mas — cobrindo o papel de cada uma, a gramática correta dos passos e os erros mais comuns. Use quando o usuário for escrever, revisar ou corrigir passos de cenários em Gherkin/BDD e precisar decidir qual palavra-chave usar, ou pedir para explicar a diferença entre elas. Do NOT use para estruturar o documento de cenários inteiro (Funcionalidade, Tópicos, Esquema do Cenário, Exemplos) — para isso use `escrita-casos-teste`, que consome esta skill apenas para a gramática de cada passo.
license: CC-BY-4.0
metadata:
  author: QAGente
  version: '1.0.0'
---

# Palavras-chave do Gherkin (pt)

Referência gramatical para os cinco conectores usados na escrita de passos em Gherkin em português. Não define a estrutura do documento de cenários (isso é escopo de `escrita-casos-teste`) — define apenas como escrever cada linha corretamente.

## Configuração

Esta skill documenta a gramática do Gherkin **em português**. Ela se aplica quando
`conventions.gherkin_language` em `.qagente/quality-profile.json` for `pt` — o default — ou
quando não houver perfil e o idioma da conversa for português.

Se o perfil definir outro idioma, avise que esta skill não se aplica e use a gramática oficial
do Gherkin para o idioma escolhido; a estrutura do documento continua em `escrita-casos-teste`.

## Quando usar

- O usuário está escrevendo ou revisando cenários em Gherkin e precisa saber se um passo é um Dado, um Quando ou um Então.
- Um cenário existente está com a gramática errada (ex.: uma ação dentro de um Dado, ou duas verificações desconexas dentro de um Então) e precisa de correção.
- O usuário pergunta diretamente a diferença entre as palavras-chave.

## As cinco palavras-chave

| Palavra-chave | Papel | Tempo/forma verbal típica | Pergunta que responde |
|---|---|---|---|
| **Dado** (Given) | Estabelece o contexto/estado inicial, antes de qualquer ação | Subjuntivo de estado: "esteja", "possua", "tenha", "exista" | Em que situação o sistema já se encontra? |
| **Quando** (When) | Descreve a ação/evento que dispara o comportamento sob teste | Infinitivo/ação: "clicar", "informar", "acessar", "enviar" | O que o ator faz (ou o que acontece) para disparar o comportamento? |
| **Então** (Then) | Descreve o resultado observável esperado após a ação | Expectativa: "deve", "não deve" | O que se observa depois, e como isso é verificado? |
| **E** (And) | Encadeia mais uma condição/ação/resultado da MESMA categoria do passo anterior | Segue o verbo do passo que continua | Preciso adicionar outro item à mesma lista (mais um Dado, mais uma verificação)? |
| **Mas** (But) | Como o "E", mas introduz uma condição ou verificação de exceção/negativa dentro da mesma sequência | Geralmente com negação: "não deve", "exceto quando" | Há uma ressalva ou exceção à mesma categoria do passo anterior? |

## Regras de uso correto

1. **Dado nunca descreve uma ação do usuário.** Ações pertencem ao Quando.
   - ❌ `Dado que o usuário clica em "Salvar"`
   - ✅ `Dado que o usuário esteja na tela de cadastro` / `Quando ele clicar em "Salvar"`

2. **Prefira um único Quando por cenário** — a ação-chave sob teste. Se duas ações não relacionadas são necessárias para chegar ao resultado, considere se não deveriam ser dois cenários.

3. **Então verifica resultado observável, não implementação interna.**
   - ❌ `Então o registro é salvo na tabela X do banco`
   - ✅ `Então o sistema deve exibir a mensagem "Cadastro realizado com sucesso"`

4. **E só continua a categoria do passo anterior** — nunca mistura Dado com Então na mesma cadeia.
   - ❌
     ```
     Dado que o usuário esteja autenticado
     E o sistema deve exibir a tela inicial
     ```
     (a segunda linha é resultado, não contexto — deveria ser um Então)
   - ✅
     ```
     Dado que o usuário esteja autenticado
     E que ele possua permissão de administrador
     Quando ele acessar o painel
     Então o sistema deve exibir as opções administrativas
     ```

5. **Mas sinaliza uma exceção/ressalva dentro da mesma categoria**, tipicamente para reforçar o que NÃO deve acontecer junto do que deve.
   - ✅
     ```
     Então o sistema deve salvar as alterações
     Mas não deve alterar o valor do campo "Data de Alteração"
     ```

6. **Valores literais sempre entre aspas duplas** — nomes de campo, textos exibidos, opções de domínio, datas: `Então o sistema deve exibir os domínios "Sim", "Não" e "Não se aplica"`.

7. **Coerência de sujeito e tempo verbal** dentro do mesmo cenário — não alterne entre "o usuário" e "o sistema" sem necessidade, e mantenha o subjuntivo em todos os Dados encadeados com E.

## Erros comuns e correção

| Erro | Por que está errado | Correção |
|---|---|---|
| `Dado que o usuário preenche o campo Nome` | Ação (preencher) dentro de um Dado | Mover para `Quando ele preencher o campo Nome` |
| `Quando o usuário esteja na tela` | Estado (esteja) dentro de um Quando | Mover para `Dado que o usuário esteja na tela` |
| `Então o usuário clica em Confirmar` | Ação dentro de um Então | Ação pertence ao Quando; Então só verifica resultado |
| `E o campo deve estar habilitado` logo após um `Quando` | O E herdou a categoria errada (deveria ser Então) | Trocar para `Então o campo deve estar habilitado` |
| Vários `Quando` numa sequência sem relação causal direta | Cenário testando mais de um comportamento | Dividir em cenários distintos, um por comportamento |

## Exemplo completo correto

```gherkin
Cenário: Validar que o campo Código ISIN não é de preenchimento obrigatório
  Dado que o usuário esteja preenchendo os dados da subclasse
  Quando ele deixar o campo Código ISIN em branco
  Então o sistema deve permitir salvar os dados sem exibir erro de campo obrigatório

Cenário: Validar que o campo Mnemônico fica limpo e desabilitado para tipos de fundo diferentes de FIDC e FII
  Dado que o tipo do fundo seja diferente de "FIDC" e de "FII"
  Quando a tela de Dados Cadastrais da Subclasse for exibida
  Então o campo Mnemônico deve estar desabilitado
  E o campo Mnemônico deve estar limpo
  Mas o valor anteriormente preenchido não deve ser exibido
```

## Ao usar em conjunto com `escrita-casos-teste`

Esta skill cobre a gramática de cada passo. A estrutura do documento inteiro (cabeçalho, `Funcionalidade`, organização em Tópicos, quando usar `Cenário` simples vs. `Esquema do Cenário` com `Exemplos`, e a seção de Observações) é definida em `escrita-casos-teste` — aplique as duas em conjunto ao gerar um arquivo de cenários completo.
