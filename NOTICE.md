# Avisos de terceiros

O QAGente deriva de material de terceiros. Este arquivo reúne os avisos de copyright e os textos
de licença exigidos por esse material, e deve acompanhar qualquer redistribuição do repositório —
é o que satisfaz a cláusula da MIT que manda preservar o aviso "in all copies or substantial
portions of the Software".

O [`README.md`](README.md) explica **o que** foi reaproveitado de cada origem e **o que mudou** na
adaptação. Aqui ficam os avisos formais.

## 1. Licenciamento do próprio QAGente

| Parte | Licença |
|---|---|
| Código (`install.py`, `validate_perfil.py`, `validate_artefatos.py`, `test_install.py`, `validate_skills.py`, `run_evals.py`) | MIT — ver [`LICENSE`](LICENSE) |
| Conteúdo das 6 skills do fluxo (`SKILL.md`) | CC-BY-4.0, declarado no frontmatter de cada arquivo |
| Conteúdo das 5 skills de apoio (`SKILL.md`) | MIT, declarado no frontmatter — são adaptações de material MIT (seção 2) |

Copyright (c) 2026 Marcio Pipuli.

## 2. qa-skills — Petr Kindlmann

Cinco skills de apoio do QAGente são **adaptações declaradas** de skills do repositório
[qa-skills](https://github.com/petrkindlmann/qa-skills), de Petr Kindlmann, licenciado sob MIT.
Elas permanecem sob MIT porque manter a licença de origem é o que preserva a atribuição que ela
exige. O campo `metadata.adaptado_de` no frontmatter de cada skill registra a origem individual.

| Skill do QAGente | Origem em qa-skills |
|---|---|
| `priorizacao-por-risco` | `risk-based-testing` |
| `reproducao-bugs` | `bug-reproduction` |
| `revisao-qualidade-testes` | `ai-qa-review` |
| `confiabilidade-testes` | `test-reliability` |
| `dados-de-teste` | `test-data-management` |

**Indicação de mudanças:** o texto foi reescrito em português; os exemplos de framework passaram de
Vitest/Jest/Playwright para os frameworks declarados pelo perfil do QAGente (Robot Framework,
Cypress, Playwright); a leitura de `.agents/qa-project-context.md` foi substituída pelo par
`.qagente/quality-profile.json` + `contexto/contexto-projeto.md`; e o roteamento entre skills foi
reescrito para o fluxo de fases do QAGente. As skills não são cópias literais.

### Texto da licença

```
MIT License

Copyright (c) 2026 Petr Kindlmann

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 3. agent-skills — Tech Leads Club

As **convenções estruturais** do QAGente vêm de
[agent-skills](https://github.com/tech-leads-club/agent-skills), de Tech Leads Club. Naquele
repositório o código está sob MIT e o conteúdo das skills sob
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/); o QAGente espelha essa mesma separação.

**O que foi adotado:** o frontmatter `name`/`description`/`license`/`metadata`; o formato
`[O quê] + [Quando usar] + [Quando NÃO usar]` na descrição; a pasta `templates/` ao lado de cada
`SKILL.md`; `CLAUDE.md` como ponteiro de uma linha para `AGENTS.md`; e o formato de subagente com
`name`/`description`/`model`/`tools`.

**Indicação de mudanças:** o que foi reaproveitado é a **estrutura**, não o texto. O conteúdo das
seis skills do fluxo é original, escrito para o domínio de QA/SDET — nenhuma delas é cópia ou
adaptação de uma skill de lá.

### Texto da licença

O conteúdo de skills daquele repositório é licenciado sob Creative Commons Attribution 4.0
International (CC-BY-4.0). Texto integral em
<https://creativecommons.org/licenses/by/4.0/legalcode>. O código é licenciado sob MIT:

```
MIT License

Copyright (c) 2026 Tech Leads Club

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
