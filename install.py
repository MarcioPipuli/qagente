#!/usr/bin/env python3
"""Instalador do harness QAGente (agent.md + AGENTS.md/CLAUDE.md + skills/) em um projeto Claude Code.

Uso:
    python install.py                               Instala no diretório atual (.)
    python install.py --target /caminho/projeto     Instala em um projeto específico
    python install.py --global                      Instala em ~/.claude (disponível em todos os projetos)
    python install.py --force                       Sobrescreve skills/agente já instalados
    python install.py --symlink                     Usa link simbólico em vez de cópia (skills/agente)
    python install.py --dry-run                     Mostra o que seria feito, sem alterar nada
    python install.py --tool copilot                Instala o adaptador de uma ferramenta
    python install.py --tools claude,cursor         Instala várias ferramentas de uma vez
    python install.py --profile backend-api         Usa um perfil de profiles/ ou um caminho JSON
    python install.py --validate-profile <perfil>   Só valida o perfil e sai, sem instalar

Idempotente: pode ser executado várias vezes. Skills e a definição do agente são
sobrescritas apenas com --force; as regras (AGENTS.md/CLAUDE.md) são mescladas de
forma segura em blocos marcados, sem apagar conteúdo que já exista no projeto alvo.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath

HARNESS_DIR = Path(__file__).resolve().parent
SKILLS_SRC = HARNESS_DIR / "skills"
AGENT_SRC = HARNESS_DIR / "agent.md"
AGENTS_MD_SRC = HARNESS_DIR / "AGENTS.md"
PROFILES_SRC = HARNESS_DIR / "profiles"
ADAPTERS_SRC = HARNESS_DIR / "adapters"
CONTEXTO_SRC = HARNESS_DIR / "contexto" / "contexto-projeto.md"
TEMPLATES_README_SRC = HARNESS_DIR / "templates-do-time" / "README.md"

MARKER_START = "<!-- QAGente:start -->"
MARKER_END = "<!-- QAGente:end -->"

TOOLS = ("claude", "copilot", "cursor", "windsurf")

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

CONVENTION_KEYS = ("gherkin_language", "scenario_title_prefix", "test_id_pattern")

# Templates que o time pode sobrescrever em `.qagente/templates/`, por nome-base. Só layout
# puro entra aqui: a ordem e a existência das seções do artefato. Os templates de automação
# carregam técnica junto com o layout, e `fabrica-dados.js`/`massa_template.resource`
# carregam isolamento e limpeza de massa — sobrescrever esses desligaria uma garantia de
# qualidade em silêncio, o que o CONTRIBUTING.md proíbe. Ver AGENTS.md, "Templates do time".
TEMPLATES_DO_TIME = (
    "cenarios.md",
    "casos-de-teste.md",
    "matriz-risco.md",
    "relatorio-revisao.md",
    "relato-reproducao.md",
    "registro-quarentena.md",
)

ENV_VAR_KEYS = ("base_url_env", "user_env", "password_env")

ENV_VAR_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")

PATH_KEY_LABELS = {
    "input": "entrada",
    "scenarios": "cenários (fase 1)",
    "test_cases": "casos de teste (fase 2)",
    "api_tests": "automação de API (fase 3a)",
    "ui_tests": "automação de UI (fase 3b)",
}


def log(msg: str) -> None:
    print(msg)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Instala o harness QAGente em um projeto Claude Code.")
    parser.add_argument(
        "--tool",
        choices=TOOLS,
        default="claude",
        help="Ferramenta alvo (padrão: claude). Ignorado quando --tools é usado.",
    )
    parser.add_argument(
        "--tools",
        type=str,
        help="Lista separada por vírgulas de ferramentas alvo.",
    )
    parser.add_argument(
        "--profile",
        default="default",
        help="Nome do perfil em profiles/ ou caminho para um arquivo JSON.",
    )
    parser.add_argument(
        "--validate-profile",
        metavar="CAMINHO_OU_NOME",
        help="Valida um perfil e sai, sem instalar nada. Sai com 1 se houver erros.",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=".",
        help="Diretório do projeto alvo (padrão: diretório atual). Ignorado com --global.",
    )
    parser.add_argument(
        "--global",
        dest="is_global",
        action="store_true",
        help="Instala em ~/.claude, disponível para todos os projetos do usuário.",
    )
    parser.add_argument(
        "--symlink",
        action="store_true",
        help="Usa link simbólico em vez de cópia para skills/ e agent.md (requer privilégio no Windows).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobrescreve skills e a definição do agente já instalados anteriormente.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra as ações que seriam feitas sem tocar no sistema de arquivos.",
    )
    return parser.parse_args()


def selected_tools(args: argparse.Namespace) -> list[str]:
    if not args.tools:
        return [args.tool]
    values = [value.strip().lower() for value in args.tools.split(",") if value.strip()]
    invalid = [value for value in values if value not in TOOLS]
    if not values or invalid:
        log(f"Erro: ferramentas inválidas: {', '.join(invalid or values)}")
        sys.exit(2)
    return list(dict.fromkeys(values))


def _texto_nao_vazio(valor: object) -> bool:
    return isinstance(valor, str) and bool(valor.strip())


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


def resolve_profile(profile_name: str) -> tuple[Path, dict]:
    """Localiza e carrega o perfil. Retorna (caminho, conteúdo já parseado)."""
    candidate = Path(profile_name)
    path = candidate if candidate.is_file() else PROFILES_SRC / f"{profile_name}.json"
    if not path.is_file():
        log(f"Erro: perfil não encontrado: {profile_name}")
        sys.exit(1)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        log(f"Erro: perfil inválido ({path}): {exc}")
        sys.exit(1)
    if not isinstance(data, dict):
        log(f"Erro: perfil inválido ({path}): o conteúdo precisa ser um objeto JSON.")
        sys.exit(1)
    problemas = validate_profile(data)
    if problemas:
        log(f"== Validação do perfil ({path.name}) ==")
        if report_problems(problemas):
            log("Instalação interrompida: corrija os erros acima ou escolha outro perfil.")
            sys.exit(1)
        log("")
    return path, data


def disabled_path_keys(profile_data: dict) -> set[str]:
    """Chaves de `paths` cujo diretório não precisa existir porque a fase está desligada no perfil."""
    disabled: set[str] = set()
    for section, key in (("api", "api_tests"), ("ui", "ui_tests")):
        config = profile_data.get(section)
        if isinstance(config, dict) and config.get("enabled") is False:
            disabled.add(key)
    return disabled


def profile_io_dirs(profile_data: dict) -> list[tuple[str, str]]:
    """Retorna [(chave, caminho relativo)] das pastas de entrada/saída definidas pelo perfil.

    Cai para DEFAULT_IO_PATHS quando o perfil não traz `paths` utilizáveis. Caminhos
    absolutos, vazios ou que escapam da raiz do projeto são descartados com aviso.
    """
    paths = profile_data.get("paths")
    if not isinstance(paths, dict) or not paths:
        log("  perfil sem 'paths' utilizável; usando os defaults do QAGente")
        return list(DEFAULT_IO_PATHS.items())

    resolved: list[tuple[str, str]] = []
    seen: set[str] = set()
    for key, value in paths.items():
        if not isinstance(value, str) or not value.strip():
            log(f"  aviso: caminho inválido no perfil, ignorado ({key}: {value!r})")
            continue
        raw = value.strip().replace("\\", "/")
        if PurePosixPath(raw).is_absolute() or PureWindowsPath(raw).is_absolute():
            log(f"  aviso: caminho absoluto ignorado ({key}: {value})")
            continue
        rel = raw.rstrip("/")  # a barra inicial já foi recusada acima como caminho absoluto
        parts = PurePosixPath(rel).parts
        if not parts or ".." in parts:
            log(f"  aviso: caminho fora da raiz do projeto ignorado ({key}: {value})")
            continue
        if rel in seen:
            continue
        seen.add(rel)
        resolved.append((key, rel))

    if not resolved:
        log("  aviso: nenhum caminho do perfil é utilizável; usando os defaults do QAGente")
        return list(DEFAULT_IO_PATHS.items())
    return resolved


def resolve_dirs(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    """Retorna (project_root, skills_dir, agents_dir). No modo --global a raiz é ~/.claude."""
    if args.is_global:
        home = Path.home()
        base = home / ".claude"
        return base, base / "skills", base / "agents"

    target = Path(args.target).resolve()
    if not target.exists():
        log(f"Erro: diretório alvo não existe: {target}")
        sys.exit(1)
    return target, target / ".claude" / "skills", target / ".claude" / "agents"


def ensure_dir(path: Path, dry_run: bool) -> None:
    if dry_run:
        log(f"  [dry-run] mkdir -p {path}")
        return
    path.mkdir(parents=True, exist_ok=True)


def install_entry(src: Path, dst: Path, *, is_dir: bool, symlink: bool, force: bool, dry_run: bool) -> str:
    """Instala um arquivo ou diretório único (skill ou agent.md). Retorna o status."""
    if dst.exists() or dst.is_symlink():
        if not force:
            return "pulado (já existe — use --force para sobrescrever)"
        if dry_run:
            log(f"  [dry-run] remover existente: {dst}")
        else:
            if dst.is_dir() and not dst.is_symlink():
                shutil.rmtree(dst)
            else:
                dst.unlink()

    if dry_run:
        action = "link simbólico" if symlink else "cópia"
        log(f"  [dry-run] {action}: {src} -> {dst}")
        return "instalado (dry-run)"

    ensure_dir(dst.parent, dry_run=False)

    if symlink:
        try:
            dst.symlink_to(src, target_is_directory=is_dir)
            return "instalado (symlink)"
        except OSError as exc:
            log(f"  aviso: symlink falhou ({exc}); copiando em vez disso")

    if is_dir:
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
    return "instalado (cópia)"


def is_skill_dir(path: Path) -> bool:
    """Uma skill e um diretorio com SKILL.md; qualquer outra entrada em skills/ e ignorada."""
    if not path.is_dir() or path.name.startswith((".", "__")):
        return False
    return (path / "SKILL.md").is_file()


def install_skills(skills_dir: Path, *, symlink: bool, force: bool, dry_run: bool) -> None:
    log("\n== Skills ==")
    for src in sorted(SKILLS_SRC.iterdir()):
        name = src.name
        if not is_skill_dir(src):
            if src.is_dir() and not name.startswith((".", "__")):
                log(f"  aviso: diretório sem SKILL.md, ignorado: {name}")
            continue
        dst = skills_dir / name
        status = install_entry(src, dst, is_dir=True, symlink=symlink, force=force, dry_run=dry_run)
        log(f"  {name}: {status} -> {dst}")


def install_agent_definition(agents_dir: Path, *, symlink: bool, force: bool, dry_run: bool) -> None:
    log("\n== Definição do agente ==")
    dst = agents_dir / "qa-especialista.md"
    status = install_entry(AGENT_SRC, dst, is_dir=False, symlink=symlink, force=force, dry_run=dry_run)
    log(f"  qa-especialista: {status} -> {dst}")


def install_profile(
    project_root: Path, profile_path: Path, profile_data: dict, *, force: bool, dry_run: bool
) -> dict:
    """Instala o perfil e retorna o perfil efetivo — o que de fato governa o projeto.

    Quando um perfil já existe e não há --force, ele é preservado e passa a ser o efetivo,
    para que as pastas de entrada/saída não sejam criadas a partir de um perfil descartado.
    """
    log("\n== Perfil de qualidade ==")
    destination = project_root / ".qagente" / "quality-profile.json"
    if destination.exists() and not force:
        log(f"  perfil existente preservado (use --force para substituir) -> {destination}")
        try:
            existing = json.loads(destination.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            log(f"  aviso: perfil existente ilegível ({exc}); usando '{profile_data.get('profile_name')}' para os caminhos")
            return profile_data
        if not isinstance(existing, dict):
            log(f"  aviso: perfil existente não é um objeto JSON; usando '{profile_data.get('profile_name')}' para os caminhos")
            return profile_data
        log(f"  perfil efetivo do projeto: {existing.get('profile_name', '(sem nome)')}")
        return existing
    if dry_run:
        log(f"  [dry-run] copiar perfil: {profile_path} -> {destination}")
        return profile_data
    ensure_dir(destination.parent, dry_run=False)
    shutil.copy2(profile_path, destination)
    log(f"  perfil instalado -> {destination}")
    return profile_data


def install_context(project_root: Path, *, force: bool, dry_run: bool) -> None:
    """Instala o template de contexto do projeto.

    Preservado como o perfil: uma vez preenchido, o conteúdo é do time, e sobrescrever
    apagaria o trabalho de quem respondeu as perguntas. Só `--force` substitui.
    """
    log("\n== Contexto do projeto ==")
    destination = project_root / ".qagente" / "contexto-projeto.md"
    if not CONTEXTO_SRC.is_file():
        log(f"  aviso: template não encontrado, pulado: {CONTEXTO_SRC}")
        return
    if destination.exists() and not force:
        log(f"  contexto existente preservado (use --force para substituir) -> {destination}")
        return
    if dry_run:
        log(f"  [dry-run] copiar contexto: {CONTEXTO_SRC} -> {destination}")
        return
    ensure_dir(destination.parent, dry_run=False)
    shutil.copy2(CONTEXTO_SRC, destination)
    log(f"  template instalado (preencha com os fatos do produto) -> {destination}")


def install_templates(project_root: Path, *, force: bool, dry_run: bool) -> None:
    """Instala o README do diretório de templates do time.

    Diferença deliberada em relação a `install_entry`, que apaga o destino com --force: aqui
    --force troca **só o README**. Os templates que o time colocou no diretório nunca são
    tocados pelo instalador — é o único lugar do harness com essa semântica, e é o ponto
    todo: hoje editar um template e atualizar o harness são mutuamente exclusivos.

    O diretório nasce sem template nenhum. Enquanto o time não colocar um arquivo aqui, cada
    skill usa o template dela; a sobrescrita é opt-in, arquivo por arquivo.
    """
    log("\n== Templates do time ==")
    destination = project_root / ".qagente" / "templates" / "README.md"
    if not TEMPLATES_README_SRC.is_file():
        log(f"  aviso: README não encontrado, pulado: {TEMPLATES_README_SRC}")
        return
    if destination.exists() and not force:
        log(f"  README existente preservado (use --force para atualizar) -> {destination}")
        return
    if dry_run:
        log(f"  [dry-run] copiar README: {TEMPLATES_README_SRC} -> {destination}")
        return
    ensure_dir(destination.parent, dry_run=False)
    shutil.copy2(TEMPLATES_README_SRC, destination)
    sobrescreviveis = ", ".join(TEMPLATES_DO_TIME)
    log(f"  diretório pronto (sobrescrevíveis: {sobrescreviveis}) -> {destination.parent}")


def install_adapter(project_root: Path, tool: str, *, force: bool, dry_run: bool) -> None:
    adapter_dir = ADAPTERS_SRC / tool
    if not adapter_dir.exists():
        log(f"  aviso: adaptador não encontrado: {tool}")
        return

    destinations = {
        "copilot": {
            "copilot-instructions.md": project_root / ".github" / "copilot-instructions.md",
            "qa-especialista.agent.md": project_root / ".github" / "agents" / "qa-especialista.agent.md",
        },
        "cursor": {"qagente.mdc": project_root / ".cursor" / "rules" / "qagente.mdc"},
        "windsurf": {"qagente.md": project_root / ".windsurf" / "rules" / "qagente.md"},
    }
    log(f"\n== Adaptador {tool} ==")
    mapping = destinations[tool]
    for source in sorted(adapter_dir.iterdir()):
        if not source.is_file():
            continue
        destination = mapping.get(source.name)
        if destination is None:
            log(f"  aviso: sem destino mapeado, ignorado: {source.name}")
            continue
        status = install_entry(source, destination, is_dir=False, symlink=False, force=force, dry_run=dry_run)
        log(f"  {source.name}: {status} -> {destination}")


def install_portable_skills(project_root: Path, *, force: bool, dry_run: bool) -> None:
    skills_dir = project_root / ".qagente" / "skills"
    log("\n== Skills portáteis ==")
    install_skills(skills_dir, symlink=False, force=force, dry_run=dry_run)


def merge_block(existing: str, block_body: str) -> tuple[str, bool]:
    """Insere/atualiza o bloco marcado dentro de `existing`. Retorna (novo_conteudo, mudou)."""
    block = f"{MARKER_START}\n{block_body.strip()}\n{MARKER_END}"

    if MARKER_START in existing and MARKER_END in existing:
        start = existing.index(MARKER_START)
        end = existing.index(MARKER_END) + len(MARKER_END)
        new_content = existing[:start] + block + existing[end:]
        return new_content, new_content != existing

    head = existing.rstrip("\n")
    separator = "\n\n" if head else ""
    new_content = f"{head}{separator}{block}\n"
    return new_content, True


def install_rules(project_root: Path, *, dry_run: bool, include_claude: bool) -> None:
    log("\n== Regras (AGENTS.md / CLAUDE.md) ==")
    agents_md_body = AGENTS_MD_SRC.read_text(encoding="utf-8")
    rules_block = "# QA Especialista — Regras (QAGente)\n\n" + agents_md_body

    agents_md_path = project_root / "AGENTS.md"
    existing = agents_md_path.read_text(encoding="utf-8") if agents_md_path.exists() else ""
    new_content, changed = merge_block(existing, rules_block)

    if not changed:
        log(f"  AGENTS.md: já atualizado, nada a fazer -> {agents_md_path}")
    elif dry_run:
        log(f"  [dry-run] escreveria bloco QAGente em: {agents_md_path}")
    else:
        agents_md_path.write_text(new_content, encoding="utf-8")
        verb = "criado" if not existing else "atualizado (bloco QAGente mesclado)"
        log(f"  AGENTS.md: {verb} -> {agents_md_path}")

    if not include_claude:
        return

    claude_md_path = project_root / "CLAUDE.md"
    if not claude_md_path.exists():
        if dry_run:
            log(f"  [dry-run] criaria CLAUDE.md apontando para AGENTS.md -> {claude_md_path}")
        else:
            claude_md_path.write_text("AGENTS.md\n", encoding="utf-8")
            log(f"  CLAUDE.md: criado (ponteiro para AGENTS.md) -> {claude_md_path}")
    else:
        existing_claude = claude_md_path.read_text(encoding="utf-8")
        if "AGENTS.md" in existing_claude:
            log(f"  CLAUDE.md: já referencia AGENTS.md, nada a fazer -> {claude_md_path}")
        else:
            note = f"{MARKER_START}\nVeja também: AGENTS.md (inclui as regras do agente QA Especialista — QAGente).\n{MARKER_END}"
            if dry_run:
                log(f"  [dry-run] adicionaria nota apontando para AGENTS.md em: {claude_md_path}")
            else:
                head = existing_claude.rstrip("\n")
                sep = "\n\n" if head else ""
                claude_md_path.write_text(f"{head}{sep}{note}\n", encoding="utf-8")
                log(f"  CLAUDE.md: nota adicionada apontando para AGENTS.md -> {claude_md_path}")


def install_io_dirs(project_root: Path, profile_data: dict, *, dry_run: bool) -> None:
    log("\n== Pastas de entrada/saída ==")
    disabled = disabled_path_keys(profile_data)
    for key, rel in profile_io_dirs(profile_data):
        label = PATH_KEY_LABELS.get(key, key)
        if key in disabled:
            log(f"  {rel} ({label}): pulada — fase desligada no perfil")
            continue
        dir_path = project_root / rel
        gitkeep = dir_path / ".gitkeep"
        if dir_path.exists():
            log(f"  {rel} ({label}): já existe, nada a fazer -> {dir_path}")
            continue
        if dry_run:
            log(f"  [dry-run] mkdir -p {dir_path} (+ .gitkeep)  [{label}]")
            continue
        ensure_dir(dir_path, dry_run=False)
        gitkeep.write_text("", encoding="utf-8")
        log(f"  {rel} ({label}): criada -> {dir_path}")


def run_validation(profile_name: str) -> int:
    """Valida um perfil e devolve o código de saída (0 = sem erros)."""
    candidate = Path(profile_name)
    path = candidate if candidate.is_file() else PROFILES_SRC / f"{profile_name}.json"
    if not path.is_file():
        log(f"Erro: perfil não encontrado: {profile_name}")
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


def main() -> None:
    args = parse_args()

    if args.validate_profile:
        sys.exit(run_validation(args.validate_profile))

    tools = selected_tools(args)
    profile_path, profile_data = resolve_profile(args.profile)
    project_root, skills_dir, agents_dir = resolve_dirs(args)

    if args.is_global and any(tool != "claude" for tool in tools):
        log("Erro: --global só pode ser usado com a ferramenta claude.")
        sys.exit(2)

    scope = "global (~/.claude)" if args.is_global else f"projeto ({project_root})"
    log(f"Instalando QAGente — escopo: {scope}")
    log(f"Ferramentas: {', '.join(tools)} | Perfil: {profile_path.stem}")
    if args.dry_run:
        log("Modo dry-run: nenhuma alteração será feita no disco.\n")

    if "claude" in tools:
        install_skills(skills_dir, symlink=args.symlink, force=args.force, dry_run=args.dry_run)
        install_agent_definition(agents_dir, symlink=args.symlink, force=args.force, dry_run=args.dry_run)

    if args.is_global:
        log("\n== Regras (AGENTS.md / CLAUDE.md) ==")
        log("  Pulado no modo --global: regras de projeto (AGENTS.md/CLAUDE.md) são instaladas por projeto.")
        log("  Rode sem --global dentro de cada projeto para instalar as regras lá.")
    else:
        install_rules(project_root, dry_run=args.dry_run, include_claude="claude" in tools)
        effective_profile = install_profile(
            project_root, profile_path, profile_data, force=args.force, dry_run=args.dry_run
        )
        install_context(project_root, force=args.force, dry_run=args.dry_run)
        install_templates(project_root, force=args.force, dry_run=args.dry_run)
        if any(tool != "claude" for tool in tools):
            install_portable_skills(project_root, force=args.force, dry_run=args.dry_run)
        for tool in tools:
            if tool != "claude":
                install_adapter(project_root, tool, force=args.force, dry_run=args.dry_run)
        install_io_dirs(project_root, effective_profile, dry_run=args.dry_run)

    log("\nConcluído. Próximos passos:")
    if not args.is_global:
        log("  - Preencha .qagente/contexto-projeto.md: sem ele o agente prioriza por palpite.")
    log('  - Experimente: "Analisa esse PRD e me diz o que precisamos testar."')
    log("  - Veja AGENTS.md para os princípios completos do agente.")


if __name__ == "__main__":
    main()
