# Epic #127: Multi-Language Transpiler Infrastructure - Technical Specification

**Component**: Foundation transpiler infrastructure for v0.6.0 multi-language strategy
**Dependencies**: Python Enhancement Bridge architecture
**Target Languages**: Python (Epic #127), C (v0.6.0), MATLAB/Octave (v0.6.0)
**Design Philosophy**: Shared infrastructure, language-specific implementations

## 🎯 Architecture Overview

### Transpiler Framework Design Principles

1. **Shared Core, Specialized Targets**: Maximum code reuse across language implementations
2. **Construct-Centric**: Each kinda construct maps to language-specific implementations
3. **Personality Preservation**: Maintain personality system behavior across all languages
4. **Performance Optimization**: Language-specific optimizations without losing semantics
5. **Extensible Plugin System**: Easy addition of new language targets

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Kinda Source Parser                       │
│                  (AST Generation)                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                Transpiler Framework                          │
│                 (Core Engine)                               │
│  ┌─────────────┬─────────────┬─────────────┬──────────────┐ │
│  │ Construct   │ Personality │ Statistical │ Optimization │ │
│  │ Registry    │ Bridge      │ Framework   │ Passes       │ │
│  └─────────────┴─────────────┴─────────────┴──────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                Language Targets                              │
│  ┌─────────────┬─────────────┬─────────────┬──────────────┐ │
│  │   Python    │      C      │   MATLAB    │   Future     │ │
│  │ Enhancement │   Target    │  Target     │  Languages   │ │
│  │   Target    │             │             │              │ │
│  └─────────────┴─────────────┴─────────────┴──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Core Framework Components

### 1. Transpiler Engine
```python
# kinda/transpiler/engine.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class TranspilationPhase(Enum):
    PARSE = "parse"
    ANALYZE = "analyze"
    OPTIMIZE = "optimize"
    GENERATE = "generate"
    VALIDATE = "validate"

@dataclass
class TranspilationContext:
    """Context information for transpilation process."""
    source_language: str = "kinda"
    target_language: str
    personality_config: Optional[Dict[str, Any]] = None
    optimization_level: int = 1
    debug_mode: bool = False
    custom_options: Dict[str, Any] = None

class TranspilerEngine:
    """Core transpiler engine coordinating all phases."""

    def __init__(self):
        self.language_targets: Dict[str, 'LanguageTarget'] = {}
        self.construct_registry = ConstructRegistry()
        self.optimization_passes: List['OptimizationPass'] = []
        self.personality_bridge = PersonalityBridge()

    def register_target(self, target: 'LanguageTarget'):
        """Register a language target."""
        self.language_targets[target.language_name] = target

    def transpile(self, source: str, context: TranspilationContext) -> 'TranspileResult':
        """Main transpilation entry point."""
        try:
            # Phase 1: Parse kinda source to AST
            ast = self._parse_source(source, context)

            # Phase 2: Analyze and validate AST
            analyzed_ast = self._analyze_ast(ast, context)

            # Phase 3: Apply optimization passes
            optimized_ast = self._optimize_ast(analyzed_ast, context)

            # Phase 4: Generate target language code
            target = self.language_targets[context.target_language]
            generated_code = target.generate_code(optimized_ast, context)

            # Phase 5: Validate output
            validation_result = target.validate_code(generated_code, context)

            return TranspileResult(
                success=True,
                generated_code=generated_code,
                metadata=self._collect_metadata(ast, context),
                validation=validation_result
            )

        except TranspilationError as e:
            return TranspileResult(
                success=False,
                error=e,
                phase=e.phase,
                context=context
            )
```

### 2. Abstract Language Target Interface
```python
# kinda/transpiler/target.py

class LanguageTarget(ABC):
    """Abstract base class for all language targets."""

    @property
    @abstractmethod
    def language_name(self) -> str:
        """Unique identifier for this language target."""
        pass

    @property
    @abstractmethod
    def supported_constructs(self) -> List[str]:
        """List of kinda constructs supported by this target."""
        pass

    @property
    @abstractmethod
    def runtime_dependencies(self) -> List[str]:
        """External dependencies required for runtime execution."""
        pass

    @abstractmethod
    def generate_code(self, ast: 'KindaAST', context: TranspilationContext) -> str:
        """Generate target language code from kinda AST."""
        pass

    @abstractmethod
    def generate_runtime_helpers(self, constructs: List[str], context: TranspilationContext) -> str:
        """Generate runtime helper functions for used constructs."""
        pass

    @abstractmethod
    def validate_code(self, code: str, context: TranspilationContext) -> 'ValidationResult':
        """Validate generated code for correctness."""
        pass

    @abstractmethod
    def optimize_for_target(self, ast: 'KindaAST', context: TranspilationContext) -> 'KindaAST':
        """Apply language-specific optimizations."""
        pass

    def get_construct_implementation(self, construct_name: str) -> Optional['ConstructImplementation']:
        """Get language-specific implementation for a construct."""
        return self.construct_implementations.get(construct_name)

    def supports_construct(self, construct_name: str) -> bool:
        """Check if this target supports the given construct."""
        return construct_name in self.supported_constructs
```

### 3. Construct Registry System
```python
# kinda/transpiler/constructs.py

@dataclass
class ConstructImplementation:
    """Language-specific implementation of a kinda construct."""
    construct_name: str
    language_target: str
    template: str                    # Code template with placeholders
    runtime_dependencies: List[str]  # Required helper functions
    personality_scaling: bool = True # Whether construct respects personality
    complexity_score: int = 1        # For optimization decisions

class ConstructRegistry:
    """Central registry for all construct implementations across languages."""

    def __init__(self):
        self.implementations: Dict[str, Dict[str, ConstructImplementation]] = {}
        self.construct_metadata: Dict[str, ConstructMetadata] = {}

    def register_implementation(self, impl: ConstructImplementation):
        """Register a construct implementation for a language."""
        if impl.construct_name not in self.implementations:
            self.implementations[impl.construct_name] = {}
        self.implementations[impl.construct_name][impl.language_target] = impl

    def get_implementation(self, construct: str, target: str) -> Optional[ConstructImplementation]:
        """Get implementation for construct in target language."""
        return self.implementations.get(construct, {}).get(target)

    def get_all_constructs(self) -> List[str]:
        """Get list of all registered constructs."""
        return list(self.implementations.keys())

    def get_supported_targets(self, construct: str) -> List[str]:
        """Get list of targets that support the given construct."""
        return list(self.implementations.get(construct, {}).keys())

# Example construct implementations
PYTHON_SOMETIMES_IMPL = ConstructImplementation(
    construct_name="sometimes",
    language_target="python_enhanced",
    template="""
if chaos_random() < {personality_probability}:
{block_content}
{else_block}
""",
    runtime_dependencies=["chaos_random", "get_personality"],
    personality_scaling=True,
    complexity_score=2
)

C_SOMETIMES_IMPL = ConstructImplementation(
    construct_name="sometimes",
    language_target="c",
    template="""
if (kinda_random() < {personality_probability}) {{
{block_content}
}}
{else_block}
""",
    runtime_dependencies=["kinda_random", "kinda_personality_get_prob"],
    personality_scaling=True,
    complexity_score=1
)
```

### 4. Personality Bridge System
```python
# kinda/transpiler/personality.py

class PersonalityBridge:
    """Bridges personality system across language targets."""

    def __init__(self):
        self.personality_mappings: Dict[str, PersonalityMapping] = {}
        self.default_probabilities = PERSONALITY_PROFILES

    def get_construct_probability(self,
                                construct: str,
                                personality: str,
                                target_language: str) -> float:
        """Get personality-adjusted probability for construct in target language."""
        base_prob = self.default_probabilities[personality].get(construct, 0.5)
        language_adjustment = self._get_language_adjustment(target_language, construct)
        return min(1.0, max(0.0, base_prob * language_adjustment))

    def generate_personality_runtime(self, target_language: str) -> str:
        """Generate personality system runtime for target language."""
        mapping = self.personality_mappings.get(target_language)
        if not mapping:
            raise UnsupportedPersonalityTarget(target_language)

        return mapping.generate_runtime_code()

    def register_personality_mapping(self, mapping: 'PersonalityMapping'):
        """Register personality mapping for a language target."""
        self.personality_mappings[mapping.target_language] = mapping

@dataclass
class PersonalityMapping:
    """Maps personality system to specific language target."""
    target_language: str
    probability_function_template: str
    chaos_level_scaling: str
    seed_integration: str
    runtime_initialization: str

    def generate_runtime_code(self) -> str:
        """Generate complete personality runtime for target language."""
        return f"""
{self.runtime_initialization}

{self.probability_function_template}

{self.chaos_level_scaling}

{self.seed_integration}
"""
```

## 🎯 Language Target Implementations

### 1. Python Enhancement Target (Epic #127)
```python
# kinda/transpiler/targets/python_enhanced.py

class PythonEnhancementTarget(LanguageTarget):
    """Python enhancement target for seamless kinda construct injection."""

    language_name = "python_enhanced"
    supported_constructs = [
        "kinda_int", "kinda_float", "kinda_bool",
        "sometimes", "maybe", "probably", "rarely",
        "sorta_print", "ish_comparison", "ish_value",
        "assert_eventually", "assert_probability"
    ]
    runtime_dependencies = ["kinda"]

    def generate_code(self, ast: KindaAST, context: TranspilationContext) -> str:
        """Generate Python code with embedded kinda constructs."""
        # Use AST visitor pattern to transform nodes
        transformer = PythonASTTransformer(self, context)
        return transformer.transform(ast)

    def generate_runtime_helpers(self, constructs: List[str], context: TranspilationContext) -> str:
        """Generate Python runtime helpers."""
        return f"""
# Auto-generated kinda runtime helpers
import kinda
from kinda.personality import chaos_random, get_personality

{self._generate_construct_helpers(constructs)}
"""

    def _generate_construct_helpers(self, constructs: List[str]) -> str:
        """Generate helpers for specific constructs."""
        helpers = []
        for construct in constructs:
            impl = self.get_construct_implementation(construct)
            if impl and impl.template:
                helpers.append(self._render_template(impl))
        return "\n\n".join(helpers)
```

### 2. C Language Target (v0.6.0)
```python
# kinda/transpiler/targets/c.py

class CTarget(LanguageTarget):
    """C language target for performance-critical applications."""

    language_name = "c"
    supported_constructs = [
        "kinda_int", "kinda_float", "kinda_bool",
        "sometimes", "maybe", "probably", "rarely",
        # Note: Some constructs like sorta_print adapted for C
    ]
    runtime_dependencies = ["kinda_runtime.h", "libkinda.a"]

    def generate_code(self, ast: KindaAST, context: TranspilationContext) -> str:
        """Generate C code with kinda constructs."""
        includes = self._generate_includes()
        main_function = self._generate_main_function(ast)
        helper_functions = self._generate_helper_functions(ast.used_constructs)

        return f"""
{includes}

{helper_functions}

{main_function}
"""

    def generate_runtime_helpers(self, constructs: List[str], context: TranspilationContext) -> str:
        """Generate C runtime helpers."""
        return f"""
// Auto-generated kinda runtime for C
#include "kinda_runtime.h"

{self._generate_c_construct_helpers(constructs)}
"""

    def _generate_includes(self) -> str:
        return """
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>
#include "kinda_runtime.h"
"""
```

### 3. MATLAB/Octave Target (v0.6.0)
```python
# kinda/transpiler/targets/matlab.py

class MATLABTarget(LanguageTarget):
    """MATLAB/Octave target for scientific computing applications."""

    language_name = "matlab"
    supported_constructs = [
        "kinda_int", "kinda_float", "kinda_bool",
        "sometimes", "maybe", "probably", "rarely",
        "ish_comparison", "ish_value"
    ]
    runtime_dependencies = ["kinda_runtime.m"]

    def generate_code(self, ast: KindaAST, context: TranspilationContext) -> str:
        """Generate MATLAB/Octave code with kinda constructs."""
        function_header = self._generate_function_header(ast)
        initialization = self._generate_initialization()
        main_logic = self._transform_ast_to_matlab(ast)

        return f"""
{function_header}

{initialization}

{main_logic}

end
"""

    def generate_runtime_helpers(self, constructs: List[str], context: TranspilationContext) -> str:
        """Generate MATLAB runtime helpers."""
        return f"""
% Auto-generated kinda runtime for MATLAB/Octave
function kinda_runtime_init()
    {self._generate_matlab_construct_helpers(constructs)}
end
"""
```

## 🔄 Optimization Framework

### Optimization Pass System
```python
# kinda/transpiler/optimization.py

class OptimizationPass(ABC):
    """Abstract base class for optimization passes."""

    @property
    @abstractmethod
    def name(self) -> str: pass

    @property
    @abstractmethod
    def description(self) -> str: pass

    @abstractmethod
    def should_apply(self, ast: KindaAST, context: TranspilationContext) -> bool:
        """Determine if this optimization should be applied."""
        pass

    @abstractmethod
    def apply(self, ast: KindaAST, context: TranspilationContext) -> KindaAST:
        """Apply the optimization to the AST."""
        pass

class DeadCodeElimination(OptimizationPass):
    """Remove unreachable or unused code constructs."""

    name = "dead_code_elimination"
    description = "Remove unreachable kinda constructs and unused variables"

class ConstructInlining(OptimizationPass):
    """Inline simple constructs to reduce runtime overhead."""

    name = "construct_inlining"
    description = "Inline simple probabilistic constructs for performance"

class ProbabilityConstantFolding(OptimizationPass):
    """Optimize constant probability expressions."""

    name = "probability_folding"
    description = "Pre-calculate deterministic probability expressions"
```

## 📊 Performance Considerations

### Runtime Performance Targets
- **Python Enhancement**: < 20% overhead vs pure Python
- **C Target**: < 5% overhead vs equivalent deterministic C
- **MATLAB Target**: < 10% overhead vs native MATLAB

### Memory Usage Optimization
```python
# Memory-efficient construct storage
class ConstructCache:
    """Cache frequently used construct implementations."""

    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}

    def get_implementation(self, construct: str, target: str) -> ConstructImplementation:
        """Get cached implementation with LRU eviction."""
        key = f"{construct}:{target}"
        if key in self.cache:
            self.access_count[key] += 1
            return self.cache[key]

        # Cache miss - generate and store
        impl = self._generate_implementation(construct, target)
        if len(self.cache) >= self.max_size:
            self._evict_lru()

        self.cache[key] = impl
        self.access_count[key] = 1
        return impl
```

## 🧪 Testing Strategy

### Multi-Language Test Framework
```python
# kinda/transpiler/testing/framework.py

class MultiLanguageTestSuite:
    """Test framework for validating transpiler across languages."""

    def __init__(self):
        self.test_cases = []
        self.language_validators = {}

    def add_cross_language_test(self, test_case: CrossLanguageTestCase):
        """Add test case that validates behavior across multiple languages."""
        self.test_cases.append(test_case)

    def run_compatibility_tests(self) -> TestResults:
        """Run tests to ensure consistent behavior across languages."""
        results = TestResults()

        for test_case in self.test_cases:
            # Generate code for each target language
            outputs = {}
            for target in test_case.target_languages:
                transpiler = self.get_transpiler_for_target(target)
                outputs[target] = transpiler.transpile(test_case.kinda_source)

            # Validate semantic equivalence
            semantic_result = self._validate_semantic_equivalence(outputs, test_case)
            results.add_result(test_case.name, semantic_result)

        return results

@dataclass
class CrossLanguageTestCase:
    """Test case that validates behavior across multiple languages."""
    name: str
    kinda_source: str
    target_languages: List[str]
    expected_behavior: Dict[str, Any]
    tolerance: float = 0.1  # For probabilistic behavior validation
```

## 🔐 Security Considerations

### Code Generation Security
```python
# kinda/transpiler/security.py

class TranspilerSecurityValidator:
    """Validates security of generated code across languages."""

    def __init__(self):
        self.dangerous_patterns = {
            'c': [r'system\s*\(', r'exec\s*\(', r'gets\s*\('],
            'python': [r'exec\s*\(', r'eval\s*\(', r'__import__\s*\('],
            'matlab': [r'system\s*\(', r'eval\s*\(']
        }

    def validate_generated_code(self, code: str, target_language: str) -> SecurityValidationResult:
        """Validate that generated code doesn't contain security vulnerabilities."""
        patterns = self.dangerous_patterns.get(target_language, [])
        violations = []

        for pattern in patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                violations.append(SecurityViolation(
                    pattern=pattern,
                    line=self._get_line_number(code, match.start()),
                    severity='HIGH'
                ))

        return SecurityValidationResult(
            is_safe=len(violations) == 0,
            violations=violations
        )
```

## 📋 Quality Gates for Implementation

### Architecture Validation
- [ ] ✅ All language targets implement required interface methods
- [ ] ✅ Construct registry supports all existing kinda constructs
- [ ] ✅ Personality bridge maintains consistent behavior across languages
- [ ] ✅ Optimization framework provides measurable performance improvements

### Implementation Validation
- [ ] ✅ Python enhancement target generates valid, executable Python code
- [ ] ✅ C target generates compilable C code with runtime library
- [ ] ✅ MATLAB target generates functional MATLAB/Octave scripts
- [ ] ✅ Cross-language test suite passes semantic equivalence tests

### Performance Validation
- [ ] ✅ Runtime overhead targets met for all language targets
- [ ] ✅ Memory usage within acceptable bounds
- [ ] ✅ Optimization passes provide measurable benefits
- [ ] ✅ Cache hit rates > 80% for construct implementations

### Security Validation
- [ ] ✅ Generated code passes security validation for all targets
- [ ] ✅ No injection vulnerabilities in code generation
- [ ] ✅ Runtime libraries follow security best practices
- [ ] ✅ Input validation prevents malicious kinda source exploitation

---

**Status**: Transpiler Infrastructure Specification Complete
**Next Phase**: Detailed component implementation by Kinda-Lang Coder
**Foundation Ready**: Architecture supports v0.6.0 multi-language strategy