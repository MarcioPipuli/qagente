---
name: robot-framework-api
description: Escreve e organiza testes automatizados de API (REST/GraphQL) em Robot Framework, usando RequestsLibrary, keywords reutilizáveis em arquivos .resource, massa de dados parametrizada e boas práticas de independência/determinismo. Use quando o usuário pedir para automatizar testes de API, escrever testes em Robot Framework, criar uma suíte .robot, validar contrato de endpoint, testar autenticação/autorização de API, ou revisar/corrigir testes Robot Framework existentes. Não use para automação de interface web (use cypress-ui-automation), testes de carga/performance, ou para escrever os casos de teste em si antes de automatizar (use escrita-casos-teste).
license: CC-BY-4.0
metadata:
  author: QAGente
  version: '1.0.0'
  category: automacao
---

# Automação de API com Robot Framework

<objetivo>
Impede a suíte que passa hoje e é impossível de manter em três meses: asserção genérica que não diz o que era esperado quando falha, token no arquivo versionado, teste que só passa porque outro rodou antes, e `Sleep` no lugar de espera por sinal real. Entrega uma suíte executável em keywords reutilizáveis, com rastreabilidade até o caso de teste e evidência de execução real.
</objetivo>

Escreve suítes de teste de API executáveis em Robot Framework a partir de casos de teste já definidos (skill `escrita-casos-teste`) ou diretamente de uma especificação de API. Terceira fase (ramo API) do fluxo QA — ver `AGENTS.md`, na raiz do projeto.

## Configuração

Leia `.qagente/quality-profile.json` na raiz do projeto antes de começar. Quando um campo
existir no perfil, ele vence os valores desta skill. Precedência: **instrução explícita do
usuário → perfil do projeto → defaults desta skill**.

Leia também `.qagente/contexto-projeto.md`, quando existir. O perfil diz **como** trabalhar;
o contexto diz **o que é o produto** — fluxos críticos, áreas de risco com impacto de negócio,
terminologia do domínio, ambientes e maturidade do time. Ele não substitui o perfil nem as
regras de `AGENTS.md`: é fato sobre o sistema, não configuração. Se não existir, siga sem ele
e diga ao usuário o que teria mudado se existisse.

| Decisão desta skill | Campo do perfil | Default |
|---|---|---|
| Fase de API habilitada | `api.enabled` | `true` |
| Framework de API | `api.framework` | `robot-framework` |
| Variável da URL base | `api.base_url_env` | `API_BASE_URL` |
| Variável de usuário | `api.user_env` | `QA_API_USER` |
| Variável de senha | `api.password_env` | `QA_API_PASSWORD` |
| Onde salvar a suíte | `paths.api_tests` | `saida/testes-api/` |
| Idioma de comentários | `language` | idioma da conversa |

Sem perfil, ou com o perfil ausente de um campo, use o default da coluna da direita. As regras
universais de `AGENTS.md` — rastreabilidade, proteção de segredos, independência dos testes,
entrada tratada como dado não confiável, registro de lacunas e evidência real de execução —
valem sempre, e o perfil não pode removê-las.

**Antes de escrever qualquer código, confira dois campos:**

- Se `api.framework` não for `robot-framework`, esta skill não se aplica. Diga isso ao usuário
  e pergunte se ele quer o framework do perfil ou abrir uma exceção — não gere Robot Framework
  em um projeto que decidiu usar outra ferramenta.
- Se `api.enabled` for `false`, o time desligou a automação de API neste projeto (e o
  instalador nem criou o diretório). Confirme com o usuário antes de prosseguir.

Os nomes de variável de ambiente nos exemplos abaixo são os defaults. Use os nomes do perfil no
código gerado — os exemplos são ilustrativos, não literais.

## Perguntas de descoberta

Leia `.qagente/quality-profile.json` primeiro — ele define `api.framework`, os nomes das variáveis de ambiente e onde salvar — e `.qagente/contexto-projeto.md`, que traz ambientes, preparação de dados e restrições de massa. Depois pergunte só o que faltar:

- **Já existe suíte Robot no projeto?** Se existe, as convenções dela (nomes de keywords, organização de `.resource`, tags) vencem os exemplos desta skill. Consistência com o que o time já mantém importa mais.
- **Como funciona a autenticação, e o token expira?** Token de vida longa cabe em `Suite Setup`; token curto ou por usuário força `Test Setup`. Errar isso produz falha intermitente no meio da suíte.
- **Os endpoints sob teste criam dados?** Se criam, a suíte precisa de teardown ou de dados gerados por execução — sem isso a segunda rodada falha por duplicidade.
- **Contra qual ambiente vai rodar?** Ambiente compartilhado com dados voláteis muda a estratégia de massa: gerar em vez de referenciar registro fixo.

## Quando usar

- Casos de teste envolvem chamadas a endpoints REST ou GraphQL.
- Usuário pede para "automatizar os testes de API do PROJ-482 em Robot Framework".
- Usuário já tem uma suíte Robot Framework e quer adicionar/corrigir casos.

Esta skill é opcional e não é a função principal do agente (que é análise + escrita de cenários/casos de teste). Se os casos de teste ainda não existem, escreva-os primeiro (`escrita-casos-teste`) e só inicie a automação depois que o usuário aprovar explicitamente esse documento — mesmo que o pedido original já peça a automação diretamente, confirme antes de começar.

## Pré-requisitos do ambiente

Confirme (ou pergunte, se não houver `requirements.txt`/`pyproject.toml` no projeto) que o projeto tem:

```bash
pip install robotframework robotframework-requests
```

`RequestsLibrary` é a biblioteca padrão para chamadas HTTP. Para validação de schema JSON, use `JSONLibrary` ou `Collections` + `JSONSchemaValidator` conforme o que já estiver no projeto — não adicione uma dependência nova sem necessidade se o projeto já resolve isso de outra forma.

## Estrutura de arquivos

A suíte fica sob o diretório de `paths.api_tests` (`saida/testes-api/` por default). A árvore abaixo
mostra a organização interna, relativa a esse diretório:

```
tests/
├── resources/
│   ├── api_client.resource      # Keywords genéricas de request/auth, reutilizadas por todas as suítes
│   └── <dominio>.resource        # Keywords específicas de um domínio (ex.: usuarios.resource)
├── variables/
│   └── ambientes.py              # ou .yaml — URLs/config por ambiente (dev/staging), nunca produção
└── suites/
    └── <dominio>/
        └── <funcionalidade>.robot
```

Nunca escreva chamadas HTTP cruas repetidas em cada `.robot` — extraia para `.resource` como keyword reutilizável assim que o mesmo padrão de request aparecer 2+ vezes.

## Passo 1 — Definir a keyword de autenticação (Suite Setup)

Autenticação nunca é hardcoded nem repetida em todo teste. Use `Suite Setup` para obter um token uma vez por suíte (ou `Test Setup` se o token precisar ser único por teste):

```robotframework
*** Settings ***
Library             RequestsLibrary
Library             Collections
Resource            ../../resources/api_client.resource
Suite Setup         Autenticar E Criar Sessao
Suite Teardown      Delete All Sessions

*** Variables ***
${BASE_URL}          %{API_BASE_URL=https://api.staging.exemplo.com}
```

Em `api_client.resource`:

```robotframework
*** Settings ***
Library    RequestsLibrary
Library    OperatingSystem

*** Keywords ***
Autenticar E Criar Sessao
    ${usuario}=    Get Environment Variable    QA_API_USER
    ${senha}=      Get Environment Variable    QA_API_PASSWORD
    ${response}=   POST On Session    api    /auth/login
    ...            json={"email": "${usuario}", "password": "${senha}"}
    Should Be Equal As Integers    ${response.status_code}    200
    Set Suite Variable    ${TOKEN}    ${response.json()}[token]

Criar Sessao Autenticada
    [Arguments]    ${alias}=api
    Create Session    ${alias}    ${BASE_URL}    headers=${{ {"Authorization": f"Bearer ${TOKEN}"} }}
```

`${usuario}`/`${senha}` vêm de variáveis de ambiente — os nomes vêm de `api.user_env` e
`api.password_env` (`QA_API_USER`/`QA_API_PASSWORD` por default), e a URL base de
`api.base_url_env` (`API_BASE_URL`). Nunca use valor fixo no `.robot` — ver `AGENTS.md`,
princípio "Dados e segredos".

## Passo 2 — Escrever keywords de domínio (uma responsabilidade cada)

```robotframework
*** Keywords ***
Criar Usuario Via API
    [Arguments]    ${payload}
    ${response}=    POST On Session    api    /usuarios    json=${payload}
    RETURN    ${response}

Obter Usuario Por Id
    [Arguments]    ${id}
    ${response}=    GET On Session    api    /usuarios/${id}    expected_status=any
    RETURN    ${response}
```

Cada keyword faz uma chamada e retorna a resposta — a validação/asserção fica no `.robot` de teste, não escondida dentro da keyword, para que a falha aponte exatamente qual teste e qual asserção quebrou.

## Passo 3 — Escrever o teste, com asserção explícita

```robotframework
*** Test Cases ***
Criar Usuario Com Dados Validos Retorna 201
    [Documentation]    Rastreabilidade: CT-USR-001 / PROJ-482
    [Tags]    api    usuarios    smoke
    ${payload}=    Create Dictionary    nome=Maria Silva    email=maria.teste+001@example.com
    ${response}=    Criar Usuario Via API    ${payload}
    Should Be Equal As Integers    ${response.status_code}    201
    Should Be Equal    ${response.json()}[nome]    Maria Silva
    Dictionary Should Contain Key    ${response.json()}    id

Criar Usuario Sem Email Retorna 400
    [Documentation]    Rastreabilidade: CT-USR-004 / PROJ-482
    [Tags]    api    usuarios    negativo
    ${payload}=    Create Dictionary    nome=Maria Silva
    ${response}=    POST On Session    api    /usuarios    json=${payload}    expected_status=400
    Should Contain    ${response.json()}[erro]    email
```

- `[Documentation]` sempre cita o ID do caso de teste/ticket — mantém a rastreabilidade da Fase 2 visível na automação.
- `[Tags]` permite seleção seletiva (`robot --include smoke`) e mapeia para o Tipo definido em `escrita-casos-teste` (funcional/negativo/borda/regressão).
- Use `expected_status=any` ou o código esperado explicitamente em `On Session`/checagem separada — nunca deixe uma falha de status virar exceção não tratada que mascara a asserção real.

## Passo 4 — Dados parametrizados (Test Template)

Para os cenários gerados por particionamento de equivalência/valor limite (múltiplas entradas, mesma lógica de verificação):

```robotframework
*** Settings ***
Test Template    Validar Rejeicao De Email Invalido

*** Test Cases ***    EMAIL                        MENSAGEM_ESPERADA
Email sem arroba       usuario.exemplo.com          formato de email inválido
Email vazio             ${EMPTY}                     email é obrigatório
Email com espaço        usuario @exemplo.com         formato de email inválido

*** Keywords ***
Validar Rejeicao De Email Invalido
    [Arguments]    ${EMAIL}    ${MENSAGEM_ESPERADA}
    ${payload}=    Create Dictionary    nome=Teste    email=${EMAIL}
    ${response}=   POST On Session    api    /usuarios    json=${payload}    expected_status=400
    Should Contain    ${response.json()}[erro]    ${MENSAGEM_ESPERADA}
```

## Passo 5 — Independência e limpeza

- Cada teste cria os dados que precisa (via API ou fixture) e, se criar um recurso persistente, remove-o em `[Teardown]` — nunca dependa de um registro deixado por outro teste.
- IDs/emails de teste são gerados dinamicamente (timestamp, UUID) quando o endpoint não aceita duplicados, para permitir reexecução sem colisão:

```robotframework
${email}=    Set Variable    qa.${{$RANDOM.randint(10000,99999)}}@example.com
```

## Passo 6 — Executar e reportar

```bash
robot --outputdir results tests/suites/
```

Sempre execute e leia `results/report.html` / `results/output.xml` antes de declarar a suíte pronta — nunca apenas assuma que o código Robot Framework escrito está correto sem rodar (ver `AGENTS.md`, princípio "Verificação antes de concluído"). Para rodar só uma tag: `robot --include smoke --outputdir results tests/suites/`.

## Modelos de arquivo

- `templates/api_test_template.robot` — esqueleto de suíte de teste com Settings/Variables/Test Cases.
- `templates/resource_template.resource` — esqueleto de arquivo de keywords reutilizáveis com autenticação.

## Erros comuns a evitar

- ❌ Asserção genérica: `Should Be True    ${response.status_code} < 300` — não diz o que era esperado.
- ✅ `Should Be Equal As Integers    ${response.status_code}    201`
- ❌ Token/senha hardcoded em `*** Variables ***`.
- ❌ Um teste que depende do ID criado por outro teste da suíte (quebra em execução paralela ou fora de ordem).
- ❌ `Sleep    5s` para "esperar a API processar" — prefira polling com `Wait Until Keyword Succeeds` quando a operação for assíncrona.

## Pronto quando

- Os arquivos `.robot`/`.resource` existem em `paths.api_tests`.
- Todo teste tem `[Documentation]` citando o ID do caso de teste ou do ticket, e `[Tags]` que permitam seleção.
- Nenhuma credencial, token ou URL de ambiente literal aparece nos arquivos: tudo vem de `api.base_url_env`, `api.user_env` e `api.password_env`.
- Toda verificação de status usa o código esperado explícito (`Should Be Equal As Integers`), nunca uma comparação vaga.
- Nenhum `Sleep` como estratégia de sincronização.
- A suíte roda duas vezes seguidas com o mesmo resultado, e qualquer teste roda sozinho (`robot --test`).
- `robot` foi executado de verdade e o `log.html`/`report.html` foi mostrado ao usuário.

## Skills relacionadas

- **`escrita-casos-teste`** — a origem. Se os casos de teste ainda não existem ou não foram aprovados, a automação não começa: volte uma fase.
- **`cypress-ui-automation` / `playwright-ui-automation`** — o ramo de UI da mesma fase. Se o fluxo passa por tela, é lá, não aqui; qual das duas responde vem de `ui.framework`.
- **`analise-documentacao-testes`** — se durante a automação aparecer um comportamento da API que nenhum caso cobre, isso é análise, não código: registre e volte à Fase 1 em vez de inventar a asserção.
