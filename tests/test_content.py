from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = PLUGIN_ROOT / "skills" / "mcp2cli" / "SKILL.md"
PROMPT_PATH = PLUGIN_ROOT / "prompts" / "default" / "agent.system.tools.mcp2cli.md"
README_PATH = PLUGIN_ROOT / "README.md"


class TestSkillFile:
    def test_file_exists(self):
        assert SKILL_PATH.is_file()

    def test_has_yaml_frontmatter(self):
        content = SKILL_PATH.read_text()
        assert content.startswith("---")
        assert content.count("---") >= 2

    def test_yaml_has_name(self):
        content = SKILL_PATH.read_text()
        fm = content.split("---")[1]
        assert "name:" in fm

    def test_yaml_has_description(self):
        content = SKILL_PATH.read_text()
        fm = content.split("---")[1]
        assert "description:" in fm

    def test_yaml_has_trigger_patterns(self):
        content = SKILL_PATH.read_text()
        fm = content.split("---")[1]
        assert "trigger_patterns:" in fm

    def test_body_mentions_workflow(self):
        content = SKILL_PATH.read_text()
        body = "---".join(content.split("---")[2:])
        assert "list" in body.lower()
        assert "search" in body.lower()
        assert "help" in body.lower()
        assert "call" in body.lower()

    def test_body_mentions_arguments(self):
        content = SKILL_PATH.read_text()
        body = "---".join(content.split("---")[2:])
        assert "server" in body.lower()
        assert "action" in body.lower()
        assert "tool_name" in body.lower()
        assert "params" in body.lower()

    def test_body_mentions_toon(self):
        content = SKILL_PATH.read_text()
        body = "---".join(content.split("---")[2:])
        assert "toon" in body.lower()

    def test_body_mentions_adhoc(self):
        content = SKILL_PATH.read_text()
        body = "---".join(content.split("---")[2:])
        assert "mcp_url" in body or "adhoc" in body.lower()

    def test_body_mentions_token_savings(self):
        content = SKILL_PATH.read_text()
        body = "---".join(content.split("---")[2:])
        assert "token" in body.lower()


class TestPromptFile:
    def test_file_exists(self):
        assert PROMPT_PATH.is_file()

    def test_is_not_empty(self):
        assert len(PROMPT_PATH.read_text()) > 100

    def test_mentions_mcp2cli(self):
        content = PROMPT_PATH.read_text().lower()
        assert "mcp2cli" in content

    def test_mentions_all_actions(self):
        content = PROMPT_PATH.read_text().lower()
        for action in ["list", "search", "help", "call", "servers"]:
            assert action in content

    def test_mentions_adhoc_url(self):
        content = PROMPT_PATH.read_text()
        assert "mcp_url" in content

    def test_mentions_adhoc_stdio(self):
        content = PROMPT_PATH.read_text()
        assert "mcp_stdio" in content

    def test_mentions_toon(self):
        content = PROMPT_PATH.read_text().lower()
        assert "toon" in content

    def test_has_usage_examples(self):
        content = PROMPT_PATH.read_text()
        assert "tool_name" in content
        assert "tool_args" in content

    def test_mentions_discovery_workflow(self):
        content = PROMPT_PATH.read_text().lower()
        assert "discover" in content


class TestReadmeFile:
    def test_file_exists(self):
        assert README_PATH.is_file()

    def test_mentions_token_savings(self):
        content = README_PATH.read_text().lower()
        assert "token" in content

    def test_mentions_setup_steps(self):
        content = README_PATH.read_text().lower()
        assert "setup" in content or "install" in content

    def test_has_usage_workflow(self):
        content = README_PATH.read_text().lower()
        assert "action" in content
        assert "list" in content

    def test_mentions_disabled_setting(self):
        content = README_PATH.read_text()
        assert 'disabled' in content

    def test_has_argument_reference_table(self):
        content = README_PATH.read_text()
        assert "Argument" in content
        assert "Description" in content


class TestFileConsistency:
    def test_skill_and_prompt_both_describe_actions(self):
        skill = SKILL_PATH.read_text().lower()
        prompt = PROMPT_PATH.read_text().lower()
        for action in ["list", "search", "help", "call"]:
            assert action in skill
            assert action in prompt

    def test_readme_and_skill_both_mention_toon(self):
        readme = README_PATH.read_text().lower()
        skill = SKILL_PATH.read_text().lower()
        assert "toon" in readme
        assert "toon" in skill
