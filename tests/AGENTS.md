# tests/ DOX

## Purpose
Plugin unit/contract tests, all runnable under the framework runtime.

## Ownership
- `test_manifest.py` — plugin.yaml name/title contracts.
- `test_extension.py` — system-prompt hint + hook wiring.
- `test_content.py` — README/skill content contracts.
- `test_skill.py` — SKILL.md workflow contracts.
- `test_hooks.py` — lifecycle hooks (install/uninstall).

## Local Contracts
- Run under `/opt/venv-a0` (framework runtime) — these guard framework-facing contracts.
- `conftest.py` computes `plugin_root` from the test file location; keep it rename-safe.

## Verification
`docker exec -w /a0/usr/plugins/mcp2cli agent-zero-loloi /opt/venv-a0/bin/python -m pytest tests/ -q` → 48 passed.
