*** Settings ***
Documentation       Suíte de testes de API para [nome do domínio/funcionalidade].
...                  Rastreabilidade: [ticket/PRD de origem]
Library              RequestsLibrary
Library              Collections
Resource             ../../resources/api_client.resource
Suite Setup          Autenticar E Criar Sessao
Suite Teardown       Delete All Sessions

*** Test Cases ***
[Nome Do Teste] Retorna [Status Esperado]
    [Documentation]    Rastreabilidade: [ID do caso de teste]
    [Tags]    api    [dominio]    [smoke|regressao|negativo]
    ${payload}=    Create Dictionary    campo=valor
    ${response}=    POST On Session    api    /recurso    json=${payload}    expected_status=any
    Should Be Equal As Integers    ${response.status_code}    201
    Should Be Equal    ${response.json()}[campo]    valor
