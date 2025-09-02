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
    """
    
    def __init__(self, output_file: Optional[Path] = None):
        self.output_file = output_file
        self.recording = False
        self.session: Optional[RecordingSession] = None
        self._sequence_counter = 0
        self._lock = threading.Lock()  # For thread safety
        
        # Hook tracking
        self._original_methods: Dict[str, Any] = {}
        self._hooked = False
    
    def start_recording(self, input_file: str, command_args: List[str]) -> str:
        """
        Start recording a new session.
        
        Args:
            input_file: The .knda file being executed
            command_args: Command line arguments used
            
        Returns:
            session_id: Unique identifier for this recording session
        """
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
                decision_points=[]
            )
            
            # Install hooks
            self._install_hooks()
            
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
        
        with self._lock:
            current_time = time.time()
            
            # Finalize session
            self.session.end_time = current_time
            self.session.duration = current_time - self.session.start_time
            self.session.total_calls = len(self.session.rng_calls)
            
            # Remove hooks
            self._remove_hooks()
            
            self.recording = False
            
            # Save to file if specified
            if self.output_file:
                self.save_session(self.session, self.output_file)
            
            return self.session
    
    def _install_hooks(self) -> None:
        """Install RNG method hooks in PersonalityContext."""
        if self._hooked:
            return
            
        from kinda.personality import PersonalityContext
        
        # Get the instance to hook
        personality = PersonalityContext.get_instance()
        
        # Hook the main RNG methods
        rng_methods = ['random', 'randint', 'uniform', 'choice', 'gauss']
        
        for method_name in rng_methods:
            if hasattr(personality, method_name):
                original_method = getattr(personality, method_name)
                self._original_methods[method_name] = original_method
                
                # Create hooked version
                hooked_method = self._create_hook(method_name, original_method)
                setattr(personality, method_name, hooked_method)
        
        self._hooked = True
    
    def _remove_hooks(self) -> None:
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
    
    def _create_hook(self, method_name: str, original_method):
        """Create a hooked version of an RNG method that records calls."""
        
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
            
        return hooked_method
    
    def _record_rng_call(self, method_name: str, args: tuple, kwargs: dict, result: Any) -> None:
        """Record a single RNG call with full context."""
        
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
                decision_impact=construct_info.get("impact")
            )
            
            # Add to session
            self.session.rng_calls.append(call_record)
            
            # Update construct usage stats
            if call_record.construct_type:
                self.session.construct_usage[call_record.construct_type] = \
                    self.session.construct_usage.get(call_record.construct_type, 0) + 1
    
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
                    "impact": "conditional execution (50% probability)"
                }
            elif "maybe" in frame_lower:
                return {
                    "type": "maybe", 
                    "location": frame,
                    "impact": "conditional execution (60% probability)"
                }
            elif "probably" in frame_lower:
                return {
                    "type": "probably",
                    "location": frame, 
                    "impact": "conditional execution (70% probability)"
                }
            elif "rarely" in frame_lower:
                return {
                    "type": "rarely",
                    "location": frame,
                    "impact": "conditional execution (15% probability)"
                }
            elif "kinda_int" in frame_lower or "fuzzy_int" in frame_lower:
                return {
                    "type": "kinda_int",
                    "location": frame,
                    "impact": "integer fuzz (±1 variance)"
                }
            elif "kinda_float" in frame_lower or "fuzzy_float" in frame_lower:
                return {
                    "type": "kinda_float",
                    "location": frame,
                    "impact": "float drift (±0.5 variance)"
                }
            elif "ish" in frame_lower:
                return {
                    "type": "ish",
                    "location": frame,
                    "impact": "fuzzy comparison or value"
                }
            elif "sorta_print" in frame_lower:
                return {
                    "type": "sorta_print",
                    "location": frame,
                    "impact": "probabilistic output (80% chance)"
                }
            elif "kinda_binary" in frame_lower:
                return {
                    "type": "kinda_binary",
                    "location": frame,
                    "impact": "ternary logic (yes/no/maybe)"
                }
            elif "chaos_probability" in frame_lower:
                return {
                    "type": "personality_chaos",
                    "location": frame,
                    "impact": "personality-adjusted probability"
                }
        
        # Default case - direct personality RNG call
        return {
            "type": "direct_rng",
            "location": stack_trace[-1] if stack_trace else "unknown",
            "impact": "direct random number generation"
        }
    
    @staticmethod
    def save_session(session: RecordingSession, output_file: Path) -> None:
        """Save a recording session to a JSON file."""
        
        # Convert session to dictionary for JSON serialization
        session_dict = asdict(session)
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save with pretty formatting for readability
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(session_dict, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_session(input_file: Path) -> RecordingSession:
        """Load a recording session from a JSON file."""
        
        with open(input_file, 'r', encoding='utf-8') as f:
            session_dict = json.load(f)
        
        # Convert RNG calls back to RNGCall objects
        rng_calls = [RNGCall(**call_dict) for call_dict in session_dict.get('rng_calls', [])]
        session_dict['rng_calls'] = rng_calls
        
        return RecordingSession(**session_dict)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current recording session."""
        
        if not self.session:
            return {"status": "no_session", "message": "No recording session active"}
        
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


# Global recorder instance for CLI usage
_global_recorder: Optional[ExecutionRecorder] = None


def get_recorder() -> ExecutionRecorder:
    """Get or create the global ExecutionRecorder instance."""
    global _global_recorder
    if _global_recorder is None:
        _global_recorder = ExecutionRecorder()
    return _global_recorder


def start_recording(input_file: str, command_args: List[str], output_file: Optional[Path] = None) -> str:
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
    if _global_recorder is None:
        raise RuntimeError("No recording session to stop")
    return _global_recorder.stop_recording()


def is_recording() -> bool:
    """Check if recording is currently active."""
    global _global_recorder
    return _global_recorder is not None and _global_recorder.recording


def get_session_summary() -> Dict[str, Any]:
    """Get summary of current recording session."""
    global _global_recorder
    if _global_recorder is None:
        return {"status": "no_session", "message": "No recording session active"}
    return _global_recorder.get_session_summary()


def _reset_global_recorder() -> None:
    """Reset the global recorder instance. For testing only."""
    global _global_recorder
    _global_recorder = None