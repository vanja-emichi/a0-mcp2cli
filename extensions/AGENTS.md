# extensions/ DOX

## Purpose
Prompt-build and system-prompt hooks that implement cli-mode suppression.

## Ownership
- `_functions/_12_mcp_prompt/build_prompt/end/_10_cli_mode.py` — blanks native MCP schema prompt when `mcp_mode=cli`.
- `_functions/_11_tools_prompt/build_prompt/end/_10_strip_mcp_routing.py` — strips dot-prefixed MCP routing line from tools prompt.
- `system_prompt/_30_mcp2cli_skill_hint.py` — injects "load mcp2cli skill" hint.

## Local Contracts
- Hook path derives from `func.__module__` (bare filename): `_functions/<module_name>/<func>/end/`, not nested under `system_prompt/`.
- Both `_functions` hooks gate on `_cli_mode_active()`: plugin enabled AND `mcp_mode=cli` (per-project config overrides global).
- Suppression must be total and silent in cli mode — never leave a partial schema or routing line behind.

## Verification
`docker exec -w /a0/usr/plugins/mcp2cli agent-zero-loloi /opt/venv-a0/bin/python -m pytest tests/test_extension.py -v`
