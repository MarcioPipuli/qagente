---
name: robot-framework-api
description: Escreve e organiza testes automatizados de API (REST/GraphQL) em Robot Framework, usando RequestsLibrary, keywords reutilizáveis em arquivos .resource, massa de dados parametrizada e boas práticas de independência/determinismo. Use quando o usuário pedir para automatizar testes de API, escrever testes em Robot Framework, criar uma suíte .robot, validar contrato de endpoint, testar autenticação/autorização de API, ou revisar/corrigir testes Robot Framework existentes. Do NOT use for automação de interface web (use cypress-ui-automation), testes de carga/performance, ou para escrever os casos de teste em si antes de automatizar (use escrita-casos-teste).
license: CC-BY-4.0
metadata:
  author: QAGente
  version: '1.0.0'
---

# Automação de API com Robot Framework

Escreve suítes de teste de API executáveis em Robot Framework a partir de casos de teste já definidos (skill `escrita-casos-teste`) ou diretamente de uma especificação de API. Terceira fase (ramo API) do fluxo QA — ver `AGENTS.md`, na raiz do projeto.

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

`${usuario}`/`${senha}` vêm de variáveis de ambiente (`QA_API_USER`, `QA_API_PASSWORD`), nunca de valor fixo no `.robot` — ver `AGENTS.md`, princípio "Dados e segredos".

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
