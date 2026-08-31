#!/usr/bin/env python3
"""Valida a estrutura das skills do QAGente.

Irmão do `validate_profile` do instalador: aquele valida a configuração do time, este
valida o conteúdo que o agente lê como instrução. Um frontmatter com o `name` errado, um
template citado que não existe ou uma referência a uma skill inexistente não quebram o
instalador — fazem o agente procurar arquivo no lugar errado, em silêncio.

Mesmo contrato do instalador: problemas são `(severidade, alvo, mensagem)`, com 'erro'
falhando a validação e 'aviso' apenas reportado.

As seções de formato (`<objetivo>`, perguntas de descoberta, `## Pronto quando`,
`## Skills relacionadas`) são obrigatórias — uma skill sem elas reprova. A exceção está em
`SECOES_DISPENSADAS`, para o que genuinamente não se aplica a uma skill de referência: uma
seção vazia só para satisfazer o validador é pior que a ausência dela.

Uso:
    python validate_skills.py            # erros falham, avisos são reportados
    python validate_skills.py --strict   # avisos também falham
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
SKILLS_DIR = HARNESS / "skills"

MAX_LINHAS_ERRO = 650
MAX_LINHAS_AVISO = 450

CATEGORIAS = {"analise", "escrita", "automacao", "referencia"}

# `Use quando` abre os gatilhos; o anti-gatilho evita que duas skills disputem o mesmo pedido.
ANTI_GATILHOS = ("Não use",)

SECOES_OBRIGATORIAS = (
    "<objetivo>",
    "## Perguntas de descoberta",
    "## Pronto quando",
    "## Skills relacionadas",
)

# Uma skill de referência é consultada dentro de outra fase e não produz artefato próprio:
# não há fluxo de descoberta a percorrer, e uma seção vazia só para satisfazer o validador
# seria pior que a ausência dela.
SECOES_DISPENSADAS = {"referencia": ("## Perguntas de descoberta",)}

# Arquivos onde uma referência `skills/<nome>` é instrução para o agente e precisa resolver.
# Documentos de manutenção do harness (CONTRIBUTING.md) ficam de fora: falam com quem mantém
# o projeto, não com o agente.
ARQUIVOS_COM_REFERENCIAS = ("agent.md", "AGENTS.md", "README.md")

# Exige crase ou parêntese de link: em português "skills/agente" também aparece como
# prosa ("as skills/agente já copiados"), e isso não é um caminho.
REF_SKILL = re.compile(r"[`(]skills/([a-z][a-z0-9-]+)")


def log(msg: str) -> None:
    print(msg)


def parse_frontmatter(conteudo: str) -> dict | None:
    """Lê o frontmatter YAML da skill. Devolve None se estiver ausente ou malformado.

    Suporta só o que as skills usam: pares `chave: valor` no topo e um nível de aninhamento
    indentado (`metadata:`). Evita a dependência de PyYAML, que o harness não tem.
    """
    if not conteudo.startswith("---"):
        return None
    fim = conteudo.find("\n---", 3)
    if fim == -1:
        return None

    dados: dict = {}
    atual: dict | None = None
    for linha in conteudo[3:fim].split("\n"):
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        if ":" not in linha:
            continue
        chave, _, valor = linha.partition(":")
        valor = valor.strip().strip("'").strip('"')
        if linha.startswith((" ", "\t")):
            if atual is not None:
                atual[chave.strip()] = valor
            continue
        if valor:
            dados[chave.strip()] = valor
            atual = None
        else:
            atual = {}
            dados[chave.strip()] = atual
    return dados


def validate_skill(skill_dir: Path, skills_existentes: set[str]) -> list[tuple[str, str, str]]:
    """Valida uma skill e devolve [(severidade, alvo, mensagem)]."""
    problemas: list[tuple[str, str, str]] = []
    nome = skill_dir.name
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.is_file():
        return [("erro", nome, "não tem SKILL.md")]

    conteudo = skill_md.read_text(encoding="utf-8")
    linhas = conteudo.split("\n")

    if len(linhas) > MAX_LINHAS_ERRO:
        problemas.append(("erro", nome, f"{len(linhas)} linhas (máximo {MAX_LINHAS_ERRO})"))
    elif len(linhas) > MAX_LINHAS_AVISO:
        problemas.append(("aviso", nome, f"{len(linhas)} linhas — acima de {MAX_LINHAS_AVISO}, mova código pesado para templates/"))

    frontmatter = parse_frontmatter(conteudo)
    if frontmatter is None:
        return problemas + [("erro", nome, "frontmatter ausente ou malformado")]

    if frontmatter.get("name") != nome:
        problemas.append(("erro", f"{nome}.name", f"frontmatter diz {frontmatter.get('name')!r}, o diretório diz {nome!r}"))

    descricao = frontmatter.get("description", "")
    if not isinstance(descricao, str) or not descricao.strip():
        problemas.append(("erro", f"{nome}.description", "ausente ou vazia — é o que faz o agente escolher esta skill"))
    else:
        if "Use quando" not in descricao:
            problemas.append(("aviso", f"{nome}.description", "sem gatilho explícito ('Use quando ...')"))
        if not any(marca in descricao for marca in ANTI_GATILHOS):
            problemas.append(("aviso", f"{nome}.description", "sem anti-gatilho — duas skills podem disputar o mesmo pedido"))

    if not frontmatter.get("license"):
        problemas.append(("erro", f"{nome}.license", "ausente"))

    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        problemas.append(("erro", f"{nome}.metadata", "ausente"))
    else:
        for campo in ("author", "version"):
            if not metadata.get(campo):
                problemas.append(("erro", f"{nome}.metadata.{campo}", "ausente"))
        categoria = metadata.get("category")
        if not categoria:
            problemas.append(("erro", f"{nome}.metadata.category", f"ausente (esperada uma de: {', '.join(sorted(CATEGORIAS))})"))
        elif categoria not in CATEGORIAS:
            problemas.append(("erro", f"{nome}.metadata.category", f"{categoria!r} fora da lista ({', '.join(sorted(CATEGORIAS))})"))

    # A skill precisa mandar ler o perfil; sem isso o perfil configura o instalador mas não
    # muda o comportamento do agente.
    if "## Configuração" not in conteudo:
        problemas.append(("erro", nome, "sem seção '## Configuração'"))
    if ".qagente/quality-profile.json" not in conteudo:
        problemas.append(("erro", nome, "não manda ler .qagente/quality-profile.json"))
    # Citar o contexto é obrigatório mesmo para quem não o usa: a skill de referência diz
    # explicitamente que não o lê e por quê. O que não pode é o arquivo simplesmente sumir
    # do texto e o agente nunca descobrir que ele existe.
    if ".qagente/contexto-projeto.md" not in conteudo:
        problemas.append(("erro", nome, "não cita .qagente/contexto-projeto.md"))

    categoria_atual = metadata.get("category") if isinstance(metadata, dict) else None
    dispensadas = SECOES_DISPENSADAS.get(categoria_atual, ())
    for secao in SECOES_OBRIGATORIAS:
        if secao not in conteudo and secao not in dispensadas:
            problemas.append(("erro", nome, f"sem '{secao}'"))

    problemas.extend(_validar_templates(skill_dir, conteudo, nome))
    problemas.extend(_validar_referencias(conteudo, f"{nome}/SKILL.md", skills_existentes))
    return problemas


def _validar_templates(skill_dir: Path, conteudo: str, nome: str) -> list[tuple[str, str, str]]:
    """Todo template citado existe, e todo template em disco é citado."""
    problemas: list[tuple[str, str, str]] = []
    citados = set(re.findall(r"templates/([A-Za-z0-9._-]+)", conteudo))
    templates_dir = skill_dir / "templates"
    em_disco = {p.name for p in templates_dir.iterdir() if p.is_file()} if templates_dir.is_dir() else set()

    for arquivo in sorted(citados - em_disco):
        problemas.append(("erro", nome, f"cita templates/{arquivo}, que não existe"))
    for arquivo in sorted(em_disco - citados):
        problemas.append(("aviso", nome, f"templates/{arquivo} existe mas não é citado — o agente nunca vai encontrá-lo"))
    return problemas


def _validar_referencias(conteudo: str, alvo: str, skills_existentes: set[str]) -> list[tuple[str, str, str]]:
    """Toda referência `skills/<nome>` aponta para uma skill que existe."""
    problemas: list[tuple[str, str, str]] = []
    for referencia in sorted(set(REF_SKILL.findall(conteudo))):
        if referencia not in skills_existentes:
            problemas.append(("erro", alvo, f"referencia skills/{referencia}, que não existe"))
    return problemas


def validate_repo(skills_existentes: set[str]) -> list[tuple[str, str, str]]:
    """Checagens que não cabem numa skill isolada."""
    problemas: list[tuple[str, str, str]] = []

    if not skills_existentes:
        return [("erro", "skills/", "nenhuma skill encontrada")]

    for arquivo in ARQUIVOS_COM_REFERENCIAS:
        caminho = HARNESS / arquivo
        if not caminho.is_file():
            problemas.append(("erro", arquivo, "não encontrado"))
            continue
        problemas.extend(_validar_referencias(caminho.read_text(encoding="utf-8"), arquivo, skills_existentes))

    readme = (HARNESS / "README.md").read_text(encoding="utf-8") if (HARNESS / "README.md").is_file() else ""
    roteamento = ""
    for arquivo in ("agent.md", "AGENTS.md"):
        if (HARNESS / arquivo).is_file():
            roteamento += (HARNESS / arquivo).read_text(encoding="utf-8")

    for nome in sorted(skills_existentes):
        if readme and nome not in readme:
            problemas.append(("aviso", "README.md", f"não menciona a skill {nome}"))
        if roteamento and nome not in roteamento:
            problemas.append(("erro", "agent.md/AGENTS.md", f"skill {nome} existe mas nada a roteia"))
    return problemas


def report_problems(problemas: list[tuple[str, str, str]]) -> int:
    """Imprime os problemas e devolve a quantidade de erros."""
    if not problemas:
        log("  nenhum problema encontrado")
        return 0
    erros = 0
    for severidade, alvo, mensagem in sorted(problemas):
        log(f"  {severidade:5} {alvo}: {mensagem}")
        erros += severidade == "erro"
    return erros


def collect_problems() -> list[tuple[str, str, str]]:
    """Roda todas as checagens e devolve os problemas encontrados."""
    if not SKILLS_DIR.is_dir():
        return [("erro", "skills/", f"diretório não encontrado: {SKILLS_DIR}")]
    diretorios = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    existentes = {p.name for p in diretorios}

    problemas: list[tuple[str, str, str]] = []
    for skill_dir in diretorios:
        problemas.extend(validate_skill(skill_dir, existentes))
    problemas.extend(validate_repo(existentes))
    return problemas


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida a estrutura das skills do QAGente.")
    parser.add_argument("--strict", action="store_true", help="trata avisos como erros")
    args = parser.parse_args()

    quantidade = len([p for p in SKILLS_DIR.iterdir() if p.is_dir()]) if SKILLS_DIR.is_dir() else 0
    log(f"== Validação das skills ({quantidade} em {SKILLS_DIR}) ==")

    problemas = collect_problems()
    erros = report_problems(problemas)
    avisos = len(problemas) - erros

    log("")
    log(f"{erros} erro(s), {avisos} aviso(s).")
    if args.strict and avisos:
        log("Modo --strict: avisos também reprovam.")
        return 1
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
