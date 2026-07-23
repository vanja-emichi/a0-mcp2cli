# MCP2CLI Plugin Integration Project

## Purpose

Canonical workspace for developing, integrating, and validating the `_mcp2cli`
plugin in Agent Zero: a token-efficient bridge that suppresses native MCP schema
injection (`mcp_mode: cli`) and lets agents discover/call MCP tools on demand via
`code_execution_tool` + the upstream `mcp2cli` CLI (`knowsuchagency/mcp2cli`, run via `uvx`).

## Ownership

- **Project owner:** Vanja Emichi
- **Repo:** [vanja-emichi/a0-mcp2cli](https://github.com/vanja-emichi/a0-mcp2cli) on the `project` branch
- **Canonical plugin source:** `main` branch of `vanja-emichi/a0-mcp2cli`
- **Live plugin path:** `/a0/usr/plugins/_mcp2cli` (host: `/home/debian/agent-zero/loloi/usr/plugins/_mcp2cli`) — an independent clone of `main`. Host and container share the filesystem; a commit + push to `main` is visible at the live path after `git pull` there.
- **Upstream reference:** `knowsuchagency/mcp2cli` (PyPI) under `sources/github/` (read-only)

## Scope

- Plugin extensions, skill, helper (`helpers/mcp_servers.py`), webui config, lifecycle hooks
- Token-efficiency evidence: native-schema vs cli-mode prompt size and call success
- Runtime integration: prompt suppression firing, per-project config, credential resolution
- Promotion of validated changes from this workspace (`project` branch) to `main`

This workspace is a checkout of `vanja-emichi/a0-mcp2cli` on branch `project`,
sharing the tree with the plugin source (same repo, both branches touch the same
files). Plugin source changes are committed to `main`; the `project` branch holds
plans, research, evals, and DOX — when editing, keep source files identical to
`main` unless the change is being promoted, and rebase `project` on `main` after
each promotion. Agent Zero project metadata points to
`/a0/usr/projects/plugin_mcp2cli`, not the live plugin path.

## Local Contracts

### Execution topology

- **Codex:** control plane and primary development operator. Edits plans, source
  records, eval definitions, and plugin changes; verifies against the live instance.
- **Agent Zero loloi instance:** runtime target and evaluation environment at
  `127.0.0.1:8082` / https://loloi.emichi.co (container `agent-zero-loloi`).

### Two-runtime model

- **`/opt/venv-a0`** (Python 3.12) — framework runtime. Plugin extensions and hooks
  fire here; `helpers/mcp_servers.py` imports resolve here. All plugin tests and
  prompt-resolution probes run under `/opt/venv-a0/bin/python3`.
- **`/opt/venv`** (Python 3.13) — agent execution runtime. The `uvx mcp2cli` CLI
  invocations the agent makes through `code_execution_tool` execute here.

Verification rule: framework behavior (extension firing, prompt suppression,
config resolution) is verified with `/opt/venv-a0/bin/python3`. CLI workflow is
verified with `/opt/venv/bin/python3` / `uvx`. The two are not interchangeable.

### Plugin contracts (from live plugin DOX)

- Config key is `mcp_mode`: `cli` (default) or `default`. Per-project config overrides global.
- Enabled + `mcp_mode: cli` → native MCP schemas suppressed; agent uses CLI discover → inspect → call.

## Work Guidance

1. **Understand:** document prompt-build hook points and upstream `mcp2cli` CLI surface.
2. **Evaluate:** measure prompt-token delta (cli vs default mode) and call success.
3. **Implement:** change plugin source; commit to `main`; `git pull` at live path.
4. **Validate:** rerun plugin tests under `/opt/venv-a0` and a live headless smoke.

## Verification

- DOX chain: every `AGENTS.md` Child DOX Index link resolves to an existing file.
- Plugin tests: `/opt/venv-a0/bin/python3 -m pytest /a0/usr/plugins/_mcp2cli/tests/`.
- Live smoke: enable cli mode, confirm MCP schema absent from built prompt, then a
  real `uvx mcp2cli` discover/call against a configured server (e.g. `deep-wiki`).

## Child DOX Index

- [docs/AGENTS.md](docs/AGENTS.md) — project documentation (plans, research, source records).
- [sources/AGENTS.md](sources/AGENTS.md) — upstream reference source clones.
- [tests/AGENTS.md](tests/AGENTS.md) — project-level test contracts.
- [planning/AGENTS.md](planning/AGENTS.md) — loose planning notes.
- [tasks/AGENTS.md](tasks/AGENTS.md) — A0 scheduler task scratch files.
