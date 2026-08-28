*** Settings ***
Library             RequestsLibrary
Library             Collections
Library             OperatingSystem

*** Variables ***
${BASE_URL}          %{API_BASE_URL=https://api.staging.exemplo.com}

*** Keywords ***
Autenticar E Criar Sessao
    [Documentation]    Autentica via variáveis de ambiente e guarda o token para as chamadas da suíte.
    ${usuario}=    Get Environment Variable    QA_API_USER
    ${senha}=      Get Environment Variable    QA_API_PASSWORD
    Create Session    auth    ${BASE_URL}
    ${response}=    POST On Session    auth    /auth/login
    ...             json=${{ {"email": "${usuario}", "password": "${senha}"} }}
    Should Be Equal As Integers    ${response.status_code}    200
    Set Suite Variable    ${TOKEN}    ${response.json()}[token]
    Create Session    api    ${BASE_URL}    headers=${{ {"Authorization": f"Bearer ${TOKEN}"} }}

Gerar Email De Teste Unico
    [Documentation]    Gera um email único para evitar colisão entre execuções.
    ${sufixo}=    Evaluate    random.randint(10000, 99999)    modules=random
    RETURN    qa.teste+${sufixo}@example.com
