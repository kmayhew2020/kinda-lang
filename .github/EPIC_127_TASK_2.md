# Epic #127 Task 2: Control Flow Injection Engine

## 📋 Task Overview
**Epic**: #127 Python Injection Framework
**Task**: Task 2 - Control Flow Injection Engine
**Duration**: 2 weeks (Weeks 3-4)
**Priority**: HIGH
**Assignee**: Coder + Architect
**Dependencies**: Task 1 (AST Framework & Primitives) completed

## 🎯 Task Objectives

### Primary Goals
1. Implement control flow injection patterns (sometimes, maybe, loops)
2. Build advanced pattern matching and transformation engine
3. Enhance CLI with conversion and interactive features
4. Establish pattern recommendation system

### Success Criteria
- [ ] Control flow patterns (sometimes, maybe, maybe_for, sometimes_while) working correctly
- [ ] Advanced pattern engine with confidence scoring and optimization
- [ ] Enhanced CLI with `inject convert` and interactive mode
- [ ] Pattern recommendation system providing intelligent suggestions
- [ ] Test coverage >95% for all new components
- [ ] Performance overhead <8% for control flow pattern injection

## 🔧 Technical Requirements

### 1. Control Flow Patterns

**File**: `kinda/injection/patterns/control_flow.py`

#### 1.1 Sometimes Conditional Pattern
```python
class SometimesPattern(InjectionPattern):
    """Inject probabilistic conditional execution"""

    def detect(self, node: ast.If) -> bool:
        """Detect if-statement suitable for sometimes injection"""
        # Requirements:
        # - Match ast.If nodes with boolean conditions
        # - Exclude critical system conditions (shutdown, security, etc.)
        # - Identify conditions suitable for probabilistic execution
        # - Return True for appropriate if-statements

    def transform(self, node: ast.If) -> ast.AST:
        """Transform if-statement to use sometimes()"""
        # Requirements:
        # - Transform "if condition:" to "if sometimes(condition):"
        # - Handle complex conditions and nested logic
        # - Preserve else clauses and elif chains
        # - Support variants: maybe(), probably(), rarely()
        # - Maintain original control flow semantics

    def validate_safety(self, node: ast.If) -> SafetyResult:
        """Ensure conditional is safe for probabilistic execution"""
        # Requirements:
        # - Check for critical system operations in if body
        # - Validate condition doesn't involve security checks
        # - Ensure probabilistic execution won't break functionality
        # - Check for side effects that must be deterministic
        # - Return detailed safety assessment

class ConditionalVariants:
    """Supporting variants for conditional patterns"""

    @staticmethod
    def get_pattern_probability(pattern_type: str) -> float:
        """Get base probability for pattern type"""
        probabilities = {
            'sometimes': 0.5,   # 50% base probability
            'maybe': 0.6,       # 60% base probability
            'probably': 0.7,    # 70% base probability
            'rarely': 0.2       # 20% base probability
        }
        return probabilities.get(pattern_type, 0.5)

    @staticmethod
    def recommend_pattern_variant(condition_context: ConditionContext) -> str:
        """Recommend appropriate pattern variant based on context"""
        # Requirements:
        # - Analyze condition frequency and importance
        # - Consider user experience impact
        # - Return most appropriate pattern variant
```

#### 1.2 Loop Injection Patterns
```python
class MaybeForPattern(InjectionPattern):
    """Inject probabilistic loop iteration"""

    def detect(self, node: ast.For) -> bool:
        """Detect for-loop suitable for maybe_for injection"""
        # Requirements:
        # - Match ast.For nodes with iterable collections
        # - Exclude critical loops (file processing, data validation)
        # - Identify loops suitable for sampling/probabilistic execution
        # - Consider loop body complexity and side effects
        # - Return True for appropriate for-loops

    def transform(self, node: ast.For) -> ast.AST:
        """Transform loop to use maybe_for pattern"""
        # Requirements:
        # - Transform "for item in items:" to probabilistic iteration
        # - Add "if maybe_for_item_execute():" inside loop body
        # - Preserve loop variable scope and iteration order
        # - Handle nested loops and complex iteration patterns
        # - Support break and continue statements

    def validate_safety(self, node: ast.For) -> SafetyResult:
        """Ensure loop is safe for probabilistic execution"""
        # Requirements:
        # - Check for accumulator variables that need all iterations
        # - Validate loop doesn't perform critical data processing
        # - Ensure side effects are acceptable with partial execution
        # - Check for dependencies between iterations
        # - Return safety assessment with recommendations

class SometimesWhilePattern(InjectionPattern):
    """Inject probabilistic while loop conditions"""

    def detect(self, node: ast.While) -> bool:
        """Detect while-loop suitable for sometimes_while injection"""
        # Requirements:
        # - Match ast.While nodes with appropriate conditions
        # - Exclude infinite loops and critical system loops
        # - Identify loops that can tolerate early termination
        # - Consider loop termination conditions and side effects

    def transform(self, node: ast.While) -> ast.AST:
        """Transform to sometimes_while pattern"""
        # Requirements:
        # - Transform "while condition:" to "while sometimes_while_condition(condition):"
        # - Preserve loop termination semantics
        # - Handle complex while conditions
        # - Support nested while loops

    def validate_safety(self, node: ast.While) -> SafetyResult:
        """Ensure while loop is safe for probabilistic execution"""
        # Requirements:
        # - Check for critical loop termination conditions
        # - Validate early termination won't cause issues
        # - Ensure loop body handles partial execution
        # - Return safety assessment
```

### 2. Advanced Pattern Engine

**File**: `kinda/injection/engine.py`

```python
class AdvancedPatternEngine:
    """Enhanced pattern matching and transformation engine"""

    def __init__(self):
        self.pattern_registry = PatternRegistry()
        self.matcher = AdvancedPatternMatcher()
        self.transformer = ASTTransformer()
        self.optimizer = PatternOptimizer()

    def analyze_injection_opportunities(self, tree: ast.AST) -> InjectionPlan:
        """Comprehensive analysis of injection opportunities"""
        # Requirements:
        # - Traverse AST to identify all injection opportunities
        # - Calculate confidence scores for each opportunity
        # - Analyze dependencies between potential injections
        # - Consider user-specified preferences and constraints
        # - Return prioritized injection plan

    def generate_injection_plan(self, opportunities: List[InjectionPoint],
                               config: InjectionConfig) -> InjectionPlan:
        """Generate optimized injection plan"""
        # Requirements:
        # - Select optimal subset of injection opportunities
        # - Resolve conflicts between overlapping injections
        # - Optimize for performance and safety constraints
        # - Consider user preferences for injection types
        # - Return executable injection plan

    def apply_injection_plan(self, tree: ast.AST, plan: InjectionPlan) -> TransformResult:
        """Apply injection plan to AST"""
        # Requirements:
        # - Execute injections in dependency order
        # - Track injection success and failure rates
        # - Handle conflicts and rollback on errors
        # - Generate comprehensive transformation report
        # - Return modified AST with injection metadata

class InjectionPlan:
    """Comprehensive plan for injection operations"""

    def __init__(self):
        self.injections = []
        self.dependencies = []
        self.conflicts = []
        self.performance_estimate = None
        self.security_assessment = None

    def add_injection(self, injection: PlannedInjection) -> None:
        """Add injection to plan with validation"""

    def resolve_conflicts(self) -> ConflictResolution:
        """Resolve conflicts between planned injections"""

    def optimize_execution_order(self) -> ExecutionOrder:
        """Optimize order of injection execution"""

class AdvancedPatternMatcher:
    """Advanced pattern matching with confidence scoring"""

    def __init__(self):
        self.confidence_calculator = ConfidenceCalculator()
        self.context_analyzer = ContextAnalyzer()

    def match_patterns(self, node: ast.AST, available_patterns: List[InjectionPattern]) -> List[PatternMatch]:
        """Match available patterns against AST node"""
        # Requirements:
        # - Try all available patterns against node
        # - Calculate confidence scores for each match
        # - Analyze injection context and suitability
        # - Filter out low-confidence matches
        # - Return ranked list of pattern matches

    def calculate_confidence(self, pattern: InjectionPattern, node: ast.AST) -> float:
        """Calculate confidence score for pattern-node combination"""
        # Requirements:
        # - Analyze code context and pattern suitability
        # - Consider variable names and usage patterns
        # - Evaluate potential impact and benefits
        # - Account for user experience and safety factors
        # - Return confidence score (0.0-1.0)
```

### 3. Enhanced CLI Features

**File**: `kinda/cli.py` (extensions)

#### 3.1 Convert Command
```python
def setup_inject_convert_parser(parser):
    """Setup convert command with advanced options"""
    parser.add_argument('file', help='Python file to convert')
    parser.add_argument('--output', help='Output file path (default: <file>_enhanced.py)')
    parser.add_argument('--level', choices=['basic', 'intermediate'], default='basic',
                       help='Conversion complexity level')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive conversion with user choices')
    parser.add_argument('--patterns', help='Comma-separated patterns to use')
    parser.add_argument('--functions', nargs='+', help='Specific functions to convert')
    parser.add_argument('--preserve-behavior', action='store_true',
                       help='Minimize behavioral changes')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show conversion plan without applying')

def handle_inject_convert(args) -> int:
    """Handle inject convert command execution"""
    # Requirements:
    # - Load and analyze Python file for conversion opportunities
    # - Generate conversion plan based on user preferences
    # - Apply conversions with proper error handling
    # - Create backup files and handle rollback
    # - Provide detailed conversion summary and statistics
    # - Support interactive mode with user choices
```

#### 3.2 Interactive Mode
```python
class InteractiveInjectionSession:
    """Interactive injection session management"""

    def __init__(self, file_path: Path, injection_engine: InjectionEngine):
        self.file_path = file_path
        self.injection_engine = injection_engine
        self.user_choices = []

    def start_interactive_session(self) -> InteractiveResult:
        """Start interactive injection session"""
        # Requirements:
        # - Present injection opportunities to user one by one
        # - Show code context and injection preview
        # - Accept user choices (yes/no/skip/quit)
        # - Provide rationale and impact explanations
        # - Allow user to modify injection parameters
        # - Generate final injection plan based on choices

    def present_injection_opportunity(self, opportunity: InjectionPoint) -> UserChoice:
        """Present single injection opportunity to user"""
        # Requirements:
        # - Display code snippet with injection preview
        # - Explain injection purpose and expected behavior
        # - Show confidence score and safety assessment
        # - Accept user input with validation
        # - Handle user questions and clarifications

    def generate_interactive_summary(self) -> InteractiveSummary:
        """Generate summary of interactive session"""
        # Requirements:
        # - Summarize user choices and applied injections
        # - Show performance and behavior impact estimates
        # - Provide recommendations for future sessions
        # - Generate detailed session report
```

### 4. Pattern Recommendation System

**File**: `kinda/injection/recommendations.py`

```python
class PatternRecommendationEngine:
    """Intelligent pattern recommendation system"""

    def __init__(self):
        self.analyzers = [
            VariableAnalyzer(),
            ControlFlowAnalyzer(),
            FunctionCallAnalyzer(),
            ContextAnalyzer()
        ]
        self.learning_engine = RecommendationLearningEngine()

    def recommend_patterns(self, ast_tree: ast.AST,
                          user_level: UserLevel,
                          domain_context: DomainContext) -> List[PatternRecommendation]:
        """Generate pattern recommendations based on code analysis"""
        # Requirements:
        # - Analyze code structure and identify injection opportunities
        # - Consider user experience level and preferences
        # - Account for application domain (game dev, scientific computing, etc.)
        # - Generate ranked recommendations with rationale
        # - Learn from user feedback to improve recommendations

    def analyze_code_patterns(self, ast_tree: ast.AST) -> CodeAnalysis:
        """Analyze code patterns for recommendation generation"""
        # Requirements:
        # - Identify variable usage patterns
        # - Analyze control flow complexity
        # - Detect domain-specific patterns
        # - Evaluate injection suitability
        # - Return comprehensive code analysis

    def calculate_recommendation_confidence(self, pattern: InjectionPattern,
                                          context: InjectionContext,
                                          user_profile: UserProfile) -> float:
        """Calculate confidence for pattern recommendation"""
        # Requirements:
        # - Analyze pattern suitability for context
        # - Consider user experience and preferences
        # - Account for safety and performance factors
        # - Calculate confidence score with detailed rationale
        # - Return confidence score and explanation

class PatternRecommendation:
    """Single pattern recommendation with metadata"""

    def __init__(self,
                 pattern: str,
                 confidence: float,
                 rationale: str,
                 complexity: PatternComplexity,
                 expected_impact: ImpactAssessment):
        self.pattern = pattern
        self.confidence = confidence
        self.rationale = rationale
        self.complexity = complexity
        self.expected_impact = expected_impact

class RecommendationLearningEngine:
    """Machine learning engine for recommendation improvement"""

    def record_user_feedback(self, recommendation: PatternRecommendation,
                           user_choice: UserChoice,
                           outcome: InjectionOutcome) -> None:
        """Record user feedback for learning"""

    def update_recommendation_model(self) -> None:
        """Update recommendation model based on collected feedback"""

    def get_personalized_recommendations(self, user_profile: UserProfile) -> RecommendationPreferences:
        """Get personalized recommendation preferences"""
```

## 📋 Implementation Tasks

### Week 3: Control Flow Patterns (Days 15-21)

#### Day 15-16: Sometimes/Maybe Patterns
- [ ] Implement `SometimesPattern` class with all variants
- [ ] Create condition analysis and safety validation
- [ ] Add support for nested conditionals and complex logic
- [ ] Implement pattern confidence scoring
- [ ] Create comprehensive unit tests for conditional patterns

#### Day 17-18: Loop Patterns
- [ ] Implement `MaybeForPattern` class
- [ ] Implement `SometimesWhilePattern` class
- [ ] Add loop safety analysis and dependency checking
- [ ] Handle complex loop constructs and edge cases
- [ ] Create loop pattern test suite

#### Day 19-21: Advanced Pattern Engine
- [ ] Implement `AdvancedPatternEngine` class
- [ ] Create `InjectionPlan` and optimization logic
- [ ] Add pattern conflict resolution
- [ ] Implement confidence scoring and ranking
- [ ] Create pattern engine integration tests

### Week 4: CLI and Recommendations (Days 22-28)

#### Day 22-23: Enhanced CLI
- [ ] Implement `inject convert` command
- [ ] Add interactive mode functionality
- [ ] Create user interface for injection choices
- [ ] Add conversion preview and dry-run capabilities
- [ ] Implement CLI integration tests

#### Day 24-25: Pattern Recommendations
- [ ] Implement `PatternRecommendationEngine` class
- [ ] Create code analysis and pattern matching
- [ ] Add recommendation confidence calculation
- [ ] Implement user feedback collection
- [ ] Create recommendation system tests

#### Day 26-28: Integration and Polish
- [ ] Integrate all Task 2 components
- [ ] Add end-to-end workflow testing
- [ ] Performance optimization and profiling
- [ ] Documentation and user guides
- [ ] Prepare for Task 2 completion review

## 🧪 Testing Requirements

### Unit Testing
- **Coverage Target**: >95% for all Task 2 components
- **Test Files**:
  - `tests/injection/test_control_flow_patterns.py`
  - `tests/injection/test_advanced_pattern_engine.py`
  - `tests/injection/test_enhanced_cli.py`
  - `tests/injection/test_recommendations.py`

### Integration Testing
- **End-to-End Workflows**:
  - Complete control flow injection pipeline
  - Interactive conversion sessions
  - Pattern recommendation and application
  - CLI command integration with Task 1 components

### Performance Testing
- **Benchmarks**:
  - Control flow pattern injection overhead
  - Advanced pattern engine performance
  - Interactive mode responsiveness
  - Recommendation system speed

## 🔒 Security Requirements

### Control Flow Security
- [ ] Validate all conditional injections are safe
- [ ] Ensure loop modifications don't create infinite loops
- [ ] Prevent injection into security-critical control flow
- [ ] Audit all control flow modifications

### Recommendation Security
- [ ] Validate recommendations don't suggest unsafe patterns
- [ ] Ensure recommendation engine isn't manipulable
- [ ] Protect user feedback data and privacy
- [ ] Audit recommendation decisions

## 📊 Success Metrics

### Functional Metrics
- [ ] Control flow patterns work correctly in 99% of detected opportunities
- [ ] Interactive mode has >90% user task completion rate
- [ ] Pattern recommendations have >80% user acceptance rate
- [ ] CLI commands complete successfully for all valid inputs

### Performance Metrics
- [ ] Control flow injection overhead: <8%
- [ ] Pattern recommendation generation: <2 seconds
- [ ] Interactive mode response time: <500ms
- [ ] Advanced pattern engine: <100ms per injection plan

### Quality Metrics
- [ ] Code coverage: >95%
- [ ] User acceptance: >85% for new features
- [ ] Recommendation accuracy: >75% user satisfaction
- [ ] Security scan: Zero critical vulnerabilities

## 🔗 Dependencies

### Internal Dependencies
- **Task 1**: AST Framework & Primitives (completed)
- **Existing Runtime**: Control flow runtime helpers
- **Security Framework**: Enhanced security validation
- **CLI Framework**: Extended command infrastructure

### External Dependencies
- **Interactive Libraries**: For CLI interaction and user input
- **Analysis Tools**: For code pattern analysis
- **Testing Framework**: Enhanced testing capabilities

## 🚨 Risk Management

### Technical Risks
- **Control Flow Complexity**: Mitigate with incremental implementation and extensive testing
- **Interactive UX Issues**: Address with user testing and feedback
- **Recommendation Quality**: Validate with real-world code samples

### Timeline Risks
- **Feature Scope**: Focus on core functionality first
- **Integration Complexity**: Early integration testing
- **User Feedback**: Parallel UX development with implementation

## 📝 Deliverables

### Code Deliverables
- [ ] `kinda/injection/patterns/control_flow.py` - Control flow injection patterns
- [ ] `kinda/injection/engine.py` - Advanced pattern engine
- [ ] `kinda/injection/recommendations.py` - Pattern recommendation system
- [ ] `kinda/cli.py` extensions - Enhanced CLI commands

### Documentation Deliverables
- [ ] Control flow pattern documentation
- [ ] Interactive mode user guide
- [ ] Pattern recommendation explanation
- [ ] Enhanced CLI documentation

### Testing Deliverables
- [ ] Control flow pattern test suite
- [ ] Interactive mode test automation
- [ ] Recommendation system validation
- [ ] Performance benchmark results

## ✅ Definition of Done

Task 2 is considered complete when:

1. **Functionality**: All control flow patterns work correctly with proper safety validation
2. **CLI**: Enhanced CLI with convert and interactive features is fully functional
3. **Recommendations**: Pattern recommendation system provides intelligent suggestions
4. **Integration**: All components integrate with Task 1 and existing infrastructure
5. **Testing**: Test coverage >95% and all tests passing
6. **Performance**: Performance targets met for all new features
7. **Documentation**: All features documented with usage examples
8. **Review**: Code review completed and approved by Epic #127 team

---

**Task Version**: 1.0
**Created**: 2025-09-15
**Next Review**: Week 3 Completion
**Assigned Team**: Coder (Lead), Architect (Review), Tester (Validation)

This task builds upon the foundation from Task 1 to implement sophisticated control flow injection capabilities, establishing the framework for advanced injection patterns in subsequent tasks.