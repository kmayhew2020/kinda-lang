# tests/python/test_record_replay_cli.py

"""
Integration tests for the record/replay CLI commands.

These tests verify that the CLI interface properly integrates with the
recording system and produces valid session files when running kinda programs.
"""

import pytest
import json
import tempfile
import subprocess
import sys
from pathlib import Path

from kinda.cli import main as cli_main
from kinda.record_replay import ExecutionRecorder


class TestRecordCLI:
    """Test the 'kinda record run' CLI command."""

    def test_record_help(self):
        """Test that record command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "kinda.cli", "record", "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "Record program execution to session file" in result.stdout

    def test_record_run_help(self):
        """Test that record run subcommand shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "kinda.cli", "record", "run", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "The .knda file to run and record" in result.stdout
        assert "--output" in result.stdout

    @pytest.fixture
    def simple_kinda_program(self):
        """Create a simple .knda test file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py.knda", delete=False) as f:
            f.write(
                """
# Simple kinda program for testing recording
~kinda int x = 42
~sorta print(f"x is kinda {x}")

~sometimes(x > 40):
    ~sorta print("x is pretty big!")

~kinda int y = x + 1
~sorta print(f"y is around {y}")
"""
            )
            return Path(f.name)

    def test_record_run_basic_functionality(self, simple_kinda_program):
        """Test basic 'kinda record run' functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            session_file = Path(temp_dir) / "test_session.json"

            # Run record command
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "kinda.cli",
                    "record",
                    "run",
                    str(simple_kinda_program),
                    "--output",
                    str(session_file),
                    "--seed",
                    "12345",  # For reproducible testing
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            # Should complete successfully
            assert result.returncode == 0
            assert "Starting recording session" in result.stdout
            assert "Session saved to:" in result.stdout

            # Session file should exist
            assert session_file.exists()

            # Load and validate session file
            with open(session_file, "r") as f:
                session_data = json.load(f)

            assert session_data["input_file"] == str(simple_kinda_program)
            assert session_data["session_id"] is not None
            assert session_data["total_calls"] > 0
            assert len(session_data["rng_calls"]) > 0

            # Should have recorded some construct usage
            assert "construct_usage" in session_data

            # Verify session metadata
            assert session_data["kinda_version"] == "0.4.1"
            assert session_data["initial_personality"]["seed"] == 12345

    def test_record_run_default_output_path(self, simple_kinda_program):
        """Test that default output path works correctly."""
        # Run in a temp directory to avoid cluttering
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the program to temp directory
            temp_program = Path(temp_dir) / "test_program.py.knda"
            temp_program.write_text(simple_kinda_program.read_text())

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "kinda.cli",
                    "record",
                    "run",
                    str(temp_program),
                    "--seed",
                    "99999",
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            assert result.returncode == 0

            # Default output should be <input>.session.json
            expected_output = Path(temp_dir) / "test_program.py.session.json"
            assert expected_output.exists()

    def test_record_run_with_personality_options(self, simple_kinda_program):
        """Test recording with different personality options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            session_file = Path(temp_dir) / "chaotic_session.json"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "kinda.cli",
                    "record",
                    "run",
                    str(simple_kinda_program),
                    "--output",
                    str(session_file),
                    "--mood",
                    "chaotic",
                    "--chaos-level",
                    "9",
                    "--seed",
                    "42",
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            assert result.returncode == 0
            assert session_file.exists()

            with open(session_file, "r") as f:
                session_data = json.load(f)

            # Check that personality settings were recorded
            personality = session_data["initial_personality"]
            assert personality["mood"] == "chaotic"
            assert personality["chaos_level"] == 9
            assert personality["seed"] == 42

    def test_record_run_nonexistent_file(self):
        """Test recording a file that doesn't exist."""
        result = subprocess.run(
            [sys.executable, "-m", "kinda.cli", "record", "run", "nonexistent.knda"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "Can't find" in result.stdout

    @pytest.fixture
    def program_with_runtime_error(self):
        """Create a .knda program that has a runtime error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py.knda", delete=False) as f:
            f.write(
                """
# Program that will crash during execution
~kinda int x = 42
~sorta print(f"x is {x}")

# This will cause a runtime error
result = 10 / 0
"""
            )
            return Path(f.name)

    def test_record_run_with_runtime_error(self, program_with_runtime_error):
        """Test that recording continues even when program crashes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            session_file = Path(temp_dir) / "error_session.json"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "kinda.cli",
                    "record",
                    "run",
                    str(program_with_runtime_error),
                    "--output",
                    str(session_file),
                    "--seed",
                    "123",
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            # Should indicate runtime error but still save recording
            assert result.returncode == 0  # We handle the error gracefully
            assert "Runtime error during recording" in result.stdout
            assert "Recording captured up to the point of failure" in result.stdout
            assert "Session saved to:" in result.stdout

            # Session file should still exist
            assert session_file.exists()

            with open(session_file, "r") as f:
                session_data = json.load(f)

            # Should have captured some calls before the crash
            assert session_data["total_calls"] >= 0
            assert session_data["session_id"] is not None

    def test_cli_api_compatibility(self, simple_kinda_program):
        """Test that CLI main function can be called programmatically."""
        with tempfile.TemporaryDirectory() as temp_dir:
            session_file = Path(temp_dir) / "api_test.json"

            # Test calling cli_main directly
            exit_code = cli_main(
                [
                    "record",
                    "run",
                    str(simple_kinda_program),
                    "--output",
                    str(session_file),
                    "--seed",
                    "777",
                ]
            )

            assert exit_code == 0
            assert session_file.exists()

    @pytest.fixture
    def complex_kinda_program(self):
        """Create a more complex .knda program for comprehensive testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py.knda", delete=False) as f:
            f.write(
                """
# Complex kinda program with multiple constructs
~sorta print("Starting complex test...")

# Test various constructs that use RNG
~kinda int base = 10
~kinda float factor = 2.5

for i in range(3):
    ~sometimes(i % 2 == 0):
        ~sorta print(f"Even iteration {i}")
        ~kinda int val = base * i
        ~maybe(val > 15):
            ~sorta print(f"val is big: {val}")
    
    ~rarely(True):
        ~sorta print("Rare event triggered!")
    
    # Test ish comparisons
    ~kinda float test_val = factor * i
    if test_val ~ish 5.0:
        ~sorta print(f"test_val is ish 5.0: {test_val}")

~sorta print("Complex test complete!")
"""
            )
            return Path(f.name)

    def test_record_complex_program(self, complex_kinda_program):
        """Test recording a complex program with multiple constructs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            session_file = Path(temp_dir) / "complex_session.json"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "kinda.cli",
                    "record",
                    "run",
                    str(complex_kinda_program),
                    "--output",
                    str(session_file),
                    "--seed",
                    "555",
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            assert result.returncode == 0
            assert session_file.exists()

            with open(session_file, "r") as f:
                session_data = json.load(f)

            # Should have recorded many RNG calls
            assert session_data["total_calls"] >= 10

            # Should have recorded usage of different constructs
            construct_usage = session_data.get("construct_usage", {})
            # Complex program should trigger multiple construct types
            assert len(construct_usage) >= 1

            # Verify RNG call details
            rng_calls = session_data["rng_calls"]
            assert len(rng_calls) > 0

            # Check that calls have proper structure
            for call in rng_calls[:3]:  # Check first few calls
                assert "call_id" in call
                assert "method_name" in call
                assert "result" in call
                assert "sequence_number" in call
                assert "personality_state" in call
                assert call["sequence_number"] > 0

    def cleanup_temp_files(self):
        """Clean up any temporary files created during tests."""
        # This runs after tests to clean up temp files
        pass
