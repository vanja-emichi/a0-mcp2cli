# MCP2CLI Plugin DOX

## Purpose

Token-efficient bridge to any MCP server. Suppresses native MCP schema injection
(`mcp_mode: cli`) and lets agents discover/call MCP tools on demand via
`code_execution_tool` + the upstream `mcp2cli` CLI binary (`knowsuchagency/mcp2cli`,
PyPI v3.3.1, run via `uvx`).

## Knowledge

- **Owning KB:** none dedicated — catalog entry in `~/knowledge/agent_zero_plugins` (② Tool). Promote to a dedicated KB if this plugin grows substantial durable knowledge (Hub placement rule #7).
- **Access:** OpenKnowledge MCP only — `cwd: ~/knowledge/agent_zero_plugins`. Tools: `exec`, `search`, `write`, `edit`, `audit`, `lint`. Never `lsp` on KB markdown.
- **Fleet index:** `vanja-emichi/vbunjevac` → `registry/repos.md`.

## Ownership

This is a community plugin in `usr/plugins/` (user-first discovery). No bundled
sibling. Enabled on this instance (`.toggle-1`).

## Architecture

No dedicated Tool class. The agent uses the standard `code_execution_tool`
(runtime=terminal) for all MCP interactions. The plugin provides:

- **Extensions** — suppress MCP prompts and redirect the agent to the CLI workflow.
- **A skill** — teaches the discover → inspect → call workflow.
- **A helper script** — resolves server configs + credentials into ready-to-use commands.

### Files

| Path | Purpose |
| --- | --- |
| `default_config.yaml` | Default config: `mcp_mode: cli` |
| `extensions/python/_functions/_12_mcp_prompt/build_prompt/end/_10_cli_mode.py` | Suppresses native MCP schema when `mcp_mode=cli` (sets `data["result"]=""`) |
| `extensions/python/_functions/_11_tools_prompt/build_prompt/end/_10_strip_mcp_routing.py` | Strips dot-prefixed MCP routing line from tools prompt in cli mode |
| `extensions/python/system_prompt/_30_mcp2cli_skill_hint.py` | Injects "load mcp2cli skill" hint |
| `skills/mcp2cli/SKILL.md` | Teaches agent to use `code_execution_tool` + `uvx mcp2cli` |
| `helpers/mcp_servers.py` | Resolves configured server connection strings with credentials |
| `hooks.py` / `execute.py` | Plugin lifecycle (install/uninstall `mcp2cli` binary) |
| `webui/config.html` | Mode dropdown (`mcp_mode: cli` / `default`) |

## Local Contracts

- `mcp_mode` config key (not `mode`): `cli` (default) or `default`.
- Plugin enabled + `mcp_mode: cli` → MCP schemas suppressed, agent uses CLI.
- Plugin enabled + `mcp_mode: default` → native injection (stock behavior).
- Plugin disabled → extensions don't fire → native injection (stock behavior).
- Extensions check `_cli_mode_active()` which requires plugin enabled AND `mcp_mode=cli`.
- The `@extensible` hook path is computed from `func.__module__` (bare filename
  via `import_module`), so hooks live at `_functions/<module_name>/<func>/end/`,
  not nested under `extensions/python/system_prompt/`.
- `helpers/mcp_servers.py` is location-independent (resolves `/a0` root
  automatically); works from both `plugins/` and `usr/plugins/`.

## Verification

```bash
# Plugin tests
docker exec -w /a0/usr/plugins/mcp2cli agent-zero-loloi /opt/venv-a0/bin/python -m pytest tests/ -v

# Prompt context-engineering tests
docker exec -w /a0 -e PYTHONPATH=/a0 agent-zero-loloi /opt/venv-a0/bin/python -m pytest tests/test_prompt_context_engineering.py -v
```

## Child DOX Index

| Child | Scope |
| --- | --- |
| [extensions/AGENTS.md](extensions/AGENTS.md) | Prompt-build/system-prompt suppression hooks. |
| [helpers/AGENTS.md](helpers/AGENTS.md) | `mcp_servers.py` config/credential resolver. |
| [skills/AGENTS.md](skills/AGENTS.md) | Agent-facing CLI workflow skill. |
| [tests/AGENTS.md](tests/AGENTS.md) | Plugin test contracts. |
| [webui/AGENTS.md](webui/AGENTS.md) | Plugin config panel. |

## References

| Fact | Canonical owner |
| --- | --- |
| Plugin discovery, shadowing, manifest rules | root `plugins/AGENTS.md` |
| MCP handler compact rendering | `helpers/mcp_handler.py.dox.md` |
| Context-engineering audit findings | `CONTEXT_ENGINEERING_PROMPT_AUDIT.md` |
| Upstream CLI | `knowsuchagency/mcp2cli` (PyPI v3.3.1) |
