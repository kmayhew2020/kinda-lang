#!/usr/bin/env python3

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess


class TestInterpreterMain:
    """Test interpreter/__main__.py module execution"""

    def test_interpreter_main_import_error_handling(self):
        """Test that interpreter __main__ imports and runs CLI correctly"""
        # Get project root dynamically
        project_root = Path(__file__).parent.parent.parent

        # Test that the module imports successfully and runs the CLI
        result = subprocess.run(
            [sys.executable, "-m", "kinda.interpreter"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )

        # Should fail with CLI usage error (not import error) because no command provided
        assert result.returncode == 2  # CLI usage error, not import error
        assert "the following arguments are required: command" in result.stderr
        # Should not have import errors
        assert "ImportError" not in result.stderr

    def test_interpreter_main_with_mock_cli(self):
        """Test interpreter __main__ execution with mocked cli module"""
        # Get project root dynamically
        project_root = Path(__file__).parent.parent.parent
        main_file = project_root / "kinda" / "interpreter" / "__main__.py"

        # Create a mock cli module in the interpreter package
        mock_cli = MagicMock()
        mock_cli.main = MagicMock()

        # Mock the import and execution
        with patch.dict("sys.modules", {"kinda.cli": mock_cli}):
            # Import the __main__ module, which should execute cli.main()
            import importlib.util

            spec = importlib.util.spec_from_file_location("test_main", str(main_file))
            test_main = importlib.util.module_from_spec(spec)

            # This should call cli.main() if executed as main
            with patch("__main__.__name__", "__main__"):
                try:
                    spec.loader.exec_module(test_main)
                except SystemExit:
                    pass  # Expected if cli.main() calls sys.exit

    def test_interpreter_main_file_structure(self):
        """Test that the __main__.py file has expected structure"""
        # Get project root dynamically
        project_root = Path(__file__).parent.parent.parent
        main_file = project_root / "kinda" / "interpreter" / "__main__.py"
        assert main_file.exists()

        content = main_file.read_text()
        # Should contain the import and main execution
        assert "from kinda import cli" in content
        assert "cli.main()" in content
        assert 'if __name__ == "__main__":' in content

    def test_interpreter_repl_module_exists(self):
        """Test that related interpreter modules exist"""
        # Test that repl module exists (which is the actual working interpreter)
        from kinda.interpreter import repl

        assert hasattr(repl, "run_interpreter")
        assert callable(repl.run_interpreter)
