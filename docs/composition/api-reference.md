# API Reference: Composition Framework

## 🎯 Overview

This document provides comprehensive API reference for the Kinda-Lang Composition Framework. All classes, methods, and functions are documented with usage examples, parameters, return values, and integration patterns.

## 📚 Core Framework APIs

### CompositeConstruct (Abstract Base Class)

The foundation class for all composite constructs in the composition framework.

```python
class CompositeConstruct(ABC):
    """Base class for all composite constructs built from basic constructs."""
```

#### Constructor

```python
def __init__(self, name: str, config: CompositionConfig)
```

**Parameters:**
- `name` (str): Unique identifier for the composite construct
- `config` (CompositionConfig): Configuration object specifying behavior

**Example:**
```python
from kinda.composition import CompositeConstruct, CompositionConfig, CompositionStrategy

config = CompositionConfig(
    strategy=CompositionStrategy.UNION,
    personality_bridges={"reliable": 0.0, "chaotic": 0.2},
    performance_target=0.20
)
```

#### Abstract Methods

##### get_basic_constructs()

```python
@abstractmethod
def get_basic_constructs(self) -> List[str]
```

**Returns:** List of basic construct names this composite depends on

**Example:**
```python
def get_basic_constructs(self):
    return ["sometimes", "maybe", "rarely"]
```

##### compose()

```python
@abstractmethod
def compose(self, *args, **kwargs) -> Any
```

**Parameters:**
- `*args`: Variable positional arguments passed to composition
- `**kwargs`: Variable keyword arguments passed to composition

**Returns:** Result of composition execution (typically boolean)

**Example:**
```python
def compose(self, condition=True):
    gate1 = sometimes(condition)
    gate2 = maybe(condition)
    return gate1 or gate2
```

##### get_target_probabilities()

```python
@abstractmethod
def get_target_probabilities(self) -> Dict[str, float]
```

**Returns:** Dictionary mapping personality names to target probability values

**Example:**
```python
def get_target_probabilities(self):
    return {
        "reliable": 0.95,
        "cautious": 0.85,
        "playful": 0.75,
        "chaotic": 0.65
    }
```

#### Instance Methods

##### validate_dependencies()

```python
def validate_dependencies(self) -> bool
```

**Returns:** True if all required basic constructs are available

**Example:**
```python
if not pattern.validate_dependencies():
    raise RuntimeError("Required constructs not available")
```

##### execute_with_tracing()

```python
def execute_with_tracing(self, *args, **kwargs) -> Any
```

**Parameters:**
- `*args`: Arguments passed to composition
- `**kwargs`: Keyword arguments passed to composition

**Returns:** Result of composition with optional debug tracing

**Example:**
```python
# Enable tracing in config
config.debug_tracing = True
result = pattern.execute_with_tracing("test_arg")
```

### CompositionConfig

Configuration class for composite construct behavior.

```python
@dataclass
class CompositionConfig:
    """Configuration for construct composition."""
```

#### Attributes

```python
strategy: CompositionStrategy                    # Composition strategy to use
personality_bridges: Dict[str, float]           # Bridge probabilities per personality
performance_target: float = 0.20               # Max acceptable overhead (default 20%)
dependency_validation: bool = True             # Enable dependency validation
statistical_validation: bool = True           # Enable statistical validation
debug_tracing: bool = False                   # Enable debug tracing
```

**Example:**
```python
config = CompositionConfig(
    strategy=CompositionStrategy.THRESHOLD,
    personality_bridges={
        "reliable": 0.0,
        "cautious": 0.05,
        "playful": 0.15,
        "chaotic": 0.25
    },
    performance_target=0.15,
    debug_tracing=True
)
```

### CompositionStrategy (Enum)

Enumeration of available composition strategies.

```python
class CompositionStrategy(Enum):
    """Strategy patterns for construct composition."""
```

#### Values

```python
UNION = "union"                    # gate1 OR gate2 (like ~sorta)
INTERSECTION = "intersection"      # gate1 AND gate2
SEQUENTIAL = "sequential"          # gate1 then gate2 if gate1 succeeds
WEIGHTED = "weighted"             # Weighted combination of results
CONDITIONAL = "conditional"       # Execute gate2 based on gate1 result
THRESHOLD = "threshold"           # Require N successes from M components
```

**Usage Examples:**
```python
# Union strategy (OR logic)
CompositionStrategy.UNION

# Threshold strategy (2 out of 3 must succeed)
CompositionStrategy.THRESHOLD
```

### CompositionEngine

Central registry and execution engine for composite constructs.

```python
class CompositionEngine:
    """Central registry and execution engine for compositions."""
```

#### Methods

##### register_composite()

```python
def register_composite(self, composite: CompositeConstruct) -> None
```

**Parameters:**
- `composite` (CompositeConstruct): Composite construct to register

**Example:**
```python
engine = get_composition_engine()
my_pattern = MyComposition("custom_pattern")
engine.register_composite(my_pattern)
```

##### get_composite()

```python
def get_composite(self, name: str) -> Optional[CompositeConstruct]
```

**Parameters:**
- `name` (str): Name of composite construct to retrieve

**Returns:** CompositeConstruct instance or None if not found

**Example:**
```python
pattern = engine.get_composite("sorta_pattern")
if pattern:
    result = pattern.compose(True)
```

##### list_composites()

```python
def list_composites(self) -> List[str]
```

**Returns:** List of registered composite construct names

**Example:**
```python
available_patterns = engine.list_composites()
print(f"Available patterns: {available_patterns}")
```

##### unregister_composite()

```python
def unregister_composite(self, name: str) -> bool
```

**Parameters:**
- `name` (str): Name of composite to unregister

**Returns:** True if successfully unregistered

**Example:**
```python
if engine.unregister_composite("old_pattern"):
    print("Pattern removed successfully")
```

## 🎨 Pattern Library APIs

### UnionComposition

Implements union (OR) composition strategy.

```python
class UnionComposition(CompositeConstruct):
    """Union composition: execute if ANY component succeeds."""
```

#### Constructor

```python
def __init__(self, name: str, constructs: List[str], bridge_probs: Dict[str, float] = None)
```

**Parameters:**
- `name` (str): Pattern name
- `constructs` (List[str]): List of basic construct names to combine
- `bridge_probs` (Dict[str, float], optional): Personality bridge probabilities

**Example:**
```python
union_pattern = UnionComposition(
    "my_union",
    ["sometimes", "maybe"],
    {"reliable": 0.0, "chaotic": 0.2}
)
```

#### Methods

##### compose()

```python
def compose(self, condition=True) -> bool
```

**Parameters:**
- `condition` (bool, optional): Condition to pass to component constructs

**Returns:** True if any component construct succeeds

### ThresholdComposition

Implements threshold composition strategy requiring N successes from M components.

```python
class ThresholdComposition(CompositeConstruct):
    """Threshold composition: require N successes from M components."""
```

#### Constructor

```python
def __init__(self, name: str, constructs: List[str], threshold: int, bridge_probs: Dict[str, float] = None)
```

**Parameters:**
- `name` (str): Pattern name
- `constructs` (List[str]): List of basic construct names
- `threshold` (int): Number of successes required
- `bridge_probs` (Dict[str, float], optional): Bridge probabilities

**Example:**
```python
threshold_pattern = ThresholdComposition(
    "consensus_pattern",
    ["sometimes", "maybe", "rarely"],
    threshold=2  # Require 2 out of 3
)
```

### ToleranceComposition

Implements tolerance-based composition for fuzzy comparisons.

```python
class ToleranceComposition(CompositeConstruct):
    """Tolerance composition: fuzzy comparisons with uncertainty."""
```

#### Constructor

```python
def __init__(self, name: str, base_construct: str, tolerance_func: str = "kinda_float")
```

**Parameters:**
- `name` (str): Pattern name
- `base_construct` (str): Base comparison construct
- `tolerance_func` (str): Function to generate fuzzy tolerance

**Example:**
```python
tolerance_pattern = ToleranceComposition(
    "fuzzy_comparison",
    "comparison",
    "kinda_float"
)
```

### IshToleranceComposition

Specialized tolerance composition for ~ish construct implementation.

```python
class IshToleranceComposition(ToleranceComposition):
    """Specialized tolerance composition for ~ish patterns."""
```

#### Constructor

```python
def __init__(self, name: str, context: str)
```

**Parameters:**
- `name` (str): Pattern name
- `context` (str): Usage context ("comparison" or "assignment")

#### Methods

##### compose_comparison()

```python
def compose_comparison(self, left_val: float, right_val: float, tolerance_base: float = None) -> bool
```

**Parameters:**
- `left_val` (float): Left operand value
- `right_val` (float): Right operand value
- `tolerance_base` (float, optional): Base tolerance (default 0.1)

**Returns:** True if values are approximately equal

**Example:**
```python
ish_pattern = IshToleranceComposition("ish_comp", "comparison")
result = ish_pattern.compose_comparison(5.0, 5.1, 0.05)
```

##### compose_assignment()

```python
def compose_assignment(self, value: float, tolerance_base: float = None) -> float
```

**Parameters:**
- `value` (float): Base value for assignment
- `tolerance_base` (float, optional): Tolerance for variation

**Returns:** Fuzzy version of input value

## 🏭 Factory APIs

### CompositionPatternFactory

Factory class for creating common composition patterns.

```python
class CompositionPatternFactory:
    """Factory for creating standard composition patterns."""
```

#### Static Methods

##### create_union_pattern()

```python
@staticmethod
def create_union_pattern(name: str, constructs: List[str], bridge_probs: Dict[str, float] = None) -> UnionComposition
```

**Parameters:**
- `name` (str): Pattern name
- `constructs` (List[str]): Basic constructs to combine
- `bridge_probs` (Dict[str, float], optional): Bridge probabilities

**Returns:** UnionComposition instance

**Example:**
```python
sorta_like = CompositionPatternFactory.create_union_pattern(
    "sorta_like",
    ["sometimes", "maybe"],
    {"chaotic": 0.15}
)
```

##### create_threshold_pattern()

```python
@staticmethod
def create_threshold_pattern(name: str, constructs: List[str], threshold: int) -> ThresholdComposition
```

**Parameters:**
- `name` (str): Pattern name
- `constructs` (List[str]): Basic constructs to combine
- `threshold` (int): Required number of successes

**Returns:** ThresholdComposition instance

**Example:**
```python
consensus = CompositionPatternFactory.create_threshold_pattern(
    "consensus",
    ["sometimes", "maybe", "rarely"],
    2
)
```

##### create_tolerance_pattern()

```python
@staticmethod
def create_tolerance_pattern(name: str, base_construct: str, tolerance_func: str = "kinda_float") -> ToleranceComposition
```

**Parameters:**
- `name` (str): Pattern name
- `base_construct` (str): Base construct for comparison
- `tolerance_func` (str): Tolerance generation function

**Returns:** ToleranceComposition instance

### Convenience Functions

#### create_sorta_pattern()

```python
def create_sorta_pattern(name: str) -> UnionComposition
```

**Parameters:**
- `name` (str): Pattern name

**Returns:** Pre-configured ~sorta-like union composition

**Example:**
```python
from kinda.composition import create_sorta_pattern

my_sorta = create_sorta_pattern("custom_sorta")
```

#### create_ish_pattern()

```python
def create_ish_pattern(name: str, context: str = "comparison") -> IshToleranceComposition
```

**Parameters:**
- `name` (str): Pattern name
- `context` (str): Usage context

**Returns:** Pre-configured ~ish-like tolerance composition

#### create_consensus_pattern()

```python
def create_consensus_pattern(name: str, threshold: int = 2) -> ThresholdComposition
```

**Parameters:**
- `name` (str): Pattern name
- `threshold` (int): Consensus threshold

**Returns:** Pre-configured consensus threshold composition

## 🧪 Testing Framework APIs

### CompositionTestFramework

Framework for testing composition behavior and statistical validation.

```python
class CompositionTestFramework:
    """Framework for testing and validating composition behavior."""
```

#### Methods

##### validate_composition_probability()

```python
def validate_composition_probability(self, composite: CompositeConstruct, personality: str,
                                   expected_prob: float, tolerance: float = 0.05) -> bool
```

**Parameters:**
- `composite` (CompositeConstruct): Composition to test
- `personality` (str): Personality mode for testing
- `expected_prob` (float): Expected success probability
- `tolerance` (float): Acceptable variance from expected

**Returns:** True if composition meets probability expectations

**Example:**
```python
framework = get_test_framework()
passed = framework.validate_composition_probability(
    my_pattern, "reliable", 0.85, tolerance=0.05
)
```

##### run_statistical_analysis()

```python
def run_statistical_analysis(self, composite: CompositeConstruct, trials: int = 1000) -> Dict[str, Any]
```

**Parameters:**
- `composite` (CompositeConstruct): Composition to analyze
- `trials` (int): Number of test iterations

**Returns:** Dictionary with statistical analysis results

**Example:**
```python
stats = framework.run_statistical_analysis(my_pattern, trials=5000)
print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Standard deviation: {stats['std_dev']:.3f}")
```

##### benchmark_performance()

```python
def benchmark_performance(self, composite: CompositeConstruct, iterations: int = 10000) -> Dict[str, float]
```

**Parameters:**
- `composite` (CompositeConstruct): Composition to benchmark
- `iterations` (int): Number of benchmark iterations

**Returns:** Performance metrics dictionary

**Example:**
```python
perf_results = framework.benchmark_performance(my_pattern)
print(f"Mean execution time: {perf_results['mean_time']:.3f}ms")
```

### CompositionAssertion

Assertion utilities for composition testing.

```python
class CompositionAssertion:
    """Assertion utilities for composition testing."""
```

#### Static Methods

##### assert_statistical_equivalence()

```python
@staticmethod
def assert_statistical_equivalence(result1: List[bool], result2: List[bool], tolerance: float = 0.05) -> None
```

**Parameters:**
- `result1` (List[bool]): First set of results
- `result2` (List[bool]): Second set of results
- `tolerance` (float): Acceptable difference in success rates

**Raises:** AssertionError if results are not statistically equivalent

**Example:**
```python
legacy_results = [legacy_func() for _ in range(1000)]
composition_results = [composition_func() for _ in range(1000)]

CompositionAssertion.assert_statistical_equivalence(
    legacy_results, composition_results, tolerance=0.03
)
```

##### assert_personality_consistency()

```python
@staticmethod
def assert_personality_consistency(composite: CompositeConstruct, tolerance: float = 0.05) -> None
```

**Parameters:**
- `composite` (CompositeConstruct): Composition to test
- `tolerance` (float): Acceptable variance from target probabilities

**Raises:** AssertionError if personality behavior is inconsistent

### CompositionIntegrationTester

Integration testing utilities for framework components.

```python
class CompositionIntegrationTester:
    """Integration testing for composition framework components."""
```

#### Methods

##### test_framework_integration()

```python
def test_framework_integration(self) -> Dict[str, bool]
```

**Returns:** Dictionary of integration test results

**Example:**
```python
tester = CompositionIntegrationTester()
results = tester.test_framework_integration()

if all(results.values()):
    print("✅ All integration tests passed")
else:
    print("❌ Some integration tests failed")
```

## 🔍 Validation APIs

### DependencyValidator

Validates composition dependencies and circular references.

```python
class DependencyValidator:
    """Validates composition dependencies and detects circular references."""
```

#### Methods

##### validate_construct_dependencies()

```python
def validate_construct_dependencies(self, constructs: List[str]) -> bool
```

**Parameters:**
- `constructs` (List[str]): List of construct names to validate

**Returns:** True if all dependencies are available

##### detect_circular_dependencies()

```python
def detect_circular_dependencies(self, composite: CompositeConstruct) -> List[str]
```

**Parameters:**
- `composite` (CompositeConstruct): Composition to check

**Returns:** List of circular dependency chains found

**Example:**
```python
validator = DependencyValidator()
circular_deps = validator.detect_circular_dependencies(my_pattern)

if circular_deps:
    print(f"Circular dependencies found: {circular_deps}")
```

### PerformanceValidator

Validates performance characteristics of compositions.

```python
class PerformanceValidator:
    """Validates performance characteristics and overhead."""
```

#### Methods

##### validate_performance_target()

```python
def validate_performance_target(self, composite: CompositeConstruct,
                               baseline_func: Callable, target_overhead: float = 0.20) -> bool
```

**Parameters:**
- `composite` (CompositeConstruct): Composition to validate
- `baseline_func` (Callable): Baseline implementation for comparison
- `target_overhead` (float): Maximum acceptable overhead

**Returns:** True if performance target is met

**Example:**
```python
validator = PerformanceValidator()
meets_target = validator.validate_performance_target(
    my_composition, legacy_implementation, target_overhead=0.15
)
```

##### establish_performance_baseline()

```python
def establish_performance_baseline(self, func: Callable, iterations: int = 10000) -> Dict[str, float]
```

**Parameters:**
- `func` (Callable): Function to establish baseline for
- `iterations` (int): Number of benchmark iterations

**Returns:** Baseline performance metrics

## 🔧 Utility Functions

### Global Framework Functions

#### get_composition_engine()

```python
def get_composition_engine() -> CompositionEngine
```

**Returns:** Global CompositionEngine instance

**Example:**
```python
from kinda.composition import get_composition_engine

engine = get_composition_engine()
available_patterns = engine.list_composites()
```

#### get_test_framework()

```python
def get_test_framework() -> CompositionTestFramework
```

**Returns:** Global CompositionTestFramework instance

#### is_framework_ready()

```python
def is_framework_ready() -> bool
```

**Returns:** True if composition framework is initialized and ready

**Example:**
```python
if is_framework_ready():
    print("✅ Framework ready for use")
else:
    print("❌ Framework needs initialization")
```

#### initialize_framework()

```python
def initialize_framework() -> Tuple[CompositionEngine, CompositionTestFramework]
```

**Returns:** Tuple of (CompositionEngine, CompositionTestFramework)

**Example:**
```python
engine, test_framework = initialize_framework()
print("Framework initialized successfully")
```

#### validate_framework_installation()

```python
def validate_framework_installation() -> Dict[str, Any]
```

**Returns:** Dictionary with installation validation results

**Example:**
```python
validation = validate_framework_installation()
if validation['overall_status']:
    print("✅ Framework installation valid")
else:
    print(f"❌ Issues found: {validation}")
```

### Quick Composition Functions

#### quick_union_composition()

```python
def quick_union_composition(name: str, constructs: List[str], bridge_probs: dict = None) -> UnionComposition
```

**Parameters:**
- `name` (str): Pattern name
- `constructs` (List[str]): Basic constructs to combine
- `bridge_probs` (dict, optional): Bridge probabilities

**Returns:** UnionComposition registered with framework

**Example:**
```python
from kinda.composition import quick_union_composition

my_pattern = quick_union_composition(
    "quick_sorta",
    ["sometimes", "maybe"],
    {"chaotic": 0.2}
)
```

#### quick_threshold_composition()

```python
def quick_threshold_composition(name: str, constructs: List[str], threshold: float = 0.5) -> ThresholdComposition
```

#### quick_tolerance_composition()

```python
def quick_tolerance_composition(name: str, base_construct: str, tolerance_func: str = "kinda_float") -> ToleranceComposition
```

#### test_composition()

```python
def test_composition(composite: CompositeConstruct, personalities: List[str] = None, tolerance: float = 0.05) -> bool
```

**Parameters:**
- `composite` (CompositeConstruct): Composition to test
- `personalities` (List[str], optional): Personalities to test (default: all)
- `tolerance` (float): Statistical tolerance

**Returns:** True if composition passes all personality tests

**Example:**
```python
if test_composition(my_pattern, tolerance=0.03):
    print("✅ Composition validated across all personalities")
```

## 📊 Framework Status APIs

### get_framework_info()

```python
def get_framework_info() -> Dict[str, Any]
```

**Returns:** Framework information and capabilities

**Example:**
```python
info = get_framework_info()
print(f"Framework version: {info['version']}")
print(f"Components: {info['components']}")
```

### create_composition_example()

```python
def create_composition_example() -> CompositeConstruct
```

**Returns:** Example composition for demonstration

## 🚨 Error Handling

### Common Exceptions

#### CompositionError

```python
class CompositionError(Exception):
    """Base exception for composition framework errors."""
```

#### DependencyError

```python
class DependencyError(CompositionError):
    """Raised when composition dependencies are not available."""
```

#### ValidationError

```python
class ValidationError(CompositionError):
    """Raised when composition validation fails."""
```

#### PerformanceError

```python
class PerformanceError(CompositionError):
    """Raised when performance targets are not met."""
```

### Error Handling Patterns

```python
try:
    result = my_composition.compose(True)
except DependencyError as e:
    print(f"Missing dependencies: {e}")
    result = fallback_implementation()
except ValidationError as e:
    print(f"Validation failed: {e}")
    result = None
except PerformanceError as e:
    print(f"Performance target not met: {e}")
    result = my_composition.compose(True)  # Continue anyway
```

## 🎯 Usage Examples

### Complete Integration Example

```python
from kinda.composition import (
    get_composition_engine,
    CompositionPatternFactory,
    get_test_framework,
    quick_union_composition
)

# 1. Create custom composition
engine = get_composition_engine()
my_pattern = CompositionPatternFactory.create_union_pattern(
    "my_custom_sorta",
    ["sometimes", "maybe"],
    {"reliable": 0.0, "chaotic": 0.15}
)

# 2. Register with framework
engine.register_composite(my_pattern)

# 3. Test composition
test_framework = get_test_framework()
if test_framework.validate_composition_probability(my_pattern, "reliable", 0.95):
    print("✅ Composition validated")

# 4. Use composition
result = my_pattern.compose(True)
print(f"Composition result: {result}")

# 5. Get framework status
print(f"Available patterns: {engine.list_composites()}")
```

---

**API Reference**: ✅ Complete
**Framework Version**: 0.1.0
**Documentation Version**: 1.0.0

**Next**: [Best Practices & Troubleshooting](./best-practices.md) - Learn effective composition techniques