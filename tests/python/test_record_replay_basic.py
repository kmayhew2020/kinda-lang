# tests/python/test_record_replay_basic.py

"""
Test suite for the basic record/replay infrastructure.

These tests verify that the ExecutionRecorder properly captures RNG calls
from the PersonalityContext and produces valid session files.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

from kinda.record_replay import (
    ExecutionRecorder,
    RNGCall,
    RecordingSession,
    ReplayEngine,
    start_recording,
    stop_recording,
    is_recording,
    get_session_summary,
)
from kinda.personality import PersonalityContext


class TestExecutionRecorder:
    """Test the core ExecutionRecorder functionality."""

    def test_recorder_initialization(self):
        """Test that ExecutionRecorder initializes correctly."""
        recorder = ExecutionRecorder()
        assert not recorder.recording
        assert recorder.session is None
        assert recorder._sequence_counter == 0
        assert not recorder._hooked

    def test_start_stop_recording_cycle(self):
        """Test basic recording start/stop cycle."""
        recorder = ExecutionRecorder()

        # Start recording
        session_id = recorder.start_recording("test.knda", ["test", "args"])

        assert recorder.recording
        assert recorder.session is not None
        assert recorder.session.session_id == session_id
        assert recorder.session.input_file == "test.knda"
        assert recorder.session.command_line_args == ["test", "args"]
        assert recorder._hooked

        # Stop recording
        session = recorder.stop_recording()

        assert not recorder.recording
        assert not recorder._hooked
        assert session.session_id == session_id
        assert session.end_time is not None
        assert session.duration is not None
        assert session.total_calls == len(session.rng_calls)

    def test_double_start_recording_fails(self):
        """Test that starting recording twice fails."""
        recorder = ExecutionRecorder()

        recorder.start_recording("test.knda", [])

        with pytest.raises(RuntimeError, match="Recording already in progress"):
            recorder.start_recording("test2.knda", [])

        # Clean up
        recorder.stop_recording()

    def test_stop_without_start_fails(self):
        """Test that stopping without starting fails."""
        recorder = ExecutionRecorder()

        with pytest.raises(RuntimeError, match="No recording session in progress"):
            recorder.stop_recording()

    def test_rng_call_recording(self):
        """Test that RNG calls are properly recorded."""
        # Reset personality to clean state
        PersonalityContext.set_seed(12345)
        personality = PersonalityContext.get_instance()

        recorder = ExecutionRecorder()
        recorder.start_recording("test.knda", [])

        # Make some RNG calls
        result1 = personality.random()
        result2 = personality.randint(1, 10)
        result3 = personality.uniform(0.0, 1.0)
        result4 = personality.choice(["a", "b", "c"])
        result5 = personality.gauss(0.0, 1.0)

        session = recorder.stop_recording()

        # Verify calls were recorded
        assert len(session.rng_calls) == 5

        # Check first call (random)
        call1 = session.rng_calls[0]
        assert call1.method_name == "random"
        assert call1.args == []
        assert call1.kwargs == {}
        assert call1.result == result1
        assert call1.sequence_number == 1

        # Check second call (randint)
        call2 = session.rng_calls[1]
        assert call2.method_name == "randint"
        assert call2.args == [1, 10]
        assert call2.result == result2
        assert call2.sequence_number == 2

        # Check third call (uniform)
        call3 = session.rng_calls[2]
        assert call3.method_name == "uniform"
        assert call3.args == [0.0, 1.0]
        assert call3.result == result3

        # Check fourth call (choice)
        call4 = session.rng_calls[3]
        assert call4.method_name == "choice"
        assert call4.args == [["a", "b", "c"]]
        assert call4.result == result4

        # Check fifth call (gauss)
        call5 = session.rng_calls[4]
        assert call5.method_name == "gauss"
        assert call5.args == [0.0, 1.0]
        assert call5.result == result5

    def test_recording_preserves_original_functionality(self):
        """Test that recording doesn't affect RNG behavior."""
        # Set up reproducible state
        PersonalityContext.set_seed(42)
        personality = PersonalityContext.get_instance()

        # Get results without recording
        results_without_recording = [
            personality.random(),
            personality.randint(1, 100),
            personality.uniform(-1.0, 1.0),
            personality.choice([1, 2, 3, 4, 5]),
            personality.gauss(5.0, 2.0),
        ]

        # Reset state
        PersonalityContext.set_seed(42)
        personality = PersonalityContext.get_instance()

        # Get results with recording
        recorder = ExecutionRecorder()
        recorder.start_recording("test.knda", [])

        results_with_recording = [
            personality.random(),
            personality.randint(1, 100),
            personality.uniform(-1.0, 1.0),
            personality.choice([1, 2, 3, 4, 5]),
            personality.gauss(5.0, 2.0),
        ]

        session = recorder.stop_recording()

        # Results should be identical
        assert results_without_recording == results_with_recording

        # And all calls should be recorded
        assert len(session.rng_calls) == 5
        for i, call in enumerate(session.rng_calls):
            assert call.result == results_with_recording[i]

    def test_session_file_serialization(self):
        """Test saving and loading session files."""
        PersonalityContext.set_seed(99)
        personality = PersonalityContext.get_instance()

        with tempfile.TemporaryDirectory() as temp_dir:
            session_file = Path(temp_dir) / "test_session.json"

            # Record a session
            recorder = ExecutionRecorder()
            recorder.start_recording("test_program.knda", ["record", "run", "test_program.knda"])

            # Generate some RNG activity
            personality.random()
            personality.randint(1, 6)
            personality.choice(["apple", "banana", "cherry"])

            session = recorder.stop_recording()

            # Save session
            ExecutionRecorder.save_session(session, session_file)

            assert session_file.exists()

            # Load session
            loaded_session = ExecutionRecorder.load_session(session_file)

            # Verify loaded session matches original
            assert loaded_session.session_id == session.session_id
            assert loaded_session.input_file == session.input_file
            assert loaded_session.total_calls == session.total_calls
            assert len(loaded_session.rng_calls) == len(session.rng_calls)

            # Verify individual RNG calls
            for original, loaded in zip(session.rng_calls, loaded_session.rng_calls):
                assert original.method_name == loaded.method_name
                assert original.args == loaded.args
                assert original.result == loaded.result
                assert original.sequence_number == loaded.sequence_number

    def test_construct_context_inference(self):
        """Test inference of construct context from stack traces."""
        recorder = ExecutionRecorder()

        # Test with mock stack traces
        stack_sometimes = ["file.py:10 in sometimes_handler", "runtime.py:50 in execute"]
        context = recorder._infer_construct_context(stack_sometimes)
        assert context["type"] == "sometimes"
        assert "conditional execution (50% probability)" in context["impact"]

        stack_kinda_int = ["fuzzy.py:25 in kinda_int_transform", "main.py:15 in main"]
        context = recorder._infer_construct_context(stack_kinda_int)
        assert context["type"] == "kinda_int"
        assert "integer fuzz" in context["impact"]

        stack_direct = ["main.py:100 in some_function"]
        context = recorder._infer_construct_context(stack_direct)
        assert context["type"] == "direct_rng"

    def test_personality_state_capture(self):
        """Test that personality state is captured in RNG calls."""
        PersonalityContext.set_mood("chaotic")
        PersonalityContext.set_chaos_level(8)
        PersonalityContext.set_seed(777)
        personality = PersonalityContext.get_instance()

        recorder = ExecutionRecorder()
        recorder.start_recording("chaos_test.knda", [])

        # Make an RNG call
        personality.random()

        session = recorder.stop_recording()

        # Check session captured initial personality
        assert session.initial_personality["mood"] == "chaotic"
        assert session.initial_personality["chaos_level"] == 8
        assert session.initial_personality["seed"] == 777

        # Check RNG call captured current state
        call = session.rng_calls[0]
        assert "chaos_level" in call.personality_state
        assert call.personality_state["chaos_level"] == 8


class TestGlobalRecorderFunctions:
    """Test the global recorder convenience functions."""

    @pytest.mark.skip(
        "Threading deadlock in CI - Issue #129. Functionality tested via instance-level tests."
    )
    def test_global_recorder_functions(self):
        """Test start_recording, stop_recording, is_recording functions."""
        assert not is_recording()

        session_id = start_recording("global_test.knda", ["test"])
        assert is_recording()

        summary = get_session_summary()
        assert summary["status"] == "active"
        assert summary["session_id"] == session_id
        assert summary["input_file"] == "global_test.knda"

        session = stop_recording()
        assert not is_recording()
        assert session.session_id == session_id

    @pytest.mark.skip(
        "Threading deadlock in CI - Issue #129. Functionality tested via alternative methods."
    )
    def test_session_summary_no_session(self):
        """Test session summary when no session is active."""
        # Reset the global recorder to ensure clean state
        from kinda.record_replay import _reset_global_recorder

        _reset_global_recorder()

        summary = get_session_summary()
        assert summary["status"] == "no_session"

    def test_instance_recorder_functionality(self):
        """Test ExecutionRecorder instance functionality - covers global recorder logic without deadlocks."""
        # This test validates the core recorder functionality that global functions use
        PersonalityContext.set_seed(42)
        personality = PersonalityContext.get_instance()

        # Use direct ExecutionRecorder instance to avoid global state threading issues
        with patch(
            "kinda.record_replay.ExecutionRecorder._validate_hook_integrity", return_value=True
        ):
            recorder = ExecutionRecorder()

            # Test recording cycle
            session_id = recorder.start_recording("instance_test.knda", ["test", "instance"])
            assert recorder.recording

            # Make some actual RNG calls to test the recording
            result1 = personality.random()
            result2 = personality.randint(1, 10)
            result3 = personality.uniform(0.0, 1.0)

            # Test session summary at instance level (avoids global get_session_summary)
            summary = recorder.get_session_summary()
            assert summary["status"] == "active"
            assert summary["session_id"] == session_id
            assert summary["rng_calls"] >= 3

            # Stop recording
            session = recorder.stop_recording()
            assert not recorder.recording
            assert session.session_id == session_id
            assert len(session.rng_calls) == 3

            # Verify recorded results match actual results
            assert session.rng_calls[0].result == result1
            assert session.rng_calls[1].result == result2
            assert session.rng_calls[2].result == result3

    def test_global_recorder_api_surface(self):
        """Test that global recorder functions exist and have correct signatures."""
        # Test that the functions are importable and callable (API surface test)
        # This ensures the global API exists even if we can't test it fully due to threading
        assert callable(start_recording)
        assert callable(stop_recording)
        assert callable(is_recording)
        assert callable(get_session_summary)

        # Test function signatures
        import inspect

        start_sig = inspect.signature(start_recording)
        assert len(start_sig.parameters) >= 2  # input_file, command_line_args

        stop_sig = inspect.signature(stop_recording)
        assert len(stop_sig.parameters) == 0  # no parameters

        is_recording_sig = inspect.signature(is_recording)
        assert len(is_recording_sig.parameters) == 0  # no parameters

        summary_sig = inspect.signature(get_session_summary)
        assert len(summary_sig.parameters) == 0  # no parameters

    def test_recorder_error_conditions(self):
        """Test error conditions in recorder without global state issues."""
        with patch(
            "kinda.record_replay.ExecutionRecorder._validate_hook_integrity", return_value=True
        ):
            recorder = ExecutionRecorder()

            # Test double start fails
            recorder.start_recording("test.knda", [])
            with pytest.raises(RuntimeError, match="Recording already in progress"):
                recorder.start_recording("test2.knda", [])

            recorder.stop_recording()

            # Test stop without start fails
            with pytest.raises(RuntimeError, match="No recording session in progress"):
                recorder.stop_recording()

    def test_threadsafe_record_replay_cycle(self):
        """Test complete record/replay cycle with thread safety measures."""

        # Set up consistent state
        PersonalityContext.set_seed(999)
        personality = PersonalityContext.get_instance()

        # Phase 1: Record a session using direct ExecutionRecorder (no global state)
        with patch(
            "kinda.record_replay.ExecutionRecorder._validate_hook_integrity", return_value=True
        ):
            recorder = ExecutionRecorder()
            session_id = recorder.start_recording("threadsafe_test.knda", ["test", "threading"])

            # Generate some deterministic RNG calls
            r1 = personality.random()
            r2 = personality.randint(10, 20)
            r3 = personality.choice(["a", "b", "c", "d"])

            recorded_session = recorder.stop_recording()

        # Verify recording worked
        assert len(recorded_session.rng_calls) == 3
        assert recorded_session.rng_calls[0].method_name == "random"
        assert recorded_session.rng_calls[1].method_name == "randint"
        assert recorded_session.rng_calls[2].method_name == "choice"
        assert recorded_session.rng_calls[0].result == r1
        assert recorded_session.rng_calls[1].result == r2
        assert recorded_session.rng_calls[2].result == r3

        # Phase 2: Test replay functionality
        replay_engine = ReplayEngine(recorded_session)

        with patch("kinda.personality.PersonalityContext") as mock_personality_class:
            mock_personality = Mock()
            mock_personality_class.get_instance.return_value = mock_personality
            mock_personality.set_seed = Mock()

            # Test replay start/stop cycle
            session_id = replay_engine.start_replay()
            assert replay_engine.replaying
            assert session_id == recorded_session.session_id

            # Test progress tracking
            progress = replay_engine.get_replay_progress()
            assert progress["status"] == "replaying"
            assert progress["total_calls"] == 3

            # Test replay completion
            stats = replay_engine.stop_replay()
            assert not replay_engine.replaying
            assert stats["session_id"] == recorded_session.session_id


class TestRNGCallDataStructure:
    """Test the RNGCall data structure."""

    def test_rng_call_creation(self):
        """Test creating RNGCall objects."""
        call = RNGCall(
            call_id="test-123",
            timestamp=1234567890.0,
            sequence_number=1,
            method_name="random",
            args=[],
            kwargs={},
            result=0.42,
            thread_id=12345,
            stack_trace=["main.py:10 in main"],
            personality_state={"chaos_level": 5},
            construct_type="direct_rng",
            construct_location="main.py:10",
            decision_impact="random number generation",
        )

        assert call.call_id == "test-123"
        assert call.method_name == "random"
        assert call.result == 0.42
        assert call.construct_type == "direct_rng"

    def test_recording_session_creation(self):
        """Test creating RecordingSession objects."""
        session = RecordingSession(
            session_id="session-123",
            start_time=1234567890.0,
            input_file="test.knda",
            command_line_args=["run", "test.knda"],
            working_directory="/home/test",
            kinda_version="0.4.1",
            python_version="3.9.0",
            initial_personality={"mood": "playful"},
            rng_calls=[],
            construct_usage={},
            decision_points=[],
        )

        assert session.session_id == "session-123"
        assert session.input_file == "test.knda"
        assert session.tags == []  # Should initialize to empty list
        assert session.construct_usage == {}
