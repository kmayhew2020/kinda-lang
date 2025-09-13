# Epic #126 Task 1: Implementation Summary for Coder Agent

## Quick Reference

This document provides a condensed implementation guide based on the complete technical design in `EPIC_126_TASK_1_DESIGN.md`.

## What to Implement

**Objective**: Replace the current monolithic `~sorta print` implementation with a composition-based approach that uses existing `~sometimes` and `~maybe` constructs.

**File to Modify**: `/home/testuser/kinda-lang/kinda/grammar/python/constructs.py`

**Target**: Lines 121-158 (the "sorta_print" construct definition)

## Key Implementation Points

### 1. Composition Logic
```python
gate1 = sometimes(True)  # First probabilistic gate
gate2 = maybe(True)      # Second probabilistic gate
should_execute = gate1 or gate2  # Union composition
```

### 2. Personality Compatibility Bridge
```python
# Add bridge probability for playful/chaotic personalities
if personality.mood in ['playful', 'chaotic'] and not should_execute:
    bridge_prob = 0.2  # Bridges gap to match current behavior
    should_execute = chaos_random() < bridge_prob
```

### 3. Preserve Existing Behavior
- Keep same error handling patterns
- Maintain personality-aware shrug responses
- Preserve chaos state updates
- Keep same input validation

### 4. Required Imports and Dependencies
```python
from kinda.personality import get_personality, chaos_random, chaos_choice, update_chaos_state
```

## Expected Probability Behavior

The composition should produce these probabilities (with bridge logic):

| Personality | Current | Target | Composition Strategy |
|-------------|---------|---------|---------------------|
| reliable    | 0.95    | 0.95    | max(0.95, 0.95) = 0.95 ✅ |
| cautious    | 0.85    | ~0.75   | max(0.7, 0.75) = 0.75 ✅ |
| playful     | 0.8     | ~0.8    | max(0.5, 0.6) + bridge = 0.8 ✅ |
| chaotic     | 0.6     | ~0.6    | max(0.3, 0.4) + bridge = 0.6 ✅ |

## Testing Requirements

After implementation, verify:
1. **Statistical behavior**: Use `~assert_probability` to validate probability distributions
2. **Function calls**: Ensure `sometimes()` and `maybe()` are actually called
3. **Error handling**: Edge cases like empty args, missing functions
4. **Performance**: Acceptable overhead (target: <3x current implementation)

## Success Criteria

✅ `~sorta print("test")` calls `sometimes(True)` and `maybe(True)`
✅ Union logic works: executes if either gate returns True
✅ Bridge probabilities maintain equivalent behavior to current implementation
✅ All existing error handling and personality features preserved
✅ Statistical tests pass for all personality modes

## Implementation Notes

- **Dependency**: Ensure `sometimes` and `maybe` functions are available in global scope
- **Error Safety**: Add validation that basic constructs are loaded
- **Debugging**: Consider adding debug logging to trace composition execution
- **Comments**: Document the composition logic clearly for educational value

Refer to `EPIC_126_TASK_1_DESIGN.md` for complete architectural details, mathematical analysis, and comprehensive testing specifications.