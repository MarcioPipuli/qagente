# Contribuindo com o QAGente

Este documento é para quem **mantém o harness**. O comportamento do agente é definido em
[AGENTS.md](AGENTS.md) e [agent.md](agent.md); aqui ficam só as regras de trabalho no
repositório.

## Invariantes de arquitetura

Estas decisões não são preferência de estilo — mudá-las muda o que o QAGente é:

- **O núcleo de qualidade é único e universal.** Princípios, fluxo e Definition of Done valem
  para qualquer time e qualquer ferramenta. O que varia por time vai para o perfil, não para
  uma cópia do núcleo.
- **Perfil declarativo em vez de agente por time.** Uma necessidade nova de configuração vira
  campo em `profiles/*.json` lido pelas skills, não um novo `agent.md`.
- **Adaptador é formato, não conteúdo.** `adapters/copilot`, `adapters/cursor` e
  `adapters/windsurf` reembalam as mesmas regras no formato que cada ferramenta lê. Não
  duplique instrução específica de ferramenta sem necessidade real, e não deixe um adaptador
  divergir do núcleo.
- **Rastreabilidade, segurança e evidência de execução são invariantes.** O perfil não pode
  removê-las (ver a lista em [AGENTS.md](AGENTS.md#perfil-de-qualidade-do-time)). Um campo
  novo que as desligue não entra.
- **Não recrie a arquitetura do zero** para resolver um problema local.

## Método de alteração

Antes de editar, formule uma hipótese local e um teste discriminante. Faça a menor alteração
possível, valide imediatamente, e só então prossiga para documentação ou refatorações
adjacentes. Não reverta alterações existentes sem pedido, e **não faça commit
automaticamente** — quem revisa decide o que entra.

## Validação obrigatória

Rode os quatro antes e depois de qualquer alteração. É o mesmo que o CI roda
(`.github/workflows/tests.yml`), em Linux e Windows, nos Python 3.9 e 3.13:

```bash
python -m py_compile install.py
python validate_skills.py --strict
python run_evals.py
python -m unittest test_install
```

Regra de conteúdo que o validador cobre e vale repetir: toda skill precisa ser roteada por
`agent.md` ou por `AGENTS.md`. Uma skill que ninguém aponta é uma skill que o agente nunca
carrega — e um gatilho anunciado na `description` sem skill nem `paths.*` correspondente é a
falha simétrica: promete artefato que o harness não produz.

## Instalação real

- Valide o instalador **em pasta temporária**. A suíte já faz isso; um teste manual deve fazer
  o mesmo.
- **Nunca rode instalação real em um projeto existente sem pedido explícito** do dono do
  projeto. `--dry-run` mostra o que seria feito sem tocar no disco.
- Nenhum teste pode escrever no harness do QAGente nem em `~/.claude`.
