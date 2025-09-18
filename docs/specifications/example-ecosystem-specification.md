# 🔧 Example Ecosystem Implementation Specification

## 🎯 Overview

This specification provides detailed implementation requirements for the Kinda-Lang Example Ecosystem, designed to systematically address broken examples (Issues #86, #87, #88, #96) and establish a maintainable, high-quality example library for v0.5.1.

## 🚨 Critical Issues to Resolve

### Immediate Fixes Required

#### Issue #86: demo_v4_features.knda Syntax Error
**Location**: `/demo_v4_features.knda:32-34`
**Problem**: Invalid syntax for conditional structure
```kinda
# BROKEN (current):
~sometimes (fuzzy_decision) {
    ~sorta print("The fuzzy decision was kinda True!")
} {
    ~sorta print("The fuzzy decision was kinda False!")
}
```

**Fix Required**: Proper conditional syntax
```kinda
# FIXED (required):
~sometimes (fuzzy_decision) {
    ~sorta print("The fuzzy decision was kinda True!")
}
```

#### Issue #96: Skipped Examples Instead of Fixes
**Current Skip List** (from `tests/python/test_all_examples.py`):
```python
skip_files = {
    "chaos_arena2_complete.py.knda",  # Multi-line sorta_print issue
}
```

**Action Required**: Fix all skipped examples instead of avoiding them

#### Issue #87: Missing CI Testing for Demo Files
**Current State**: Demo files not tested in CI
**Required**: Complete CI integration for all demo and example files

#### Issue #88: Incomplete v0.4.0 Documentation
**Missing Features**:
- `~probably` (70% conditional) documentation
- `~rarely` (15% conditional) documentation
- `~kinda bool` fuzzy boolean documentation
- Chaos level and mood parameter documentation

## 📁 Example Ecosystem Structure

### 1. Directory Organization
```
examples/
├── 01-beginner/          # 🟢 Basic syntax and concepts
│   ├── hello.knda
│   ├── simple-variables.knda
│   ├── basic-probability.knda
│   └── first-chaos.knda
├── 02-intermediate/      # 🟡 Multiple constructs and logic
│   ├── conditional-logic.knda
│   ├── fuzzy-loops.knda
│   ├── chaos-control.knda
│   └── composition.knda
├── 03-advanced/          # 🟠 Complex patterns and validation
│   ├── statistical-testing.knda
│   ├── performance-patterns.knda
│   ├── integration-examples.knda
│   └── enterprise-patterns.knda
├── 04-real-world/        # 🔴 Production-ready patterns
│   ├── testing-frameworks.knda
│   ├── monitoring-systems.knda
│   ├── fault-tolerance.knda
│   └── deployment-patterns.knda
├── language-integration/
│   ├── python/          # Python integration examples
│   │   ├── basic-integration.py.knda
│   │   ├── statistical-testing.py.knda
│   │   └── chaos-arena.py.knda
│   └── c/              # C integration examples
│       ├── simple-example.c.knda
│       └── monte-carlo-pi.c.knda
├── probabilistic-control-flow/  # Special category for complex patterns
│   ├── README.md
│   ├── fuzzy-batch-processing.knda
│   ├── chaos-testing-framework.knda
│   └── [existing examples...]
└── deprecated/         # Moved from root for cleanup
    ├── demo_v4_features.knda (after fixing)
    └── simple_v4_demo.knda
```

### 2. Example Metadata System

#### Example Header Standard
```kinda
#!/usr/bin/env kinda
# 🎲 [Example Title] - [Difficulty: 🟢🟡🟠🔴]
#
# Category: [Core Syntax|Probabilistic Logic|Statistical Testing|Integration|Real-World]
# Concepts: [List of kinda constructs demonstrated]
# Prerequisites: [Required knowledge or previous examples]
# Expected Runtime: [Typical execution time]
#
# Purpose:
# [1-2 sentence description of what this example demonstrates]
#
# Learning Objectives:
# - [Specific skill or concept user will learn]
# - [Additional learning objective]
#
# Expected Behavior:
# [Description of what users should observe, including probabilistic variations]
#
# Chaos Level Impact:
# - Level 1-2: [How behavior changes with minimal chaos]
# - Level 5-6: [Standard chaos behavior]
# - Level 9-10: [Maximum chaos behavior]
#
# Usage:
# kinda run [filename] --seed 42 --chaos-level 5

# Example implementation with comprehensive inline comments
[implementation]
```

#### Example Quality Standards
```yaml
example_quality_standards:
  syntax:
    must_parse: true
    must_execute: true
    error_tolerance: 0

  documentation:
    header_required: true
    inline_comments: extensive
    learning_objectives: required
    expected_behavior: documented

  testing:
    ci_validation: required
    multiple_chaos_levels: [1, 5, 10]
    multiple_seeds: [42, 123, 999]
    execution_timeout: 30_seconds

  categorization:
    difficulty_level: required
    concept_tags: required
    prerequisites: documented
    learning_path: defined
```

## 🧪 Validation Framework Implementation

### 1. Example Validator Class

```python
# File: kinda/validation/example_validator.py

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import subprocess
import time
import re

class DifficultyLevel(Enum):
    BEGINNER = "🟢"
    INTERMEDIATE = "🟡"
    ADVANCED = "🟠"
    EXPERT = "🔴"

class ExampleCategory(Enum):
    CORE_SYNTAX = "Core Syntax"
    PROBABILISTIC_LOGIC = "Probabilistic Logic"
    STATISTICAL_TESTING = "Statistical Testing"
    INTEGRATION = "Integration"
    REAL_WORLD = "Real-World"

@dataclass
class ExampleMetadata:
    title: str
    difficulty: DifficultyLevel
    category: ExampleCategory
    concepts: List[str]
    prerequisites: List[str]
    expected_runtime: float
    learning_objectives: List[str]

@dataclass
class ValidationResult:
    file_path: Path
    syntax_valid: bool
    execution_successful: bool
    statistical_valid: bool
    documentation_complete: bool
    metadata_valid: bool
    execution_time: float
    error_messages: List[str]
    warnings: List[str]

class ExampleValidator:
    """Comprehensive validation system for kinda-lang examples."""

    def __init__(self,
                 chaos_levels: List[int] = [1, 5, 10],
                 seeds: List[int] = [42, 123, 999],
                 timeout: float = 30.0):
        self.chaos_levels = chaos_levels
        self.seeds = seeds
        self.timeout = timeout

    def validate_example(self, file_path: Path) -> ValidationResult:
        """Validate a single example file completely."""
        result = ValidationResult(
            file_path=file_path,
            syntax_valid=False,
            execution_successful=False,
            statistical_valid=False,
            documentation_complete=False,
            metadata_valid=False,
            execution_time=0.0,
            error_messages=[],
            warnings=[]
        )

        # 1. Syntax validation
        result.syntax_valid = self._validate_syntax(file_path, result)

        # 2. Metadata validation
        result.metadata_valid = self._validate_metadata(file_path, result)

        # 3. Documentation validation
        result.documentation_complete = self._validate_documentation(file_path, result)

        # 4. Execution validation
        if result.syntax_valid:
            result.execution_successful = self._validate_execution(file_path, result)

        # 5. Statistical validation (for probabilistic examples)
        if result.execution_successful:
            result.statistical_valid = self._validate_statistical_behavior(file_path, result)

        return result

    def _validate_syntax(self, file_path: Path, result: ValidationResult) -> bool:
        """Validate that the example parses correctly."""
        try:
            # Use kinda parser to validate syntax
            cmd = ["kinda", "parse", str(file_path)]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if proc.returncode != 0:
                result.error_messages.append(f"Syntax error: {proc.stderr}")
                return False

            return True
        except subprocess.TimeoutExpired:
            result.error_messages.append("Syntax validation timeout")
            return False
        except Exception as e:
            result.error_messages.append(f"Syntax validation error: {e}")
            return False

    def _validate_execution(self, file_path: Path, result: ValidationResult) -> bool:
        """Validate that the example executes successfully across chaos levels and seeds."""
        success_count = 0
        total_tests = len(self.chaos_levels) * len(self.seeds)

        for chaos_level in self.chaos_levels:
            for seed in self.seeds:
                start_time = time.time()

                try:
                    cmd = [
                        "kinda", "run", str(file_path),
                        "--chaos-level", str(chaos_level),
                        "--seed", str(seed)
                    ]

                    proc = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=self.timeout
                    )

                    execution_time = time.time() - start_time
                    result.execution_time = max(result.execution_time, execution_time)

                    if proc.returncode == 0:
                        success_count += 1
                    else:
                        result.error_messages.append(
                            f"Execution failed (chaos={chaos_level}, seed={seed}): {proc.stderr}"
                        )

                except subprocess.TimeoutExpired:
                    result.error_messages.append(
                        f"Execution timeout (chaos={chaos_level}, seed={seed})"
                    )
                except Exception as e:
                    result.error_messages.append(
                        f"Execution error (chaos={chaos_level}, seed={seed}): {e}"
                    )

        # Require 100% success rate
        success_rate = success_count / total_tests
        if success_rate < 1.0:
            result.error_messages.append(
                f"Execution success rate {success_rate:.1%} below required 100%"
            )

        return success_rate == 1.0

    def _validate_statistical_behavior(self, file_path: Path, result: ValidationResult) -> bool:
        """Validate probabilistic behavior for examples with statistical constructs."""
        # Read file content to detect probabilistic constructs
        content = file_path.read_text()

        probabilistic_constructs = [
            "~sometimes", "~maybe", "~probably", "~rarely",
            "~assert_probability", "~assert_eventually"
        ]

        has_probabilistic = any(construct in content for construct in probabilistic_constructs)

        if not has_probabilistic:
            return True  # No statistical validation needed

        # For probabilistic examples, run statistical validation
        try:
            # Run example multiple times to validate statistical behavior
            cmd = [
                "kinda", "run", str(file_path),
                "--statistical-validation",
                "--samples", "100"
            ]

            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if proc.returncode != 0:
                result.error_messages.append(f"Statistical validation failed: {proc.stderr}")
                return False

            return True

        except Exception as e:
            result.error_messages.append(f"Statistical validation error: {e}")
            return False

    def _validate_metadata(self, file_path: Path, result: ValidationResult) -> bool:
        """Validate that example has complete metadata."""
        content = file_path.read_text()

        required_metadata = [
            r"# 🎲 .+ - \[Difficulty: [🟢🟡🟠🔴]\]",
            r"# Category:",
            r"# Concepts:",
            r"# Purpose:",
            r"# Learning Objectives:",
            r"# Expected Behavior:",
            r"# Usage:"
        ]

        missing_metadata = []
        for pattern in required_metadata:
            if not re.search(pattern, content, re.MULTILINE):
                missing_metadata.append(pattern)

        if missing_metadata:
            result.error_messages.append(f"Missing metadata: {missing_metadata}")
            return False

        return True

    def _validate_documentation(self, file_path: Path, result: ValidationResult) -> bool:
        """Validate documentation quality and completeness."""
        content = file_path.read_text()

        # Check for inline comments
        code_lines = [line for line in content.split('\n')
                     if line.strip() and not line.strip().startswith('#')]

        if len(code_lines) > 5:  # For non-trivial examples
            comment_lines = [line for line in content.split('\n')
                           if '#' in line and not line.strip().startswith('#!/')]

            comment_ratio = len(comment_lines) / len(code_lines)
            if comment_ratio < 0.3:  # At least 30% comment-to-code ratio
                result.warnings.append("Low comment-to-code ratio, consider adding more explanations")

        return True  # Documentation validation is mostly warnings for now

class ExampleCatalog:
    """Manage and organize the complete example catalog."""

    def __init__(self, examples_dir: Path):
        self.examples_dir = examples_dir
        self._examples_cache: Dict[Path, ExampleMetadata] = {}

    def scan_examples(self) -> List[Path]:
        """Scan and return all example files in the catalog."""
        return list(self.examples_dir.rglob("*.knda"))

    def get_examples_by_difficulty(self, difficulty: DifficultyLevel) -> List[Path]:
        """Get examples filtered by difficulty level."""
        examples = []
        for example_file in self.scan_examples():
            metadata = self.get_example_metadata(example_file)
            if metadata and metadata.difficulty == difficulty:
                examples.append(example_file)
        return examples

    def get_examples_by_category(self, category: ExampleCategory) -> List[Path]:
        """Get examples filtered by category."""
        examples = []
        for example_file in self.scan_examples():
            metadata = self.get_example_metadata(example_file)
            if metadata and metadata.category == category:
                examples.append(example_file)
        return examples

    def get_example_metadata(self, file_path: Path) -> Optional[ExampleMetadata]:
        """Extract metadata from example file."""
        if file_path in self._examples_cache:
            return self._examples_cache[file_path]

        try:
            content = file_path.read_text()

            # Parse metadata from header comments
            title_match = re.search(r"# 🎲 (.+) - \[Difficulty: ([🟢🟡🟠🔴])\]", content)
            if not title_match:
                return None

            title = title_match.group(1)
            difficulty_symbol = title_match.group(2)

            # Map symbols to enum
            difficulty_map = {
                "🟢": DifficultyLevel.BEGINNER,
                "🟡": DifficultyLevel.INTERMEDIATE,
                "🟠": DifficultyLevel.ADVANCED,
                "🔴": DifficultyLevel.EXPERT
            }

            difficulty = difficulty_map.get(difficulty_symbol)
            if not difficulty:
                return None

            # Extract other metadata
            category_match = re.search(r"# Category: (.+)", content)
            category_str = category_match.group(1) if category_match else ""

            # Map category string to enum
            category_map = {
                "Core Syntax": ExampleCategory.CORE_SYNTAX,
                "Probabilistic Logic": ExampleCategory.PROBABILISTIC_LOGIC,
                "Statistical Testing": ExampleCategory.STATISTICAL_TESTING,
                "Integration": ExampleCategory.INTEGRATION,
                "Real-World": ExampleCategory.REAL_WORLD
            }

            category = category_map.get(category_str, ExampleCategory.CORE_SYNTAX)

            # Extract concepts, prerequisites, objectives
            concepts = self._extract_list_metadata(content, "# Concepts:")
            prerequisites = self._extract_list_metadata(content, "# Prerequisites:")
            learning_objectives = self._extract_list_metadata(content, "# Learning Objectives:")

            # Extract expected runtime
            runtime_match = re.search(r"# Expected Runtime: (.+)", content)
            expected_runtime = 30.0  # Default
            if runtime_match:
                runtime_str = runtime_match.group(1)
                # Parse various formats like "5 seconds", "1.5s", "30 sec"
                runtime_number = re.search(r"(\d+(?:\.\d+)?)", runtime_str)
                if runtime_number:
                    expected_runtime = float(runtime_number.group(1))

            metadata = ExampleMetadata(
                title=title,
                difficulty=difficulty,
                category=category,
                concepts=concepts,
                prerequisites=prerequisites,
                expected_runtime=expected_runtime,
                learning_objectives=learning_objectives
            )

            self._examples_cache[file_path] = metadata
            return metadata

        except Exception:
            return None

    def _extract_list_metadata(self, content: str, prefix: str) -> List[str]:
        """Extract list-style metadata from content."""
        items = []
        lines = content.split('\n')

        start_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith(prefix):
                start_idx = i
                break

        if start_idx is None:
            return items

        # Look for list items after the prefix
        for i in range(start_idx + 1, len(lines)):
            line = lines[i].strip()
            if line.startswith('# -') or line.startswith('#   -'):
                item = line.replace('# -', '').replace('#   -', '').strip()
                items.append(item)
            elif line.startswith('#') and not line.startswith('# '):
                break  # Hit next section
            elif not line.startswith('#'):
                break  # Hit code section

        return items

class ValidationReport:
    """Generate comprehensive validation reports."""

    def __init__(self, results: List[ValidationResult]):
        self.results = results

    def generate_summary(self) -> Dict:
        """Generate validation summary statistics."""
        total_examples = len(self.results)
        syntax_valid = sum(1 for r in self.results if r.syntax_valid)
        execution_successful = sum(1 for r in self.results if r.execution_successful)
        statistical_valid = sum(1 for r in self.results if r.statistical_valid)
        documentation_complete = sum(1 for r in self.results if r.documentation_complete)
        metadata_valid = sum(1 for r in self.results if r.metadata_valid)

        failed_examples = [r for r in self.results
                          if not (r.syntax_valid and r.execution_successful)]

        return {
            "total_examples": total_examples,
            "syntax_success_rate": syntax_valid / total_examples,
            "execution_success_rate": execution_successful / total_examples,
            "statistical_success_rate": statistical_valid / total_examples,
            "documentation_success_rate": documentation_complete / total_examples,
            "metadata_success_rate": metadata_valid / total_examples,
            "failed_examples": [str(r.file_path) for r in failed_examples],
            "error_summary": self._categorize_errors()
        }

    def _categorize_errors(self) -> Dict[str, int]:
        """Categorize and count error types."""
        error_categories = {}

        for result in self.results:
            for error in result.error_messages:
                if "syntax" in error.lower():
                    category = "syntax_errors"
                elif "timeout" in error.lower():
                    category = "timeout_errors"
                elif "execution" in error.lower():
                    category = "execution_errors"
                elif "statistical" in error.lower():
                    category = "statistical_errors"
                else:
                    category = "other_errors"

                error_categories[category] = error_categories.get(category, 0) + 1

        return error_categories

    def generate_detailed_report(self) -> str:
        """Generate detailed markdown report."""
        summary = self.generate_summary()

        report = f"""# Example Validation Report

## Summary
- **Total Examples**: {summary['total_examples']}
- **Syntax Success Rate**: {summary['syntax_success_rate']:.1%}
- **Execution Success Rate**: {summary['execution_success_rate']:.1%}
- **Statistical Success Rate**: {summary['statistical_success_rate']:.1%}
- **Documentation Success Rate**: {summary['documentation_success_rate']:.1%}
- **Metadata Success Rate**: {summary['metadata_success_rate']:.1%}

## Failed Examples
"""

        for failed_file in summary['failed_examples']:
            result = next(r for r in self.results if str(r.file_path) == failed_file)
            report += f"\n### {failed_file}\n"
            report += f"- Syntax Valid: {result.syntax_valid}\n"
            report += f"- Execution Successful: {result.execution_successful}\n"
            report += f"- Statistical Valid: {result.statistical_valid}\n"
            report += f"- Documentation Complete: {result.documentation_complete}\n"
            report += f"- Metadata Valid: {result.metadata_valid}\n"

            if result.error_messages:
                report += "\n**Errors:**\n"
                for error in result.error_messages:
                    report += f"- {error}\n"

            if result.warnings:
                report += "\n**Warnings:**\n"
                for warning in result.warnings:
                    report += f"- {warning}\n"

        report += f"\n## Error Categories\n"
        for category, count in summary['error_summary'].items():
            report += f"- **{category}**: {count}\n"

        return report
```

### 2. CI Integration Implementation

```yaml
# File: .github/workflows/examples-validation.yml

name: Examples Validation

on:
  push:
    branches: [ main, dev ]
    paths:
      - 'examples/**'
      - 'demo*.knda'
      - 'simple*.knda'
  pull_request:
    branches: [ main, dev ]
    paths:
      - 'examples/**'
      - 'demo*.knda'
      - 'simple*.knda'

jobs:
  validate-examples:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11, 3.12]
        chaos-level: [1, 5, 10]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest pytest-cov

    - name: Validate demo files
      run: |
        echo "Validating demo files..."
        for demo in *.knda; do
          if [ -f "$demo" ]; then
            echo "Testing $demo with chaos level ${{ matrix.chaos-level }}"
            timeout 30s kinda run "$demo" --chaos-level ${{ matrix.chaos-level }} --seed 42 || {
              echo "FAILED: $demo"
              exit 1
            }
          fi
        done

    - name: Run example validation framework
      run: |
        python -m kinda.validation.example_validator examples/ --chaos-levels 1,5,10 --seeds 42,123,999

    - name: Generate validation report
      run: |
        python -m kinda.validation.generate_report examples/ > example_validation_report.md

    - name: Upload validation report
      uses: actions/upload-artifact@v3
      with:
        name: validation-report-py${{ matrix.python-version }}-chaos${{ matrix.chaos-level }}
        path: example_validation_report.md

  example-organization-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Check example organization
      run: |
        # Verify examples are properly categorized
        python -c "
        from pathlib import Path
        import sys

        examples_dir = Path('examples')
        required_dirs = ['01-beginner', '02-intermediate', '03-advanced', '04-real-world']
        missing_dirs = []

        for dir_name in required_dirs:
            if not (examples_dir / dir_name).exists():
                missing_dirs.append(dir_name)

        if missing_dirs:
            print(f'Missing required directories: {missing_dirs}')
            sys.exit(1)

        print('Example organization validation passed')
        "

    - name: Validate example metadata
      run: |
        python -c "
        from pathlib import Path
        import re
        import sys

        examples_dir = Path('examples')
        issues = []

        for example_file in examples_dir.rglob('*.knda'):
            content = example_file.read_text()

            # Check for required metadata
            if not re.search(r'# 🎲 .+ - \[Difficulty: [🟢🟡🟠🔴]\]', content):
                issues.append(f'{example_file}: Missing title/difficulty header')

            if not re.search(r'# Category:', content):
                issues.append(f'{example_file}: Missing category')

            if not re.search(r'# Purpose:', content):
                issues.append(f'{example_file}: Missing purpose')

        if issues:
            print('Example metadata issues:')
            for issue in issues:
                print(f'  - {issue}')
            sys.exit(1)

        print('Example metadata validation passed')
        "
```

### 3. Example Migration and Repair Specifications

#### Priority 1: Critical Fixes

**demo_v4_features.knda** - Fix syntax error
```kinda
# Current broken syntax (lines 30-34):
~kinda bool fuzzy_decision = True
~sometimes (fuzzy_decision) {
    ~sorta print("The fuzzy decision was kinda True!")
} {
    ~sorta print("The fuzzy decision was kinda False!")
}

# Fix required:
~kinda bool fuzzy_decision = True
~sometimes (fuzzy_decision) {
    ~sorta print("The fuzzy decision was kinda True!")
}
# Note: else blocks are not currently supported in ~sometimes
```

**chaos_arena2_complete.py.knda** - Fix multi-line sorta_print
```kinda
# Current broken pattern:
~sorta print("""
Multi-line
String
""")

# Fix to:
~sorta print("Multi-line content in single line format")
# Or:
~sorta print("Line 1")
~sorta print("Line 2")
~sorta print("Line 3")
```

#### Priority 2: Example Reorganization

**Move existing examples to appropriate directories**:

1. **Beginner Examples** (move to `examples/01-beginner/`):
   - `hello.knda` → `01-beginner/hello.knda`
   - Simple single-construct examples

2. **Intermediate Examples** (move to `examples/02-intermediate/`):
   - Multi-construct examples
   - Conditional logic examples

3. **Advanced Examples** (move to `examples/03-advanced/`):
   - Statistical testing examples
   - Complex probabilistic patterns

4. **Real-World Examples** (move to `examples/04-real-world/`):
   - Production-ready patterns
   - Integration examples

#### Priority 3: New Example Creation

**Required new examples** to complete the ecosystem:

```kinda
# examples/01-beginner/hello.knda
#!/usr/bin/env kinda
# 🎲 Hello Kinda World - [Difficulty: 🟢]
#
# Category: Core Syntax
# Concepts: ~sorta print, basic fuzzy output
# Prerequisites: None (first example)
# Expected Runtime: 2 seconds
#
# Purpose:
# Introduces users to kinda-lang with the most basic fuzzy construct.
#
# Learning Objectives:
# - Understand that kinda constructs behave probabilistically
# - Observe ~sorta print's 80% success rate
# - Experience controlled randomness in action
#
# Expected Behavior:
# Usually prints "Hello, kinda world!" but sometimes shows "[shrug]"
# The exact behavior depends on chaos level and random seed.
#
# Chaos Level Impact:
# - Level 1-2: Prints message almost always (95%+ success rate)
# - Level 5-6: Standard 80% print success rate
# - Level 9-10: More unpredictable, lower success rate (60-70%)
#
# Usage:
# kinda run examples/01-beginner/hello.knda --seed 42 --chaos-level 5

~sorta print("Hello, kinda world!")  # 80% chance to print
~sorta print("Welcome to controlled chaos!")  # Another 80% chance
~sorta print("This might not appear every time...")  # You get the idea
```

### 4. Testing Integration Specifications

#### Example Test Suite Structure

```python
# File: tests/examples/test_example_ecosystem.py

import pytest
from pathlib import Path
from kinda.validation.example_validator import ExampleValidator, ValidationResult
from kinda.validation.example_validator import ExampleCatalog, DifficultyLevel, ExampleCategory

class TestExampleEcosystem:
    """Comprehensive test suite for the example ecosystem."""

    @pytest.fixture
    def examples_dir(self):
        return Path(__file__).parent.parent.parent / "examples"

    @pytest.fixture
    def validator(self):
        return ExampleValidator(
            chaos_levels=[1, 5, 10],
            seeds=[42, 123, 999],
            timeout=30.0
        )

    @pytest.fixture
    def catalog(self, examples_dir):
        return ExampleCatalog(examples_dir)

    def test_all_examples_validate_successfully(self, examples_dir, validator):
        """Test that all examples pass validation."""
        example_files = list(examples_dir.rglob("*.knda"))
        assert len(example_files) > 0, "No example files found"

        failed_examples = []

        for example_file in example_files:
            result = validator.validate_example(example_file)

            if not (result.syntax_valid and result.execution_successful):
                failed_examples.append((example_file, result))

        if failed_examples:
            failure_report = "\n".join([
                f"{file}: {', '.join(result.error_messages)}"
                for file, result in failed_examples
            ])
            pytest.fail(f"Failed examples:\n{failure_report}")

    def test_example_directory_structure(self, examples_dir):
        """Test that examples are properly organized."""
        required_dirs = [
            "01-beginner",
            "02-intermediate",
            "03-advanced",
            "04-real-world",
            "language-integration/python",
            "language-integration/c"
        ]

        for dir_name in required_dirs:
            dir_path = examples_dir / dir_name
            assert dir_path.exists(), f"Required directory missing: {dir_name}"
            assert dir_path.is_dir(), f"Path exists but is not directory: {dir_name}"

    def test_beginner_examples_meet_standards(self, catalog):
        """Test that beginner examples are appropriate for new users."""
        beginner_examples = catalog.get_examples_by_difficulty(DifficultyLevel.BEGINNER)

        assert len(beginner_examples) >= 5, "Need at least 5 beginner examples"

        for example_file in beginner_examples:
            metadata = catalog.get_example_metadata(example_file)

            # Beginner examples should have minimal prerequisites
            assert len(metadata.prerequisites) <= 1, f"Too many prerequisites for beginner: {example_file}"

            # Should have clear learning objectives
            assert len(metadata.learning_objectives) >= 1, f"Missing learning objectives: {example_file}"

            # Should have reasonable runtime
            assert metadata.expected_runtime <= 30.0, f"Runtime too long for beginner: {example_file}"

    def test_example_metadata_completeness(self, catalog):
        """Test that all examples have complete metadata."""
        all_examples = catalog.scan_examples()

        for example_file in all_examples:
            metadata = catalog.get_example_metadata(example_file)
            assert metadata is not None, f"Could not parse metadata: {example_file}"

            assert metadata.title, f"Missing title: {example_file}"
            assert metadata.difficulty, f"Missing difficulty: {example_file}"
            assert metadata.category, f"Missing category: {example_file}"
            assert metadata.concepts, f"Missing concepts: {example_file}"
            assert metadata.learning_objectives, f"Missing learning objectives: {example_file}"

    def test_no_skipped_examples_in_test_suite(self):
        """Test that we don't skip examples instead of fixing them."""
        test_file = Path(__file__).parent.parent / "python" / "test_all_examples.py"

        if test_file.exists():
            content = test_file.read_text()

            # Check for skip patterns
            skip_patterns = [
                "pytest.skip",
                "skip_files",
                "@pytest.mark.skip",
                "SKIP"
            ]

            for pattern in skip_patterns:
                assert pattern not in content, f"Found skip pattern '{pattern}' in test file. Fix examples instead of skipping!"

    def test_demo_files_execute_successfully(self, validator):
        """Test that root-level demo files work correctly."""
        project_root = Path(__file__).parent.parent.parent
        demo_files = list(project_root.glob("*demo*.knda"))

        assert len(demo_files) > 0, "No demo files found"

        for demo_file in demo_files:
            result = validator.validate_example(demo_file)

            assert result.syntax_valid, f"Demo file has syntax errors: {demo_file}\nErrors: {result.error_messages}"
            assert result.execution_successful, f"Demo file execution failed: {demo_file}\nErrors: {result.error_messages}"

    def test_statistical_examples_validate_correctly(self, examples_dir, validator):
        """Test that examples with statistical constructs validate properly."""
        statistical_examples = []

        # Find examples with statistical constructs
        for example_file in examples_dir.rglob("*.knda"):
            content = example_file.read_text()
            if any(construct in content for construct in ["~assert_probability", "~assert_eventually", "statistical"]):
                statistical_examples.append(example_file)

        assert len(statistical_examples) > 0, "No statistical examples found"

        for example_file in statistical_examples:
            result = validator.validate_example(example_file)

            assert result.statistical_valid, f"Statistical validation failed: {example_file}\nErrors: {result.error_messages}"

    @pytest.mark.parametrize("chaos_level", [1, 5, 10])
    def test_examples_work_across_chaos_levels(self, examples_dir, chaos_level):
        """Test that examples work correctly at different chaos levels."""
        validator = ExampleValidator(
            chaos_levels=[chaos_level],
            seeds=[42],
            timeout=30.0
        )

        # Test a sample of examples across each difficulty level
        catalog = ExampleCatalog(examples_dir)

        for difficulty in DifficultyLevel:
            examples = catalog.get_examples_by_difficulty(difficulty)

            if examples:
                # Test first example from each difficulty level
                example_file = examples[0]
                result = validator.validate_example(example_file)

                assert result.execution_successful, f"Example failed at chaos level {chaos_level}: {example_file}\nErrors: {result.error_messages}"
```

## 📊 Implementation Timeline

### Week 1: Critical Fixes
- [ ] Fix demo_v4_features.knda syntax error
- [ ] Fix chaos_arena2_complete.py.knda multi-line issue
- [ ] Remove all skip patterns from test files
- [ ] Implement basic example validator
- [ ] Set up CI integration for demo files

### Week 2: Ecosystem Structure
- [ ] Create new directory structure
- [ ] Migrate existing examples to appropriate categories
- [ ] Implement example metadata system
- [ ] Create beginner example set (5-10 examples)
- [ ] Implement comprehensive CI validation

### Week 3: Quality Assurance
- [ ] Complete intermediate and advanced example sets
- [ ] Implement statistical validation for probabilistic examples
- [ ] Create example catalog and discovery system
- [ ] Generate comprehensive validation reports
- [ ] Final testing and quality assurance

## 🎯 Success Criteria

### Critical Requirements
- [ ] 100% example execution success rate across all chaos levels and seeds
- [ ] Zero skipped examples in test suite
- [ ] All broken issues (#86, #87, #88, #96) resolved
- [ ] CI integration validates all examples

### Quality Requirements
- [ ] Complete example metadata for all files
- [ ] Progressive difficulty learning paths
- [ ] Statistical validation for probabilistic examples
- [ ] Comprehensive documentation and comments

### User Experience Requirements
- [ ] Clear beginner onboarding path
- [ ] Effective example discovery and categorization
- [ ] Consistent quality and formatting
- [ ] Community contribution framework ready

---

This specification provides a complete implementation roadmap for transforming the Kinda-Lang example ecosystem from its current state to a production-ready, maintainable, and user-friendly system that supports the v0.5.1 release goals.