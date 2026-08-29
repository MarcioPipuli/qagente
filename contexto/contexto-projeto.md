# Contexto do Projeto — QAGente

> Preencha este arquivo com os fatos do **seu produto**. O agente lê antes de qualquer tarefa
> de QA e usa isto para não perguntar duas vezes a mesma coisa e para priorizar com base no
> negócio, não no palpite.
>
> Diferença em relação a `.qagente/quality-profile.json`: o perfil diz **como** trabalhar
> (idioma, caminhos, frameworks, escala de risco); este arquivo diz **o que é o produto**.
> Nenhum dos dois desliga as regras universais de `AGENTS.md`.
>
> Cada seção indica a fase que a consome. Seção que você não souber responder ainda: apague
> ou escreva "não definido" — meia resposta inventada é pior que a ausência, porque o agente
> a trata como fato. Substitua tudo entre `[colchetes]`.

---

## Produto

*Usado em todas as fases, para dar sentido ao vocabulário do requisito.*

- **Nome:** [nome do produto]
- **O que faz:** [uma frase — o problema que resolve, para quem]
- **Quem usa:** [perfis de usuário; quem tem permissão de quê, se isso importa para os testes]

---

## Fluxos críticos

*Usado na Fase 1, para separar o que é core do que é periférico.*

Liste os caminhos que, se quebrarem, param o produto ou o negócio. Ordene do mais crítico
para o menos.

1. [ex.: cadastro e primeiro acesso]
2. [ex.: criação e envio de pedido]
3. [ex.: pagamento e emissão de comprovante]

---

## Áreas de risco

*Usado na Fase 1, na priorização por probabilidade × impacto.*

Sem esta tabela, a prioridade de cada cenário é chute. Com ela, o agente consegue justificar
por que um cenário é `critical` e outro é `medium`.

| Área | Impacto se falhar em produção | Por que é arriscada |
|---|---|---|
| [Pagamento] | [Perda de receita, exposição regulatória] | [Integração com terceiro, muitos casos de borda de moeda] |
| [Autenticação] | [Usuário sem acesso, risco de segurança] | [OAuth + senha, sessão com regra de expiração] |
| [Exportação de dados] | [Perda de confiança do cliente] | [Volume grande, sujeito a timeout] |

---

## Terminologia do domínio

*Usado na Fase 2 — os casos de teste copiam estes termos exatamente, sem parafrasear.*

| Termo | O que significa aqui |
|---|---|
| [Subclasse] | [Divisão de um fundo com regras próprias de resgate] |
| [Mnemônico] | [Código curto de negociação, só existe para FIDC e FII] |

---

## Stack e ambientes

*Usado nas Fases 3a/3b, para saber contra o que a automação roda.*

- **Frontend:** [framework, linguagem]
- **Backend / API:** [framework, REST ou GraphQL]
- **Banco:** [qual, e se o teste pode escrever nele]
- **Ambiente de teste:** [URL, e se os dados são resetados, compartilhados ou voláteis]
- **Acesso:** [como se obtém credencial de teste — nunca escreva a credencial aqui]
- **Preparação de dados:** [dá para criar estado via API? via seed? só pela interface?]

---

## Testes que já existem

*Usado nas Fases 3a/3b, para seguir o que o time mantém em vez de impor um padrão novo.*

- **Suíte atual:** [ex.: Cypress em `cypress/e2e`, ~40 specs / ou "nenhuma"]
- **Convenções a respeitar:** [nomes de arquivo, comandos customizados, fixtures existentes]
- **Atributo de seletor na aplicação:** [ex.: `data-testid` já presente nos formulários; ausente nas telas de relatório]
- **Onde roda:** [local, CI, ambos; e em qual pipeline]

---

## Restrições

*Usado em todas as fases. É o que impede uma sugestão tecnicamente correta e inaceitável aqui.*

- **Dados sensíveis:** [ex.: base tem CPF real — nenhum teste pode usar massa copiada de produção]
- **Compliance:** [ex.: LGPD, SOX, auditoria — algo que obrigue evidência formal de execução]
- **Janelas e limites:** [ex.: ambiente de teste cai às 22h; API de terceiro tem cota diária]

---

## Time e maturidade

*Usado para calibrar o tamanho da entrega — a mesma skill entrega menos ou mais conforme isto.*

- **Maturidade:** [inicial | crescimento | estabelecido]
  - *inicial* — pouca ou nenhuma automação. Cobrir caminho crítico primeiro; não propor
    matriz de browsers, sharding ou regressão visual ainda.
  - *crescimento* — CI existe e a suíte cresce. Vale investir em estrutura reutilizável,
    massa de dados e execução paralela.
  - *estabelecido* — prática madura. Cabe matriz completa, métricas de flakiness e evidência
    formal.
- **Quem executa o QA:** [ex.: 1 QA para 6 devs; ou "os próprios devs"]
- **Quando o QA entra:** [antes do desenvolvimento, revisando o requisito / depois, testando o pronto]

---

## Observações

[Qualquer coisa que ajude e não coube acima: dívida técnica conhecida, migração em
andamento, parte do sistema que ninguém entende, incidente recente que vale usar como
cenário de regressão.]
