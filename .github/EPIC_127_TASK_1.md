# Epic #127 Task 1: Python AST Framework & Primitives

## 📋 Task Overview
**Epic**: #127 Python Injection Framework
**Task**: Task 1 - Python AST Framework & Primitives
**Duration**: 2 weeks (Weeks 1-2)
**Priority**: HIGH
**Assignee**: Coder + Architect

## 🎯 Task Objectives

### Primary Goals
1. Build robust Python AST analysis foundation for injection framework
2. Implement primitive injection patterns (kinda_int, kinda_float, sorta_print)
3. Establish security validation framework for code injection
4. Create basic CLI interface for injection operations

### Success Criteria
- [ ] AST analysis engine parsing Python files with 99.9% accuracy
- [ ] Primitive patterns (kinda_int, kinda_float, sorta_print) working correctly
- [ ] Security framework preventing dangerous code injection
- [ ] Basic CLI commands functional (`inject run`, `inject analyze`, `inject validate`)
- [ ] Test coverage >95% for all implemented components
- [ ] Performance overhead <5% for primitive pattern injection

## 🔧 Technical Requirements

### 1. AST Analysis Engine

**File**: `kinda/injection/ast_analyzer.py`

**Core Components**:
```python
class PythonASTAnalyzer:
    """Core AST analysis for Python injection"""

    def __init__(self):
        self.parser = ASTParser()
        self.visitor = InjectionVisitor()
        self.validator = SyntaxValidator()

    def parse_file(self, file_path: Path) -> ast.AST:
        """Parse Python file into AST with error handling"""
        # Requirements:
        # - Handle encoding detection (UTF-8, Latin-1, etc.)
        # - Provide detailed error messages for syntax errors
        # - Support Python 3.8+ syntax features
        # - Memory-efficient parsing for large files

    def find_injection_points(self, tree: ast.AST) -> List[InjectionPoint]:
        """Identify opportunities for injection"""
        # Requirements:
        # - Use ast.NodeVisitor pattern for traversal
        # - Identify variable assignments suitable for kinda_* patterns
        # - Detect print statements for sorta_print conversion
        # - Calculate confidence scores for each opportunity
        # - Return sorted list by confidence and safety

    def validate_syntax(self, tree: ast.AST) -> ValidationResult:
        """Validate AST for injection compatibility"""
        # Requirements:
        # - Check for syntax compatibility with injection framework
        # - Validate import statements don't conflict
        # - Ensure no conflicting variable names
        # - Return detailed validation report

class InjectionPoint:
    """Represents an injection opportunity"""
    def __init__(self,
                 location: CodeLocation,
                 pattern_type: PatternType,
                 confidence: float,
                 safety_level: SecurityLevel,
                 context: InjectionContext):
        self.location = location
        self.pattern_type = pattern_type
        self.confidence = confidence
        self.safety_level = safety_level
        self.context = context

class CodeLocation:
    """Precise code location information"""
    def __init__(self, line: int, column: int, end_line: int, end_column: int):
        self.line = line
        self.column = column
        self.end_line = end_line
        self.end_column = end_column
```

**Integration Requirements**:
- Extend existing `kinda/langs/python/transformer.py` patterns
- Use Python built-in `ast` module for maximum compatibility
- Integrate with existing `kinda.security` framework
- Follow existing error handling patterns from `kinda/cli.py`

### 2. Primitive Injection Patterns

**File**: `kinda/injection/patterns/primitives.py`

**Pattern Implementations**:

#### 2.1 Kinda Integer Pattern
```python
class KindaIntPattern(InjectionPattern):
    """Inject kinda_int behavior into integer assignments"""

    def detect(self, node: ast.AST) -> bool:
        """Detect integer assignment patterns"""
        # Requirements:
        # - Match ast.Assign nodes with integer constants
        # - Exclude security-sensitive variables (password, key, etc.)
        # - Exclude loop counters and array indices
        # - Return True for suitable integer assignments

    def transform(self, node: ast.Assign) -> ast.AST:
        """Transform assignment to use kinda_int"""
        # Requirements:
        # - Transform "x = 42" to "x = kinda_int(42)"
        # - Preserve variable name and context
        # - Add necessary import statements
        # - Maintain original line number information

    def validate_safety(self, node: ast.AST) -> SafetyResult:
        """Ensure safe to apply kinda_int"""
        # Requirements:
        # - Check variable name for security sensitivity
        # - Validate integer value is reasonable for fuzzing
        # - Ensure no conflicts with existing kinda constructs
        # - Return detailed safety assessment
```

#### 2.2 Kinda Float Pattern
```python
class KindaFloatPattern(InjectionPattern):
    """Inject kinda_float behavior into float assignments"""

    def detect(self, node: ast.AST) -> bool:
        """Detect float assignment patterns"""
        # Requirements:
        # - Match ast.Assign nodes with float constants
        # - Handle both literal floats and integer-to-float promotions
        # - Exclude scientific constants and precise measurements
        # - Return True for suitable float assignments

    def transform(self, node: ast.Assign) -> ast.AST:
        """Transform assignment to use kinda_float"""
        # Requirements:
        # - Transform "x = 3.14" to "x = kinda_float(3.14)"
        # - Support variance configuration
        # - Handle edge cases (very small/large numbers)
        # - Preserve numerical precision where critical

    def validate_safety(self, node: ast.AST) -> SafetyResult:
        """Ensure safe to apply kinda_float"""
        # Requirements:
        # - Check for mathematical constants (pi, e, etc.)
        # - Validate float value range
        # - Ensure precision requirements are met
        # - Return safety recommendation
```

#### 2.3 Sorta Print Pattern
```python
class SortaPrintPattern(InjectionPattern):
    """Convert print statements to probabilistic output"""

    def detect(self, node: ast.AST) -> bool:
        """Detect print statement patterns"""
        # Requirements:
        # - Match ast.Call nodes with print function
        # - Exclude debug print statements in critical paths
        # - Handle both simple and formatted print statements
        # - Return True for suitable print calls

    def transform(self, node: ast.Call) -> ast.AST:
        """Transform to sorta_print"""
        # Requirements:
        # - Transform "print(x)" to "sorta_print(x)"
        # - Preserve all print arguments and formatting
        # - Support print parameters (sep, end, file, flush)
        # - Maintain output behavior compatibility

    def validate_safety(self, node: ast.AST) -> SafetyResult:
        """Ensure safe to apply sorta_print"""
        # Requirements:
        # - Check for critical logging or error output
        # - Validate print statement context
        # - Ensure no security-sensitive information
        # - Return safety assessment
```

### 3. Security Validation Framework

**File**: `kinda/injection/security.py`

**Security Framework Extension**:
```python
class InjectionSecurityValidator:
    """Enhanced security for injection operations"""

    def __init__(self, base_security: SecurityValidator):
        self.base_security = base_security
        self.injection_policies = InjectionSecurityPolicies()

    def validate_injection_request(self, request: InjectionRequest) -> SecurityResult:
        """Validate entire injection request"""
        # Requirements:
        # - Validate all requested patterns are safe
        # - Check file permissions and ownership
        # - Ensure no dangerous code patterns in target file
        # - Validate user authorization for injection
        # - Return comprehensive security assessment

    def validate_ast_modification(self, original: ast.AST, modified: ast.AST) -> SecurityResult:
        """Ensure AST modifications are safe"""
        # Requirements:
        # - Compare original and modified AST trees
        # - Ensure only authorized modifications were made
        # - Validate no malicious code was injected
        # - Check for unexpected side effects
        # - Return modification safety report

    def authorize_pattern_usage(self, pattern: InjectionPattern,
                              context: InjectionContext) -> bool:
        """Authorize specific pattern usage"""
        # Requirements:
        # - Check pattern against security policies
        # - Validate context is appropriate for pattern
        # - Ensure user has permission for pattern type
        # - Log authorization decisions for audit
        # - Return authorization decision

class InjectionSecurityPolicies:
    """Security policies for injection operations"""

    PROHIBITED_VARIABLE_PATTERNS = [
        'password', 'secret', 'key', 'token', 'auth',
        'credential', 'private', 'protected', 'secure'
    ]

    CRITICAL_FUNCTION_PATTERNS = [
        'exec', 'eval', 'compile', '__import__',
        'open', 'file', 'input', 'raw_input'
    ]

    def check_variable_safety(self, var_name: str) -> SecurityResult:
        """Check if variable is safe for injection"""

    def check_context_safety(self, context: InjectionContext) -> SecurityResult:
        """Check if injection context is safe"""
```

### 4. Basic CLI Interface

**File**: `kinda/cli.py` (extensions)

**CLI Command Implementation**:
```python
def add_injection_commands(parser: argparse.ArgumentParser):
    """Add injection command group to existing kinda CLI"""

    # Create injection subcommand group
    inject_parser = parser.add_subparsers(dest='inject_command')
    inject_main = inject_parser.add_parser('inject',
                                         help='Python injection framework commands')

    # Add injection-specific subcommands
    inject_sub = inject_main.add_subparsers(dest='inject_action', required=True)

    # inject run command
    run_parser = inject_sub.add_parser('run', help='Inject and execute Python file')
    run_parser.add_argument('file', help='Python file to inject and run')
    run_parser.add_argument('--level', choices=['basic'], default='basic',
                           help='Injection complexity level')
    run_parser.add_argument('--patterns', help='Comma-separated list of patterns to use')
    run_parser.add_argument('--dry-run', action='store_true',
                           help='Show injection plan without executing')
    run_parser.add_argument('--backup', action='store_true', default=True,
                           help='Create backup before modification')

    # inject analyze command
    analyze_parser = inject_sub.add_parser('analyze',
                                         help='Analyze injection opportunities')
    analyze_parser.add_argument('file', help='Python file to analyze')
    analyze_parser.add_argument('--report', choices=['summary', 'detailed'],
                               default='summary', help='Report detail level')
    analyze_parser.add_argument('--show-code', action='store_true',
                               help='Show code snippets for opportunities')

    # inject validate command
    validate_parser = inject_sub.add_parser('validate',
                                          help='Validate injection compatibility')
    validate_parser.add_argument('file', help='Python file to validate')
    validate_parser.add_argument('--strict', action='store_true',
                                help='Use strict validation mode')
    validate_parser.add_argument('--security-scan', action='store_true',
                                help='Include security validation')

def handle_injection_command(args) -> int:
    """Handle injection command execution"""
    # Requirements:
    # - Setup personality system integration
    # - Initialize injection framework components
    # - Execute requested command with error handling
    # - Provide user-friendly feedback and guidance
    # - Return appropriate exit codes
```

## 📋 Implementation Tasks

### Week 1: Foundation (Days 1-7)

#### Day 1-2: Project Setup
- [ ] Create `kinda/injection/` package structure
- [ ] Setup `__init__.py` with proper imports
- [ ] Create base classes and interfaces
- [ ] Setup development environment and testing framework
- [ ] Initialize git branch `task/epic-127-task-1`

#### Day 3-4: AST Analysis Engine
- [ ] Implement `PythonASTAnalyzer` class
- [ ] Create `InjectionPoint` and related data structures
- [ ] Implement AST parsing with error handling
- [ ] Add injection opportunity detection logic
- [ ] Create comprehensive unit tests for AST components

#### Day 5-7: Security Framework
- [ ] Implement `InjectionSecurityValidator` class
- [ ] Create security policies and validation rules
- [ ] Integrate with existing `kinda.security` module
- [ ] Add audit logging for security events
- [ ] Create security validation test suite

### Week 2: Patterns and CLI (Days 8-14)

#### Day 8-10: Primitive Patterns
- [ ] Implement `KindaIntPattern` class
- [ ] Implement `KindaFloatPattern` class
- [ ] Implement `SortaPrintPattern` class
- [ ] Create pattern safety validation
- [ ] Add comprehensive pattern tests

#### Day 11-12: CLI Interface
- [ ] Extend existing CLI with injection commands
- [ ] Implement `inject run` command
- [ ] Implement `inject analyze` command
- [ ] Implement `inject validate` command
- [ ] Add CLI integration tests

#### Day 13-14: Integration and Polish
- [ ] Integrate all components into cohesive system
- [ ] Add end-to-end integration tests
- [ ] Performance optimization and profiling
- [ ] Documentation and code cleanup
- [ ] Prepare for Task 1 completion review

## 🧪 Testing Requirements

### Unit Testing
- **Coverage Target**: >95% for all implemented components
- **Test Files**:
  - `tests/injection/test_ast_analyzer.py`
  - `tests/injection/test_primitive_patterns.py`
  - `tests/injection/test_security.py`
  - `tests/injection/test_cli.py`

### Integration Testing
- **End-to-End Workflows**:
  - Complete injection pipeline from file to execution
  - CLI command integration with existing kinda CLI
  - Security validation integration
  - Error handling and recovery scenarios

### Performance Testing
- **Benchmarks**:
  - AST parsing performance for large files (>1000 lines)
  - Pattern detection performance
  - Memory usage for injection operations
  - CLI response time measurements

## 🔒 Security Requirements

### Security Validation
- [ ] No arbitrary code execution during injection
- [ ] Comprehensive input validation and sanitization
- [ ] Security policy enforcement
- [ ] Audit logging for all injection operations

### Security Testing
- [ ] Penetration testing for injection vulnerabilities
- [ ] Input fuzzing for AST parser
- [ ] Security policy validation tests
- [ ] Privilege escalation prevention tests

## 📊 Success Metrics

### Functional Metrics
- [ ] AST parser handles 100% of valid Python 3.8+ syntax
- [ ] Primitive patterns work correctly in 99% of detected opportunities
- [ ] Security framework blocks 100% of dangerous injection attempts
- [ ] CLI commands complete successfully for valid inputs

### Performance Metrics
- [ ] AST parsing: >1000 lines/second
- [ ] Pattern detection: <100ms for typical files
- [ ] Injection overhead: <5% for primitive patterns
- [ ] CLI response time: <100ms for basic commands

### Quality Metrics
- [ ] Code coverage: >95%
- [ ] Documentation coverage: 100% of public APIs
- [ ] Security scan: Zero critical vulnerabilities
- [ ] User acceptance: >90% task completion rate

## 🔗 Dependencies

### Internal Dependencies
- **Epic #124/#125**: Complete probabilistic programming foundation
- **Existing Security Framework**: `kinda.security` module
- **Runtime Helpers**: `kinda.langs.python.runtime.fuzzy`
- **CLI Framework**: `kinda.cli` module

### External Dependencies
- **Python Standard Library**: `ast`, `argparse`, `pathlib`
- **Testing Framework**: `pytest`, `unittest.mock`
- **Development Tools**: `black`, `flake8`, `mypy`

## 🚨 Risk Management

### Technical Risks
- **AST Complexity**: Mitigate with incremental implementation and extensive testing
- **Security Vulnerabilities**: Address with security-first design and penetration testing
- **Performance Impact**: Monitor with continuous benchmarking and optimization

### Timeline Risks
- **Scope Creep**: Focus on MVP primitive patterns only
- **Integration Issues**: Start integration early with existing codebase
- **Testing Delays**: Parallel development of tests with implementation

## 📝 Deliverables

### Code Deliverables
- [ ] `kinda/injection/ast_analyzer.py` - AST analysis engine
- [ ] `kinda/injection/patterns/primitives.py` - Primitive injection patterns
- [ ] `kinda/injection/security.py` - Security validation framework
- [ ] `kinda/cli.py` extensions - Basic CLI commands

### Documentation Deliverables
- [ ] API documentation for all public interfaces
- [ ] Usage examples for CLI commands
- [ ] Security documentation and policies
- [ ] Testing documentation and results

### Testing Deliverables
- [ ] Comprehensive unit test suite
- [ ] Integration test suite
- [ ] Performance benchmark results
- [ ] Security validation test results

## ✅ Definition of Done

Task 1 is considered complete when:

1. **Functionality**: All primitive patterns (kinda_int, kinda_float, sorta_print) work correctly
2. **Security**: Security framework prevents dangerous injections and passes penetration tests
3. **CLI**: Basic injection commands are functional and integrated with existing CLI
4. **Testing**: Test coverage >95% and all tests passing
5. **Performance**: Performance targets met for AST parsing and pattern injection
6. **Documentation**: All code documented and usage examples provided
7. **Integration**: Components integrate seamlessly with existing kinda-lang infrastructure
8. **Review**: Code review completed and approved by Epic #127 team

---

**Task Version**: 1.0
**Created**: 2025-09-15
**Next Review**: Week 1 Completion
**Assigned Team**: Coder (Lead), Architect (Review), Tester (Validation)

This task establishes the foundation for the Python Injection Framework, enabling the implementation of more advanced features in subsequent tasks.