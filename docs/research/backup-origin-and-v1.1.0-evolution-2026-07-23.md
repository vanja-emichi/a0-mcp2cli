# MCP2CLI: Backup Origin and v1.1.0 Evolution

Date: 2026-07-23
Author: Codex (control plane), from live repo + backup archaeology

## Origin

Development started in the **vanja-1** backup instance (pre-migration VPS snapshot,
July 10 2026 archive): `/home/debian/agent-zero/backup/vanja-1/usr/projects/mcp2cli/`.
That workspace is an A0 project (`.a0proj/project.json` title "MCP2CLI") containing
the plugin source inline — there was no separate `usr/plugins/` install at that time.
It also holds a vendored copy of upstream `knowsuchagency/mcp2cli` under
`.a0proj/mcp2cli-src/`.

Repo: `vanja-emichi/a0-mcp2cli`. Community index entry: `agent0ai/a0-plugins` →
`plugins/mcp2cli/index.yaml`.

## Version history (git, `main`)

| Commit | Version | What |
| --- | --- | --- |
| `b7f485f` | 1.0.0 | Initial commit — dedicated `tools/mcp2cli.py` Tool class, `prompts/default/agent.system.tools.mcp2cli.md` tool prompt |
| `449c875` | 1.0.x | README: `disabled: true` MCP-server setup pattern |
| `ba583b0` | 1.0.1 | Fix: `hooks.py` bare import fails on fresh installs |
| `d3e600f` | 1.0.x | Test suite, security hardening, UX improvements |
| `1ba721b` | 1.0.2 | `uninstall()` lifecycle hook. **Last commit mirrored in vanja-1 backup** |
| `5b8377c` | 1.1.0 | Instance evolution on loloi (see below) |
| `bcd4d1c` | 1.1.0+ | Rename plugin dir `_mcp2cli` → `mcp2cli` to match index name |

## v1.1.0 changes (`1ba721b..5b8377c`, 21 files, +523/−1637)

Architectural pivot: **dropped the dedicated Tool class entirely** in favor of
prompt-level suppression + the agent's native `code_execution_tool`.

- **Removed:** `tools/mcp2cli.py` (266-line Tool), `prompts/default/agent.system.tools.mcp2cli.md`
  (114-line tool prompt), `tests/test_tool.py`, `test_enhancements.py`, `test_review_fixes.py`.
- **Added:**
  - `default_config.yaml` — `mcp_mode: cli` config key.
  - `extensions/python/_functions/_12_mcp_prompt/build_prompt/end/_10_cli_mode.py` —
    blanks the native MCP schema prompt when cli mode is on.
  - `extensions/python/_functions/_11_tools_prompt/build_prompt/end/_10_strip_mcp_routing.py` —
    strips the dot-prefixed MCP routing line from the tools prompt.
  - `helpers/mcp_servers.py` — resolves configured (disabled) server connection
    strings + credentials into ready-to-use CLI commands; replaces the old Tool.
  - `webui/config.html` — mode dropdown.
  - `AGENTS.md` (plugin DOX), `tests/test_skill.py`.
- **Changed:** `skills/mcp2cli/SKILL.md` rewritten (290 → concise discover → inspect →
  call workflow); `plugin.yaml` (per-project config support); README slimmed.

Rationale: a dedicated Tool still injects its own prompt/schema every turn; routing
through `code_execution_tool` + `uvx mcp2cli` costs ~100–300 tokens/turn vs
5,000–20,000 for native MCP injection. The `_functions` prompt-build hooks are the
framework-sanctioned extension points, so no core patch is needed.

## Rename commit (`bcd4d1c`)

- Dir `_mcp2cli` → `mcp2cli` (community index name; `_` prefix is reserved for
  internal plugins in `agent0ai/a0-plugins` rules).
- `plugins.get_plugin_config("mcp2cli")` in both `_functions` extensions.
- Helper paths in `mcp_servers.py` docstring + `SKILL.md`.
- Verified: 48/48 tests pass under `/opt/venv-a0`; framework lists `mcp2cli`.

## Backup-only content (not carried forward)

- `tools/`, `prompts/` dirs — intentionally obsolete (see v1.1.0 rationale).
- `.a0proj/knowledge/` (fragments, instruments, main, solutions) — old workspace
  knowledge; superseded by this project's DOX.
- `.a0proj/mcp2cli-src/` — vendored upstream CLI source; re-vendor under
  `sources/github/` here if needed for reference.
