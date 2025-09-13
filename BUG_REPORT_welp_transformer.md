# Bug Report: ~welp Transformer Missing Closing Parenthesis

## Summary
The transformer for the `~welp` construct generates invalid Python syntax by omitting the closing parenthesis for `welp_fallback()` function calls.

## Severity
**HIGH** - Code fails to compile/execute

## Issue Details

### Expected Behavior
When transforming `result = (1 / 1) ~welp 0`, the transformer should generate valid Python syntax like:
```python
result = welp_fallback(lambda: (1 / 1), 0)
```

### Actual Behavior
The transformer generates invalid syntax:
```python
result = welp_fallback(lambda: (1 / 1), 0  # Should succeed)
```
Note the missing closing parenthesis after `0`.

### Reproduction Steps
1. Create a `.knda` file with content:
   ```
   result = (1 / 1) ~welp 0
   ```
2. Run `python -m kinda transform <file>`
3. Check the generated Python code
4. Try to run the generated code - it fails with syntax error

### Error Output
```
💥 Runtime error: '(' was never closed (debug_welp_test.py, line 10)
[?] Your code transformed fine but crashed during execution
```

### Test Case That Fails
From `tests/python/test_repetition_integration.py::TestRepetitionWithErrorHandling::test_kinda_repeat_with_welp_fallback`:

```knda
~kinda_repeat(10):
    result = (1 / 1) ~welp 0  # Should succeed
    successful_operations += result
```

### Analysis
The issue is in the transformer's pattern matching and replacement logic for the `~welp` construct. The transformer correctly identifies the pattern but fails to properly close the `welp_fallback()` function call.

## Priority
**Priority 3** (Implementation Bug) - This is a transformer bug that prevents valid kinda-lang code from executing.

## Recommendation
Fix the transformer's regex pattern or replacement logic for the `~welp` construct to ensure proper parenthesis matching in the generated `welp_fallback()` calls.

## Files Affected
- Transformer module (likely in `kinda/langs/python/transformer.py`)
- Test file: `tests/python/test_repetition_integration.py`