"""
Comprehensive test suite for kinda/run.py
Target: 95% coverage for the run execution module
"""

import pytest
import subprocess
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import tempfile
import sys

# Import the run module
from kinda import run


class TestExecuteFunction:
    """Test the execute function that transforms and runs .knda files."""

    def test_execute_with_valid_transformer(self):
        """Test execute with a valid transformer."""
        # Create a mock transformer
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = Path("/tmp/build/output.py")

        # Create a temporary input file
        with tempfile.NamedTemporaryFile(suffix=".knda", delete=False) as f:
            input_path = Path(f.name)
            f.write(b"~sorta print('Hello')")

        try:
            with patch("subprocess.run") as mock_subprocess:
                with patch("builtins.print") as mock_print:
                    run.execute(input_path, out_dir="build", transformer=mock_transformer)

                    # Verify transformer was called
                    mock_transformer.transform.assert_called_once_with(
                        input_path, out_dir=Path("build")
                    )

                    # Verify subprocess was called with correct arguments
                    mock_subprocess.assert_called_once()
                    args, kwargs = mock_subprocess.call_args
                    assert args[0][0] == "python"
                    assert str(Path("/tmp/build/output.py")) in args[0][1]

                    # Verify PYTHONPATH was set
                    assert "env" in kwargs
                    assert "PYTHONPATH" in kwargs["env"]

                    # Verify print statements
                    mock_print.assert_any_call(
                        f"[kinda] Running transformed file: {Path('/tmp/build/output.py')}"
                    )
        finally:
            # Clean up
            if input_path.exists():
                input_path.unlink()

    def test_execute_with_no_transformer(self):
        """Test execute raises ValueError when no transformer provided."""
        input_path = Path("test.knda")

        with pytest.raises(ValueError, match="No transformer provided"):
            run.execute(input_path, out_dir="build", transformer=None)

    def test_execute_with_multiple_output_files(self):
        """Test execute raises error when transformer returns multiple files."""
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = [Path("file1.py"), Path("file2.py")]

        input_path = Path("test.knda")

        with pytest.raises(ValueError, match="Expected one transformed file, got multiple"):
            run.execute(input_path, transformer=mock_transformer)

    def test_execute_with_list_single_file(self):
        """Test execute handles transformer returning list with single file."""
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = [Path("/tmp/build/single.py")]

        with tempfile.NamedTemporaryFile(suffix=".knda", delete=False) as f:
            input_path = Path(f.name)

        try:
            with patch("subprocess.run"):
                with patch("builtins.print"):
                    run.execute(input_path, transformer=mock_transformer)

                    # Verify transformer was called
                    mock_transformer.transform.assert_called_once()
        finally:
            if input_path.exists():
                input_path.unlink()

    def test_execute_pythonpath_setup(self):
        """Test that PYTHONPATH is correctly configured."""
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = Path("/tmp/output.py")

        input_path = Path("test.knda")

        with patch("subprocess.run") as mock_subprocess:
            with patch("builtins.print"):
                # Set up existing PYTHONPATH
                original_pythonpath = "/some/existing/path"
                with patch.dict(os.environ, {"PYTHONPATH": original_pythonpath}):
                    run.execute(input_path, transformer=mock_transformer)

                    # Get the env passed to subprocess
                    call_kwargs = mock_subprocess.call_args.kwargs
                    env = call_kwargs["env"]

                    # Verify PYTHONPATH includes both project root and existing path
                    pythonpath = env["PYTHONPATH"]
                    assert original_pythonpath in pythonpath

                    # Project root should be in the path
                    project_root = Path(run.__file__).resolve().parent.parent
                    assert str(project_root) in pythonpath

    def test_execute_pythonpath_without_existing(self):
        """Test PYTHONPATH setup when no existing PYTHONPATH."""
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = Path("/tmp/output.py")

        input_path = Path("test.knda")

        with patch("subprocess.run") as mock_subprocess:
            with patch("builtins.print"):
                # Ensure no existing PYTHONPATH
                with patch.dict(os.environ, {}, clear=True):
                    run.execute(input_path, transformer=mock_transformer)

                    # Get the env passed to subprocess
                    call_kwargs = mock_subprocess.call_args.kwargs
                    env = call_kwargs["env"]

                    # Verify PYTHONPATH is set
                    assert "PYTHONPATH" in env
                    pythonpath = env["PYTHONPATH"]

                    # Project root should be in the path
                    project_root = Path(run.__file__).resolve().parent.parent
                    assert str(project_root) in pythonpath

                    # Should not have trailing separator
                    assert not pythonpath.endswith(os.pathsep)

    def test_execute_custom_output_directory(self):
        """Test execute with custom output directory."""
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = Path("/custom/dir/output.py")

        input_path = Path("test.knda")
        custom_dir = "custom_build"

        with patch("subprocess.run"):
            with patch("builtins.print"):
                run.execute(input_path, out_dir=custom_dir, transformer=mock_transformer)

                # Verify transformer was called with custom directory
                mock_transformer.transform.assert_called_once_with(
                    input_path, out_dir=Path(custom_dir)
                )

    def test_execute_debug_output(self):
        """Test that debug output is printed."""
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = Path("/tmp/output.py")

        input_path = Path("test.knda")

        with patch("subprocess.run"):
            with patch("builtins.print") as mock_print:
                run.execute(input_path, transformer=mock_transformer)

                # Check for debug output
                print_calls = [str(call) for call in mock_print.call_args_list]
                debug_call_found = any("[debug] PYTHONPATH" in str(call) for call in print_calls)
                assert debug_call_found, "Debug output for PYTHONPATH not found"

    def test_execute_path_object_handling(self):
        """Test execute handles both string and Path objects."""
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = Path("/tmp/output.py")

        # Test with string path
        with patch("subprocess.run"):
            with patch("builtins.print"):
                run.execute("test.knda", transformer=mock_transformer)
                mock_transformer.transform.assert_called()
                call_args = mock_transformer.transform.call_args[0]
                assert isinstance(call_args[0], Path)

        # Reset mock
        mock_transformer.reset_mock()

        # Test with Path object
        with patch("subprocess.run"):
            with patch("builtins.print"):
                run.execute(Path("test.knda"), transformer=mock_transformer)
                mock_transformer.transform.assert_called()
                call_args = mock_transformer.transform.call_args[0]
                assert isinstance(call_args[0], Path)

    def test_execute_subprocess_environment_copy(self):
        """Test that subprocess gets a copy of the environment."""
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = Path("/tmp/output.py")

        input_path = Path("test.knda")

        # Set some test environment variables
        test_env = {"TEST_VAR": "test_value", "ANOTHER_VAR": "another_value"}

        with patch("subprocess.run") as mock_subprocess:
            with patch("builtins.print"):
                with patch.dict(os.environ, test_env):
                    run.execute(input_path, transformer=mock_transformer)

                    # Get the env passed to subprocess
                    call_kwargs = mock_subprocess.call_args.kwargs
                    env = call_kwargs["env"]

                    # Verify test variables are preserved
                    assert env["TEST_VAR"] == "test_value"
                    assert env["ANOTHER_VAR"] == "another_value"

                    # Verify it's a copy, not the original
                    assert env is not os.environ
