#!/usr/bin/env python3
"""Testes do instalador do QAGente.

Sem dependências externas — só `unittest` da biblioteca padrão.

    python -m unittest test_install -v
    python test_install.py

Os testes de integração executam o `install.py` real como subprocesso, sempre dentro de um
diretório temporário. Nenhum teste escreve no harness do QAGente nem em `~/.claude`.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
INSTALL = HARNESS / "install.py"

sys.path.insert(0, str(HARNESS))
import install  # noqa: E402

SKILL_NAMES = {
    "analise-documentacao-testes",
    "cypress-ui-automation",
    "escrita-casos-teste",
    "gherkin-palavras-chave",
    "robot-framework-api",
}


def make_profile(**overrides) -> dict:
    """Perfil mínimo válido, para ser ajustado por teste."""
    profile = {
        "profile_version": "1.0",
        "profile_name": "teste",
        "language": "pt-BR",
        "workflow": {},
        "paths": {
            "input": "entrada",
            "scenarios": "saida/cenarios",
            "test_cases": "saida/casos-de-teste",
            "api_tests": "saida/robot",
            "ui_tests": "saida/cypress",
        },
    }
    profile.update(overrides)
    return profile


def snapshot(root: Path) -> dict[str, str]:
    """Mapa {caminho relativo: sha256} de todos os arquivos sob `root`."""
    digests = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digests[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


class InstallerTestCase(unittest.TestCase):
    """Base com diretório temporário e um atalho para rodar o instalador."""

    def setUp(self) -> None:
        # mkdtemp + rmtree(ignore_errors) em vez de TemporaryDirectory: no Windows a limpeza
        # falha quando o antivírus ainda segura um arquivo recém-copiado, e isso não deve
        # derrubar um teste que já passou.
        self.parent = Path(tempfile.mkdtemp(prefix="qagente-test-"))
        self.addCleanup(shutil.rmtree, self.parent, True)
        self.project = self.parent / "projeto"
        self.project.mkdir()

    def write_profile(self, name: str, profile: dict | str) -> Path:
        path = self.parent / f"{name}.json"
        content = profile if isinstance(profile, str) else json.dumps(profile, ensure_ascii=False)
        path.write_text(content, encoding="utf-8")
        return path

    def run_install(self, *args: str, script: Path | None = None) -> subprocess.CompletedProcess:
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        return subprocess.run(
            [sys.executable, str(script or INSTALL), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )

    def install_ok(self, *args: str, script: Path | None = None) -> str:
        """Roda o instalador no projeto de teste, exige sucesso e devolve o stdout."""
        result = self.run_install("--target", str(self.project), *args, script=script)
        self.assertEqual(result.returncode, 0, f"instalador falhou:\n{result.stdout}\n{result.stderr}")
        return result.stdout

    def assertExists(self, relative: str) -> None:
        self.assertTrue((self.project / relative).exists(), f"esperado existir: {relative}")

    def assertMissing(self, relative: str) -> None:
        self.assertFalse((self.project / relative).exists(), f"não deveria existir: {relative}")

    def dirs_under(self, relative: str) -> set[str]:
        base = self.project / relative
        if not base.is_dir():
            return set()
        return {p.name for p in base.iterdir() if p.is_dir()}


# --------------------------------------------------------------------------------------
# Funções puras
# --------------------------------------------------------------------------------------


class ProfilePathsTest(unittest.TestCase):
    """`profile_io_dirs` e `disabled_path_keys` — o coração da Etapa 1."""

    def resolve(self, profile: dict) -> tuple[list[tuple[str, str]], str]:
        """Chama profile_io_dirs capturando os avisos impressos."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            result = install.profile_io_dirs(profile)
        return result, buffer.getvalue()

    def test_usa_os_caminhos_do_perfil_na_ordem_declarada(self):
        profile = make_profile(paths={"input": "docs/req", "scenarios": "qa/cenarios"})
        result, _ = self.resolve(profile)
        self.assertEqual(result, [("input", "docs/req"), ("scenarios", "qa/cenarios")])

    def test_cai_no_fallback_quando_paths_esta_vazio(self):
        result, log = self.resolve(make_profile(paths={}))
        self.assertEqual(result, list(install.DEFAULT_IO_PATHS.items()))
        self.assertIn("defaults do QAGente", log)

    def test_cai_no_fallback_quando_paths_nao_e_dicionario(self):
        result, _ = self.resolve(make_profile(paths=["entrada"]))
        self.assertEqual(result, list(install.DEFAULT_IO_PATHS.items()))

    def test_cai_no_fallback_quando_nenhum_caminho_e_utilizavel(self):
        result, log = self.resolve(make_profile(paths={"input": "/etc/qa", "scenarios": ".."}))
        self.assertEqual(result, list(install.DEFAULT_IO_PATHS.items()))
        self.assertIn("nenhum caminho do perfil é utilizável", log)

    def test_recusa_caminho_absoluto_posix(self):
        result, log = self.resolve(make_profile(paths={"input": "/etc/qa", "scenarios": "ok"}))
        self.assertEqual(result, [("scenarios", "ok")])
        self.assertIn("caminho absoluto ignorado", log)

    def test_recusa_caminho_absoluto_windows(self):
        result, log = self.resolve(make_profile(paths={"input": "C:/Windows/Temp", "scenarios": "ok"}))
        self.assertEqual(result, [("scenarios", "ok")])
        self.assertIn("caminho absoluto ignorado", log)

    def test_recusa_escape_da_raiz(self):
        paths = {"input": "../fora", "scenarios": "a/../../b", "test_cases": "ok"}
        result, log = self.resolve(make_profile(paths=paths))
        self.assertEqual(result, [("test_cases", "ok")])
        self.assertEqual(log.count("fora da raiz do projeto"), 2)

    def test_recusa_valores_vazios_ou_de_outro_tipo(self):
        paths = {"input": "", "scenarios": "   ", "test_cases": 42, "api_tests": "ok"}
        result, log = self.resolve(make_profile(paths=paths))
        self.assertEqual(result, [("api_tests", "ok")])
        self.assertEqual(log.count("caminho inválido no perfil"), 3)

    def test_normaliza_barras_invertidas_e_barras_sobrando(self):
        result, _ = self.resolve(make_profile(paths={"input": "qa\\cenarios/", "scenarios": "qa/casos//"}))
        self.assertEqual(result, [("input", "qa/cenarios"), ("scenarios", "qa/casos")])

    def test_barra_inicial_e_tratada_como_caminho_absoluto_e_recusada(self):
        # "/qa/casos" é ambíguo: pode significar "qa/casos a partir da raiz do projeto" ou a
        # raiz do sistema de arquivos. Recusar com aviso é mais seguro do que reinterpretar.
        result, log = self.resolve(make_profile(paths={"input": "/qa/casos", "scenarios": "ok"}))
        self.assertEqual(result, [("scenarios", "ok")])
        self.assertIn("caminho absoluto ignorado", log)

    def test_remove_caminhos_duplicados(self):
        result, _ = self.resolve(make_profile(paths={"input": "qa", "scenarios": "qa/", "test_cases": "outro"}))
        self.assertEqual(result, [("input", "qa"), ("test_cases", "outro")])

    def test_fases_desligadas_sao_identificadas(self):
        profile = make_profile(api={"enabled": False}, ui={"enabled": True})
        self.assertEqual(install.disabled_path_keys(profile), {"api_tests"})

    def test_fase_sem_a_chave_enabled_continua_ligada(self):
        self.assertEqual(install.disabled_path_keys(make_profile(api={}, ui={})), set())

    def test_perfil_sem_secoes_de_fase_nao_desliga_nada(self):
        self.assertEqual(install.disabled_path_keys(make_profile()), set())


class IsSkillDirTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="qagente-skilldir-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def make(self, name: str, *, skill_md: bool) -> Path:
        path = self.tmp / name
        path.mkdir()
        if skill_md:
            (path / "SKILL.md").write_text("x", encoding="utf-8")
        return path

    def test_diretorio_com_skill_md_e_uma_skill(self):
        self.assertTrue(install.is_skill_dir(self.make("boa", skill_md=True)))

    def test_diretorio_sem_skill_md_nao_e(self):
        self.assertFalse(install.is_skill_dir(self.make("rascunho", skill_md=False)))

    def test_arquivo_solto_nao_e(self):
        path = self.tmp / "LEIA-ME.md"
        path.write_text("x", encoding="utf-8")
        self.assertFalse(install.is_skill_dir(path))

    def test_diretorios_de_infraestrutura_sao_ignorados(self):
        self.assertFalse(install.is_skill_dir(self.make("__pycache__", skill_md=True)))
        self.assertFalse(install.is_skill_dir(self.make(".git", skill_md=True)))


class MergeBlockTest(unittest.TestCase):
    def test_cria_o_bloco_em_arquivo_vazio(self):
        content, changed = install.merge_block("", "REGRAS")
        self.assertTrue(changed)
        self.assertIn("REGRAS", content)
        self.assertIn(install.MARKER_START, content)

    def test_preserva_o_conteudo_existente(self):
        content, changed = install.merge_block("# Meu projeto\n\nRegras do time.\n", "REGRAS")
        self.assertTrue(changed)
        self.assertIn("Regras do time.", content)
        self.assertIn("REGRAS", content)

    def test_atualiza_o_bloco_sem_duplicar(self):
        primeiro, _ = install.merge_block("# Projeto\n", "VERSAO 1")
        segundo, changed = install.merge_block(primeiro, "VERSAO 2")
        self.assertTrue(changed)
        self.assertEqual(segundo.count(install.MARKER_START), 1)
        self.assertNotIn("VERSAO 1", segundo)
        self.assertIn("VERSAO 2", segundo)
        self.assertIn("# Projeto", segundo)

    def test_reaplicar_o_mesmo_bloco_nao_muda_nada(self):
        primeiro, _ = install.merge_block("# Projeto\n", "REGRAS")
        segundo, changed = install.merge_block(primeiro, "REGRAS")
        self.assertFalse(changed)
        self.assertEqual(primeiro, segundo)


# --------------------------------------------------------------------------------------
# Instalação por ferramenta
# --------------------------------------------------------------------------------------


class ClaudeInstallTest(InstallerTestCase):
    def test_instalacao_claude(self):
        self.install_ok("--tool", "claude", "--profile", "default")
        self.assertEqual(self.dirs_under(".claude/skills"), SKILL_NAMES)
        self.assertExists(".claude/agents/qa-especialista.md")
        self.assertExists("AGENTS.md")
        self.assertExists("CLAUDE.md")
        self.assertExists(".qagente/quality-profile.json")
        # skills portáteis são só para as outras ferramentas
        self.assertMissing(".qagente/skills")

    def test_claude_md_aponta_para_agents_md(self):
        self.install_ok("--tool", "claude")
        self.assertIn("AGENTS.md", (self.project / "CLAUDE.md").read_text(encoding="utf-8"))


class OutrasFerramentasTest(InstallerTestCase):
    def test_instalacao_copilot(self):
        self.install_ok("--tool", "copilot", "--profile", "frontend-web")
        self.assertExists(".github/copilot-instructions.md")
        self.assertExists(".github/agents/qa-especialista.agent.md")
        self.assertEqual(self.dirs_under(".qagente/skills"), SKILL_NAMES)
        self.assertExists("AGENTS.md")
        self.assertMissing("CLAUDE.md")
        self.assertMissing(".claude")

    def test_instalacao_cursor(self):
        self.install_ok("--tool", "cursor", "--profile", "frontend-web")
        self.assertExists(".cursor/rules/qagente.mdc")
        self.assertEqual(self.dirs_under(".qagente/skills"), SKILL_NAMES)
        self.assertMissing("CLAUDE.md")
        self.assertMissing(".claude")

    def test_instalacao_windsurf(self):
        self.install_ok("--tool", "windsurf", "--profile", "backend-api")
        self.assertExists(".windsurf/rules/qagente.md")
        self.assertEqual(self.dirs_under(".qagente/skills"), SKILL_NAMES)
        self.assertMissing("CLAUDE.md")
        self.assertMissing(".claude")

    def test_instalacao_combinada(self):
        self.install_ok("--tools", "claude,copilot,cursor,windsurf", "--profile", "default")
        self.assertExists(".claude/agents/qa-especialista.md")
        self.assertExists(".github/copilot-instructions.md")
        self.assertExists(".cursor/rules/qagente.mdc")
        self.assertExists(".windsurf/rules/qagente.md")
        self.assertExists("CLAUDE.md")
        self.assertEqual(self.dirs_under(".qagente/skills"), SKILL_NAMES)

    def test_ferramentas_repetidas_nao_duplicam_a_instalacao(self):
        stdout = self.install_ok("--tools", "cursor,cursor,cursor")
        self.assertEqual(stdout.count("== Adaptador cursor =="), 1)


# --------------------------------------------------------------------------------------
# Entradas inválidas
# --------------------------------------------------------------------------------------


class EntradasInvalidasTest(InstallerTestCase):
    def test_perfil_inexistente(self):
        result = self.run_install("--target", str(self.project), "--profile", "nao-existe")
        self.assertEqual(result.returncode, 1)
        self.assertIn("perfil não encontrado", result.stdout)
        self.assertMissing("AGENTS.md")

    def test_perfil_com_json_quebrado(self):
        path = self.write_profile("quebrado", "{ isso não é json ")
        result = self.run_install("--target", str(self.project), "--profile", str(path))
        self.assertEqual(result.returncode, 1)
        self.assertIn("perfil inválido", result.stdout)

    def test_perfil_sem_campos_obrigatorios(self):
        path = self.write_profile("incompleto", {"profile_version": "1.0"})
        result = self.run_install("--target", str(self.project), "--profile", str(path))
        self.assertEqual(result.returncode, 1)
        self.assertIn("campos obrigatórios", result.stdout)

    def test_perfil_que_nao_e_objeto_json(self):
        path = self.write_profile("lista", "[1, 2, 3]")
        result = self.run_install("--target", str(self.project), "--profile", str(path))
        self.assertEqual(result.returncode, 1)

    def test_ferramenta_invalida(self):
        result = self.run_install("--target", str(self.project), "--tools", "claude,vscode")
        self.assertEqual(result.returncode, 2)
        self.assertIn("vscode", result.stdout)
        self.assertMissing("AGENTS.md")

    def test_diretorio_alvo_inexistente(self):
        result = self.run_install("--target", str(self.parent / "nao-existe"))
        self.assertEqual(result.returncode, 1)

    def test_global_recusa_ferramentas_que_nao_sejam_claude(self):
        # Não passa --target: o modo global ignora o alvo. O instalador precisa recusar
        # ANTES de tocar em ~/.claude.
        result = self.run_install("--global", "--tool", "cursor")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--global", result.stdout)

    def test_versao_de_perfil_desconhecida_avisa_mas_prossegue(self):
        path = self.write_profile("futuro", make_profile(profile_version="9.9"))
        stdout = self.install_ok("--tool", "claude", "--profile", str(path))
        self.assertIn("profile_version", stdout)
        self.assertExists("AGENTS.md")


# --------------------------------------------------------------------------------------
# Caminhos vindos do perfil (regressão da Etapa 1)
# --------------------------------------------------------------------------------------


class CaminhosDoPerfilTest(InstallerTestCase):
    def test_perfil_customizado_cria_exatamente_os_seus_caminhos(self):
        self.install_ok("--tool", "claude", "--profile", "backend-api")
        for esperado in ("docs/requisitos", "qa/cenarios", "qa/casos-de-teste", "tests/api"):
            self.assertExists(esperado)
        # os defaults históricos não devem mais aparecer
        self.assertMissing("entrada")
        self.assertMissing("saida")

    def test_perfil_default_mantem_os_caminhos_historicos(self):
        self.install_ok("--tool", "claude", "--profile", "default")
        for esperado in ("entrada", "saida/cenarios", "saida/casos-de-teste", "saida/robot", "saida/cypress"):
            self.assertExists(esperado)

    def test_fase_de_ui_desligada_nao_cria_a_pasta(self):
        self.install_ok("--tool", "claude", "--profile", "backend-api")  # ui.enabled = false
        self.assertExists("tests/api")
        self.assertMissing("tests/e2e")

    def test_fase_de_api_desligada_nao_cria_a_pasta(self):
        self.install_ok("--tool", "claude", "--profile", "frontend-web")  # api.enabled = false
        self.assertExists("cypress/e2e")
        self.assertMissing("tests/api")

    def test_perfil_sem_paths_utilizavel_cai_no_fallback(self):
        path = self.write_profile("sem-paths", make_profile(paths={}))
        self.install_ok("--tool", "claude", "--profile", str(path))
        self.assertExists("entrada")
        self.assertExists("saida/cenarios")

    def test_caminhos_hostis_sao_recusados_sem_vazar_da_raiz(self):
        absoluto = self.parent / "absoluto"
        path = self.write_profile(
            "hostil",
            make_profile(
                paths={
                    "input": "../vizinho",
                    "scenarios": str(absoluto),
                    "test_cases": "",
                    "api_tests": "qa/ok",
                }
            ),
        )
        self.install_ok("--tool", "claude", "--profile", str(path))
        self.assertExists("qa/ok")
        self.assertFalse(absoluto.exists(), "caminho absoluto do perfil foi criado")
        self.assertFalse((self.parent / "vizinho").exists(), "'..' escapou da raiz do projeto")
        # nada além do próprio projeto e dos perfis de teste no diretório pai
        vizinhos = {p.name for p in self.parent.iterdir() if p.is_dir()}
        self.assertEqual(vizinhos, {"projeto"})

    def test_pastas_criadas_ganham_gitkeep(self):
        self.install_ok("--tool", "claude", "--profile", "default")
        self.assertExists("entrada/.gitkeep")
        self.assertExists("saida/cenarios/.gitkeep")


# --------------------------------------------------------------------------------------
# Perfil efetivo, --force e idempotência
# --------------------------------------------------------------------------------------


class PerfilEfetivoTest(InstallerTestCase):
    def perfil_em_disco(self) -> str:
        data = json.loads((self.project / ".qagente/quality-profile.json").read_text(encoding="utf-8"))
        return data["profile_name"]

    def test_perfil_existente_e_preservado_sem_force(self):
        self.install_ok("--tool", "claude", "--profile", "backend-api")
        self.install_ok("--tool", "claude", "--profile", "frontend-web")
        self.assertEqual(self.perfil_em_disco(), "backend-api")

    def test_perfil_preservado_governa_os_diretorios_criados(self):
        self.install_ok("--tool", "claude", "--profile", "backend-api")
        stdout = self.install_ok("--tool", "claude", "--profile", "frontend-web")
        self.assertIn("perfil efetivo do projeto: backend-api", stdout)
        # os caminhos do frontend-web não podem aparecer
        self.assertMissing("cypress/e2e")
        self.assertExists("tests/api")

    def test_force_substitui_o_perfil_e_os_diretorios_passam_a_segui_lo(self):
        self.install_ok("--tool", "claude", "--profile", "backend-api")
        self.install_ok("--tool", "claude", "--profile", "frontend-web", "--force")
        self.assertEqual(self.perfil_em_disco(), "frontend-web")
        self.assertExists("cypress/e2e")

    def test_perfil_em_disco_ilegivel_nao_derruba_a_instalacao(self):
        self.install_ok("--tool", "claude", "--profile", "backend-api")
        (self.project / ".qagente/quality-profile.json").write_text("{ quebrado", encoding="utf-8")
        stdout = self.install_ok("--tool", "claude", "--profile", "frontend-web")
        self.assertIn("ilegível", stdout)
        self.assertExists("cypress/e2e")

    def test_force_atualiza_as_skills_ja_instaladas(self):
        self.install_ok("--tool", "claude", "--profile", "default")
        alvo = self.project / ".claude/skills/gherkin-palavras-chave/SKILL.md"
        alvo.write_text("conteúdo obsoleto", encoding="utf-8")
        self.install_ok("--tool", "claude", "--profile", "default", "--force")
        self.assertNotEqual(alvo.read_text(encoding="utf-8"), "conteúdo obsoleto")

    def test_sem_force_as_skills_instaladas_sao_preservadas(self):
        self.install_ok("--tool", "claude", "--profile", "default")
        alvo = self.project / ".claude/skills/gherkin-palavras-chave/SKILL.md"
        alvo.write_text("edição local do time", encoding="utf-8")
        self.install_ok("--tool", "claude", "--profile", "default")
        self.assertEqual(alvo.read_text(encoding="utf-8"), "edição local do time")


class AgentsMdTest(InstallerTestCase):
    def test_agents_md_existente_e_preservado(self):
        original = "# Regras do time\n\nNão apague isto.\n"
        (self.project / "AGENTS.md").write_text(original, encoding="utf-8")
        self.install_ok("--tool", "claude", "--profile", "default")
        content = (self.project / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Não apague isto.", content)
        self.assertIn(install.MARKER_START, content)

    def test_reinstalar_nao_duplica_o_bloco(self):
        self.install_ok("--tool", "claude", "--profile", "default")
        self.install_ok("--tool", "claude", "--profile", "default")
        content = (self.project / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(content.count(install.MARKER_START), 1)

    def test_claude_md_existente_ganha_nota_sem_perder_conteudo(self):
        (self.project / "CLAUDE.md").write_text("# Instruções próprias\n", encoding="utf-8")
        self.install_ok("--tool", "claude", "--profile", "default")
        content = (self.project / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("Instruções próprias", content)
        self.assertIn("AGENTS.md", content)


class DryRunTest(InstallerTestCase):
    def test_dry_run_nao_toca_no_disco(self):
        antes = snapshot(self.project)
        stdout = self.install_ok("--tools", "claude,copilot,cursor,windsurf", "--profile", "backend-api", "--dry-run")
        self.assertEqual(snapshot(self.project), antes)
        self.assertEqual(list(self.project.iterdir()), [])
        self.assertIn("dry-run", stdout)

    def test_dry_run_mostra_os_caminhos_efetivos_do_perfil(self):
        stdout = self.install_ok("--tool", "claude", "--profile", "backend-api", "--dry-run")
        self.assertIn("docs" + os.sep + "requisitos", stdout)
        self.assertIn("qa" + os.sep + "cenarios", stdout)
        self.assertIn("fase desligada no perfil", stdout)


class IdempotenciaTest(InstallerTestCase):
    def test_reinstalar_nao_altera_nenhum_byte(self):
        args = ("--tools", "claude,copilot,cursor,windsurf", "--profile", "backend-api")
        self.install_ok(*args)
        antes = snapshot(self.project)
        self.install_ok(*args)
        self.assertEqual(snapshot(self.project), antes)


# --------------------------------------------------------------------------------------
# Robustez a arquivos inesperados no harness
# --------------------------------------------------------------------------------------


class HarnessComArquivosSoltosTest(InstallerTestCase):
    """Regressão dos dois crashes: KeyError em adapters/ e copytree em skills/.

    O harness é copiado para um diretório temporário antes de ser sujado — os testes nunca
    escrevem no QAGente de verdade.
    """

    def setUp(self) -> None:
        super().setUp()
        self.harness = self.parent / "harness"
        shutil.copytree(
            HARNESS,
            self.harness,
            ignore=shutil.ignore_patterns("__pycache__", ".git", "test_install.py"),
        )
        self.script = self.harness / "install.py"

    def test_arquivo_solto_em_skills_e_ignorado(self):
        (self.harness / "skills" / "LEIA-ME.md").write_text("nota", encoding="utf-8")
        self.install_ok("--tool", "claude", "--profile", "default", script=self.script)
        self.assertEqual(self.dirs_under(".claude/skills"), SKILL_NAMES)
        self.assertMissing(".claude/skills/LEIA-ME.md")

    def test_diretorio_sem_skill_md_e_ignorado_com_aviso(self):
        (self.harness / "skills" / "rascunho").mkdir()
        stdout = self.install_ok("--tool", "claude", "--profile", "default", script=self.script)
        self.assertIn("sem SKILL.md", stdout)
        self.assertEqual(self.dirs_under(".claude/skills"), SKILL_NAMES)

    def test_arquivo_sem_destino_mapeado_em_adapters_nao_derruba_a_instalacao(self):
        (self.harness / "adapters" / "cursor" / "README.md").write_text("nota", encoding="utf-8")
        stdout = self.install_ok("--tool", "cursor", "--profile", "default", script=self.script)
        self.assertIn("sem destino mapeado", stdout)
        self.assertExists(".cursor/rules/qagente.mdc")
        self.assertMissing(".cursor/rules/README.md")

    def test_subdiretorio_em_adapters_e_ignorado(self):
        (self.harness / "adapters" / "windsurf" / "extras").mkdir()
        self.install_ok("--tool", "windsurf", "--profile", "default", script=self.script)
        self.assertExists(".windsurf/rules/qagente.md")


# --------------------------------------------------------------------------------------
# Referências de caminho dentro do conteúdo instalado
# --------------------------------------------------------------------------------------


class ReferenciasDeCaminhoTest(unittest.TestCase):
    """O texto das skills e dos adaptadores é lido pelo agente como instrução.

    Um caminho errado ali não quebra o instalador — só faz o agente procurar arquivo no
    lugar errado em silêncio, que é pior. Estes testes leem o conteúdo do harness.
    """

    def skill_files(self) -> list[Path]:
        return sorted((HARNESS / "skills").glob("*/SKILL.md"))

    def adapter_files(self) -> list[Path]:
        return sorted(p for p in (HARNESS / "adapters").rglob("*.md*") if p.is_file())

    def test_o_harness_tem_as_cinco_skills_esperadas(self):
        # protege os dois testes abaixo de passarem por vacuidade
        self.assertEqual({p.parent.name for p in self.skill_files()}, SKILL_NAMES)

    def test_skills_nao_referenciam_agents_md_por_caminho_relativo(self):
        """`../../AGENTS.md` resolve certo no repositório e em `.qagente/skills/`, mas aponta
        para `.claude/AGENTS.md` — que não existe — na instalação do Claude Code."""
        ofensores = [p.parent.name for p in self.skill_files() if "../../AGENTS.md" in p.read_text(encoding="utf-8")]
        self.assertEqual(ofensores, [], "use `AGENTS.md`, na raiz do projeto — não um caminho relativo")

    def test_nada_no_harness_aponta_para_um_diretorio_de_skills_inexistente(self):
        """As skills portáteis vão para `.qagente/skills/`; `.github/skills/` nunca é criado."""
        for path in self.skill_files() + self.adapter_files():
            with self.subTest(arquivo=path.name):
                self.assertNotIn(".github/skills", path.read_text(encoding="utf-8"))

    def test_toda_skill_manda_ler_o_perfil(self):
        """Sem isto o perfil configura o instalador mas não muda o comportamento do agente."""
        for path in self.skill_files():
            with self.subTest(skill=path.parent.name):
                texto = path.read_text(encoding="utf-8")
                self.assertIn("## Configuração", texto)
                self.assertIn(".qagente/quality-profile.json", texto)

    def test_skills_de_automacao_citam_os_campos_de_framework_do_perfil(self):
        """Gerar Cypress num projeto que escolheu Playwright é o modo de falhar mais caro aqui."""
        casos = {
            "robot-framework-api": ["api.framework", "api.enabled", "paths.api_tests"],
            "cypress-ui-automation": ["ui.framework", "ui.enabled", "paths.ui_tests"],
        }
        for skill, campos in casos.items():
            texto = (HARNESS / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            for campo in campos:
                with self.subTest(skill=skill, campo=campo):
                    self.assertIn(campo, texto)

    def test_convencoes_prescritivas_estao_atreladas_ao_perfil(self):
        """Cada default rígido precisa citar o campo que pode substituí-lo."""
        casos = {
            "escrita-casos-teste": ["conventions.scenario_title_prefix", "conventions.gherkin_language"],
            "analise-documentacao-testes": ["risk_levels", "risk_method"],
            "cypress-ui-automation": ["ui.selector_attribute"],
            "robot-framework-api": ["api.base_url_env", "api.user_env", "api.password_env"],
        }
        for skill, campos in casos.items():
            texto = (HARNESS / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            for campo in campos:
                with self.subTest(skill=skill, campo=campo):
                    self.assertIn(campo, texto)

    def test_os_dois_arquivos_do_adaptador_copilot_concordam(self):
        base = HARNESS / "adapters" / "copilot"
        for nome in ("copilot-instructions.md", "qa-especialista.agent.md"):
            with self.subTest(arquivo=nome):
                self.assertIn(".qagente/skills/", (base / nome).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
