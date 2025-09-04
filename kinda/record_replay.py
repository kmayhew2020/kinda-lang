# kinda/record_replay.py

"""
Kinda-Lang Record/Replay System for Debugging and Testing

This module provides comprehensive record/replay functionality for debugging
kinda programs by capturing PersonalityContext RNG calls and enabling
exact replay of fuzzy execution sequences.
"""

import json
import time
import threading
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4
import traceback


@dataclass
class RNGCall:
    """Represents a single RNG method call with full context."""

    # Call identification
    call_id: str  # Unique identifier for this call
    timestamp: float  # When this call was made
    sequence_number: int  # Sequential order of calls

    # Method information
    method_name: str  # e.g., "random", "randint", "uniform"
    args: List[Any]  # Arguments passed to the method
    kwargs: Dict[str, Any]  # Keyword arguments (usually empty for RNG)
    result: Any  # The value returned by the method

    # Execution context
    thread_id: int  # Thread that made this call
    stack_trace: List[str]  # Call stack at time of RNG call
    personality_state: Dict[str, Any]  # PersonalityContext state snapshot

    # Fuzzy construct context (if available)
    construct_type: Optional[str] = None  # e.g., "sometimes", "kinda_int"
    construct_location: Optional[str] = None  # Source location info
    decision_impact: Optional[str] = None  # Description of what this RNG affects


@dataclass
class RecordingSession:
    """Complete recording session with metadata and call sequence."""

    # Session metadata (required fields first)
    session_id: str
    start_time: float
    input_file: str
    command_line_args: List[str]
    working_directory: str
    kinda_version: str
    python_version: str
    initial_personality: Dict[str, Any]
    rng_calls: List[RNGCall]
    construct_usage: Dict[str, int]
    decision_points: List[Dict[str, Any]]

    # Optional fields with defaults
    end_time: Optional[float] = None
    duration: Optional[float] = None
    total_calls: int = 0
    notes: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ExecutionRecorder:
    """
    Records PersonalityContext RNG calls for exact replay debugging.

    This class hooks into the PersonalityContext's random number generation
    to capture every decision point in a kinda program's execution.

    Security Features:
    - Global recording state management prevents concurrent sessions
    - Hook integrity validation prevents bypass attacks
    - Secure token-based hook validation system
    """

    def __init__(self, output_file: Optional[Path] = None):
        self.output_file = output_file
        self.recording = False
        self.session: Optional[RecordingSession] = None
        self._sequence_counter = 0
        self._lock = threading.Lock()  # For thread safety

        # Hook tracking with security enhancements
        self._original_methods: Dict[str, Any] = {}
        self._hooked = False
        self._security_token = str(uuid4())  # Unique security token for this recorder
        self._hook_checksums: Dict[str, str] = {}  # Track hook integrity

    def start_recording(self, input_file: str, command_args: List[str]) -> str:
        """
        Start recording a new session.

        Args:
            input_file: The .knda file being executed
            command_args: Command line arguments used

        Returns:
            session_id: Unique identifier for this recording session

        Raises:
            RuntimeError: If recording is already in progress or if concurrent recording detected
        """
        # Global recording state protection
        with _recording_lock:
            global _global_recorder, _hook_validator_token

            # Prevent concurrent recordings across all instances
            if _global_recorder is not None and _global_recorder.recording:
                if _global_recorder is not self:
                    raise RuntimeError(
                        "Another recording session is already active. "
                        "Only one recording session can be active at a time for security reasons."
                    )
                else:
                    raise RuntimeError("Recording already in progress. Stop current session first.")

            if self.recording:
                raise RuntimeError("Recording already in progress. Stop current session first.")

        # Import here to avoid circular import
        from kinda.personality import PersonalityContext
        import sys
        import platform

        with self._lock:
            session_id = str(uuid4())
            current_time = time.time()

            # Get current personality state
            personality = PersonalityContext.get_instance()
            personality_state = {
                "mood": personality.mood,
                "chaos_level": personality.chaos_level,
                "chaos_multiplier": personality.chaos_multiplier,
                "seed": personality.seed,
                "seed_info": personality.get_seed_info(),
                "execution_count": personality.execution_count,
                "instability_level": personality.instability_level,
            }

            self.session = RecordingSession(
                session_id=session_id,
                start_time=current_time,
                input_file=input_file,
                command_line_args=command_args,
                working_directory=str(Path.cwd()),
                kinda_version="0.4.1",  # TODO: Get from package metadata
                python_version=platform.python_version(),
                initial_personality=personality_state,
                rng_calls=[],
                construct_usage={},
                decision_points=[],
            )

            # Install hooks with security validation
            self._install_hooks()

            # Register as the active global recorder
            _global_recorder = self
            _hook_validator_token = self._security_token

            self.recording = True
            self._sequence_counter = 0

            return session_id

    def stop_recording(self) -> RecordingSession:
        """
        Stop recording and finalize the session.

        Returns:
            The completed recording session
        """
        if not self.recording:
            raise RuntimeError("No recording session in progress")

        # Validate hook integrity before stopping
        if not self._validate_hook_integrity():
            raise RuntimeError(
                "Hook integrity compromised! Recording may have been tampered with. "
                "This could indicate a security breach or malicious code execution."
            )

        with self._lock:
            current_time = time.time()

            # Finalize session
            self.session.end_time = current_time
            self.session.duration = current_time - self.session.start_time
            self.session.total_calls = len(self.session.rng_calls)

            # Remove hooks with security cleanup
            self._remove_hooks()

            # Clear global recording state
            with _recording_lock:
                global _global_recorder, _hook_validator_token
                if _global_recorder is self:
                    _global_recorder = None
                    _hook_validator_token = None

            self.recording = False

            # Save to file if specified
            if self.output_file:
                self.save_session(self.session, self.output_file)

            return self.session

    def _install_hooks(self) -> None:
        """Install RNG method hooks in PersonalityContext with security validation."""
        if self._hooked:
            return

        from kinda.personality import PersonalityContext
        import hashlib

        # Get the instance to hook
        personality = PersonalityContext.get_instance()

        # Hook the main RNG methods
        rng_methods = ["random", "randint", "uniform", "choice", "gauss"]

        global _active_hooks

        for method_name in rng_methods:
            if hasattr(personality, method_name):
                original_method = getattr(personality, method_name)

                # Check if method is already hooked by another recorder
                method_id = f"{id(personality)}.{method_name}"
                if method_id in _active_hooks:
                    raise RuntimeError(
                        f"Method {method_name} is already hooked by another recorder. "
                        "Concurrent recording sessions are not allowed for security reasons."
                    )

                self._original_methods[method_name] = original_method

                # Create security checksum for the original method
                method_checksum = hashlib.sha256(
                    str(id(original_method)).encode() + method_name.encode()
                ).hexdigest()[:16]
                self._hook_checksums[method_name] = method_checksum

                # Create hooked version with security token
                hooked_method = self._create_hook(method_name, original_method, method_checksum)
                setattr(personality, method_name, hooked_method)

                # Register active hook
                _active_hooks[method_id] = {
                    "recorder_token": self._security_token,
                    "method_checksum": method_checksum,
                    "original_method": original_method,
                }

        self._hooked = True

    def _remove_hooks(self) -> None:
        """Remove RNG method hooks from PersonalityContext with security cleanup."""
        if not self._hooked:
            return

        from kinda.personality import PersonalityContext

        # Get the instance to unhook
        personality = PersonalityContext.get_instance()

        global _active_hooks

        # Restore original methods and clear hook registry
        for method_name, original_method in self._original_methods.items():
            # Validate that we're removing the correct hook
            method_id = f"{id(personality)}.{method_name}"
            if method_id in _active_hooks:
                hook_info = _active_hooks[method_id]
                if hook_info["recorder_token"] != self._security_token:
                    # Hook was tampered with - still restore but log warning
                    pass  # In production, this should log a security warning

                # Remove from active hooks registry
                del _active_hooks[method_id]

            setattr(personality, method_name, original_method)

        self._original_methods.clear()
        self._hook_checksums.clear()
        self._hooked = False

    def _create_hook(self, method_name: str, original_method, method_checksum: str):
        """Create a hooked version of an RNG method that records calls with security validation."""

        def hooked_method(*args, **kwargs):
            # Call original method first
            result = original_method(*args, **kwargs)

            # Record the call if we're actively recording
            if self.recording and self.session:
                try:
                    self._record_rng_call(method_name, args, kwargs, result)
                except Exception as e:
                    # Don't let recording failures break the program
                    # TODO: Add optional debug logging here
                    pass

            return result

        # Add security metadata to the hooked method
        hooked_method._kinda_hook_token = self._security_token
        hooked_method._kinda_hook_checksum = method_checksum
        hooked_method._kinda_original_method = original_method

        return hooked_method

    def _validate_method_hook(self, method_name: str, expected_checksum: str) -> bool:
        """Validate that a hooked method hasn't been tampered with."""
        from kinda.personality import PersonalityContext

        personality = PersonalityContext.get_instance()
        current_method = getattr(personality, method_name, None)

        if current_method is None:
            return False

        # Check if method has our security metadata
        if not hasattr(current_method, "_kinda_hook_token"):
            return False

        # Validate security token and checksum
        return (
            current_method._kinda_hook_token == self._security_token
            and current_method._kinda_hook_checksum == expected_checksum
        )

    def _validate_hook_integrity(self) -> bool:
        """Validate the integrity of all installed hooks."""
        if not self._hooked:
            return True

        for method_name, expected_checksum in self._hook_checksums.items():
            if not self._validate_method_hook(method_name, expected_checksum):
                return False

        # Validate global hook registry consistency
        global _active_hooks, _hook_validator_token
        if _hook_validator_token != self._security_token:
            return False

        return True

    def detect_and_prevent_hook_bypass(self) -> bool:
        """
        Actively detect and prevent hook bypass attempts.

        This method should be called periodically during recording to detect
        if someone has bypassed our hooks by reassigning original methods.

        Returns:
            True if hooks are intact, False if tampering detected
        """
        if not self.recording or not self._hooked:
            return True

        from kinda.personality import PersonalityContext

        personality = PersonalityContext.get_instance()

        # Check each hooked method to see if it's still our hook
        for method_name in self._original_methods.keys():
            current_method = getattr(personality, method_name, None)

            # If the method doesn't have our security metadata, it's been bypassed
            if not hasattr(current_method, "_kinda_hook_token"):
                # Re-install our hook to prevent bypass
                original_method = self._original_methods[method_name]
                expected_checksum = self._hook_checksums[method_name]
                new_hook = self._create_hook(method_name, original_method, expected_checksum)
                setattr(personality, method_name, new_hook)

                # Update global hooks registry
                global _active_hooks
                method_id = f"{id(personality)}.{method_name}"
                if method_id in _active_hooks:
                    _active_hooks[method_id]["method_checksum"] = expected_checksum

                # Log security event (in production this should be logged properly)
                # For now, we'll raise an exception to alert about the bypass attempt
                raise RuntimeError(
                    f"SECURITY ALERT: Hook bypass detected and prevented for method '{method_name}'! "
                    "Malicious code attempted to restore original method to evade recording. "
                    "Hook has been re-installed for protection."
                )

        return True

    def _record_rng_call(self, method_name: str, args: tuple, kwargs: dict, result: Any) -> None:
        """Record a single RNG call with full context."""

        # Security check: Validate hook integrity on every recording call
        if not self._validate_hook_integrity():
            raise RuntimeError(
                f"Security breach detected during RNG recording! "
                f"Hook integrity compromised for method '{method_name}'. "
                "This indicates malicious tampering with recording hooks."
            )

        with self._lock:
            current_time = time.time()
            self._sequence_counter += 1

            # Get current thread info
            current_thread = threading.current_thread()
            thread_id = current_thread.ident or 0

            # Capture stack trace (excluding this recording code)
            stack = traceback.extract_stack()[:-2]  # Skip this method and _create_hook
            stack_trace = [
                f"{frame.filename}:{frame.lineno} in {frame.name}"
                for frame in stack[-10:]  # Keep last 10 frames
            ]

            # Get current personality state snapshot
            from kinda.personality import PersonalityContext

            personality = PersonalityContext.get_instance()
            personality_state = {
                "chaos_level": personality.chaos_level,
                "chaos_multiplier": personality.chaos_multiplier,
                "execution_count": personality.execution_count,
                "instability_level": personality.instability_level,
            }

            # Try to infer construct context from stack trace
            construct_info = self._infer_construct_context(stack_trace)

            # Create RNG call record
            call_record = RNGCall(
                call_id=str(uuid4()),
                timestamp=current_time,
                sequence_number=self._sequence_counter,
                method_name=method_name,
                args=list(args),  # Convert tuple to list for JSON serialization
                kwargs=dict(kwargs),
                result=result,
                thread_id=thread_id,
                stack_trace=stack_trace,
                personality_state=personality_state,
                construct_type=construct_info.get("type"),
                construct_location=construct_info.get("location"),
                decision_impact=construct_info.get("impact"),
            )

            # Add to session
            self.session.rng_calls.append(call_record)

            # Update construct usage stats
            if call_record.construct_type:
                self.session.construct_usage[call_record.construct_type] = (
                    self.session.construct_usage.get(call_record.construct_type, 0) + 1
                )

    def _infer_construct_context(self, stack_trace: List[str]) -> Dict[str, Optional[str]]:
        """
        Infer fuzzy construct context from stack trace.

        This analyzes the call stack to determine what kinda construct
        triggered this RNG call.
        """

        # Look for kinda runtime patterns in stack trace
        for frame in reversed(stack_trace):  # Start from most recent
            frame_lower = frame.lower()

            # Check for construct patterns
            if "sometimes" in frame_lower:
                return {
                    "type": "sometimes",
                    "location": frame,
                    "impact": "conditional execution (50% probability)",
                }
            elif "maybe" in frame_lower:
                return {
                    "type": "maybe",
                    "location": frame,
                    "impact": "conditional execution (60% probability)",
                }
            elif "probably" in frame_lower:
                return {
                    "type": "probably",
                    "location": frame,
                    "impact": "conditional execution (70% probability)",
                }
            elif "rarely" in frame_lower:
                return {
                    "type": "rarely",
                    "location": frame,
                    "impact": "conditional execution (15% probability)",
                }
            elif "kinda_int" in frame_lower or "fuzzy_int" in frame_lower:
                return {
                    "type": "kinda_int",
                    "location": frame,
                    "impact": "integer fuzz (±1 variance)",
                }
            elif "kinda_float" in frame_lower or "fuzzy_float" in frame_lower:
                return {
                    "type": "kinda_float",
                    "location": frame,
                    "impact": "float drift (±0.5 variance)",
                }
            elif "ish" in frame_lower:
                return {"type": "ish", "location": frame, "impact": "fuzzy comparison or value"}
            elif "sorta_print" in frame_lower:
                return {
                    "type": "sorta_print",
                    "location": frame,
                    "impact": "probabilistic output (80% chance)",
                }
            elif "kinda_binary" in frame_lower:
                return {
                    "type": "kinda_binary",
                    "location": frame,
                    "impact": "ternary logic (yes/no/maybe)",
                }
            elif "chaos_probability" in frame_lower:
                return {
                    "type": "personality_chaos",
                    "location": frame,
                    "impact": "personality-adjusted probability",
                }

        # Default case - direct personality RNG call
        return {
            "type": "direct_rng",
            "location": stack_trace[-1] if stack_trace else "unknown",
            "impact": "direct random number generation",
        }

    @staticmethod
    def save_session(session: RecordingSession, output_file: Path) -> None:
        """Save a recording session to a JSON file."""

        # Convert session to dictionary for JSON serialization
        session_dict = asdict(session)

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save with pretty formatting for readability
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(session_dict, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_session(input_file: Path) -> RecordingSession:
        """Load a recording session from a JSON file."""

        with open(input_file, "r", encoding="utf-8") as f:
            session_dict = json.load(f)

        # Convert RNG calls back to RNGCall objects
        rng_calls = [RNGCall(**call_dict) for call_dict in session_dict.get("rng_calls", [])]
        session_dict["rng_calls"] = rng_calls

        return RecordingSession(**session_dict)

    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current recording session."""

        if not self.session:
            return {"status": "no_session", "message": "No recording session active"}

        # Security validation: Check hook integrity when queried
        if self.recording and not self._validate_hook_integrity():
            return {
                "status": "compromised",
                "session_id": self.session.session_id,
                "message": "SECURITY ALERT: Recording session integrity compromised!",
                "warning": "Hook tampering detected - recording may be unreliable",
            }

        current_time = time.time()
        duration = current_time - self.session.start_time

        return {
            "status": "active" if self.recording else "stopped",
            "session_id": self.session.session_id,
            "duration": duration,
            "rng_calls": len(self.session.rng_calls),
            "construct_usage": dict(self.session.construct_usage),
            "personality": self.session.initial_personality,
            "input_file": self.session.input_file,
        }


# Global recorder instance for CLI usage with singleton protection
_global_recorder: Optional[ExecutionRecorder] = None
_recording_lock = threading.Lock()  # Global lock to prevent concurrent recordings
_active_hooks: Dict[str, Any] = {}  # Track active hooks for integrity validation
_hook_validator_token: Optional[str] = None  # Security token for hook validation


def get_recorder() -> ExecutionRecorder:
    """Get or create the global ExecutionRecorder instance with security validation."""
    global _global_recorder

    # Use the recording lock to prevent race conditions
    with _recording_lock:
        if _global_recorder is None:
            _global_recorder = ExecutionRecorder()
        return _global_recorder


def start_recording(
    input_file: str, command_args: List[str], output_file: Optional[Path] = None
) -> str:
    """
    Convenience function to start recording with the global recorder.

    Args:
        input_file: The .knda file being executed
        command_args: Command line arguments
        output_file: Optional output file path

    Returns:
        session_id: Unique session identifier
    """
    recorder = get_recorder()
    if output_file:
        recorder.output_file = output_file
    return recorder.start_recording(input_file, command_args)


def stop_recording() -> RecordingSession:
    """Stop recording with the global recorder and return the session."""
    global _global_recorder

    with _recording_lock:
        if _global_recorder is None:
            raise RuntimeError("No recording session to stop")
        return _global_recorder.stop_recording()


def is_recording() -> bool:
    """Check if recording is currently active with security validation."""
    global _global_recorder, _hook_validator_token

    with _recording_lock:
        if _global_recorder is None:
            return False

        # Additional security check: validate hook integrity
        if _global_recorder.recording:
            # Quick integrity check without full validation (for performance)
            return _hook_validator_token == _global_recorder._security_token

        return _global_recorder.recording


def get_session_summary() -> Dict[str, Any]:
    """Get summary of current recording session with security validation."""
    global _global_recorder

    with _recording_lock:
        if _global_recorder is None:
            return {"status": "no_session", "message": "No recording session active"}

        # Validate session integrity before returning summary
        if _global_recorder.recording and not _global_recorder._validate_hook_integrity():
            return {
                "status": "compromised",
                "message": "Recording session may have been compromised - hook integrity validation failed",
            }

        return _global_recorder.get_session_summary()


def _reset_global_recorder() -> None:
    """Reset the global recorder instance. For testing only."""
    global _global_recorder, _hook_validator_token, _active_hooks

    with _recording_lock:
        if _global_recorder is not None and _global_recorder.recording:
            # Force stop recording if active (for testing cleanup)
            try:
                _global_recorder.stop_recording()
            except:
                pass  # Ignore errors during cleanup

        _global_recorder = None
        _hook_validator_token = None
        _active_hooks.clear()


class ReplayEngine:
    """
    Replays PersonalityContext RNG calls for exact execution reproduction.

    This class implements deterministic replay by intercepting RNG calls and
    returning pre-recorded values in the exact sequence they were captured.
    """

    def __init__(self, session: RecordingSession):
        self.session = session
        self.replaying = False
        self._call_index = 0
        self._lock = threading.Lock()

        # Hook tracking
        self._original_methods: Dict[str, Any] = {}
        self._hooked = False

        # Validation tracking
        self._mismatches: List[Dict[str, Any]] = []

    def start_replay(self) -> str:
        """
        Start replaying the recorded session.

        Returns:
            session_id: The ID of the session being replayed
        """
        if self.replaying:
            raise RuntimeError("Replay already in progress. Stop current replay first.")

        # Import here to avoid circular import
        from kinda.personality import PersonalityContext

        with self._lock:
            # Restore initial personality state
            personality = PersonalityContext.get_instance()
            initial_state = self.session.initial_personality

            # Set personality to match recorded state
            if "mood" in initial_state:
                personality.mood = initial_state["mood"]
            if "chaos_level" in initial_state:
                personality.chaos_level = initial_state["chaos_level"]
            if "seed" in initial_state and initial_state["seed"] is not None:
                personality.set_seed(initial_state["seed"])

            # Install replay hooks
            self._install_replay_hooks()

            self.replaying = True
            self._call_index = 0
            self._mismatches.clear()

            return self.session.session_id

    def stop_replay(self) -> Dict[str, Any]:
        """
        Stop replaying and return replay statistics.

        Returns:
            Replay summary with statistics and any validation issues
        """
        if not self.replaying:
            raise RuntimeError("No replay session in progress")

        with self._lock:
            # Remove hooks
            self._remove_replay_hooks()

            self.replaying = False

            # Generate replay summary
            total_calls = len(self.session.rng_calls)
            calls_replayed = self._call_index
            success_rate = (calls_replayed / total_calls * 100) if total_calls > 0 else 100

            return {
                "session_id": self.session.session_id,
                "total_calls": total_calls,
                "calls_replayed": calls_replayed,
                "success_rate": success_rate,
                "mismatches": self._mismatches.copy(),
                "validation_issues": len(self._mismatches),
                "replay_complete": calls_replayed == total_calls,
            }

    def _install_replay_hooks(self) -> None:
        """Install RNG method hooks for replay in PersonalityContext."""
        if self._hooked:
            return

        from kinda.personality import PersonalityContext

        # Get the instance to hook
        personality = PersonalityContext.get_instance()

        # Hook the main RNG methods
        rng_methods = ["random", "randint", "uniform", "choice", "gauss"]

        for method_name in rng_methods:
            if hasattr(personality, method_name):
                original_method = getattr(personality, method_name)
                self._original_methods[method_name] = original_method

                # Create replay hook
                replay_method = self._create_replay_hook(method_name, original_method)
                setattr(personality, method_name, replay_method)

        self._hooked = True

    def _remove_replay_hooks(self) -> None:
        """Remove RNG method hooks from PersonalityContext."""
        if not self._hooked:
            return

        from kinda.personality import PersonalityContext

        # Get the instance to unhook
        personality = PersonalityContext.get_instance()

        # Restore original methods
        for method_name, original_method in self._original_methods.items():
            setattr(personality, method_name, original_method)

        self._original_methods.clear()
        self._hooked = False

    def _create_replay_hook(self, method_name: str, original_method):
        """Create a replay hook that returns pre-recorded values."""

        def replay_method(*args, **kwargs):
            # Return pre-recorded value if we're actively replaying
            if self.replaying:
                try:
                    return self._get_recorded_result(method_name, args, kwargs)
                except Exception as e:
                    # If replay fails, fall back to original method and log mismatch
                    result = original_method(*args, **kwargs)
                    self._log_replay_mismatch(method_name, args, kwargs, None, result, str(e))
                    return result
            else:
                # Not replaying, use original method
                return original_method(*args, **kwargs)

        return replay_method

    def _get_recorded_result(self, method_name: str, args: tuple, kwargs: dict) -> Any:
        """Get the next recorded result for this RNG call."""

        with self._lock:
            # Check if we have more recorded calls
            if self._call_index >= len(self.session.rng_calls):
                raise RuntimeError(
                    f"Replay exhausted: no more recorded calls (index {self._call_index})"
                )

            # Get the next recorded call
            recorded_call = self.session.rng_calls[self._call_index]
            self._call_index += 1

            # Validate the call matches what we expect
            if recorded_call.method_name != method_name:
                raise ValueError(
                    f"Method mismatch: expected {recorded_call.method_name}, got {method_name}"
                )

            # Check arguments match (with some tolerance for floating point)
            if not self._args_match(
                recorded_call.args, list(args), recorded_call.kwargs, dict(kwargs)
            ):
                # Log mismatch but continue with recorded result
                self._log_replay_mismatch(
                    method_name,
                    args,
                    kwargs,
                    (recorded_call.args, recorded_call.kwargs),
                    recorded_call.result,
                    "Argument mismatch during replay",
                )

            return recorded_call.result

    def _args_match(
        self,
        recorded_args: List[Any],
        actual_args: List[Any],
        recorded_kwargs: Dict[str, Any],
        actual_kwargs: Dict[str, Any],
    ) -> bool:
        """Check if arguments match with tolerance for floating point values."""

        # Check positional args
        if len(recorded_args) != len(actual_args):
            return False

        for recorded, actual in zip(recorded_args, actual_args):
            if isinstance(recorded, float) and isinstance(actual, float):
                if abs(recorded - actual) > 1e-10:  # Floating point tolerance
                    return False
            elif recorded != actual:
                return False

        # Check keyword args
        if set(recorded_kwargs.keys()) != set(actual_kwargs.keys()):
            return False

        for key in recorded_kwargs:
            recorded_val = recorded_kwargs[key]
            actual_val = actual_kwargs[key]
            if isinstance(recorded_val, float) and isinstance(actual_val, float):
                if abs(recorded_val - actual_val) > 1e-10:
                    return False
            elif recorded_val != actual_val:
                return False

        return True

    def _log_replay_mismatch(
        self,
        method_name: str,
        actual_args: tuple,
        actual_kwargs: dict,
        expected_args: Any,
        fallback_result: Any,
        reason: str,
    ) -> None:
        """Log a mismatch between recorded and actual RNG calls."""

        mismatch = {
            "call_index": self._call_index - 1,
            "method_name": method_name,
            "actual_args": list(actual_args),
            "actual_kwargs": dict(actual_kwargs),
            "expected_args": expected_args,
            "fallback_result": fallback_result,
            "reason": reason,
            "timestamp": time.time(),
        }

        self._mismatches.append(mismatch)

    def get_replay_progress(self) -> Dict[str, Any]:
        """Get current replay progress information."""

        if not self.replaying:
            return {"status": "not_replaying"}

        total_calls = len(self.session.rng_calls)
        current_index = self._call_index
        progress_percent = (current_index / total_calls * 100) if total_calls > 0 else 100

        return {
            "status": "replaying",
            "session_id": self.session.session_id,
            "current_call": current_index,
            "total_calls": total_calls,
            "progress_percent": progress_percent,
            "mismatches": len(self._mismatches),
        }


# Global replay engine instance for CLI usage
_global_replay_engine: Optional[ReplayEngine] = None


def start_replay(session: RecordingSession) -> str:
    """
    Convenience function to start replay with a global engine.

    Args:
        session: The recorded session to replay

    Returns:
        session_id: The ID of the session being replayed
    """
    global _global_replay_engine
    _global_replay_engine = ReplayEngine(session)
    return _global_replay_engine.start_replay()


def stop_replay() -> Dict[str, Any]:
    """Stop replay with the global engine and return statistics."""
    global _global_replay_engine
    if _global_replay_engine is None:
        raise RuntimeError("No replay session to stop")

    result = _global_replay_engine.stop_replay()
    _global_replay_engine = None  # Clear global instance
    return result


def is_replaying() -> bool:
    """Check if replay is currently active."""
    global _global_replay_engine
    return _global_replay_engine is not None and _global_replay_engine.replaying


def get_replay_progress() -> Dict[str, Any]:
    """Get progress of current replay session."""
    global _global_replay_engine
    if _global_replay_engine is None:
        return {"status": "no_replay_session"}
    return _global_replay_engine.get_replay_progress()


def _reset_global_replay_engine() -> None:
    """Reset the global replay engine instance. For testing only."""
    global _global_replay_engine
    _global_replay_engine = None
