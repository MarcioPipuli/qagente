#!/usr/bin/env python3
"""Roda os evals estáticos das skills do QAGente.

O `validate_skills.py` valida a *forma* da skill; este valida o *conteúdo*. Cada caso em
`evals/<skill>-evals.json` é um pedido que o usuário poderia fazer, com os padrões que a
skill precisa ensinar e os que precisa desaconselhar. Sem isso, apagar a regra contra
`cy.wait(3000)` da skill de Cypress não quebra teste nenhum.

Estático significa: a checagem é feita contra o texto da skill, não contra a resposta de um
modelo. É determinístico, roda em CI e não custa chamada de API. Um eval verde não prova que
o agente acertou — prova que a skill continua ensinando o que o caso exige. Modo `--live`
(rodar o prompt num agente e conferir a saída) não está implementado de propósito: exigiria
dependência de rede e de modelo, que o harness não tem.

## Semântica dos dois campos

- `expected_patterns` — a skill precisa **ensinar** isto. Falha se o padrão não aparece no
  corpus (SKILL.md + templates/).
- `anti_patterns` — a skill precisa **desaconselhar** isto. Falha em dois casos: se o padrão
  nunca é mencionado (a skill não avisa contra ele) ou se alguma ocorrência está em contexto
  de recomendação. Uma ocorrência conta como aviso quando a própria linha, uma das três
  acima, ou o título da seção onde ela está carrega marca de negação (`❌`, "nunca", "evite",
  "errado", "em vez de"...).

Essa segunda regra é deliberada. A leitura ingênua — "o anti-padrão não pode aparecer no
texto" — reprova justamente a skill que faz a coisa certa, que é mostrar o erro para ensinar
a evitá-lo.

## Gramática dos padrões

- `A OR B` — alternativa: basta uma das partes casar.
- `.*` em qualquer parte — tratado como expressão regular.
- Qualquer outra coisa — substring, sem diferenciar maiúsculas.

Uso:
    python run_evals.py                      # todas as skills
    python run_evals.py --skill cypress-ui-automation
    python run_evals.py --verbose            # mostra cada caso, não só as falhas
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
SKILLS_DIR = HARNESS / "skills"
EVALS_DIR = HARNESS / "evals"

MIN_CASOS = 8

# Marcas que tornam uma linha um aviso, não uma recomendação.
NEGACOES = (
    "❌", "nunca", "não ", "não use", "não faça", "evite", "evitar", "errado", "erro",
    "frágil", "em vez de", "prefira", "proibido", "jamais", "ruim", "problema",
    "nenhum", "nenhuma",
)

# Títulos de seção que colocam tudo abaixo deles em contexto de aviso.
TITULOS_NEGATIVOS = ("erros comuns", "evitar", "nunca", "anti", "não ")

# Quantas linhas acima da ocorrência ainda contam como contexto (comentário `// ❌` sobre o
# bloco de código, item de lista com a marca na linha anterior).
JANELA = 3


def log(msg: str) -> None:
    print(msg)


def carregar_corpus(skill_dir: Path) -> list[tuple[str, list[str]]]:
    """Devolve [(nome do arquivo, linhas)] com tudo que o agente lê da skill.

    Inclui os templates: eles são copiados para o projeto do usuário, então o que está lá
    dentro é ensinado tanto quanto o que está no SKILL.md.
    """
    arquivos: list[tuple[str, list[str]]] = []
    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        arquivos.append(("SKILL.md", skill_md.read_text(encoding="utf-8").split("\n")))
    templates = skill_dir / "templates"
    if templates.is_dir():
        for path in sorted(p for p in templates.iterdir() if p.is_file()):
            arquivos.append((f"templates/{path.name}", path.read_text(encoding="utf-8").split("\n")))
    return arquivos


def _alternativas(padrao: str) -> list[str]:
    return [parte.strip() for parte in padrao.split(" OR ")] if " OR " in padrao else [padrao]


def _casa_na_linha(alternativa: str, linha: str) -> bool:
    if ".*" in alternativa:
        return re.search(alternativa, linha, re.IGNORECASE) is not None
    return alternativa.lower() in linha.lower()


def ocorrencias(padrao: str, corpus: list[tuple[str, list[str]]]) -> list[tuple[str, int]]:
    """Onde o padrão aparece: [(arquivo, índice da linha)]."""
    achados: list[tuple[str, int]] = []
    for nome, linhas in corpus:
        for i, linha in enumerate(linhas):
            if any(_casa_na_linha(alt, linha) for alt in _alternativas(padrao)):
                achados.append((nome, i))
    return achados


def em_contexto_de_aviso(linhas: list[str], indice: int) -> bool:
    """A ocorrência está desaconselhando, e não recomendando?"""
    janela = linhas[max(0, indice - JANELA) : indice + 1]
    if any(marca in linha.lower() for linha in janela for marca in NEGACOES):
        return True
    for linha in reversed(linhas[:indice]):
        if linha.startswith("#"):
            return any(marca in linha.lower() for marca in TITULOS_NEGATIVOS)
    return False


def avaliar_caso(caso: dict, corpus: list[tuple[str, list[str]]]) -> list[str]:
    """Devolve as falhas do caso. Lista vazia = aprovado."""
    falhas: list[str] = []
    mapa = dict(corpus)

    for padrao in caso.get("expected_patterns", []):
        if not ocorrencias(padrao, corpus):
            falhas.append(f"não ensina {padrao!r}")

    for padrao in caso.get("anti_patterns", []):
        achados = ocorrencias(padrao, corpus)
        if not achados:
            falhas.append(f"não avisa contra {padrao!r}")
            continue
        recomendados = [
            f"{nome}:{i + 1}" for nome, i in achados if not em_contexto_de_aviso(mapa[nome], i)
        ]
        if recomendados:
            falhas.append(f"{padrao!r} aparece sem ressalva em {', '.join(recomendados)}")
    return falhas


def carregar_spec(skill: str) -> tuple[dict | None, str | None]:
    """Devolve (spec, erro)."""
    caminho = EVALS_DIR / f"{skill}-evals.json"
    if not caminho.is_file():
        return None, f"sem spec de eval ({caminho.name})"
    try:
        spec = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"spec inválida: {exc}"
    if not isinstance(spec, dict) or not isinstance(spec.get("evals"), list):
        return None, "spec precisa ser um objeto com a lista 'evals'"
    if spec.get("skill") != skill:
        return None, f"spec diz skill={spec.get('skill')!r}, esperado {skill!r}"
    if len(spec["evals"]) < MIN_CASOS:
        return None, f"{len(spec['evals'])} casos (mínimo {MIN_CASOS})"
    return spec, None


def avaliar_skill(skill: str) -> tuple[int, int, list[str]]:
    """Devolve (aprovados, total, falhas formatadas)."""
    spec, erro = carregar_spec(skill)
    if erro:
        return 0, 0, [f"{skill}: {erro}"]

    corpus = carregar_corpus(SKILLS_DIR / skill)
    if not corpus:
        return 0, 0, [f"{skill}: sem conteúdo para avaliar"]

    aprovados = 0
    falhas: list[str] = []
    for caso in spec["evals"]:
        problemas = avaliar_caso(caso, corpus)
        if problemas:
            for problema in problemas:
                falhas.append(f"{skill}/{caso.get('id', '?')}: {problema}")
        else:
            aprovados += 1
    return aprovados, len(spec["evals"]), falhas


def main() -> int:
    parser = argparse.ArgumentParser(description="Roda os evals estáticos das skills do QAGente.")
    parser.add_argument("--skill", help="avalia só esta skill")
    parser.add_argument("--verbose", action="store_true", help="lista cada skill, não só as falhas")
    args = parser.parse_args()

    if args.skill:
        skills = [args.skill]
    else:
        skills = sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir()) if SKILLS_DIR.is_dir() else []

    if not skills:
        log("Erro: nenhuma skill encontrada.")
        return 1

    log(f"== Evals estáticos ({len(skills)} skill(s)) ==")
    total_aprovados = total_casos = 0
    todas_falhas: list[str] = []

    for skill in skills:
        aprovados, total, falhas = avaliar_skill(skill)
        total_aprovados += aprovados
        total_casos += total
        todas_falhas.extend(falhas)
        if args.verbose or falhas:
            marca = "ok " if not falhas else "FALHA"
            log(f"  {marca} {skill}: {aprovados}/{total}")

    for falha in todas_falhas:
        log(f"  - {falha}")

    log("")
    log(f"{total_aprovados}/{total_casos} casos aprovados.")
    return 1 if todas_falhas else 0


if __name__ == "__main__":
    sys.exit(main())
