# Kinda-Lang Record/Replay System - Phase 1 Implementation

## Overview

Phase 1 of Issue #122 implements comprehensive recording infrastructure for debugging kinda programs. This system captures every random decision made during program execution, enabling exact replay for debugging and analysis.

## Features Implemented

### 🎥 Recording Infrastructure

- **ExecutionRecorder Class**: Core recording engine that hooks into PersonalityContext RNG methods
- **Complete Decision Capture**: Records all calls to `random()`, `randint()`, `uniform()`, `choice()`, `gauss()`
- **Rich Context Information**: Captures stack traces, personality state, and construct usage
- **Thread-Safe Operation**: Supports multi-threaded kinda programs
- **JSON Session Format**: Human-readable and machine-parseable session files

### 🎮 CLI Integration

- **`kinda record run`**: New CLI command to record program execution
  ```bash
  kinda record run program.py.knda --output session.json --seed 123
  ```
- **Automatic Output Naming**: Defaults to `<program>.session.json`
- **Full Personality Support**: Works with all mood and chaos level settings
- **Error Handling**: Graceful failure handling with partial recording preservation

### 📊 Session File Structure

Each session file contains:

- **Session Metadata**: Unique ID, timestamps, command line args, working directory
- **Execution Environment**: Kinda version, Python version, initial personality settings
- **RNG Call Sequence**: Complete ordered list of all random decisions with:
  - Method name and parameters
  - Return values
  - Stack traces
  - Personality state snapshots
  - Construct context inference
- **Statistics**: Construct usage counts, decision points, execution metrics

## Usage Examples

### Basic Recording
```bash
# Record a simple program
kinda record run examples/python/hello.py.knda --seed 42

# Record with custom output path
kinda record run my_program.py.knda --output debug_session.json

# Record with specific personality
kinda record run chaos_test.py.knda --mood chaotic --chaos-level 9
```

### Session File Analysis
```python
from kinda.record_replay import ExecutionRecorder

# Load a session file
session = ExecutionRecorder.load_session(Path("my_session.json"))

print(f"Recorded {session.total_calls} RNG calls")
print(f"Constructs used: {session.construct_usage}")

# Examine specific RNG calls
for call in session.rng_calls[:5]:
    print(f"{call.method_name}({call.args}) -> {call.result}")
    print(f"  Construct: {call.construct_type}")
    print(f"  Impact: {call.decision_impact}")
```

## Implementation Details

### Recording Hooks

The system uses method replacement to hook into PersonalityContext:

```python
# Original method is preserved
original_random = personality.random

# Hooked method records call then executes original
def hooked_random(*args, **kwargs):
    result = original_random(*args, **kwargs)
    recorder.record_call("random", args, kwargs, result)
    return result

# Hook is installed transparently
personality.random = hooked_random
```

### Construct Context Inference

The system analyzes stack traces to determine which kinda construct triggered each RNG call:

- **Stack Frame Analysis**: Examines function names and file paths
- **Pattern Matching**: Identifies construct types (sometimes, kinda_int, sorta_print, etc.)
- **Impact Assessment**: Describes what each RNG call affects
- **Location Tracking**: Records source file and line information

### Performance Considerations

- **Low Overhead**: Recording adds minimal performance impact
- **Memory Efficient**: Uses lazy serialization and streaming for large sessions
- **Non-Blocking**: Recording failures don't interrupt program execution
- **Thread Safety**: Full support for concurrent kinda programs

## Testing

Comprehensive test suite covers:

- **Basic Functionality**: Recording start/stop, RNG call capture
- **CLI Integration**: Command parsing, file handling, error cases
- **Session Persistence**: Save/load cycle verification
- **Construct Recognition**: Proper context inference for all kinda constructs
- **Edge Cases**: Runtime errors, large programs, concurrent execution

Run tests with:
```bash
python3 -m pytest tests/python/test_record_replay_basic.py -v
python3 -m pytest tests/python/test_record_replay_cli.py -v
```

## Architecture

The recording system builds on kinda-lang's existing strengths:

- **PersonalityContext Foundation**: Leverages centralized RNG system
- **Minimal Code Changes**: No modifications to existing construct implementations
- **Clean Separation**: Recording logic isolated in `record_replay.py`
- **Future-Proof Design**: Ready for Phase 2 replay functionality

## Example Session File

```json
{
  "session_id": "abc123-def456-ghi789",
  "start_time": 1640995200.0,
  "input_file": "test_program.py.knda",
  "command_line_args": ["record", "run", "test_program.py.knda", "--seed", "42"],
  "working_directory": "/home/user/projects",
  "kinda_version": "0.4.1",
  "python_version": "3.9.0",
  "initial_personality": {
    "mood": "playful",
    "chaos_level": 5,
    "seed": 42
  },
  "rng_calls": [
    {
      "call_id": "call-001",
      "sequence_number": 1,
      "method_name": "random",
      "args": [],
      "result": 0.374,
      "construct_type": "sorta_print", 
      "decision_impact": "probabilistic output (80% chance)"
    }
  ],
  "construct_usage": {
    "sorta_print": 3,
    "kinda_int": 2,
    "sometimes": 1
  },
  "total_calls": 6,
  "duration": 0.042
}
```

## Next Steps (Phase 2-4)

The recording infrastructure is now ready for:

- **Replay Engine**: Exact execution reproduction using recorded sessions
- **Analysis Tools**: Session comparison, debugging helpers, visualization
- **CLI Commands**: `kinda replay`, `kinda analyze` with rich reporting
- **Advanced Features**: Partial replay, breakpoint insertion, state inspection

## Known Limitations

- **Python Only**: Currently supports Python programs only (C support planned)
- **Single Process**: Multi-process programs need separate recording per process
- **File Size**: Large programs generate large session files (optimization planned)
- **Stack Traces**: Deep call stacks may be truncated for readability

## Files Added/Modified

- `kinda/record_replay.py`: Core recording implementation
- `kinda/cli.py`: Added `record run` CLI command
- `tests/python/test_record_replay_basic.py`: Basic functionality tests
- `tests/python/test_record_replay_cli.py`: CLI integration tests

The Phase 1 implementation provides a solid foundation for the complete record/replay debugging system envisioned in Issue #122.