import yaml
from pathlib import Path

import pytest

MANIFEST_PATH = Path(__file__).resolve().parent.parent / "plugin.yaml"


def _load_manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


class TestManifestStructure:
    def test_file_exists(self):
        assert MANIFEST_PATH.is_file()

    def test_valid_yaml(self):
        data = _load_manifest()
        assert isinstance(data, dict)

    def test_required_fields(self):
        data = _load_manifest()
        for field in ["name", "title", "description", "version"]:
            assert field in data, f"Missing field: {field}"

    def test_name_is_mcp2cli(self):
        data = _load_manifest()
        assert data["name"] == "mcp2cli"

    def test_title_is_mcp2cli(self):
        data = _load_manifest()
        assert data["title"] == "MCP2CLI"

    def test_description_not_empty(self):
        data = _load_manifest()
        assert len(data["description"]) > 20

    def test_version_is_valid_semver(self):
        data = _load_manifest()
        ver = data["version"]
        parts = ver.split(".")
        assert len(parts) == 2 or len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_per_project_config_is_false(self):
        data = _load_manifest()
        assert data.get("per_project_config") is False

    def test_per_agent_config_is_false(self):
        data = _load_manifest()
        assert data.get("per_agent_config") is False

    def test_always_enabled_is_false(self):
        data = _load_manifest()
        assert data.get("always_enabled") is False


class TestManifestReferences:
    def test_description_mentions_token_savings(self):
        data = _load_manifest()
        desc = data["description"].lower()
        assert "token" in desc

    def test_description_mentions_mcp(self):
        data = _load_manifest()
        desc = data["description"].lower()
        assert "mcp" in desc
