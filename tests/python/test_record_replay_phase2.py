"""
Tests for Phase 2 of the Record/Replay System - Replay Engine

This test module covers the ReplayEngine class and replay functionality
added in Phase 2 of Issue #122.
"""

import json
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import the replay functionality
from kinda.record_replay import (
    ReplayEngine,
    RecordingSession,
    RNGCall,
    start_replay,
    stop_replay,
    is_replaying,
    get_replay_progress,
    _reset_global_replay_engine,
    ExecutionRecorder,
)


class TestReplayEngine:
    """Test the core ReplayEngine class functionality."""

    def test_replay_engine_initialization(self):
        """Test creating a ReplayEngine instance."""
        # Create a minimal session
        session = RecordingSession(
            session_id="test-session",
            start_time=1234567890.0,
            input_file="test.knda",
            command_line_args=["run", "test.knda"],
            working_directory="/home/test",
            kinda_version="0.4.1",
            python_version="3.9.0",
            initial_personality={"mood": "playful", "chaos_level": 5},
            rng_calls=[],
            construct_usage={},
            decision_points=[],
        )

        engine = ReplayEngine(session)
        assert engine.session == session
        assert not engine.replaying
        assert engine._call_index == 0
        assert len(engine._mismatches) == 0

    def test_replay_start_stop_cycle(self):
        """Test starting and stopping a replay session."""
        # Create session with some RNG calls
        rng_calls = [
            RNGCall(
                call_id="call-1",
                timestamp=time.time(),
                sequence_number=1,
                method_name="random",
                args=[],
                kwargs={},
                result=0.5,
                thread_id=1,
                stack_trace=[],
                personality_state={},
            ),
            RNGCall(
                call_id="call-2",
                timestamp=time.time(),
                sequence_number=2,
                method_name="randint",
                args=[1, 10],
                kwargs={},
                result=7,
                thread_id=1,
                stack_trace=[],
                personality_state={},
            ),
        ]

        session = RecordingSession(
            session_id="replay-test",
            start_time=time.time(),
            input_file="replay.knda",
            command_line_args=["run", "replay.knda"],
            working_directory="/test",
            kinda_version="0.4.1",
            python_version="3.9.0",
            initial_personality={"mood": "reliable", "chaos_level": 3, "seed": 42},
            rng_calls=rng_calls,
            construct_usage={"direct_rng": 2},
            decision_points=[],
        )

        engine = ReplayEngine(session)

        with patch("kinda.personality.PersonalityContext") as mock_personality_class:
            mock_personality = Mock()
            mock_personality_class.get_instance.return_value = mock_personality
            mock_personality.set_seed = Mock()

            # Start replay
            session_id = engine.start_replay()
            assert session_id == "replay-test"
            assert engine.replaying
            assert engine._call_index == 0

            # Verify personality was set correctly
            assert mock_personality.mood == "reliable"
            assert mock_personality.chaos_level == 3
            mock_personality.set_seed.assert_called_once_with(42)

            # Stop replay
            stats = engine.stop_replay()
            assert not engine.replaying
            assert stats["session_id"] == "replay-test"
            assert stats["total_calls"] == 2
            assert stats["calls_replayed"] == 0  # No actual RNG calls were made
            assert stats["success_rate"] == 0.0

    def test_double_start_replay_fails(self):
        """Test that starting replay twice raises an error."""
        session = RecordingSession(
            session_id="double-start",
            start_time=time.time(),
            input_file="test.knda",
            command_line_args=[],
            working_directory="/test",
            kinda_version="0.4.1",
            python_version="3.9.0",
            initial_personality={},
            rng_calls=[],
            construct_usage={},
            decision_points=[],
        )

        engine = ReplayEngine(session)

        with patch("kinda.personality.PersonalityContext"):
            engine.start_replay()

            with pytest.raises(RuntimeError, match="already in progress"):
                engine.start_replay()

    def test_stop_without_start_fails(self):
        """Test that stopping replay without starting raises an error."""
        session = RecordingSession(
            session_id="no-start",
            start_time=time.time(),
            input_file="test.knda",
            command_line_args=[],
            working_directory="/test",
            kinda_version="0.4.1",
            python_version="3.9.0",
            initial_personality={},
            rng_calls=[],
            construct_usage={},
            decision_points=[],
        )

        engine = ReplayEngine(session)

        with pytest.raises(RuntimeError, match="No replay session in progress"):
            engine.stop_replay()

    def test_replay_hook_installation_and_removal(self):
        """Test that replay hooks are properly installed and removed."""
        session = RecordingSession(
            session_id="hook-test",
            start_time=time.time(),
            input_file="test.knda",
            command_line_args=[],
            working_directory="/test",
            kinda_version="0.4.1",
            python_version="3.9.0",
            initial_personality={},
            rng_calls=[],
            construct_usage={},
            decision_points=[],
        )

        engine = ReplayEngine(session)

        with patch("kinda.personality.PersonalityContext") as mock_personality_class:
            mock_personality = Mock()
            mock_personality_class.get_instance.return_value = mock_personality

            # Mock original methods
            original_random = Mock()
            original_randint = Mock()
            mock_personality.random = original_random
            mock_personality.randint = original_randint

            # Start replay (installs hooks)
            engine.start_replay()

            # Verify hooks were installed
            assert engine._hooked
            assert mock_personality.random != original_random
            assert mock_personality.randint != original_randint
            assert "random" in engine._original_methods
            assert "randint" in engine._original_methods

            # Stop replay (removes hooks)
            engine.stop_replay()

            # Verify hooks were removed
            assert not engine._hooked
            assert mock_personality.random == original_random
            assert mock_personality.randint == original_randint
            assert len(engine._original_methods) == 0

    def test_recorded_result_retrieval(self):
        """Test getting recorded results during replay."""
        rng_calls = [
            RNGCall(
                call_id="call-1",
                timestamp=time.time(),
                sequence_number=1,
                method_name="random",
                args=[],
                kwargs={},
                result=0.42,
                thread_id=1,
                stack_trace=[],
                personality_state={},
            ),
            RNGCall(
                call_id="call-2",
                timestamp=time.time(),
                sequence_number=2,
                method_name="randint",
                args=[1, 6],
                kwargs={},
                result=4,
                thread_id=1,
                stack_trace=[],
                personality_state={},
            ),
        ]

        session = RecordingSession(
            session_id="result-test",
            start_time=time.time(),
            input_file="test.knda",
            command_line_args=[],
            working_directory="/test",
            kinda_version="0.4.1",
            python_version="3.9.0",
            initial_personality={},
            rng_calls=rng_calls,
            construct_usage={},
            decision_points=[],
        )

        engine = ReplayEngine(session)
        engine.replaying = True

        # Test getting recorded results
        result1 = engine._get_recorded_result("random", (), {})
        assert result1 == 0.42
        assert engine._call_index == 1

        result2 = engine._get_recorded_result("randint", (1, 6), {})
        assert result2 == 4
        assert engine._call_index == 2

        # Test exhaustion
        with pytest.raises(RuntimeError, match="Replay exhausted"):
            engine._get_recorded_result("random", (), {})

    def test_argument_validation(self):
        """Test that argument validation works correctly."""
        rng_call = RNGCall(
            call_id="val-test",
            timestamp=time.time(),
            sequence_number=1,
            method_name="uniform",
            args=[0.0, 1.0],
            kwargs={},
            result=0.75,
            thread_id=1,
            stack_trace=[],
            personality_state={},
        )

        session = RecordingSession(
            session_id="validation",
            start_time=time.time(),
            input_file="test.knda",
            command_line_args=[],
            working_directory="/test",
            kinda_version="0.4.1",
            python_version="3.9.0",
            initial_personality={},
            rng_calls=[rng_call],
            construct_usage={},
            decision_points=[],
        )

        engine = ReplayEngine(session)

        # Test exact match
        assert engine._args_match([0.0, 1.0], [0.0, 1.0], {}, {})

        # Test floating point tolerance
        assert engine._args_match([0.0, 1.0], [1e-15, 1.0 - 1e-15], {}, {})

        # Test mismatch
        assert not engine._args_match([0.0, 1.0], [0.0, 2.0], {}, {})
        assert not engine._args_match([0.0], [0.0, 1.0], {}, {})

    def test_replay_progress_tracking(self):
        """Test that replay progress is tracked correctly."""
        rng_calls = [
            RNGCall(
                call_id=f"call-{i}",
                timestamp=time.time(),
                sequence_number=i,
                method_name="random",
                args=[],
                kwargs={},
                result=i / 10.0,
                thread_id=1,
                stack_trace=[],
                personality_state={},
            )
            for i in range(1, 6)  # 5 calls
        ]

        session = RecordingSession(
            session_id="progress-test",
            start_time=time.time(),
            input_file="test.knda",
            command_line_args=[],
            working_directory="/test",
            kinda_version="0.4.1",
            python_version="3.9.0",
            initial_personality={},
            rng_calls=rng_calls,
            construct_usage={},
            decision_points=[],
        )

        engine = ReplayEngine(session)

        # Test not replaying
        progress = engine.get_replay_progress()
        assert progress["status"] == "not_replaying"

        # Test during replay
        engine.replaying = True
        engine._call_index = 2

        progress = engine.get_replay_progress()
        assert progress["status"] == "replaying"
        assert progress["session_id"] == "progress-test"
        assert progress["current_call"] == 2
        assert progress["total_calls"] == 5
        assert progress["progress_percent"] == 40.0
        assert progress["mismatches"] == 0


class TestGlobalReplayFunctions:
    """Test the global replay management functions."""

    def test_global_replay_functions(self):
        """Test the global start_replay and stop_replay functions."""
        # Create test session
        session = RecordingSession(
            session_id="global-test",
            start_time=time.time(),
            input_file="test.knda",
            command_line_args=[],
            working_directory="/test",
            kinda_version="0.4.1",
            python_version="3.9.0",
            initial_personality={"seed": 123},
            rng_calls=[],
            construct_usage={},
            decision_points=[],
        )

        # Reset global state
        _reset_global_replay_engine()

        assert not is_replaying()

        with patch("kinda.personality.PersonalityContext") as mock_personality_class:
            mock_personality = Mock()
            mock_personality_class.get_instance.return_value = mock_personality
            mock_personality.set_seed = Mock()

            # Start replay
            session_id = start_replay(session)
            assert session_id == "global-test"
            assert is_replaying()

            progress = get_replay_progress()
            assert progress["status"] == "replaying"
            assert progress["session_id"] == "global-test"

            # Stop replay
            stats = stop_replay()
            assert not is_replaying()
            assert stats["session_id"] == "global-test"

    def test_global_replay_progress_no_session(self):
        """Test replay progress when no session is active."""
        _reset_global_replay_engine()
        progress = get_replay_progress()
        assert progress["status"] == "no_replay_session"

    def test_stop_replay_no_session_fails(self):
        """Test that stopping replay without a session raises an error."""
        _reset_global_replay_engine()

        with pytest.raises(RuntimeError, match="No replay session to stop"):
            stop_replay()


class TestReplayIntegration:
    """Integration tests for record/replay cycle."""

    def test_record_then_replay_cycle(self):
        """Test recording a session and then replaying it."""
        # This test would require more complex setup with actual PersonalityContext
        # For now, we'll test the data flow and compatibility

        # Create a recorded session (simulating what ExecutionRecorder produces)
        rng_calls = [
            RNGCall(
                call_id="integration-1",
                timestamp=time.time(),
                sequence_number=1,
                method_name="random",
                args=[],
                kwargs={},
                result=0.123,
                thread_id=1,
                stack_trace=["test.py:10"],
                personality_state={"chaos_level": 5},
                construct_type="direct_rng",
                construct_location="test.py:10",
                decision_impact="random number generation",
            ),
            RNGCall(
                call_id="integration-2",
                timestamp=time.time(),
                sequence_number=2,
                method_name="randint",
                args=[1, 10],
                kwargs={},
                result=8,
                thread_id=1,
                stack_trace=["test.py:11"],
                personality_state={"chaos_level": 5},
                construct_type="kinda_int",
                construct_location="test.py:11",
                decision_impact="integer fuzz (±1 variance)",
            ),
        ]

        recorded_session = RecordingSession(
            session_id="integration-session",
            start_time=time.time(),
            input_file="integration_test.knda",
            command_line_args=["record", "run", "integration_test.knda", "--seed", "42"],
            working_directory="/test",
            kinda_version="0.4.1",
            python_version="3.9.0",
            initial_personality={"mood": "playful", "chaos_level": 5, "seed": 42},
            rng_calls=rng_calls,
            construct_usage={"direct_rng": 1, "kinda_int": 1},
            decision_points=[],
        )

        # Test serialization/deserialization cycle
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            # Save and load session
            ExecutionRecorder.save_session(recorded_session, temp_path)
            loaded_session = ExecutionRecorder.load_session(temp_path)

            # Verify session loaded correctly
            assert loaded_session.session_id == recorded_session.session_id
            assert len(loaded_session.rng_calls) == 2
            assert loaded_session.rng_calls[0].result == 0.123
            assert loaded_session.rng_calls[1].result == 8
            assert loaded_session.construct_usage == {"direct_rng": 1, "kinda_int": 1}

            # Test replay engine can use loaded session
            engine = ReplayEngine(loaded_session)
            assert engine.session.session_id == "integration-session"
            assert len(engine.session.rng_calls) == 2

        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()

    def test_session_file_compatibility(self):
        """Test that session files are compatible between record and replay."""
        # Create a session in the exact format that ExecutionRecorder produces
        session_data = {
            "session_id": "compatibility-test",
            "start_time": 1640995200.0,
            "input_file": "test_program.knda",
            "command_line_args": ["record", "run", "test_program.knda", "--seed", "42"],
            "working_directory": "/home/user/projects",
            "kinda_version": "0.4.1",
            "python_version": "3.9.0",
            "initial_personality": {"mood": "playful", "chaos_level": 5, "seed": 42},
            "rng_calls": [
                {
                    "call_id": "call-001",
                    "timestamp": 1640995200.1,
                    "sequence_number": 1,
                    "method_name": "random",
                    "args": [],
                    "kwargs": {},
                    "result": 0.374,
                    "thread_id": 12345,
                    "stack_trace": ["test.py:5 in main"],
                    "personality_state": {"chaos_level": 5},
                    "construct_type": "sorta_print",
                    "construct_location": "test.py:5",
                    "decision_impact": "probabilistic output (80% chance)",
                }
            ],
            "construct_usage": {"sorta_print": 1},
            "decision_points": [],
            "end_time": 1640995200.5,
            "duration": 0.5,
            "total_calls": 1,
            "notes": "",
            "tags": [],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            json.dump(session_data, temp_file, indent=2)
            temp_path = Path(temp_file.name)

        try:
            # Load session using the replay system
            loaded_session = ExecutionRecorder.load_session(temp_path)

            # Verify all fields loaded correctly
            assert loaded_session.session_id == "compatibility-test"
            assert loaded_session.input_file == "test_program.knda"
            assert loaded_session.initial_personality["seed"] == 42
            assert len(loaded_session.rng_calls) == 1
            assert loaded_session.rng_calls[0].construct_type == "sorta_print"
            assert loaded_session.construct_usage == {"sorta_print": 1}

        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__])
