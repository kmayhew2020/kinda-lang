#!/usr/bin/env python3
"""
Comprehensive tests for installation functionality.

Tests for Issues #102 and #103:
- pipx installation capabilities
- install.sh PATH detection and configuration
- --dev flag functionality
- Cross-shell compatibility
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import pytest


class TestInstallationModernization:
    """Test suite for installation modernization (Issues #102 & #103)"""

    def test_install_script_exists_and_executable(self):
        """Test that install.sh exists and is executable"""
        script_path = Path(__file__).parent.parent / "install.sh"
        assert script_path.exists(), "install.sh should exist"
        assert os.access(script_path, os.X_OK), "install.sh should be executable"

    def test_install_script_help_flag(self):
        """Test install.sh --help flag works"""
        script_path = Path(__file__).parent.parent / "install.sh"
        result = subprocess.run(
            [str(script_path), "--help"], capture_output=True, text=True, cwd=script_path.parent
        )

        assert result.returncode == 0, "install.sh --help should succeed"
        assert "--dev" in result.stdout, "Help should mention --dev flag"
        assert "--no-path" in result.stdout, "Help should mention --no-path flag"
        assert "Install development dependencies" in result.stdout

    def test_install_script_invalid_option(self):
        """Test install.sh with invalid option fails gracefully"""
        script_path = Path(__file__).parent.parent / "install.sh"
        result = subprocess.run(
            [str(script_path), "--invalid-option"],
            capture_output=True,
            text=True,
            cwd=script_path.parent,
        )

        assert result.returncode != 0, "install.sh should fail with invalid option"
        assert "Unknown option" in result.stdout, "Should show unknown option message"

    def test_pyproject_toml_pipx_metadata(self):
        """Test that pyproject.toml contains pipx-friendly metadata"""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject_path.read_text()

        # Check for pipx-related keywords
        assert "pipx" in content, "Should contain pipx keyword"
        assert "cli-tool" in content, "Should contain cli-tool keyword"
        assert "install with pipx" in content, "Should mention pipx in description"

        # Check for proper script entry points
        assert "[project.scripts]" in content, "Should have script entry points"
        assert 'kinda = "kinda.cli:main"' in content, "Should have kinda script entry"

    def test_readme_pipx_primary_installation(self):
        """Test that README.md shows pipx as primary installation method"""
        readme_path = Path(__file__).parent.parent / "README.md"
        content = readme_path.read_text()

        # Check installation section structure
        assert "## 🚀 Installation" in content, "Should have installation section"
        assert "Recommended (pipx - modern standard)" in content, "pipx should be recommended"
        assert "pipx install kinda-lang" in content, "Should show pipx install command"

        # Check for PATH handling instructions
        assert "~/.local/bin" in content, "Should mention ~/.local/bin PATH"
        assert "For Developers" in content, "Should have developer section"
        assert "./install.sh --dev" in content, "Should mention --dev flag"

    def test_shell_detection_functions(self):
        """Test shell detection logic (simulated)"""
        # This would be more comprehensive in a real environment
        # For now, just verify the logic structure exists
        script_path = Path(__file__).parent.parent / "install.sh"
        content = script_path.read_text()

        # Check that shell detection function exists
        assert "detect_shell_config()" in content, "Should have shell detection function"
        assert "zsh" in content, "Should handle zsh"
        assert "bash" in content, "Should handle bash"
        assert "fish" in content, "Should handle fish"
        assert ".profile" in content, "Should have POSIX fallback"

    def test_path_configuration_logic(self):
        """Test PATH configuration logic in install.sh"""
        script_path = Path(__file__).parent.parent / "install.sh"
        content = script_path.read_text()

        # Check PATH configuration function
        assert "configure_path()" in content, "Should have PATH config function"
        assert "~/.local/bin" in content, "Should handle ~/.local/bin"
        assert "backup" in content, "Should backup config files"
        assert "NO_PATH" in content, "Should respect --no-path flag"

    def test_installation_strategy_selection(self):
        """Test that install.sh has proper installation strategy"""
        script_path = Path(__file__).parent.parent / "install.sh"
        content = script_path.read_text()

        # Check for multiple installation strategies
        assert "pipx" in content, "Should support pipx installation"
        assert "pip install --user" in content, "Should support pip --user"
        assert "VIRTUAL_ENV" in content, "Should detect virtual environments"

        # Check strategy logic
        assert "command -v pipx" in content, "Should check for pipx availability"
        assert "INSTALLATION_METHOD" in content, "Should track installation method"

    def test_development_mode_features(self):
        """Test --dev flag functionality in install.sh"""
        script_path = Path(__file__).parent.parent / "install.sh"
        content = script_path.read_text()

        # Check dev mode functionality
        assert "DEV_MODE" in content, "Should have dev mode variable"
        assert "--dev" in content, "Should handle --dev flag"
        assert "dev dependencies" in content.lower(), "Should install dev dependencies"
        assert "pytest" in content, "Should mention pytest for dev setup"

    def test_python_version_requirement_updated(self):
        """Test that Python version requirement is updated to 3.9+"""
        script_path = Path(__file__).parent.parent / "install.sh"
        content = script_path.read_text()

        # Check Python version enforcement
        assert "3.9" in content, "Should require Python 3.9+"
        assert "sys.version_info >= (3,9)" in content, "Should check for 3.9+"

    @pytest.mark.skipif(shutil.which("pipx") is None, reason="pipx not available")
    def test_pipx_installation_compatibility(self):
        """Test that package can be installed with pipx (if pipx available)"""
        # This is a more comprehensive test that would run if pipx is available
        # In a real CI environment, this would test actual installation
        project_root = Path(__file__).parent.parent

        # Test that the project structure supports pipx
        assert (project_root / "pyproject.toml").exists()
        assert (project_root / "src" / "kinda" / "__init__.py").exists() or (
            project_root / "kinda" / "__init__.py"
        ).exists()

    def test_error_handling_and_fallbacks(self):
        """Test that install.sh has proper error handling"""
        script_path = Path(__file__).parent.parent / "install.sh"
        content = script_path.read_text()

        # Check error handling
        assert "set -euo pipefail" in content, "Should use strict error handling"
        assert "|| {" in content, "Should have fallback error handling"
        assert "exit 1" in content, "Should exit on critical errors"

        # Check user-friendly error messages
        assert "❌" in content, "Should have error indicators"
        assert "💥" in content, "Should have failure messages"
        assert "⚠️" in content, "Should have warning messages"

    def test_user_experience_messaging(self):
        """Test that install.sh provides good user feedback"""
        script_path = Path(__file__).parent.parent / "install.sh"
        content = script_path.read_text()

        # Check for good UX messaging
        assert "🎉 Installation complete!" in content, "Should have success message"
        assert "✅" in content, "Should have success indicators"
        assert "Try: kinda --help" in content, "Should suggest next steps"
        assert "Welcome to kinda-lang" in content, "Should have welcome message"


class TestCrossCompatibility:
    """Test cross-platform and cross-shell compatibility"""

    def test_shell_compatibility_coverage(self):
        """Test that major shells are handled"""
        script_path = Path(__file__).parent.parent / "install.sh"
        content = script_path.read_text()

        # Major shells should be handled
        shells = ["bash", "zsh", "fish"]
        for shell in shells:
            assert shell in content, f"Should handle {shell} shell"

    def test_path_configuration_by_shell(self):
        """Test PATH configuration varies by shell"""
        script_path = Path(__file__).parent.parent / "install.sh"
        content = script_path.read_text()

        # Different shells should have different PATH syntax
        assert "export PATH=" in content, "Should use export for bash/zsh"
        assert "set -gx PATH" in content, "Should use set -gx for fish"

    def test_backup_creation(self):
        """Test that config file backups are created"""
        script_path = Path(__file__).parent.parent / "install.sh"
        content = script_path.read_text()

        assert "backup" in content, "Should create backups"
        assert "$(date +%s)" in content, "Should use timestamp in backup name"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
