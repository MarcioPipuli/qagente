# Manual do Usuário — QAGente

Este manual leva você do zero até o primeiro teste pronto.

São **15 passos**. Faça na ordem. Cada passo mostra o que fazer e o que você deve ver na tela.

| Parte | Passos | Quando você faz |
|---|---|---|
| 1. Preparar o computador | 1 a 3 | Uma vez só |
| 2. Instalar o agente no projeto | 4 a 7 | Uma vez por projeto |
| 3. Configurar | 8 a 10 | Uma vez, ~30 minutos |
| 4. Usar no dia a dia | 11 a 15 | Toda vez |
| 5. Consulta rápida | — | Quando precisar |

---

## O que é o QAGente, em 5 linhas

É um assistente de QA que trabalha dentro da sua ferramenta de IA.

Você entrega um requisito (PRD, ticket, história). Ele devolve:

- os **cenários de teste**, já priorizados por risco;
- as **dúvidas que o requisito não responde** (ótimo para levar ao refinamento);
- os **casos de teste em Gherkin**;
- e, se você aprovar, os **testes automatizados** — rodados de verdade.

Ele não mexe no código da aplicação e não roda nada em produção.

---

# PARTE 1 — Preparar o computador

## Passo 1 — Ver se você tem o Python

O Python é usado **só na instalação**. Você não vai programar nada.

Abra o **PowerShell**:

> Aperte a tecla `Windows`, digite `powershell` e aperte `Enter`.

Digite o comando abaixo e aperte `Enter`:

```
python --version
```

**O que você deve ver** (o número pode ser diferente):

```
Python 3.13.1
```

✅ Apareceu um número **3.9 ou maior**? Pode ir para o Passo 2.

❌ **Apareceu erro, ou abriu a loja da Microsoft?** Você não tem o Python. Instale assim:

1. Acesse **python.org/downloads**
2. Clique no botão amarelo de download
3. Abra o arquivo baixado
4. **Importante:** marque a caixinha **"Add Python to PATH"** antes de clicar em Install
5. Termine a instalação, **feche o PowerShell e abra de novo**
6. Repita o comando `python --version`

## Passo 2 — Ter a ferramenta de IA aberta

O QAGente funciona dentro de uma dessas: **Claude Code**, GitHub Copilot, Cursor ou Windsurf.

Use a que o seu time já usa. Se for o Claude Code, você vai abri-lo no Passo 12.

Não precisa fazer nada agora — só confirme que você tem acesso a uma delas.

## Passo 3 — Descompactar o pacote

Você recebeu um arquivo `QAGente.zip`.

1. Clique com o botão direito nele → **Extrair tudo**
2. Escolha um lugar fácil de achar. Sugestão: a pasta **Documentos**
3. Abra a pasta que apareceu

**O que você deve ver dentro dela** (entre outros arquivos):

```
PRIMEIROS-PASSOS-QAGENTE.md     ← este manual
README.md
install.py                       ← o instalador que você vai usar no Passo 6
docs                             ← os outros dois documentos ficam aqui
skills
profiles
```

⚠️ **Não mude esses arquivos de lugar.** Os comandos deste manual são executados de dentro
desta pasta.

> Recebeu um endereço do GitHub em vez de um arquivo `.zip`? Nessa página, clique no botão
> verde **Code** → **Download ZIP**. Dá no mesmo.

---

# PARTE 2 — Instalar o agente no seu projeto

A partir daqui, "seu projeto" é a pasta do sistema que você vai testar.

## Passo 4 — Abrir o PowerShell na pasta do pacote

1. Abra a pasta que você descompactou no Passo 3
2. Clique com o botão direito num espaço vazio dentro dela
3. Escolha **"Abrir no Terminal"**

> Não apareceu essa opção? Clique na barra de endereço da pasta (onde fica o caminho), apague o
> que estiver escrito, digite `powershell` e aperte `Enter`.

**Como saber que deu certo:** a janela preta que abriu mostra, no começo da linha, o caminho da
pasta do pacote. Algo como:

```
PS C:\Users\SeuNome\Documents\QAGente>
```

Confira que você está no lugar certo: digite `dir` e aperte `Enter`. Você deve ver o arquivo
`install.py` na lista.

## Passo 5 — Descobrir o caminho do seu projeto

Você vai precisar dele no próximo passo.

1. Abra a pasta do seu projeto no Explorador de Arquivos
2. Clique na barra de endereço
3. O caminho fica selecionado. Aperte `Ctrl + C` para copiar

Vai ser algo como `C:\Users\SeuNome\Documents\meu-projeto`.

Anote ou deixe copiado.

## Passo 6 — Fazer um teste antes de instalar

Este comando **não altera nada**. Ele só mostra o que aconteceria. Serve para você ver o que vai
entrar no projeto antes de decidir.

Digite (troque o caminho pelo do seu projeto) e aperte `Enter`:

```
python install.py --target "C:\Users\SeuNome\Documents\meu-projeto" --profile default --dry-run
```

> 💡 Para colar no PowerShell, clique com o **botão direito** dentro da janela.
> Mantenha as **aspas** em volta do caminho.

**O que você deve ver:** várias linhas começando com `[dry-run]`, e no final:

```
Concluído. Próximos passos:
  - Preencha .qagente/contexto-projeto.md: sem ele o agente prioriza por palpite.
```

❌ **Deu erro?** Veja a tabela do Passo 15.

## Passo 7 — Instalar de verdade

Mesmo comando, **sem** o `--dry-run` no final, e com `--tool claude`:

```
python install.py --target "C:\Users\SeuNome\Documents\meu-projeto" --tool claude --profile default
```

> Usa outra ferramenta? Troque `claude` por `copilot`, `cursor` ou `windsurf`.

**Confira que deu certo.** Abra a pasta do seu projeto. Devem ter aparecido:

| Apareceu | O que é |
|---|---|
| `.qagente` | A configuração do agente (você mexe nela nos Passos 8 e 9) |
| `.claude` | O agente em si |
| `entrada` | Onde você vai colocar os requisitos |
| `saida` | Onde o agente vai gravar o que produzir |
| `AGENTS.md` e `CLAUDE.md` | As regras que o agente segue |

> Não está vendo as pastas `.qagente` e `.claude`? Elas começam com ponto e ficam escondidas.
> No Explorador de Arquivos, vá em **Exibir → Mostrar → Itens ocultos**.

---

# PARTE 3 — Configurar

Duas edições. Reserve uns 30 minutos.

> **Não tente responder tudo agora.** Preencha o essencial, use o agente por uma ou duas semanas,
> e volte para ajustar. Resposta chutada é pior que resposta em branco, porque o agente trata
> como fato.

> ### 💬 O caminho curto: peça ao agente
>
> Os Passos 8, 9 e 10 podem ser feitos por conversa, sem abrir nenhum arquivo. Abra a ferramenta
> de IA no seu projeto e diga:
>
> > **configure o QAGente neste projeto**
>
> Ele olha o seu repositório primeiro — descobre sozinho o framework de teste, a suíte que já
> existe, o atributo dos elementos e onde ficam as pastas — e depois confirma o que achou em vez
> de perguntar do zero. São dois blocos de até 5 perguntas: o primeiro deixa o
> `quality-profile.json` pronto, o segundo conta a ele como é o seu produto. No fim, ele mesmo
> valida o arquivo (o Passo 10) e lista o que ficou sem resposta.
>
> **"Não sei" é resposta válida** em qualquer pergunta: ele mantém o padrão, marca a seção como
> *Não respondido* e segue. Você pode pedir a mesma coisa de novo daqui a um mês para preencher o
> que faltou — ele pergunta só o que ainda está em branco e nunca troca o que você já respondeu
> sem mostrar antes o que mudaria.
>
> Prefere fazer na mão, ou quer entender o que cada campo significa antes? Siga os Passos 8 a 10
> normalmente — eles continuam valendo, e são a mesma configuração.

## Passo 8 — Dizer o que o seu time automatiza

Abra o arquivo `.qagente/quality-profile.json`, dentro do seu projeto.

> Abra com o Bloco de Notas ou com o VS Code. É um arquivo de texto comum.

Procure a parte que começa com `"api"`. Você vai ver isto:

```json
  "api": {
    "enabled": true,
    "framework": "robot-framework",
```

E logo abaixo, a parte que começa com `"ui"`:

```json
  "ui": {
    "enabled": true,
    "framework": "cypress",
    "selector_attribute": "data-testid",
```

Agora ajuste **três coisas**, conforme o seu time:

| Se... | Mude para |
|---|---|
| Vocês **não** automatizam testes de API | `"enabled": false` na parte do `"api"` |
| Vocês **não** automatizam testes de tela | `"enabled": false` na parte do `"ui"` |
| Vocês usam **Playwright** em vez de Cypress | `"framework": "playwright"` |
| A aplicação de vocês usa outro atributo nos elementos | Troque `"data-testid"` pelo que ela usa (ex.: `"data-cy"`) |

**Não sabe o que é o atributo?** Deixe como está e pergunte para um desenvolvedor depois.

Salve o arquivo.

⚠️ **Cuidado com a vírgula.** É um arquivo JSON: se você apagar ou adicionar uma vírgula sem
querer, ele quebra. O Passo 10 verifica isso para você.

## Passo 9 — Contar ao agente como é o seu produto

Este é o passo que mais muda a qualidade do resultado.

Abra o arquivo `.qagente/contexto-projeto.md`, dentro do seu projeto.

Ele é um formulário com espaços entre `[colchetes]`. **Preencha só duas seções agora.**

### Seção "Fluxos críticos"

Os caminhos que, se quebrarem, param o produto. Do mais grave para o menos.

Apague o que está entre colchetes e escreva os seus:

```
1. Login e primeiro acesso
2. Criação e envio de pedido
3. Pagamento e emissão de comprovante
```

### Seção "Áreas de risco"

É desta tabela que sai a **prioridade** de cada cenário de teste. Preencha assim:

```
| Área | Impacto se falhar em produção | Por que é arriscada |
|---|---|---|
| Pagamento | Perda de receita e problema com auditoria | Depende de um sistema de terceiro e tem muito cálculo de valor |
| Login | Cliente sem acesso ao sistema | Tem regra de expiração de sessão e senha |
```

**Compare:**

❌ Assim não ajuda — o agente já poderia ter chutado isso:
```
| Pagamento | Alto | Importante |
```

✅ Assim ajuda — agora ele consegue justificar a prioridade:
```
| Pagamento | Perda de receita e problema com auditoria | Depende de um sistema de terceiro e tem muito cálculo de valor |
```

### Regra importante

Se você **não souber** responder alguma parte, **apague a linha** ou escreva `não definido`.

Nunca deixe `[colchetes]` e nunca invente. Meia resposta inventada é pior que nenhuma, porque o
agente vai tratar como verdade.

Salve o arquivo.

## Passo 10 — Conferir se a configuração está válida

Volte para a janela do PowerShell (a do Passo 4) e digite:

```
python install.py --validate-profile "C:\Users\SeuNome\Documents\meu-projeto\.qagente\quality-profile.json"
```

**O que você deve ver:**

```
  nenhum problema encontrado

0 erro(s), 0 aviso(s).
```

✅ Deu isso? Configuração pronta.

❌ **Apareceu "erro"?** Provavelmente foi uma vírgula no Passo 8. A mensagem diz qual campo está
com problema. Abra o arquivo, corrija e rode o comando de novo.

---

# PARTE 4 — Usar no dia a dia

Agora sim, o trabalho.

## Passo 11 — Colocar o requisito na pasta de entrada

Pegue o PRD, o ticket ou a história que você quer testar e salve dentro da pasta `entrada` do
seu projeto.

Exemplo: `entrada/recuperacao-senha.md`

> **Não tem o requisito em arquivo?** Você pode colar o texto direto no chat. Mas o resultado é
> melhor com arquivo, porque o agente lê o documento inteiro.

## Passo 12 — Abrir a ferramenta de IA no seu projeto

**No Claude Code:** abra o PowerShell na pasta do **seu projeto** (mesmo jeito do Passo 4),
digite `claude` e aperte `Enter`.

**No Cursor, Windsurf ou VS Code com Copilot:** abra a pasta do seu projeto pelo próprio
programa e abra o chat.

## Passo 13 — Pedir a análise

Escreva no chat, em português mesmo:

```
Analisa o arquivo entrada/recuperacao-senha.md e me diz o que precisamos testar.
```

Pronto. Não existe comando especial nem palavra mágica.

### O agente pode fazer uma ou duas perguntas antes

É normal. São perguntas curtas, do tipo:

> Esse ticket muda um comportamento que já existe? O fluxo usa algum serviço externo?

**Responda o que você souber. E diga quando não souber.** "Não sei" é uma resposta boa — ele
registra a dúvida em vez de inventar.

### O que ele devolve

Ele grava um arquivo em `saida/cenarios/` e mostra o conteúdo no chat. Assim:

```
## Cenários de Teste — Recuperação de senha
Origem: PROJ-482

| ID | Cenário | Tipo | Prioridade | Observação |
|---|---|---|---|---|
| TC-SENHA-001 | Solicitar recuperação com e-mail cadastrado | Caminho feliz | Alta | Área de risco: Login |
| TC-SENHA-002 | Solicitar com e-mail não cadastrado | Negativo | Alta | Não deve revelar se o e-mail existe |
| TC-SENHA-003 | Usar o link dentro dos 15 minutos | Borda | Crítica | Área de risco: Login |
| TC-SENHA-004 | Usar o link depois de 16 minutos | Negativo | Crítica | |
| TC-SENHA-005 | Pedir o 4º link na mesma hora | Negativo | Alta | |

### Lacunas identificadas na documentação
- O ticket não diz o que acontece se o usuário pedir um link novo com o anterior ainda válido.
  Confirmar com o time.
- O limite de 15 minutos vale ou não vale no minuto 15 exato? Assumido que vale.
```

### O que olhar primeiro

**Leia a parte de "Lacunas" antes da tabela.**

São as dúvidas que o requisito não responde. Leve para o refinamento com o PO — é o melhor uso
do agente, porque essas perguntas aparecem **antes** de o sistema estar pronto.

### Se você tiver as respostas, devolva para ele

```
Falei com o PO: pedir um link novo cancela o anterior, e o limite de 15 minutos vale no
minuto 15. Atualiza os cenários.
```

## Passo 14 — Pedir os casos de teste

```
Escreve os casos de teste em Gherkin para esses cenários.
```

Ele grava em `saida/casos-de-teste/` e mostra algo assim:

```gherkin
Funcionalidade: Recuperação de senha

  Cenário: Validar que o e-mail cadastrado recebe o link de recuperação
    Dado que exista um usuário com o e-mail "maria@example.com"
    Quando ele pedir a recuperação de senha
    Então o sistema deve enviar o e-mail com o link
    E deve exibir a mensagem "Verifique seu e-mail"
```

No final do arquivo tem uma seção **Observações**, com tudo que ele assumiu e precisa da sua
confirmação. Leia essa parte.

### Não gostou de algo? Peça a correção

```
Falta o caso de link já usado. Adiciona.
```
```
Aqui a gente chama de "colaborador", não "usuário". Corrige.
```
```
Esse cenário não é crítico, é uma tela interna. Baixa a prioridade.
```

## Passo 15 — Decidir sobre a automação

Quando os casos ficarem prontos, ele vai **parar e perguntar**:

> Você aprova seguir para a automação agora, ou os casos ficam como documentação?

Isso sempre acontece. Ele **nunca** escreve código de teste sem você aprovar.

**Se você quer os testes automatizados:**

```
Aprovado. Pode automatizar.
```

**Se ainda não é hora:**

```
Por enquanto fica só a documentação.
```

**Quer só uma parte:**

```
Automatiza só os cenários de prioridade Crítica.
```

### Depois de aprovar

Ele escreve os testes, **roda de verdade** e mostra o resultado — inclusive se algum falhar.

⚠️ **Se ele disser que está pronto sem mostrar o resultado da execução**, peça:

```
Roda e me mostra o resultado real.
```

Mostrar a execução é obrigatório para ele. Não é opcional.

---

# PARTE 5 — Consulta rápida

## Frases prontas para copiar

**No dia a dia:**
```
Analisa o arquivo entrada/<nome-do-arquivo> e me diz o que precisamos testar.
Escreve os casos de teste em Gherkin para esses cenários.
Aprovado. Pode automatizar.
```

**Quando chega um bug:**
```
Bug <número>: "<o que o usuário relatou>". Me ajuda a reproduzir.
Escreve o teste de regressão desse bug.
```

**Sobre testes que já existem:**
```
Revisa os testes deste PR.
Esse teste passa às vezes e falha às vezes. Descobre o motivo.
Nossos testes estão atrapalhando uns aos outros por causa dos dados. Organiza isso.
```

**Para planejar:**
```
Monta a matriz de risco das áreas do produto.
```

**Dúvidas rápidas (não geram arquivo):**
```
Nesse passo, é Dado ou Quando?
```

## Cinco coisas que assustam no começo (e estão certas)

| O que acontece | Por que é assim |
|---|---|
| **Ele para antes de automatizar**, mesmo se você já pediu | Para não gastar tempo automatizando um entendimento errado do requisito |
| **Ele faz perguntas** antes de trabalhar | Cada resposta sua evita um chute dele |
| **Ele escreve "Assumido: ..."** no meio do resultado | É ele avisando que deduziu algo. Um assistente que não avisa está chutando escondido |
| **Ele acha bugs mas não conserta** | Ele reporta; corrigir código da aplicação é do desenvolvedor |
| **Ele grava arquivos** em vez de só responder no chat | Assim, meses depois, dá para saber de qual ticket veio cada teste |

## Se der errado

| O que aconteceu | O que fazer |
|---|---|
| `python não é reconhecido...` | Python não instalado ou sem "Add to PATH". Refaça o Passo 1 |
| `Erro: diretório alvo não existe` | O caminho do projeto está errado. Refaça o Passo 5 e mantenha as aspas |
| `Erro: perfil inválido` | Erro de digitação no arquivo do Passo 8, geralmente vírgula. Rode o Passo 10 para ver qual campo |
| Não acho as pastas `.qagente` / `.claude` | Estão ocultas. Explorador → **Exibir → Mostrar → Itens ocultos** |
| O agente não entendeu que é tarefa de QA | Comece a frase com o objetivo: "Analisa esse requisito e levanta os cenários de teste" |
| Ele diz que está priorizando sem base | O contexto do Passo 9 está vazio ou com `[colchetes]`. Preencha as **Áreas de risco** |
| Ele gerou Cypress e vocês usam Playwright | Refaça o Passo 8 trocando `"framework": "playwright"` |
| Ele disse que não pode automatizar API (ou tela) | Está desligado na configuração. Refaça o Passo 8 |
| Ele salvou numa pasta que não é a de vocês | É configurável. Peça ajuda a quem entende do projeto, ou veja o guia completo |
| Ele repete a mesma pergunta toda semana | A resposta deveria estar no arquivo do Passo 9. Acrescente lá |

## Palavras que ele usa

| Palavra | O que quer dizer |
|---|---|
| **Cenário** | Uma linha dizendo *o que* testar e qual a prioridade |
| **Caso de teste** | O passo a passo pronto para executar, em Gherkin |
| **Gherkin** | O formato "Dado / Quando / Então" de escrever teste |
| **Lacuna** | Uma dúvida que o requisito não responde |
| **Rastreabilidade** | Saber de qual ticket ou requisito cada teste veio |
| **Teste instável (flaky)** | Teste que às vezes passa e às vezes falha sem ninguém mexer no código |
| **Evidência de execução** | A prova de que o teste rodou mesmo: o relatório que a ferramenta gera |

## Quando quiser ir além

| Documento | Para quê |
|---|---|
| [`GUIA-DE-USO-QAGENTE.md`](docs/GUIA-DE-USO-QAGENTE.md) | Mais formas de usar: revisão de código de teste, estabilizar suíte instável, todos os ajustes de configuração |
| [`DOCUMENTACAO-TECNICA-QAGENTE.md`](docs/DOCUMENTACAO-TECNICA-QAGENTE.md) | Como o agente funciona por dentro. Só para quem for mexer no agente |

---

## Se você levar só quatro coisas deste manual

1. **Coloque o requisito em arquivo** na pasta `entrada` e cite o nome dele no pedido.
2. **Leia as "Lacunas" primeiro.** É o que você leva para o refinamento.
3. **Preencha as Áreas de risco** (Passo 9). É o que faz a prioridade valer alguma coisa.
4. **Se ele disser "pronto" sem mostrar a execução, peça o resultado real.**
