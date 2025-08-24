#!/usr/bin/env python3
"""Tests for kinda CLI commands and infrastructure"""

import subprocess
import sys
import pytest
from pathlib import Path
from unittest.mock import patch
from io import StringIO
import platform

from kinda.cli import main


def normalize_emoji_output(text: str) -> str:
    """Normalize emoji output for cross-platform testing"""
    # On Windows, emojis get converted to ASCII fallbacks
    if platform.system() == "Windows":
        return (text
               .replace("🎲", "*")
               .replace("🤷", "?") 
               .replace("📚", "*")
               .replace("✨", "*")
               .replace("🎯", "*"))
    return text


class TestCLICommands:
    """Test CLI command functionality"""

    def test_help_command(self, capsys):
        """Test --help shows snarky help text"""
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['kinda', '--help']):
                main()
        
        captured = capsys.readouterr()
        assert "A programming language for people who aren't totally sure" in captured.out

    def test_examples_command(self, capsys):
        """Test examples command shows example code"""
        with patch('sys.argv', ['kinda', 'examples']):
            main()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check for expected content
        expected = normalize_emoji_output("🎲 Here are some kinda programs to get you started:")
        assert expected in normalize_emoji_output(output)
        assert "Hello World" in output
        assert "~kinda int" in output
        assert "~sorta print" in output
        assert "~sometimes" in output
        assert "Pro tip:" in output

    def test_syntax_command(self, capsys):
        """Test syntax command shows reference"""
        with patch('sys.argv', ['kinda', 'syntax']):
            main()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check for syntax constructs
        expected = normalize_emoji_output("📚 Kinda Syntax Reference")
        assert expected in normalize_emoji_output(output)
        assert "~kinda int" in output
        assert "~sorta print" in output  
        assert "~sometimes" in output
        assert "Fuzzy reassignment" in output

    def test_transform_command_missing_file(self, capsys):
        """Test transform with missing file shows snarky error"""
        with patch('sys.argv', ['kinda', 'transform', 'nonexistent.knda']):
            main()
        
        captured = capsys.readouterr()
        output = captured.out  # Error messages go to stdout
        assert "🤔" in output or "doesn't exist" in output

    def test_run_command_missing_file(self, capsys):
        """Test run with missing file shows snarky error"""
        with patch('sys.argv', ['kinda', 'run', 'nonexistent.knda']):
            main()
        
        captured = capsys.readouterr()
        output = captured.out  # Error messages go to stdout
        assert "🤷‍♂️" in output or "Can't find" in output

    def test_interpret_command_missing_file(self, capsys):
        """Test interpret with missing file shows snarky error"""
        with patch('sys.argv', ['kinda', 'interpret', 'nonexistent.knda']):
            main()
        
        captured = capsys.readouterr()
        output = captured.out  # Error messages go to stdout
        assert "🙃" in output or "nowhere to be found" in output


class TestCLIIntegration:
    """Test CLI integration with actual kinda command"""

    def test_kinda_command_exists(self):
        """Test that kinda command is available after installation"""
        result = subprocess.run(['kinda', '--help'], capture_output=True, text=True)
        assert result.returncode == 0
        assert "A programming language for people who aren't totally sure" in result.stdout

    def test_examples_command_integration(self):
        """Test examples command via subprocess"""
        result = subprocess.run(['kinda', 'examples'], capture_output=True, text=True)
        assert result.returncode == 0
        expected = normalize_emoji_output("🎲 Here are some kinda programs")
        assert expected in normalize_emoji_output(result.stdout)
        assert "~kinda int" in result.stdout

    def test_syntax_command_integration(self):
        """Test syntax command via subprocess"""  
        result = subprocess.run(['kinda', 'syntax'], capture_output=True, text=True)
        assert result.returncode == 0
        expected = normalize_emoji_output("📚 Kinda Syntax Reference")
        assert expected in normalize_emoji_output(result.stdout)
        assert "~sorta print" in result.stdout

    def test_transform_nonexistent_file(self):
        """Test transform command with nonexistent file"""
        result = subprocess.run(['kinda', 'transform', 'does_not_exist.knda'], 
                              capture_output=True, text=True)
        assert result.returncode != 0
        # Should show error message (in stdout for kinda)
        assert len(result.stdout) > 0

    def test_run_with_actual_example(self):
        """Test run command with actual example file if it exists"""
        example_file = Path("examples/hello.py.knda")
        if example_file.exists():
            result = subprocess.run(['kinda', 'transform', str(example_file)], 
                                  capture_output=True, text=True)
            # Should not crash (return code 0 or at least not crash completely)
            assert result.returncode == 0 or "Traceback" not in result.stderr


class TestInstallationInfrastructure:
    """Test installation scripts and configuration"""

    def test_pyproject_toml_exists(self):
        """Test pyproject.toml has correct metadata"""
        pyproject_path = Path("pyproject.toml")
        assert pyproject_path.exists()
        
        content = pyproject_path.read_text()
        assert 'name = "kinda-lang"' in content
        assert 'version = "0.2.0"' in content
        assert 'kinda = "kinda.cli:main"' in content
        assert 'license = { file = "LICENSE" }' in content

    def test_license_file_exists(self):
        """Test LICENSE file exists"""
        license_path = Path("LICENSE")
        assert license_path.exists()
        
        content = license_path.read_text()
        assert "GNU AFFERO GENERAL PUBLIC LICENSE" in content

    def test_install_scripts_exist(self):
        """Test installation scripts exist and are executable"""
        install_sh = Path("install.sh")
        install_bat = Path("install.bat")
        
        assert install_sh.exists()
        assert install_bat.exists()
        
        # Check install.sh is executable (skip on Windows)
        if platform.system() != "Windows":
            import stat
            mode = install_sh.stat().st_mode
            assert mode & stat.S_IEXEC

    def test_makefile_exists(self):
        """Test Makefile exists with expected targets"""
        makefile = Path("Makefile")
        assert makefile.exists()
        
        content = makefile.read_text()
        assert "install:" in content
        assert "dev:" in content
        assert "test:" in content
        assert "clean:" in content
        assert "examples:" in content

    def test_readme_has_correct_syntax(self):
        """Test README uses unified tilde syntax"""
        readme = Path("README.md")
        assert readme.exists()
        
        # Use UTF-8 encoding to avoid Windows cp1252 issues
        content = readme.read_text(encoding='utf-8')
        # Should use ~= for assignment, not =
        assert "~kinda int x ~= 42" in content
        # Should reference correct license
        assert "AGPL v3" in content
        # Should have installation instructions
        assert "pip install kinda-lang" in content


if __name__ == "__main__":
    pytest.main([__file__])