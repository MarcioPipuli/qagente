#!/usr/bin/env python3
"""Valida os artefatos que o agente produz — os documentos de cenários e de casos de teste.

O terceiro validador do harness, e o primeiro que olha para a **saída**. `validate_profile`
valida a configuração do time; `validate_skills.py` valida o que o agente lê como instrução;
este valida o que ele escreveu. A lacuna que ele fecha foi apontada por três itens
independentes: o gate prende a regra no texto da skill, e nada prova que o artefato entregue
respeita o valor efetivo do perfil em vez do default citado no exemplo da skill.

Escopo deliberado: só o que é verificável **sem julgamento** — totais do resumo contra o
corpo, aderência à lista de casos sugeridos, tags obrigatórias por caso, e os campos que o
perfil decide. O que exige entender o requisito ("há um cenário negativo por regra de
validação?", "estes dois cenários diferem só na condição de entrada?") continua sendo
trabalho da skill: um validador que chuta nisso gera falso positivo, e um validador em que
não se confia deixa de ser rodado.

Severidade segue o mesmo contrato dos outros dois: 'erro' é contradição interna do documento
— um total que não bate, uma referência órfã, uma tag obrigatória ausente. 'aviso' é
convenção que o perfil governa e que o idioma do artefato pode legitimamente variar.

Uso:
    python validate_artefatos.py saida/cenarios/x.cenarios.md
    python validate_artefatos.py saida/cenarios/x.cenarios.md saida/casos-de-teste/x.casos.md
    python validate_artefatos.py <arquivos> --profile .qagente/quality-profile.json
    python validate_artefatos.py <arquivos> --strict   # avisos também falham

Passando os dois documentos na mesma chamada, as checagens de contrato entre as fases também
rodam: toda tag de rastreio aponta para um cenário que existe, e a aderência declarada bate
com a lista de casos sugeridos da Fase 1.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
DEFAULT_PROFILE = HARNESS / "profiles" / "default.json"

# Níveis canônicos são declarados em inglês no perfil e escritos no idioma de `language`
# nos artefatos (AGENTS.md). Só o pt-BR tem tradução conhecida aqui; em qualquer outro
# idioma a checagem de prioridade é omitida em vez de gerar falso positivo.
NIVEIS_PT = {
    "critical": "crítica",
    "high": "alta",
    "medium": "média",
    "low": "baixa",
}

CAMADAS = ("@api", "@interface")
EXECUCOES = ("@pendente-de-automacao", "@nao-automatizavel")

# Um total escrito como `[N]` é o placeholder do template, não um artefato preenchido.
RE_PLACEHOLDER = re.compile(r"\[N\]")

RE_LINHA_TABELA = re.compile(r"^\|(.+)\|\s*$")
RE_SEPARADOR = re.compile(r"^[\s|:-]+$")
RE_BLOCO_CENARIO = re.compile(r"^## (\S+) —")
RE_TOTAL_CENARIOS = re.compile(r"\*\*Total de cenários:\*\*\s*(\d+)")
RE_TOTAL_SUGERIDOS = re.compile(r"\*\*Total de casos sugeridos:\*\*\s*(\d+)")
RE_CABECALHO_SUGERIDOS = re.compile(r"^\*\*(\S+) —")
RE_CASO_SUGERIDO = re.compile(r"^\s*\d+\.\s*(\[[A-Z]+\])?")
RE_TOTAL_CASOS = re.compile(r"\*\*Total de casos:\*\*\s*(\d+)")
RE_ADERENCIA = re.compile(r"\*\*Aderência ao contrato:\*\*\s*(\d+)\s*casos? sugeridos?,\s*(\d+)\s*escritos?")
RE_TAGS = re.compile(r"^\s*(@[\w-]+(?:\s+@[\w-]+)*)\s*$")
RE_CASO = re.compile(r"^\s*(Esquema do Cenário|Cenário):\s*(.*)$")
RE_LANGUAGE = re.compile(r"^\s*#\s*language:\s*(\S+)")


def log(msg: str) -> None:
    print(msg)


# --------------------------------------------------------------------------------------
# Perfil efetivo
# --------------------------------------------------------------------------------------


def carregar_perfil(caminho: Path | None, artefato: Path) -> tuple[dict, str]:
    """Devolve (perfil, origem). Procura `.qagente/quality-profile.json` subindo do artefato.

    O artefato mora no projeto do usuário e o validador roda a partir do clone do harness —
    o mesmo caminho que `--validate-profile` já estabeleceu. Procurar para cima a partir do
    arquivo evita exigir que o usuário saiba onde o perfil está.
    """
    if caminho is not None:
        return _ler_json(caminho), str(caminho)

    for pasta in [artefato.resolve().parent, *artefato.resolve().parents]:
        candidato = pasta / ".qagente" / "quality-profile.json"
        if candidato.is_file():
            return _ler_json(candidato), str(candidato)

    return _ler_json(DEFAULT_PROFILE), "defaults do QAGente (perfil do projeto não encontrado)"


def _ler_json(caminho: Path) -> dict:
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        log(f"Erro: perfil ilegível ({caminho}): {exc}")
        sys.exit(1)
    return dados if isinstance(dados, dict) else {}


def prioridades_aceitas(perfil: dict) -> set[str] | None:
    """Níveis aceitos na coluna de prioridade, ou None quando não dá para saber.

    None quando o idioma não é pt-BR: os níveis saem traduzidos, e inventar tradução aqui
    produziria aviso em documento correto.
    """
    niveis = perfil.get("risk_levels") or ["critical", "high", "medium", "low"]
    if not isinstance(niveis, list):
        return None
    canonicos = {str(n).strip().lower() for n in niveis}
    idioma = str(perfil.get("language") or "pt-BR").lower()
    if not idioma.startswith("pt"):
        return None
    return canonicos | {NIVEIS_PT[n] for n in canonicos if n in NIVEIS_PT}


def prefixo_de_titulo(perfil: dict) -> str:
    convencoes = perfil.get("conventions")
    if not isinstance(convencoes, dict):
        return "Validar que"
    prefixo = convencoes.get("scenario_title_prefix")
    return prefixo if isinstance(prefixo, str) else "Validar que"


# --------------------------------------------------------------------------------------
# Leitura dos artefatos
# --------------------------------------------------------------------------------------


def _celulas(linha: str) -> list[str]:
    return [c.strip() for c in linha.strip().strip("|").split("|")]


def e_template(texto: str) -> bool:
    """O template embarcado traz `[N]` nos totais. Validá-lo reprovaria tudo, sem sentido."""
    return bool(RE_PLACEHOLDER.search(texto))


def ler_cenarios(texto: str) -> dict:
    """Extrai do documento de cenários tudo que as checagens precisam."""
    linhas = texto.split("\n")
    dados: dict = {
        "indice": [],          # [(id, prioridade)]
        "blocos": [],          # ids com bloco próprio
        "sugeridos_por": {},   # id -> quantidade de casos sugeridos
        "sugeridos_sem_camada": 0,
        "total_declarado": None,
        "total_sugeridos_declarado": None,
        "tem_origem": False,
        "tem_lacunas": False,
    }

    secao = None
    cabecalho_atual = None
    dentro_do_indice = False

    for linha in linhas:
        if linha.startswith("## ") or linha.startswith("### "):
            titulo = linha.lstrip("#").strip()
            secao = titulo
            dentro_do_indice = titulo.lower().startswith("índice")
            if titulo.lower().startswith("lacunas"):
                dados["tem_lacunas"] = True
            bloco = RE_BLOCO_CENARIO.match(linha)
            if bloco:
                dados["blocos"].append(bloco.group(1))
                dentro_do_indice = False
            continue

        if linha.startswith("Origem:") and linha[len("Origem:"):].strip():
            dados["tem_origem"] = True

        if dentro_do_indice and RE_LINHA_TABELA.match(linha) and not RE_SEPARADOR.match(linha):
            celulas = _celulas(linha)
            if len(celulas) >= 2 and celulas[0].upper() != "ID":
                prioridade = celulas[-1] if len(celulas) >= 5 else ""
                dados["indice"].append((celulas[0], prioridade))
            continue

        if secao and "casos sugeridos" in secao.lower():
            cabecalho = RE_CABECALHO_SUGERIDOS.match(linha)
            if cabecalho:
                cabecalho_atual = cabecalho.group(1)
                dados["sugeridos_por"].setdefault(cabecalho_atual, 0)
                continue
            caso = RE_CASO_SUGERIDO.match(linha)
            if caso and cabecalho_atual:
                dados["sugeridos_por"][cabecalho_atual] += 1
                if not caso.group(1):
                    dados["sugeridos_sem_camada"] += 1
            continue

        total = RE_TOTAL_CENARIOS.search(linha)
        if total:
            dados["total_declarado"] = int(total.group(1))
        total_sug = RE_TOTAL_SUGERIDOS.search(linha)
        if total_sug:
            dados["total_sugeridos_declarado"] = int(total_sug.group(1))

    return dados


def ler_casos(texto: str) -> dict:
    """Extrai do documento de casos tudo que as checagens precisam."""
    linhas = texto.split("\n")
    dados: dict = {
        "casos": [],            # [(titulo, tags, tipo)]
        "funcionalidades": 0,
        "language": None,
        "tem_bloco_gherkin": "```gherkin" in texto,
        "total_declarado": None,
        "aderencia": None,      # (sugeridos, escritos)
        "exemplos_por_caso": {},
        "tem_origem": "Origem:" in texto,
    }

    dentro_do_gherkin = False
    tags_pendentes: list[str] = []
    caso_atual = None

    for linha in linhas:
        if linha.strip().startswith("```"):
            dentro_do_gherkin = linha.strip().startswith("```gherkin")
            continue

        if dentro_do_gherkin:
            idioma = RE_LANGUAGE.match(linha)
            if idioma:
                dados["language"] = idioma.group(1)
                continue
            if re.match(r"^\s*Funcionalidade:", linha):
                dados["funcionalidades"] += 1
                continue
            tags = RE_TAGS.match(linha)
            if tags:
                tags_pendentes = tags.group(1).split()
                continue
            caso = RE_CASO.match(linha)
            if caso:
                caso_atual = (caso.group(2).strip(), tuple(tags_pendentes), caso.group(1))
                dados["casos"].append(caso_atual)
                dados["exemplos_por_caso"][len(dados["casos"]) - 1] = 0
                tags_pendentes = []
                continue
            if caso_atual and RE_LINHA_TABELA.match(linha) and not RE_SEPARADOR.match(linha):
                indice = len(dados["casos"]) - 1
                dados["exemplos_por_caso"][indice] = dados["exemplos_por_caso"].get(indice, 0) + 1
            continue

        total = RE_TOTAL_CASOS.search(linha)
        if total:
            dados["total_declarado"] = int(total.group(1))
        aderencia = RE_ADERENCIA.search(linha)
        if aderencia:
            dados["aderencia"] = (int(aderencia.group(1)), int(aderencia.group(2)))

    return dados


# --------------------------------------------------------------------------------------
# Checagens
# --------------------------------------------------------------------------------------


def validar_cenarios(dados: dict, perfil: dict, alvo: str) -> list[tuple[str, str, str]]:
    problemas: list[tuple[str, str, str]] = []
    ids_indice = [i for i, _ in dados["indice"]]

    if not ids_indice:
        problemas.append(("erro", alvo, "sem índice de cenários — nada a validar"))
        return problemas

    duplicados = {i for i in ids_indice if ids_indice.count(i) > 1}
    for identificador in sorted(duplicados):
        problemas.append(("erro", alvo, f"o índice repete o ID {identificador}"))

    for identificador in ids_indice:
        if identificador not in dados["blocos"]:
            problemas.append(("erro", alvo, f"{identificador} está no índice mas não tem bloco próprio"))
    for identificador in dados["blocos"]:
        if identificador not in ids_indice:
            problemas.append(("erro", alvo, f"{identificador} tem bloco mas não está no índice"))

    declarado = dados["total_declarado"]
    if declarado is None:
        problemas.append(("aviso", alvo, "o resumo não declara 'Total de cenários'"))
    elif declarado != len(ids_indice):
        problemas.append(
            ("erro", alvo, f"'Total de cenários' diz {declarado}, o índice tem {len(ids_indice)}")
        )

    sugeridos = sum(dados["sugeridos_por"].values())
    declarado_sug = dados["total_sugeridos_declarado"]
    if declarado_sug is None:
        problemas.append(("aviso", alvo, "o resumo não declara 'Total de casos sugeridos'"))
    elif declarado_sug != sugeridos:
        problemas.append(
            ("erro", alvo, f"'Total de casos sugeridos' diz {declarado_sug}, a lista tem {sugeridos}")
        )

    for identificador in sorted(dados["sugeridos_por"]):
        if identificador not in ids_indice:
            problemas.append(
                ("erro", alvo, f"a lista de casos sugeridos cita {identificador}, que não está no índice")
            )
    for identificador in ids_indice:
        if identificador not in dados["sugeridos_por"]:
            problemas.append(
                ("erro", alvo, f"{identificador} não tem caso sugerido — a Fase 2 não saberia o que escrever")
            )

    if dados["sugeridos_sem_camada"]:
        problemas.append(
            ("aviso", alvo, f"{dados['sugeridos_sem_camada']} caso(s) sugerido(s) sem prefixo [API]/[INTERFACE]")
        )

    aceitas = prioridades_aceitas(perfil)
    if aceitas is not None:
        for identificador, prioridade in dados["indice"]:
            if prioridade and prioridade.lower() not in aceitas:
                problemas.append(
                    ("aviso", alvo, f"{identificador} tem prioridade {prioridade!r}, fora de risk_levels")
                )

    if not dados["tem_origem"]:
        problemas.append(("aviso", alvo, "não há linha 'Origem:' — a rastreabilidade começa nela"))
    if not dados["tem_lacunas"]:
        problemas.append(("aviso", alvo, "sem seção de lacunas — quando não há nenhuma, ela diz isso"))

    return problemas


def validar_casos(dados: dict, perfil: dict, alvo: str) -> list[tuple[str, str, str]]:
    problemas: list[tuple[str, str, str]] = []

    if not dados["tem_bloco_gherkin"]:
        problemas.append(("erro", alvo, "sem bloco de código gherkin"))
        return problemas
    if not dados["casos"]:
        problemas.append(("erro", alvo, "o bloco gherkin não tem nenhum Cenário"))
        return problemas

    if dados["language"] is None:
        problemas.append(("erro", alvo, "o bloco gherkin não abre com '# language:'"))
    if dados["funcionalidades"] != 1:
        problemas.append(
            ("erro", alvo, f"esperada exatamente uma Funcionalidade, encontradas {dados['funcionalidades']}")
        )

    prefixo = prefixo_de_titulo(perfil)
    for indice, (titulo, tags, tipo) in enumerate(dados["casos"], start=1):
        etiqueta = f"{alvo} (caso {indice})"
        rastreio = [t for t in tags if t not in CAMADAS and t not in EXECUCOES]
        if not rastreio:
            problemas.append(("erro", etiqueta, "sem tag de rastreio ao cenário de origem"))
        camadas = [t for t in tags if t in CAMADAS]
        if len(camadas) != 1:
            problemas.append(("erro", etiqueta, f"esperada uma tag de camada (@api/@interface), encontradas {len(camadas)}"))
        execucoes = [t for t in tags if t in EXECUCOES]
        if len(execucoes) != 1:
            problemas.append(("erro", etiqueta, f"esperada uma tag de execução, encontradas {len(execucoes)}"))
        if prefixo and not titulo.startswith(prefixo):
            problemas.append(("aviso", etiqueta, f"o título não começa com {prefixo!r}"))
        if tipo == "Esquema do Cenário" and dados["exemplos_por_caso"].get(indice - 1, 0) < 3:
            problemas.append(
                ("erro", etiqueta, "Esquema do Cenário sem tabela de Exemplos com ao menos duas linhas de dados")
            )

    declarado = dados["total_declarado"]
    if declarado is None:
        problemas.append(("aviso", alvo, "o resumo não declara 'Total de casos'"))
    elif declarado != len(dados["casos"]):
        problemas.append(
            ("erro", alvo, f"'Total de casos' diz {declarado}, o bloco tem {len(dados['casos'])}")
        )

    if dados["aderencia"] is None:
        problemas.append(("aviso", alvo, "o resumo não declara 'Aderência ao contrato'"))
    else:
        _, escritos = dados["aderencia"]
        if escritos != len(dados["casos"]):
            problemas.append(
                ("erro", alvo, f"a aderência diz {escritos} casos escritos, o bloco tem {len(dados['casos'])}")
            )

    if not dados["tem_origem"]:
        problemas.append(("aviso", alvo, "não há linha 'Origem:' — a rastreabilidade começa nela"))

    return problemas


def validar_contrato(cenarios: dict, casos: dict, alvo: str) -> list[tuple[str, str, str]]:
    """As checagens que só existem com os dois documentos na mão.

    É o que nenhum dos dois arquivos consegue provar sozinho, e é a fronteira que o item 3
    criou: a lista de casos sugeridos da Fase 1 é o contrato da Fase 2.
    """
    problemas: list[tuple[str, str, str]] = []
    ids = {i for i, _ in cenarios["indice"]}

    for indice, (_, tags, _) in enumerate(casos["casos"], start=1):
        rastreio = [t.lstrip("@") for t in tags if t not in CAMADAS and t not in EXECUCOES]
        for referencia in rastreio:
            if referencia not in ids:
                problemas.append(
                    ("erro", f"{alvo} (caso {indice})", f"rastreia @{referencia}, que não existe no documento de cenários")
                )

    sugeridos = sum(cenarios["sugeridos_por"].values())
    if casos["aderencia"] is not None:
        declarado, _ = casos["aderencia"]
        if declarado != sugeridos:
            problemas.append(
                ("erro", alvo, f"a aderência diz {declarado} casos sugeridos, os cenários sugerem {sugeridos}")
            )

    cobertos = {t.lstrip("@") for _, tags, _ in casos["casos"] for t in tags if t not in CAMADAS and t not in EXECUCOES}
    for identificador in sorted(ids - cobertos):
        problemas.append(
            ("aviso", alvo, f"nenhum caso rastreia {identificador} — o cenário ficou sem cobertura")
        )

    return problemas


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def report_problems(problemas: list[tuple[str, str, str]]) -> int:
    """Imprime os problemas e devolve a quantidade de erros. Mesmo contrato dos outros dois."""
    if not problemas:
        log("  nenhum problema encontrado")
        return 0
    erros = 0
    for severidade, alvo, mensagem in sorted(problemas):
        log(f"  {severidade:5} {alvo}: {mensagem}")
        erros += severidade == "erro"
    return erros


def classificar(texto: str) -> str:
    """Diz se o arquivo é de cenários, de casos, ou nenhum dos dois."""
    if "```gherkin" in texto:
        return "casos"
    if "## Índice" in texto or "Casos sugeridos por cenário" in texto:
        return "cenarios"
    return "desconhecido"


def collect_problems(caminhos: list[Path], perfil_cli: Path | None) -> list[tuple[str, str, str]]:
    problemas: list[tuple[str, str, str]] = []
    lidos: dict[str, tuple[Path, dict]] = {}

    for caminho in caminhos:
        alvo = caminho.name
        if not caminho.is_file():
            problemas.append(("erro", alvo, "arquivo não encontrado"))
            continue
        texto = caminho.read_text(encoding="utf-8")
        tipo = classificar(texto)
        if tipo == "desconhecido":
            problemas.append(("erro", alvo, "não parece um documento de cenários nem de casos de teste"))
            continue
        if e_template(texto):
            problemas.append(("aviso", alvo, "é um template, não um artefato preenchido — pulado"))
            continue

        perfil, origem = carregar_perfil(perfil_cli, caminho)
        log(f"  perfil aplicado a {alvo}: {origem}")
        if tipo == "cenarios":
            dados = ler_cenarios(texto)
            problemas.extend(validar_cenarios(dados, perfil, alvo))
        else:
            dados = ler_casos(texto)
            problemas.extend(validar_casos(dados, perfil, alvo))
        lidos[tipo] = (caminho, dados)

    if "cenarios" in lidos and "casos" in lidos:
        problemas.extend(validar_contrato(lidos["cenarios"][1], lidos["casos"][1], lidos["casos"][0].name))

    return problemas


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida os artefatos de QA gerados pelo agente.")
    parser.add_argument("arquivos", nargs="+", help="documentos de cenários e/ou de casos de teste")
    parser.add_argument("--profile", help="perfil a aplicar; sem isto, procura .qagente/quality-profile.json")
    parser.add_argument("--strict", action="store_true", help="avisos também reprovam")
    args = parser.parse_args()

    caminhos = [Path(a) for a in args.arquivos]
    log(f"== Validação de artefatos ({len(caminhos)} arquivo(s)) ==")
    problemas = collect_problems(caminhos, Path(args.profile) if args.profile else None)

    erros = report_problems(problemas)
    avisos = len(problemas) - erros
    log(f"\n{erros} erro(s), {avisos} aviso(s).")
    if args.strict and avisos:
        log("Modo --strict: avisos também reprovam.")
        return 1
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
