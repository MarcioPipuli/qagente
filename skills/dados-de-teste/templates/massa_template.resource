*** Settings ***
Documentation    Massa de teste em Robot Framework — fábricas, sequência e limpeza garantida.
...
...              Adapte à terminologia do domínio declarada em `.qagente/contexto-projeto.md`.
...              NUNCA escreva usuário ou senha literais aqui: eles vêm das variáveis de
...              ambiente declaradas em `api.user_env` e `api.password_env` no perfil.

Library          RequestsLibrary
Library          Collections
Library          String
Library          OperatingSystem
Library          DateTime


*** Variables ***
# Credenciais e endereço: sempre do ambiente, nunca literais no repositório.
${BASE_URL}            %{API_BASE_URL}
${QA_USER}             %{QA_API_USER}
${QA_PASSWORD}         %{QA_API_PASSWORD}

# Sufixo único por execução: evita colisão de campo único entre execuções paralelas.
${EXECUCAO}            %{TEST_RUN_ID=local}

# Data fixa da massa. Congelar aqui é o que torna a asserção repetível.
# Nunca use `Get Current Date` num valor sobre o qual o teste vai afirmar.
${DATA_BASE}           2026-01-15T12:00:00.000Z

@{TEXTOS_DE_BORDA}     ${EMPTY}    ${SPACE}${SPACE}    Ação e acentuação    <script>alert(1)</script>    ' OR 1=1 --
@{DATAS_DE_BORDA}      2026-01-01T00:00:00.000Z    2026-01-31T23:59:59.999Z    2028-02-29T12:00:00.000Z


*** Keywords ***
Gerar Sufixo Unico
    [Documentation]    Sequência por execução para todo campo único (e-mail, código, documento).
    ${aleatorio}=    Generate Random String    6    [NUMBERS]
    RETURN    ${EXECUCAO}-${aleatorio}

Criar Payload De Usuario
    [Documentation]    Padrões sensatos; o teste sobrescreve só o campo que investiga.
    [Arguments]    ${perfil}=comum    ${ativo}=${TRUE}
    ${sufixo}=    Gerar Sufixo Unico
    ${payload}=    Create Dictionary
    ...    email=usuario-${sufixo}@teste.exemplo.com
    ...    nome=Usuário de Teste ${sufixo}
    ...    perfil=${perfil}
    ...    ativo=${ativo}
    ...    criadoEm=${DATA_BASE}
    RETURN    ${payload}

Criar Payload De Usuario Admin
    [Documentation]    Variante nomeada — substitui um arquivo de massa por combinação.
    ${payload}=    Criar Payload De Usuario    perfil=admin
    RETURN    ${payload}

Criar Payload De Pedido
    [Documentation]    Associação: o pedido constrói o próprio usuário quando não recebe um.
    [Arguments]    ${usuario_id}=${NONE}    ${status}=pendente
    ${sufixo}=    Gerar Sufixo Unico
    IF    $usuario_id is None
        ${usuario}=    Criar Usuario Via API
        ${usuario_id}=    Set Variable    ${usuario}[id]
    END
    ${item}=    Create Dictionary    sku=SKU-${sufixo}    quantidade=${1}    precoUnitario=${100.0}
    ${payload}=    Create Dictionary
    ...    codigo=PED-${sufixo}
    ...    usuarioId=${usuario_id}
    ...    itens=${{ [$item] }}
    ...    status=${status}
    RETURN    ${payload}

Criar Usuario Via API
    [Documentation]    Cria a massa e registra o ID para a limpeza no teardown.
    [Arguments]    ${perfil}=comum
    ${payload}=    Criar Payload De Usuario    perfil=${perfil}
    ${resposta}=    POST    ${BASE_URL}/usuarios    json=${payload}
    Should Be Equal As Integers    ${resposta.status_code}    201
    ${corpo}=    Set Variable    ${resposta.json()}
    Registrar Para Limpeza    usuarios    ${corpo}[id]
    RETURN    ${corpo}

Registrar Para Limpeza
    [Documentation]    Acumula o que foi criado, para remover na ordem inversa da criação.
    [Arguments]    ${recurso}    ${id}
    ${criados}=    Get Variable Value    ${RECURSOS_CRIADOS}    @{EMPTY}
    ${criados}=    Create List    @{criados}    ${recurso}/${id}
    Set Test Variable    ${RECURSOS_CRIADOS}    ${criados}

Limpar Massa Criada
    [Documentation]    Vai no [Teardown] do teste — roda mesmo quando o teste falha.
    ...                Um passo final solto seria pulado pela falha; teardown não é.
    ${criados}=    Get Variable Value    ${RECURSOS_CRIADOS}    @{EMPTY}
    ${invertido}=    Copy List    ${criados}
    Reverse List    ${invertido}
    FOR    ${caminho}    IN    @{invertido}
        Run Keyword And Ignore Error    DELETE    ${BASE_URL}/${caminho}
    END
    Set Test Variable    ${RECURSOS_CRIADOS}    @{EMPTY}


*** Comments ***
Uso típico numa suíte:

    *** Settings ***
    Resource     massa_template.resource
    Test Teardown    Limpar Massa Criada

    *** Test Cases ***
    Validar Que Usuario Admin Acessa O Relatorio
        ${usuario}=    Criar Usuario Via API    perfil=admin
        ...
