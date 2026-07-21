"""Tests for scaffold-satellite.py."""

import re
import subprocess
import sys
from pathlib import Path

import pytest

SCAFFOLD_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "scaffold-satellite.py"


def run_scaffold(name: str, output_dir: Path | None = None) -> subprocess.CompletedProcess:
    """Run the scaffold script and return the result."""
    args = [sys.executable, str(SCAFFOLD_SCRIPT), name]
    if output_dir:
        args.append(str(output_dir))
    return subprocess.run(args, capture_output=True, text=True)


class TestValidation:
    """Tests for name validation."""

    def test_valid_simple_name(self, temp_dir):
        """A simple lowercase name should succeed."""
        result = run_scaffold("my-sat", output_dir=temp_dir)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert (temp_dir / "rvrb-my-sat").is_dir()

    def test_valid_underscore_name(self, temp_dir):
        """Names with underscores should succeed."""
        result = run_scaffold("my_sat", output_dir=temp_dir)
        assert result.returncode == 0
        assert (temp_dir / "rvrb-my_sat").is_dir()

    def test_invalid_uppercase(self, temp_dir):
        """Uppercase names should be rejected."""
        result = run_scaffold("MySat", output_dir=temp_dir)
        assert result.returncode != 0

    def test_invalid_spaces(self, temp_dir):
        """Names with spaces should be rejected."""
        result = run_scaffold("my sat", output_dir=temp_dir)
        assert result.returncode != 0

    def test_invalid_special_chars(self, temp_dir):
        """Names with special characters should be rejected."""
        result = run_scaffold("my-sat!", output_dir=temp_dir)
        assert result.returncode != 0

    def test_invalid_start_with_digit(self, temp_dir):
        """Names starting with digits should be rejected."""
        result = run_scaffold("1sat", output_dir=temp_dir)
        assert result.returncode != 0

    def test_duplicate_dir_error(self, temp_dir):
        """Creating a satellite where the dir already exists should fail."""
        (temp_dir / "rvrb-dupe").mkdir()
        result = run_scaffold("dupe", output_dir=temp_dir)
        assert result.returncode != 0
        assert "already exists" in (result.stderr + result.stdout)


class TestScaffoldOutput:
    """Tests for the scaffolded project structure."""

    @pytest.fixture
    def scaffolded(self, temp_dir):
        """Scaffold a test satellite and return its path."""
        result = run_scaffold("test-scout", output_dir=temp_dir)
        assert result.returncode == 0, f"Scaffold failed: {result.stderr}"
        return temp_dir / "rvrb-test-scout"

    def test_directory_structure(self, scaffolded):
        """Scaffolded project has expected directories."""
        assert scaffolded.is_dir()
        assert (scaffolded / "src").is_dir()
        assert (scaffolded / "tests").is_dir()

    def test_pyproject_exists(self, scaffolded):
        """Scaffolded project has a pyproject.toml."""
        pyproject = scaffolded / "pyproject.toml"
        assert pyproject.is_file()
        content = pyproject.read_text()

        # Verify key fields
        assert 'name = "rvrb-test-scout"' in content
        assert "hatchling" in content
        assert "typer" in content
        assert "pydantic" in content
        assert "openai" in content
        assert "pytest" in content
        assert "ruff" in content
        assert "mypy" in content
        assert ">=3.11" in content

    def test_package_init(self, scaffolded):
        """Scaffolded project has __init__.py with version."""
        init_file = scaffolded / "src" / "rvrb_test_scout" / "__init__.py"
        assert init_file.is_file()
        content = init_file.read_text()
        assert '__version__ = "0.1.0"' in content

    def test_cli_module(self, scaffolded):
        """Scaffolded project has a CLI module with v2 flags."""
        cli_file = scaffolded / "src" / "rvrb_test_scout" / "cli.py"
        assert cli_file.is_file()
        content = cli_file.read_text()
        assert "typer.Typer" in content
        assert "rvrb-test-scout" in content
        assert "def version" in content
        # v2 protocol: --json and --model flags
        assert "--json" in content
        assert "--model" in content

    def test_test_file(self, scaffolded):
        """Scaffolded project has a test file with a working test."""
        test_file = scaffolded / "tests" / "test_rvrb_test_scout.py"
        assert test_file.is_file()
        content = test_file.read_text()
        assert "CliRunner" in content
        assert "test_version" in content
        assert "0.1.0" in content

    def test_readme_exists(self, scaffolded):
        """Scaffolded project has a README."""
        readme = scaffolded / "README.md"
        assert readme.is_file()
        content = readme.read_text()
        assert "rvrb-test-scout" in content

    def test_pyproject_entry_point(self, scaffolded):
        """pyproject.toml has the correct entry point."""
        pyproject = scaffolded / "pyproject.toml"
        content = pyproject.read_text()
        assert 'rvrb-test-scout = "rvrb_test_scout.cli:app"' in content

    def test_satellite_protocol_conformance(self, scaffolded):
        """Scaffolded project conforms to satellite protocol requirements."""
        pyproject = scaffolded / "pyproject.toml"
        content = pyproject.read_text()

        # Build backend is hatchling
        assert "hatchling" in content

        # Package naming: rvrb-<name>
        assert re.search(r'name\s*=\s*"rvrb-\w', content)

        # Python >= 3.11
        assert ">=3.11" in content

        # CLI framework is typer
        assert "typer" in content

        # Test runner is pytest
        assert "pytest" in content

        # Entry point uses underscore Python import
        assert re.search(r'rvrb-test-scout\s*=\s*"rvrb_test_scout\.cli:app"', content)

    # --- Protocol v2 tests ---

    def test_protocol_v2_mandatory_modules(self, scaffolded):
        """Mandatory kernel modules exist: __init__, models, provider, engine."""
        pkg_dir = scaffolded / "src" / "rvrb_test_scout"
        for module in ["__init__.py", "models.py", "provider.py", "engine.py"]:
            assert (pkg_dir / module).is_file(), f"Missing mandatory module: {module}"

    def test_models_has_media_types(self, scaffolded):
        """models.py defines MediaModality, MediaInput, MediaOutput."""
        models_file = scaffolded / "src" / "rvrb_test_scout" / "models.py"
        content = models_file.read_text()
        assert "class MediaModality" in content
        assert "TEXT" in content
        assert "AUDIO" in content
        assert "IMAGE" in content
        assert "VIDEO" in content
        assert "class MediaInput" in content
        assert "class MediaOutput" in content

    def test_provider_has_protocol_and_factory(self, scaffolded):
        """provider.py defines ModelProvider Protocol and get_provider()."""
        provider_file = scaffolded / "src" / "rvrb_test_scout" / "provider.py"
        content = provider_file.read_text()
        assert "class ModelProvider" in content
        assert "Protocol" in content
        assert "DEFAULT_MODEL" in content
        assert "def get_provider" in content
        # Fallback pattern for when n3rverberage not installed
        assert "_GenericProvider" in content or "ImportError" in content

    def test_provider_has_env_var_defaults(self, scaffolded):
        """DEFAULT_MODEL reads from env var, not hardcoded."""
        provider_file = scaffolded / "src" / "rvrb_test_scout" / "provider.py"
        content = provider_file.read_text()
        assert "N3RVERBERAGE_DEFAULT_MODEL" in content
        assert "N3RVERBERAGE_DEFAULT_BASE_URL" in content

    def test_provider_has_generic_fallback(self, scaffolded):
        """Provider has _GenericProvider (not Qwen-specific _DashScopeProvider)."""
        provider_file = scaffolded / "src" / "rvrb_test_scout" / "provider.py"
        content = provider_file.read_text()
        assert "_GenericProvider" in content
        # Should NOT have Qwen-specific fallback classes
        assert "_DashScopeProvider" not in content
        assert "_DefaultProvider" not in content

    def test_cli_has_provider_flag(self, scaffolded):
        """CLI has --provider flag."""
        cli_file = scaffolded / "src" / "rvrb_test_scout" / "cli.py"
        content = cli_file.read_text()
        assert "--provider" in content
        assert "N3RVERBERAGE_PROVIDER" in content

    def test_conftest_has_mock_provider(self, scaffolded):
        """tests/conftest.py has MockProvider class."""
        conftest_file = scaffolded / "tests" / "conftest.py"
        assert conftest_file.is_file()
        content = conftest_file.read_text()
        assert "class MockProvider" in content
        assert "def complete" in content
        assert "def complete_structured" in content
        assert "def complete_with_tools" in content

    def test_test_file_uses_mock_provider(self, scaffolded):
        """test_*.py imports and uses MockProvider (except CLI, provider, and models tests)."""
        test_dir = scaffolded / "tests"
        for test_file in test_dir.glob("test_*.py"):
            # CLI tests don't need MockProvider - they test the CLI interface
            if test_file.name == f"test_{scaffolded.name.replace('-', '_')}.py":
                continue
            # Provider tests test provider resolution, not engine behavior
            if test_file.name == "test_provider.py":
                continue
            # Models tests test data structures, not provider behavior
            if test_file.name == "test_models.py":
                continue
            content = test_file.read_text()
            assert "MockProvider" in content, f"{test_file} does not use MockProvider"

    def test_engine_has_provider_injection(self, scaffolded):
        """engine.py has constructor-injected provider with Protocol type hint."""
        engine_file = scaffolded / "src" / "rvrb_test_scout" / "engine.py"
        content = engine_file.read_text()
        assert "class TestScoutEngine" in content
        assert "def __init__(self, provider" in content
        assert "self.provider = provider" in content


class TestScaffoldIntegration:
    """Integration tests that require pip install of scaffolded project."""

    @pytest.fixture
    def scaffolded(self, temp_dir):
        """Scaffold a test satellite and install it."""
        result = run_scaffold("test-integrate", output_dir=temp_dir)
        assert result.returncode == 0
        path = temp_dir / "rvrb-test-integrate"

        # pip install editable
        install = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            capture_output=True,
            text=True,
            cwd=path,
        )
        if install.returncode != 0:
            pytest.skip(f"pip install failed: {install.stderr}")
        return path

    def test_scaffolded_tests_pass(self, scaffolded):
        """The scaffolded project's own tests should pass."""
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v"],
            capture_output=True,
            text=True,
            cwd=scaffolded,
        )
        assert result.returncode == 0, f"Tests failed:\n{result.stdout}\n{result.stderr}"

    def test_cli_help_works(self, scaffolded):
        """The scaffolded CLI should show help."""
        result = subprocess.run(
            [sys.executable, "-m", "rvrb_test_integrate.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=scaffolded,
        )
        assert result.returncode == 0
        assert "Usage" in result.stdout or "Usage" in result.stderr
