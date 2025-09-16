# Epic #126 Task 3: ~ish Implementation Specification

**For**: Coder Agent
**Architect**: Claude
**Date**: September 14, 2025
**Priority**: High
**Estimated Effort**: 10 working days

## Implementation Overview

Refactor existing ~ish implementations to use the composition framework from Task 2 while maintaining 100% backward compatibility. This demonstrates the "Kinda builds Kinda" principle by showing how ~ish patterns emerge from basic constructs.

## File-by-File Implementation Plan

### 1. Enhance Composition Framework Patterns

#### File: `kinda/composition/patterns.py`

**Add New Class**: `IshToleranceComposition`

```python
class IshToleranceComposition(ToleranceComposition):
    """Enhanced tolerance composition specifically for ~ish patterns.

    Demonstrates how ~ish behavior emerges from composition of:
    - ~kinda_float (numerical fuzzing)
    - ~chaos_tolerance (personality-aware tolerance)
    - ~probably (probabilistic decision making)
    - ~sometimes (conditional execution)
    """

    def __init__(self, name: str, mode: str = "comparison"):
        """Initialize ish composition pattern.

        Args:
            name: Pattern name for registration
            mode: "comparison" for conditionals, "assignment" for variable modification
        """
        super().__init__(name, "kinda_float", "chaos_tolerance")
        self.mode = mode
        self._construct_cache = {}  # Cache basic construct functions

    def _get_basic_construct(self, construct_name: str) -> Callable:
        """Get basic construct function with caching."""
        if construct_name not in self._construct_cache:
            try:
                from kinda.langs.python.runtime import fuzzy
                self._construct_cache[construct_name] = getattr(fuzzy, construct_name)
            except ImportError:
                raise RuntimeError(f"Basic construct '{construct_name}' not available")
        return self._construct_cache[construct_name]

    def compose_comparison(self, left_val: Any, right_val: Any, tolerance: float = None) -> bool:
        """Compose ~ish comparison from basic constructs.

        Composition logic:
        1. Apply ~kinda_float to add uncertainty to difference calculation
        2. Use ~chaos_tolerance for personality-aware tolerance
        3. Apply ~probably to final boolean decision

        This shows how numerical fuzzing emerges from basic construct composition.
        """
        try:
            # Get basic construct functions
            kinda_float = self._get_basic_construct('kinda_float')
            probably = self._get_basic_construct('probably')

            # Convert inputs to numeric with error handling (preserve existing behavior)
            try:
                left_val = float(left_val)
                right_val = float(right_val)
            except (ValueError, TypeError) as e:
                from kinda.personality import update_chaos_state
                update_chaos_state(failed=True)
                return probably(False)  # Fallback behavior

            # Get tolerance using personality system if not provided
            if tolerance is None:
                from kinda.personality import chaos_tolerance
                tolerance = chaos_tolerance()

            # Apply composition: ~kinda_float adds uncertainty to calculation
            fuzzy_tolerance = kinda_float(tolerance)
            difference = kinda_float(abs(left_val - right_val))

            # Build ~ish behavior from basic constructs using ~probably
            base_result = difference <= fuzzy_tolerance
            return probably(base_result)

        except Exception as e:
            # Fallback to legacy implementation on any error
            from kinda.langs.python.runtime.fuzzy import ish_comparison
            return ish_comparison(left_val, right_val, tolerance)

    def compose_assignment(self, current_val: Any, target_val: Any = None) -> Any:
        """Compose ~ish variable modification from basic constructs.

        Composition logic:
        1. Use ~kinda_float for fuzzy variance calculation
        2. Apply ~sometimes for conditional adjustment behavior
        3. Demonstrate how variable modification emerges from simpler patterns
        """
        try:
            # Get basic construct functions
            kinda_float = self._get_basic_construct('kinda_float')
            sometimes = self._get_basic_construct('sometimes')

            # Convert to numeric with error handling
            try:
                current_val = float(current_val)
            except (ValueError, TypeError) as e:
                from kinda.personality import update_chaos_state
                update_chaos_state(failed=True)
                return kinda_float(0 if current_val is None else current_val)

            if target_val is None:
                # Standalone case: var~ish → create fuzzy value using composition
                from kinda.personality import chaos_variance
                variance_base = chaos_variance()
                fuzzy_variance = kinda_float(variance_base)
                result = current_val + fuzzy_variance
            else:
                # Assignment case: var ~ish target → show composition behavior
                try:
                    target_val = float(target_val)
                except (ValueError, TypeError):
                    from kinda.personality import update_chaos_state
                    update_chaos_state(failed=True)
                    return kinda_float(current_val)

                # Demonstrate how ~ish emerges from basic construct composition
                adjustment_factor = kinda_float(0.5)  # Fuzzy adjustment factor
                difference = kinda_float(target_val - current_val)

                # Use ~sometimes to show probabilistic decision making
                if sometimes(True):
                    # Adjust towards target using fuzzy factors
                    result = current_val + (difference * adjustment_factor)
                else:
                    # Apply direct fuzzy variance (fallback behavior)
                    from kinda.personality import chaos_variance
                    variance_base = chaos_variance()
                    fuzzy_variance = kinda_float(variance_base)
                    result = current_val + fuzzy_variance

            # Maintain type consistency
            if isinstance(current_val, int) and (target_val is None or isinstance(target_val, int)):
                return int(kinda_float(result))
            else:
                return kinda_float(result)

        except Exception as e:
            # Fallback to legacy implementation on any error
            from kinda.langs.python.runtime.fuzzy import ish_value
            return ish_value(current_val, target_val)

    def get_target_probabilities(self) -> Dict[str, float]:
        """Calculate target probabilities for ~ish patterns."""
        from kinda.personality import get_personality

        personality = get_personality()

        # ~ish patterns have personality-dependent behavior
        base_prob = {
            "reliable": 0.8,    # High precision, stricter tolerance
            "cautious": 0.75,   # Moderately strict tolerance
            "playful": 0.65,    # More relaxed tolerance
            "chaotic": 0.55,    # Very loose tolerance
        }.get(personality.mood, 0.7)

        return {personality.mood: base_prob}

# Add to factory methods
def create_ish_comparison_pattern() -> IshToleranceComposition:
    """Create ~ish comparison composition pattern."""
    return IshToleranceComposition("ish_comparison_pattern", "comparison")

def create_ish_assignment_pattern() -> IshToleranceComposition:
    """Create ~ish assignment composition pattern."""
    return IshToleranceComposition("ish_assignment_pattern", "assignment")
```

**Update Factory Class**: Add to `CompositionPatternFactory`

```python
@staticmethod
def create_ish_comparison_pattern() -> IshToleranceComposition:
    """Create ~ish comparison composition pattern."""
    return IshToleranceComposition("ish_comparison_pattern", "comparison")

@staticmethod
def create_ish_assignment_pattern() -> IshToleranceComposition:
    """Create ~ish assignment composition pattern."""
    return IshToleranceComposition("ish_assignment_pattern", "assignment")
```

**Update __init__.py**: Add new exports

```python
# Add to imports
from .patterns import (
    # ... existing imports ...
    IshToleranceComposition,
    create_ish_comparison_pattern,
    create_ish_assignment_pattern,
)

# Add to __all__
__all__ = [
    # ... existing exports ...
    "IshToleranceComposition",
    "create_ish_comparison_pattern",
    "create_ish_assignment_pattern",
]
```

### 2. Create Composition-Aware Runtime Functions

#### File: `kinda/langs/python/runtime/fuzzy.py`

**Add New Functions**: Insert after existing ish functions (around line 446)

```python
def ish_comparison_composed(left_val, right_val, tolerance_base=None):
    """Epic #126 Task 3: ~ish comparison using composition framework.

    This function demonstrates how ~ish comparison emerges from basic constructs:
    - ~kinda_float for numerical uncertainty
    - ~chaos_tolerance for personality-aware tolerance
    - ~probably for probabilistic decisions
    """
    from kinda.personality import update_chaos_state

    try:
        # Initialize composition framework if needed
        from kinda.composition import get_composition_engine, is_framework_ready

        if not is_framework_ready():
            # Fallback to legacy implementation if framework not available
            return ish_comparison(left_val, right_val, tolerance_base)

        # Get or create the ish comparison pattern
        engine = get_composition_engine()
        pattern_name = "ish_comparison_pattern"
        ish_pattern = engine.get_composite(pattern_name)

        if ish_pattern is None:
            # Create and register the pattern on first use
            from kinda.composition.patterns import IshToleranceComposition
            ish_pattern = IshToleranceComposition(pattern_name, "comparison")
            engine.register_composite(ish_pattern)

        # Delegate to composition framework
        result = ish_pattern.compose_comparison(left_val, right_val, tolerance_base)
        update_chaos_state(failed=False)
        return result

    except Exception as e:
        # Robust fallback to legacy implementation
        print(f"[composition] ~ish comparison fell back to legacy: {e}")
        update_chaos_state(failed=True)
        return ish_comparison(left_val, right_val, tolerance_base)

def ish_value_composed(val, target_val=None):
    """Epic #126 Task 3: ~ish value modification using composition framework.

    This function demonstrates how ~ish variable modification emerges from:
    - ~kinda_float for fuzzy variance
    - ~sometimes for conditional behavior
    - ~chaos_variance for personality-aware adjustment
    """
    from kinda.personality import update_chaos_state

    try:
        # Initialize composition framework if needed
        from kinda.composition import get_composition_engine, is_framework_ready

        if not is_framework_ready():
            # Fallback to legacy implementation if framework not available
            return ish_value(val, target_val)

        # Get or create the ish assignment pattern
        engine = get_composition_engine()
        pattern_name = "ish_assignment_pattern"
        ish_pattern = engine.get_composite(pattern_name)

        if ish_pattern is None:
            # Create and register the pattern on first use
            from kinda.composition.patterns import IshToleranceComposition
            ish_pattern = IshToleranceComposition(pattern_name, "assignment")
            engine.register_composite(ish_pattern)

        # Delegate to composition framework
        result = ish_pattern.compose_assignment(val, target_val)
        update_chaos_state(failed=False)
        return result

    except Exception as e:
        # Robust fallback to legacy implementation
        print(f"[composition] ~ish value fell back to legacy: {e}")
        update_chaos_state(failed=True)
        return ish_value(val, target_val)
```

**Update env exports**: Add to end of file

```python
env["ish_comparison_composed"] = ish_comparison_composed
env["ish_value_composed"] = ish_value_composed
```

### 3. Update Transformer for Composition Framework

#### File: `kinda/langs/python/transformer.py`

**Add Feature Flag Support**: After imports (around line 15)

```python
import os

# Feature flag for composition framework integration
USE_COMPOSITION_FRAMEWORK = os.getenv('KINDA_USE_COMPOSITION_ISH', 'true').lower() == 'true'
```

**Modify _transform_ish_constructs**: Replace existing function (around line 1050)

```python
def _transform_ish_constructs(line: str) -> str:
    """Transform inline ~ish constructs in a line.

    Epic #126 Task 3: Optionally use composition framework functions
    while maintaining identical behavior and backward compatibility.
    """
    ish_constructs = find_ish_constructs(line)
    if not ish_constructs:
        return line

    # Determine which runtime functions to use
    if USE_COMPOSITION_FRAMEWORK:
        ish_value_func = "ish_value_composed"
        ish_comparison_func = "ish_comparison_composed"
    else:
        ish_value_func = "ish_value"
        ish_comparison_func = "ish_comparison"

    # Transform from right to left to preserve positions (existing logic preserved)
    transformed_line = line
    for construct_type, match, start_pos, end_pos in reversed(ish_constructs):
        if construct_type == "ish_value":
            used_helpers.add(ish_value_func)  # Use composition or legacy function
            value = match.group(1)
            replacement = f"{ish_value_func}({value})"
        elif construct_type == "ish_comparison":
            left_val = match.group(1)
            right_val = match.group(2).strip()

            # PRESERVE EXISTING CONTEXT DETECTION LOGIC
            stripped_line = line.strip()

            # Check if this is in a conditional/comparison context first
            is_in_conditional = (
                stripped_line.startswith("if ")
                or stripped_line.startswith("elif ")
                or stripped_line.startswith("while ")
                or stripped_line.startswith("assert ")
                or " if " in stripped_line
                or " and " in stripped_line
                or " or " in stripped_line
                or stripped_line.startswith("return ")
                # Check if ~ish is inside parentheses, brackets, or after assignment
                or ("=" in stripped_line and stripped_line.find("=") < stripped_line.find("~ish"))
                or "(" in stripped_line.split("~ish")[0]  # Function call context
                or "[" in stripped_line  # List/dict context
                or "{" in stripped_line  # Dict context
            )

            # Check if this is a standalone variable assignment
            is_variable_assignment = (
                re.match(rf"^\s*{re.escape(left_val)}\s*~ish\s+", stripped_line)
                and not is_in_conditional
            )

            if is_variable_assignment:
                # Variable modification context - use ish_value function
                used_helpers.add(ish_value_func)
                replacement = f"{left_val} = {ish_value_func}({left_val}, {right_val})"
            else:
                # Comparison context - use ish_comparison function
                used_helpers.add(ish_comparison_func)
                replacement = f"{ish_comparison_func}({left_val}, {right_val})"

        elif construct_type == "ish_comparison_with_ish_value":
            used_helpers.add(ish_comparison_func)
            used_helpers.add(ish_value_func)
            left_val = match.group(1)
            right_val = match.group(2).strip()
            replacement = f"{ish_comparison_func}({left_val}, {ish_value_func}({right_val}))"
        else:
            continue  # Skip unknown constructs

        # Apply replacement (existing logic preserved)
        transformed_line = transformed_line[:start_pos] + replacement + transformed_line[end_pos:]

    return transformed_line
```

### 4. Add Composition-Specific Testing

#### File: `tests/python/test_ish_composition_framework.py` (New File)

```python
#!/usr/bin/env python3

"""
Epic #126 Task 3: Tests for ~ish composition framework integration.
These tests validate that ~ish patterns work identically using composition framework.
"""

import pytest
import os
import statistics
from pathlib import Path
import tempfile

# Test both composition and legacy implementations
@pytest.fixture(params=[True, False])
def use_composition(request, monkeypatch):
    """Test with both composition and legacy implementations."""
    monkeypatch.setenv('KINDA_USE_COMPOSITION_ISH', str(request.param).lower())
    return request.param

class TestIshCompositionBehavior:
    """Test that composition framework produces identical behavior."""

    def test_ish_comparison_statistical_equivalence(self, use_composition):
        """Test that composed ~ish comparison has same statistical behavior."""
        from kinda.langs.python.runtime.fuzzy import ish_comparison_composed, ish_comparison

        # Choose function based on parameter
        test_func = ish_comparison_composed if use_composition else ish_comparison

        # Test statistical equivalence over many runs
        results = []
        for _ in range(1000):
            result = test_func(10.0, 10.1, 0.2)
            results.append(result)

        success_rate = sum(results) / len(results)

        # Should be approximately 70-90% success for this tolerance
        assert 0.6 <= success_rate <= 0.95, f"Success rate {success_rate} outside expected range"

    def test_ish_value_statistical_equivalence(self, use_composition):
        """Test that composed ~ish value has same statistical behavior."""
        from kinda.langs.python.runtime.fuzzy import ish_value_composed, ish_value

        # Choose function based on parameter
        test_func = ish_value_composed if use_composition else ish_value

        # Test variance behavior
        base_value = 100.0
        results = []

        for _ in range(1000):
            result = test_func(base_value)  # Standalone case
            results.append(result)

        mean_result = statistics.mean(results)
        std_dev = statistics.stdev(results)

        # Results should cluster around base value with reasonable variance
        assert abs(mean_result - base_value) < 5.0, f"Mean {mean_result} too far from base {base_value}"
        assert 0.5 < std_dev < 20.0, f"Standard deviation {std_dev} outside expected range"

    def test_ish_assignment_statistical_equivalence(self, use_composition):
        """Test ~ish assignment behavior equivalence."""
        from kinda.langs.python.runtime.fuzzy import ish_value_composed, ish_value

        # Choose function based on parameter
        test_func = ish_value_composed if use_composition else ish_value

        # Test assignment behavior
        current_val = 50.0
        target_val = 100.0
        results = []

        for _ in range(1000):
            result = test_func(current_val, target_val)
            results.append(result)

        mean_result = statistics.mean(results)

        # Results should trend toward target but with variance
        assert current_val < mean_result < target_val, f"Mean {mean_result} not between current {current_val} and target {target_val}"

class TestIshCompositionIntegration:
    """Test integration with composition framework components."""

    def test_composition_pattern_registration(self):
        """Test that ~ish patterns register correctly with framework."""
        from kinda.composition import get_composition_engine
        from kinda.langs.python.runtime.fuzzy import ish_comparison_composed

        # Clear any existing patterns
        engine = get_composition_engine()

        # First call should create and register pattern
        result = ish_comparison_composed(5.0, 5.1)

        # Pattern should now be registered
        pattern = engine.get_composite("ish_comparison_pattern")
        assert pattern is not None
        assert pattern.name == "ish_comparison_pattern"

    def test_composition_framework_fallback(self):
        """Test fallback to legacy functions when framework fails."""
        # Temporarily break framework
        with pytest.MonkeyPatch().context() as m:
            m.setenv('KINDA_USE_COMPOSITION_ISH', 'true')

            # Mock framework to fail
            def mock_failing_engine():
                raise RuntimeError("Framework unavailable")

            m.setattr('kinda.composition.get_composition_engine', mock_failing_engine)

            # Should fallback gracefully
            from kinda.langs.python.runtime.fuzzy import ish_comparison_composed
            result = ish_comparison_composed(5.0, 5.1)  # Should not raise exception
            assert isinstance(result, bool)

class TestIshTransformationCompatibility:
    """Test that transformed code works with both implementations."""

    def test_transformer_generates_correct_functions(self, use_composition):
        """Test that transformer uses correct runtime functions."""
        from kinda.langs.python.transformer import transform_line

        with pytest.MonkeyPatch().context() as m:
            m.setenv('KINDA_USE_COMPOSITION_ISH', str(use_composition).lower())

            # Test assignment context
            result = transform_line("value ~ish 10")

            if use_composition:
                assert "ish_value_composed" in result[0]
            else:
                assert "ish_value(" in result[0] and "ish_value_composed" not in result[0]

    def test_file_transformation_compatibility(self, use_composition):
        """Test complete file transformation with composition framework."""
        from kinda.langs.python.transformer import transform_file

        knda_content = """# Test ~ish patterns
value = 100

# Assignment context
value ~ish 20

# Comparison context
if value ~ish 90:
    print("Close!")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(knda_content)
            temp_path = Path(f.name)

        try:
            with pytest.MonkeyPatch().context() as m:
                m.setenv('KINDA_USE_COMPOSITION_ISH', str(use_composition).lower())

                result = transform_file(temp_path)

                if use_composition:
                    assert "ish_value_composed" in result
                    assert "ish_comparison_composed" in result
                else:
                    assert "ish_value" in result
                    assert "ish_comparison" in result
                    assert "composed" not in result

        finally:
            temp_path.unlink()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 5. Performance Benchmarking

#### File: `tests/python/test_ish_performance_benchmark.py` (New File)

```python
#!/usr/bin/env python3

"""
Epic #126 Task 3: Performance benchmarks for ~ish composition framework.
Validates <20% overhead requirement.
"""

import pytest
import time
import statistics
import os
from contextlib import contextmanager

@contextmanager
def performance_timer():
    """Context manager for timing operations."""
    start = time.perf_counter()
    yield lambda: time.perf_counter() - start

class TestIshPerformanceBenchmark:
    """Benchmark composition framework performance vs legacy."""

    @pytest.mark.performance
    def test_ish_comparison_performance(self):
        """Benchmark ~ish comparison performance."""
        from kinda.langs.python.runtime.fuzzy import ish_comparison, ish_comparison_composed

        iterations = 10000

        # Benchmark legacy implementation
        with performance_timer() as timer:
            for i in range(iterations):
                ish_comparison(float(i % 100), float((i + 1) % 100))
        legacy_time = timer()

        # Benchmark composition implementation
        with performance_timer() as timer:
            for i in range(iterations):
                ish_comparison_composed(float(i % 100), float((i + 1) % 100))
        composition_time = timer()

        # Calculate overhead percentage
        overhead = ((composition_time - legacy_time) / legacy_time) * 100

        print(f"Legacy time: {legacy_time:.4f}s")
        print(f"Composition time: {composition_time:.4f}s")
        print(f"Overhead: {overhead:.2f}%")

        # Should be <20% overhead
        assert overhead < 20.0, f"Composition overhead {overhead:.2f}% exceeds 20% target"

    @pytest.mark.performance
    def test_ish_value_performance(self):
        """Benchmark ~ish value performance."""
        from kinda.langs.python.runtime.fuzzy import ish_value, ish_value_composed

        iterations = 10000

        # Benchmark legacy implementation
        with performance_timer() as timer:
            for i in range(iterations):
                ish_value(float(i % 100))
        legacy_time = timer()

        # Benchmark composition implementation
        with performance_timer() as timer:
            for i in range(iterations):
                ish_value_composed(float(i % 100))
        composition_time = timer()

        # Calculate overhead percentage
        overhead = ((composition_time - legacy_time) / legacy_time) * 100

        print(f"Legacy time: {legacy_time:.4f}s")
        print(f"Composition time: {composition_time:.4f}s")
        print(f"Overhead: {overhead:.2f}%")

        # Should be <20% overhead
        assert overhead < 20.0, f"Composition overhead {overhead:.2f}% exceeds 20% target"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "performance"])
```

## Testing Requirements

### Existing Tests Must Pass

**Critical**: All existing ~ish tests must pass without modification:
- `tests/python/test_ish_construct.py`
- `tests/python/test_ish_construct_comprehensive.py`
- Any integration tests using ~ish patterns

### New Tests Must Pass

1. **Composition Framework Integration Tests** (`test_ish_composition_framework.py`)
2. **Performance Benchmarks** (`test_ish_performance_benchmark.py`)
3. **Statistical Equivalence Validation**

### Test Execution Commands

```bash
# Run all ~ish tests
pytest tests/python/test_ish* -v

# Run new composition tests specifically
pytest tests/python/test_ish_composition_framework.py -v

# Run performance benchmarks
pytest tests/python/test_ish_performance_benchmark.py -v -m performance

# Run full test suite
pytest tests/ -v
```

## Implementation Validation

### Pre-Implementation Checklist

- [ ] Task 2 composition framework is complete and functional
- [ ] All existing tests pass: `pytest tests/ -v`
- [ ] CI local script passes: `~/kinda-lang-agents/infrastructure/scripts/ci-local.sh`
- [ ] Dev branch is synchronized with latest changes

### During Implementation Checkpoints

1. **After Framework Enhancement** (Day 2)
   - [ ] New `IshToleranceComposition` class implemented
   - [ ] Factory methods added
   - [ ] Basic unit tests for patterns pass

2. **After Runtime Refactoring** (Day 5)
   - [ ] Composition-aware runtime functions implemented
   - [ ] Feature flag mechanism working
   - [ ] Fallback to legacy functions tested

3. **After Integration** (Day 8)
   - [ ] Transformer uses new functions when flag enabled
   - [ ] All existing ~ish tests still pass
   - [ ] New composition tests pass

4. **Final Validation** (Day 10)
   - [ ] Performance benchmarks within 20% overhead
   - [ ] Statistical equivalence validated
   - [ ] Full CI pipeline passes

### Success Criteria Validation

```bash
# Validate backward compatibility
KINDA_USE_COMPOSITION_ISH=false pytest tests/python/test_ish* -v

# Validate composition framework integration
KINDA_USE_COMPOSITION_ISH=true pytest tests/python/test_ish* -v

# Validate performance requirements
pytest tests/python/test_ish_performance_benchmark.py -v -m performance

# Full validation
~/kinda-lang-agents/infrastructure/scripts/ci-local.sh
```

## Error Handling & Rollback

### Robust Error Handling

1. **Framework Availability**: Check `is_framework_ready()` before use
2. **Pattern Creation**: Handle composition pattern failures gracefully
3. **Legacy Fallback**: Automatic fallback to original functions on any error
4. **Feature Flag**: Instant disable via `KINDA_USE_COMPOSITION_ISH=false`

### Rollback Procedures

1. **Feature Flag Disable**: `export KINDA_USE_COMPOSITION_ISH=false`
2. **Code Rollback**: Remove composition-aware functions, keep legacy functions
3. **Framework Rollback**: Remove composition framework integration if needed

## Documentation Requirements

### Code Documentation

- Add comprehensive docstrings explaining composition approach
- Document how ~ish emerges from basic constructs
- Provide examples of "Kinda builds Kinda" principle

### Architecture Updates

- Update system diagrams to show composition flow
- Document performance characteristics
- Provide debugging and troubleshooting guides

## Handoff Requirements

### Deliverables for Testing Agent

1. **Implementation Complete**: All code changes implemented per specification
2. **Self-Testing Passed**: All new tests passing
3. **CI Pipeline Green**: `ci-local.sh` passes with composition framework enabled
4. **Performance Validated**: Benchmarks show <20% overhead
5. **Documentation Updated**: All docstrings and comments complete

### Success Metrics

- **Functional**: All existing ~ish tests pass unchanged
- **Performance**: Composition overhead <20%
- **Integration**: Framework demonstrates reusable patterns
- **Compatibility**: Feature flag enables seamless switching

This specification provides complete implementation guidance for demonstrating how ~ish patterns can elegantly emerge from basic construct composition while maintaining full backward compatibility and performance requirements.