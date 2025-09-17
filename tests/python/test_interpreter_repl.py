#!/usr/bin/env python3

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from kinda.interpreter.repl import run_interpreter, load_fuzzy_runtime


class TestInterpreterREPL:
    """Test interpreter REPL functionality and exception handling"""

    def test_run_interpreter_execution_exception(self):
        """Test run_interpreter handles execution exceptions"""
        # Create a temporary kinda file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py.knda", delete=False) as f:
            f.write("~kinda int x = 42\n~sorta print(x)")
            temp_path = f.name

        try:
            # Mock print to capture error messages
            captured_output = []

            def mock_print(*args, **kwargs):
                captured_output.append(" ".join(str(arg) for arg in args))

            with patch("builtins.print", side_effect=mock_print):
                # Temporarily patch exec to raise an exception only when executing user code
                original_exec = exec

                def selective_exec(code, globals_dict=None, locals_dict=None):
                    # If this looks like user code (not helper imports), raise exception
                    code_str = str(code)
                    if "~kinda int x = 42" in code_str or "x = kinda_int(42)" in code_str:
                        raise RuntimeError("Test execution error")
                    return original_exec(code, globals_dict, locals_dict)

                with patch("builtins.exec", side_effect=selective_exec):
                    # This should not raise, but should print error message
                    run_interpreter(temp_path)

                    # Check that error messages were printed
                    output = " ".join(captured_output)
                    assert "Well, that went sideways: Test execution error" in output
                    assert "Your code was... creative. Maybe too creative." in output
        finally:
            import os

            try:
                os.unlink(temp_path)
            except (OSError, PermissionError):
                pass  # Ignore Windows file permission issues

    def test_run_interpreter_successful_execution(self):
        """Test run_interpreter with successful execution"""
        # Create a simple kinda file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py.knda", delete=False) as f:
            f.write("x = 42")
            temp_path = f.name

        try:
            # Mock the transformer and runtime components
            with patch("kinda.langs.python.transformer.transform_file") as mock_transform:
                mock_transform.return_value = "x = 42"

                with patch("kinda.langs.python.runtime_gen.generate_runtime") as mock_gen_runtime:
                    with patch(
                        "kinda.langs.python.runtime_gen.generate_runtime_helpers"
                    ) as mock_gen_helpers:
                        mock_gen_helpers.return_value = ""

                        with patch("kinda.interpreter.repl.load_fuzzy_runtime") as mock_load_fuzzy:
                            mock_fuzzy = MagicMock()
                            mock_fuzzy.env = {}
                            mock_load_fuzzy.return_value = mock_fuzzy

                            # Should execute without exceptions
                            run_interpreter(temp_path)
        finally:
            import os

            try:
                os.unlink(temp_path)
            except (OSError, PermissionError):
                pass  # Ignore Windows file permission issues

    def test_load_fuzzy_runtime(self):
        """Test loading fuzzy runtime module"""
        # Create a temporary fuzzy.py file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
import random
env = {'test_var': 42}

def test_function():
    return 'test'
"""
            )
            temp_path = Path(f.name)

        try:
            fuzzy = load_fuzzy_runtime(temp_path)
            assert hasattr(fuzzy, "env")
            assert fuzzy.env["test_var"] == 42
            assert hasattr(fuzzy, "test_function")
            assert fuzzy.test_function() == "test"
        finally:
            import os
            import sys

            # Clean up sys.modules
            if "fuzzy" in sys.modules:
                del sys.modules["fuzzy"]
            try:
                os.unlink(temp_path)
            except (OSError, PermissionError):
                pass  # Ignore Windows file permission issues

    def test_run_interpreter_with_various_exceptions(self):
        """Test run_interpreter with different types of exceptions"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py.knda", delete=False) as f:
            f.write("x = 1 / 0")  # This will cause division by zero
            temp_path = f.name

        try:
            # Test different exception types
            exception_types = [
                ZeroDivisionError("division by zero"),
                NameError("name 'undefined_var' is not defined"),
                TypeError("'int' object is not callable"),
                ValueError("invalid literal for int()"),
                AttributeError("'NoneType' object has no attribute 'method'"),
            ]

            for exception in exception_types:
                # Mock print to capture error messages
                captured_output = []

                def mock_print(*args, **kwargs):
                    captured_output.append(" ".join(str(arg) for arg in args))

                with patch("builtins.print", side_effect=mock_print):
                    # Temporarily patch exec to raise exception only when executing user code
                    original_exec = exec

                    def selective_exec(code, globals_dict=None, locals_dict=None):
                        # If this looks like user code (not helper imports), raise exception
                        code_str = str(code)
                        if "x = 1 / 0" in code_str or "1 / 0" in code_str:
                            raise exception
                        return original_exec(code, globals_dict, locals_dict)

                    with patch("builtins.exec", side_effect=selective_exec):
                        run_interpreter(temp_path)

                        # Check error was handled gracefully
                        output = " ".join(captured_output)
                        assert str(exception) in output
        finally:
            import os

            try:
                os.unlink(temp_path)
            except (OSError, PermissionError):
                pass  # Ignore Windows file permission issues
