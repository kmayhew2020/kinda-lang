# Performance Tests - Disabled During Development

## Status: DISABLED

Performance tests are currently **disabled** during active development for the following reasons:

1. **Time**: Performance tests take significantly longer to run than functional tests
2. **Invalidation**: Code changes frequently invalidate performance baselines
3. **CI Overhead**: Long-running tests slow down the development feedback loop
4. **Flakiness**: Performance tests can be inconsistent across different environments

## When Performance Tests Are Run

Performance tests will be:
- ✅ Re-enabled before each release
- ✅ Run manually during performance optimization work
- ✅ Validated as part of release QA process
- ❌ NOT run during daily development CI

## How to Identify Performance Tests

Performance tests are marked with:
```python
@pytest.mark.skip(reason="Performance tests disabled until release - they take too long and get invalidated by changes")
```

## How to Run Performance Tests Manually

When needed, run performance tests with:
```bash
# Run all performance tests (remove skip marker temporarily)
pytest -m performance

# Or run specific performance test file
pytest tests/security/test_dos_protection.py::TestPerformanceImpact -v
```

## Files with Performance Tests

Current locations:
- `tests/security/test_dos_protection.py` - DoS protection performance overhead tests
- `tests/performance/` - General performance benchmark tests (if they exist)

## Re-enabling for Release

Before release, remove `@pytest.mark.skip` decorators and validate:
1. All performance tests pass
2. Performance baselines are reasonable
3. No regressions compared to previous release
4. Document any expected performance changes
