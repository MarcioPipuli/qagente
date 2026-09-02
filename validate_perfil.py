#!/usr/bin/env python3
"""Valida o perfil de qualidade — `.qagente/quality-profile.json` ou um perfil embarcado.

Primeiro dos três validadores do harness, e o único que roda nos dois lados: o instalador
o importa (toda instalação valida o perfil antes de copiar qualquer coisa) e o agente o
chama no projeto instalado, ao fim da entrevista da skill `configuracao-do-projeto`.

Ele mora em arquivo próprio exatamente por causa do segundo lado. Enquanto a validação era
uma função dentro de `install.py`, a única forma de chamá-la era `install.py
--validate-profile` — e o instalador não se copia para o projeto, então o agente saía
procurando um arquivo que não existe ali. Agora o instalador copia este arquivo para
`.qagente/bin/`, e a skill cita um caminho que existe.

Uso:
    python validate_perfil.py                       Valida o perfil do projeto (.qagente/)
    python validate_perfil.py <caminho.json>        Valida um arquivo específico
    python validate_perfil.py <nome>                Valida um perfil embarcado (profiles/)

Severidade: 'erro' impede a instalação — o valor não significa mais o que a skill diz;
'aviso' é reportado e o default entra no lugar. Sai com 1 se houver erro.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath

# No clone do harness este arquivo fica na raiz, com `profiles/` ao lado. Instalado, ele fica
# em `.qagente/bin/`, e o vizinho que importa é `../quality-profile.json`.
BASE_DIR = Path(__file__).resolve().parent
PROFILES_DIR = BASE_DIR / "profiles"
PERFIL_DO_PROJETO = "quality-profile.json"

SUPPORTED_PROFILE_VERSIONS = ("1.0",)

# Fallback usado apenas quando o perfil não define `paths` utilizáveis.
DEFAULT_IO_PATHS = {
    "input": "entrada",
    "scenarios": "saida/cenarios",
    "test_cases": "saida/casos-de-teste",
    "api_tests": "saida/testes-api",
    "ui_tests": "saida/testes-ui",
}

# Saídas das skills de apoio. Reconhecidas e validadas como caminho, mas fora de
# DEFAULT_IO_PATHS de propósito: o instalador não cria pasta para artefato que não
# corresponde a uma fase (ver AGENTS.md, "Entradas e saídas"). Quem declara a chave
# ganha a pasta; quem não declara usa o fallback documentado em cada skill.
OPTIONAL_IO_PATHS = ("risk_matrix", "reviews")

REQUIRED_KEYS = ("profile_version", "profile_name", "language", "workflow", "paths")

# Invariantes de AGENTS.md: o perfil não pode desligá-las. Declarar `false` aqui não
# desativa nada — só cria uma expectativa falsa, então vira aviso.
WORKFLOW_KEYS = (
    "require_traceability",
    "require_approval_before_automation",
    "require_execution_evidence",
)

CONVENTION_KEYS = (
    "gherkin_language",
    "scenario_title_prefix",
    "test_id_pattern",
    "scenario_outline_threshold",
    "stability_runs",
    "quarantine_max_days",
)

# Convenções numéricas: (chave, mínimo aceitável, faixa esperada, razão do aviso fora dela).
# O mínimo é erro — abaixo dele o número não significa mais o que a skill diz. A faixa é só
# aviso: é decisão do time, e o instalador não sabe do contexto dele.
CONVENTION_NUMBERS = (
    ("scenario_outline_threshold", 2, (2, 10), "acima disso o Esquema do Cenário quase nunca é usado"),
    ("stability_runs", 1, (10, 500), "poucas execuções não distinguem correção de sorte"),
    ("quarantine_max_days", 1, (1, 30), "quarentena longa vira permanente, que é o que a regra evita"),
)

ENV_VAR_KEYS = ("base_url_env", "user_env", "password_env")

ENV_VAR_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def log(msg: str) -> None:
    print(msg)


def _texto_nao_vazio(valor: object) -> bool:
    return isinstance(valor, str) and bool(valor.strip())


def _inteiro(valor: object) -> bool:
    """`True` só para inteiro de verdade. `bool` é subclasse de `int` e não conta aqui."""
    return isinstance(valor, int) and not isinstance(valor, bool)


def _validar_caminho(valor: str) -> str | None:
    """Devolve a razão pela qual o caminho é inválido, ou None se estiver ok."""
    bruto = valor.strip().replace("\\", "/")
    if PurePosixPath(bruto).is_absolute() or PureWindowsPath(bruto).is_absolute():
        return "caminho absoluto — os caminhos do perfil são relativos à raiz do projeto"
    partes = PurePosixPath(bruto.strip("/")).parts
    if not partes:
        return "caminho vazio"
    if ".." in partes:
        return "escapa da raiz do projeto"
    return None


def _validar_secao_automacao(dados: dict, secao: str, problemas: list[tuple[str, str, str]]) -> None:
    config = dados.get(secao)
    if config is None:
        return
    if not isinstance(config, dict):
        problemas.append(("erro", secao, "precisa ser um objeto"))
        return

    habilitado = config.get("enabled")
    if habilitado is not None and not isinstance(habilitado, bool):
        problemas.append(("erro", f"{secao}.enabled", f"precisa ser true ou false (recebido: {habilitado!r})"))

    framework = config.get("framework")
    if framework is not None and not _texto_nao_vazio(framework):
        problemas.append(("erro", f"{secao}.framework", "precisa ser um texto não vazio"))
    elif habilitado is True and framework is None:
        problemas.append(("erro", f"{secao}.framework", "obrigatório quando a fase está habilitada"))

    for chave in ENV_VAR_KEYS:
        valor = config.get(chave)
        if valor is None:
            continue
        if not _texto_nao_vazio(valor):
            problemas.append(("erro", f"{secao}.{chave}", "precisa ser um texto não vazio"))
        elif not ENV_VAR_RE.match(valor):
            problemas.append(
                ("aviso", f"{secao}.{chave}", f"'{valor}' não parece nome de variável de ambiente (MAIÚSCULAS_COM_UNDERSCORE)")
            )


def validate_profile(dados: dict) -> list[tuple[str, str, str]]:
    """Valida o perfil e devolve [(severidade, campo, mensagem)].

    'erro' impede a instalação; 'aviso' é reportado e a instalação segue com os defaults.
    """
    problemas: list[tuple[str, str, str]] = []

    faltando = sorted(set(REQUIRED_KEYS) - dados.keys())
    if faltando:
        problemas.append(("erro", "perfil", f"faltam campos obrigatórios: {', '.join(faltando)}"))

    versao = dados.get("profile_version")
    if versao is not None and versao not in SUPPORTED_PROFILE_VERSIONS:
        suportadas = ", ".join(SUPPORTED_PROFILE_VERSIONS)
        problemas.append(("aviso", "profile_version", f"'{versao}' não é reconhecida (suportadas: {suportadas})"))

    for chave in ("profile_name", "language", "artifact_format", "risk_method"):
        valor = dados.get(chave)
        if valor is not None and not _texto_nao_vazio(valor):
            problemas.append(("erro", chave, "precisa ser um texto não vazio"))

    niveis = dados.get("risk_levels")
    if niveis is not None:
        if not isinstance(niveis, list) or not niveis:
            problemas.append(("erro", "risk_levels", "precisa ser uma lista não vazia"))
        elif not all(_texto_nao_vazio(n) for n in niveis):
            problemas.append(("erro", "risk_levels", "todos os níveis precisam ser textos não vazios"))
        elif len({n.lower() for n in niveis}) != len(niveis):
            problemas.append(("erro", "risk_levels", "há níveis duplicados"))
        elif len(niveis) < 2:
            problemas.append(("aviso", "risk_levels", "uma escala de um nível só não prioriza nada"))

    fluxo = dados.get("workflow")
    if fluxo is not None:
        if not isinstance(fluxo, dict):
            problemas.append(("erro", "workflow", "precisa ser um objeto"))
        else:
            for chave, valor in fluxo.items():
                if chave not in WORKFLOW_KEYS:
                    problemas.append(("aviso", f"workflow.{chave}", "chave desconhecida — será ignorada"))
                elif not isinstance(valor, bool):
                    problemas.append(("erro", f"workflow.{chave}", f"precisa ser true ou false (recebido: {valor!r})"))
                elif valor is False:
                    problemas.append(
                        ("aviso", f"workflow.{chave}", "é invariante de AGENTS.md e não pode ser desligada; o false será ignorado")
                    )

    caminhos = dados.get("paths")
    if caminhos is not None:
        if not isinstance(caminhos, dict):
            problemas.append(("erro", "paths", "precisa ser um objeto"))
        else:
            for chave, valor in caminhos.items():
                if chave not in DEFAULT_IO_PATHS and chave not in OPTIONAL_IO_PATHS:
                    conhecidas = ", ".join(DEFAULT_IO_PATHS)
                    opcionais = ", ".join(OPTIONAL_IO_PATHS)
                    problemas.append(
                        (
                            "aviso",
                            f"paths.{chave}",
                            f"chave desconhecida (esperadas: {conhecidas}; opcionais: {opcionais})",
                        )
                    )
                if not _texto_nao_vazio(valor):
                    problemas.append(("aviso", f"paths.{chave}", f"valor inválido ({valor!r}) — será ignorado"))
                else:
                    razao = _validar_caminho(valor)
                    if razao:
                        problemas.append(("aviso", f"paths.{chave}", f"{razao} — será ignorado"))

    convencoes = dados.get("conventions")
    if convencoes is not None:
        if not isinstance(convencoes, dict):
            problemas.append(("erro", "conventions", "precisa ser um objeto"))
        else:
            for chave in convencoes:
                if chave not in CONVENTION_KEYS:
                    problemas.append(("aviso", f"conventions.{chave}", "chave desconhecida — será ignorada"))
            idioma = convencoes.get("gherkin_language")
            if idioma is not None and not (isinstance(idioma, str) and re.fullmatch(r"[a-z]{2}(-[A-Za-z]{2})?", idioma)):
                problemas.append(("aviso", "conventions.gherkin_language", f"'{idioma}' não parece um código de idioma do Gherkin (ex.: pt, en)"))
            prefixo = convencoes.get("scenario_title_prefix")
            if prefixo is not None and not isinstance(prefixo, str):
                problemas.append(("erro", "conventions.scenario_title_prefix", "precisa ser texto (use \"\" para nenhum prefixo)"))
            padrao = convencoes.get("test_id_pattern")
            if padrao is not None:
                if not _texto_nao_vazio(padrao):
                    problemas.append(("erro", "conventions.test_id_pattern", "precisa ser um texto não vazio"))
                elif "{NUMBER}" not in padrao:
                    problemas.append(("aviso", "conventions.test_id_pattern", f"'{padrao}' não contém {{NUMBER}} — os IDs podem colidir"))

            for chave, minimo, (piso, teto), razao in CONVENTION_NUMBERS:
                valor = convencoes.get(chave)
                if valor is None:
                    continue
                if not _inteiro(valor):
                    problemas.append(("erro", f"conventions.{chave}", f"precisa ser um número inteiro (recebido: {valor!r})"))
                elif valor < minimo:
                    problemas.append(("erro", f"conventions.{chave}", f"precisa ser {minimo} ou mais (recebido: {valor})"))
                elif not (piso <= valor <= teto):
                    problemas.append(("aviso", f"conventions.{chave}", f"{valor} está fora da faixa usual ({piso}-{teto}) — {razao}"))

    for secao in ("api", "ui"):
        _validar_secao_automacao(dados, secao, problemas)

    return problemas


def report_problems(problemas: list[tuple[str, str, str]]) -> int:
    """Imprime os problemas e devolve a quantidade de erros."""
    if not problemas:
        log("  nenhum problema encontrado")
        return 0
    erros = 0
    for severidade, campo, mensagem in problemas:
        log(f"  {severidade:5} {campo}: {mensagem}")
        erros += severidade == "erro"
    return erros


def localizar_perfil(profile_name: str | None) -> Path | None:
    """Resolve o argumento em um arquivo de perfil, ou None se não achar.

    Sem argumento, procura o perfil do projeto: primeiro ao lado deste arquivo (o caso do
    validador instalado em `.qagente/bin/`), depois subindo a partir do diretório atual —
    assim o comando funciona de qualquer subpasta do projeto.
    """
    if profile_name:
        candidate = Path(profile_name)
        if candidate.is_file():
            return candidate
        embarcado = PROFILES_DIR / f"{profile_name}.json"
        return embarcado if embarcado.is_file() else None

    vizinho = BASE_DIR.parent / PERFIL_DO_PROJETO
    if vizinho.is_file():
        return vizinho
    for pasta in [Path.cwd(), *Path.cwd().parents]:
        candidato = pasta / ".qagente" / PERFIL_DO_PROJETO
        if candidato.is_file():
            return candidato
    return None


def run_validation(profile_name: str | None = None) -> int:
    """Valida um perfil e devolve o código de saída (0 = sem erros)."""
    path = localizar_perfil(profile_name)
    if path is None:
        if profile_name:
            log(f"Erro: perfil não encontrado: {profile_name}")
        else:
            log(f"Erro: nenhum {PERFIL_DO_PROJETO} encontrado em .qagente/ a partir de {Path.cwd()}")
            log("Passe o caminho do arquivo, ou rode o instalador para criá-lo.")
        return 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        log(f"Erro: perfil inválido ({path}): {exc}")
        return 1
    if not isinstance(data, dict):
        log(f"Erro: perfil inválido ({path}): o conteúdo precisa ser um objeto JSON.")
        return 1

    log(f"== Validação do perfil ({path}) ==")
    problemas = validate_profile(data)
    erros = report_problems(problemas)
    avisos = len(problemas) - erros
    log("")
    log(f"{erros} erro(s), {avisos} aviso(s).")
    if erros:
        log("Erros impedem a instalação. Avisos são aplicados como default e não a impedem.")
    return 1 if erros else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida um perfil de qualidade do QAGente.")
    parser.add_argument(
        "perfil",
        nargs="?",
        metavar="CAMINHO_OU_NOME",
        help="Arquivo JSON ou nome de perfil embarcado. Sem isto, usa o perfil do projeto.",
    )
    args = parser.parse_args()
    return run_validation(args.perfil)


if __name__ == "__main__":
    sys.exit(main())
