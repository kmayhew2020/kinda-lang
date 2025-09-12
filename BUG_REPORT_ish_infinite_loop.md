# Bug Report: ~ish Comparison Creates Infinite Loop in ~eventually_until

## Summary
Using `~ish` fuzzy comparisons inside `~eventually_until` conditions causes infinite loops due to incorrect convergence logic.

## Severity
**HIGH** - Code hangs indefinitely (infinite loop)

## Issue Details

### Expected Behavior
The following code should terminate when `counter` is approximately equal to `target`:
```knda
counter = 0
target = 25~ish
~eventually_until counter ~ish target:
    counter += 1
```

Should terminate around counter ≈ 25 ± some tolerance.

### Actual Behavior
The code runs indefinitely, never terminating. The `~eventually_until` confidence logic appears to never be satisfied when using `ish_comparison()`.

### Reproduction Steps
1. Create a `.knda` file with the test case above
2. Run `python -m kinda run <file>`
3. Code will hang - must be killed manually

### Test Case That Fails
From `tests/python/test_repetition_integration.py::TestRepetitionWithFuzzyValues::test_eventually_until_with_fuzzy_comparison`:

```knda
counter = 0
target = 25~ish
~eventually_until counter ~ish target:
    counter += 1

print(f"COUNTER:{counter}")
print(f"TARGET:{target:.2f}")
```

### Generated Code Analysis
The transformer correctly generates:
```python
from kinda.langs.python.runtime.fuzzy import eventually_until_condition, ish_comparison, ish_value

counter = 0
target = ish_value(25)
while eventually_until_condition(ish_comparison(counter, target)):
    counter += 1
```

### Root Cause Analysis
The issue is likely in one of these runtime functions:
1. **`ish_comparison()`** - May have incorrect logic for fuzzy equality comparison
2. **`eventually_until_condition()`** - May not properly handle the statistical confidence when the condition involves fuzzy comparisons

The `eventually_until_condition()` is designed to continue the loop until it's statistically confident the condition is true. However, with fuzzy `~ish` comparisons, the condition evaluation may be inconsistent or the confidence threshold may never be reached.

## Priority
**Priority 3** (Implementation Bug) - This is a runtime logic bug that prevents valid kinda-lang constructs from working together.

## Analysis Areas
1. **`ish_comparison()` logic**: Check if the fuzzy comparison correctly returns True/False for approximately equal values
2. **Statistical confidence calculation**: Verify that `eventually_until_condition()` can handle probabilistic/fuzzy conditions
3. **Integration testing**: The individual constructs may work in isolation but fail when combined

## Recommendation
1. Debug the runtime functions `ish_comparison()` and `eventually_until_condition()`
2. Add logging to see what values are being compared and what confidence levels are being calculated
3. Consider if fuzzy comparisons need special handling in statistical confidence calculations

## Files Affected
- Runtime module: `kinda/langs/python/runtime/fuzzy.py` or similar
- Test file: `tests/python/test_repetition_integration.py`