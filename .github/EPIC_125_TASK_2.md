# Epic #125 - Task 2: Repetition Constructs

## 🎯 Epic Context
**Epic #125: Probabilistic Control Flow Constructs** - Complete the fuzzy programming paradigm by adding probabilistic control over program flow structures.

## 📋 Task Overview
Implement `~kinda_repeat(n)` and `~eventually_until` constructs to provide fuzzy repetition counts and probabilistic termination conditions.

## 🔧 Technical Requirements

### 1. `~kinda_repeat(n)` - Fuzzy Repetition Counts

#### Core Behavior
```kinda
~kinda_repeat(5):
    action()
    # Executes approximately n times with personality-based variance
    # Actual repetitions: n ± personality-based variance
```

#### Implementation Specifications
- **Base Logic**: Repeat block approximately n times with fuzzy variance
- **Personality Integration**:
  - `reliable`: ±10% variance (n=5 → 4-6 repetitions, usually 5)
  - `cautious`: ±20% variance (n=5 → 4-6 repetitions, tends toward lower bound)
  - `playful`: ±30% variance (n=5 → 3-7 repetitions, unpredictable)
  - `chaotic`: ±40% variance (n=5 → 3-7 repetitions, extreme variance)
- **Distribution**: Uses normal distribution centered on n with personality-based standard deviation
- **Minimum Bound**: Always executes at least 1 time (unless n=0)

#### Test Requirements
```kinda
# Test cases to implement
def test_kinda_repeat_reliable():
    count = 0
    ~kinda_repeat(10):
        count += 1
    # With reliable personality, count should be 9-11, usually 10

def test_kinda_repeat_chaotic():
    count = 0  
    ~kinda_repeat(10):
        count += 1
    # With chaotic personality, count should be 6-14, highly variable
```

### 2. `~eventually_until` - Probabilistic Termination

#### Core Behavior
```kinda
~eventually_until condition:
    action()
    # Loop continues until condition becomes "statistically true"
    # Termination based on probability accumulation over time
```

#### Implementation Specifications
- **Base Logic**: Loop continues until condition meets statistical significance threshold
- **Statistical Framework**: Integrates with existing `~assert_eventually()` framework
- **Termination Logic**:
  - Tracks condition evaluation history over iterations
  - Uses Wilson score interval for confidence calculation
  - Terminates when condition confidence exceeds personality threshold
- **Personality Integration**:
  - `reliable`: 95% confidence threshold (very certain before terminating)
  - `cautious`: 90% confidence threshold (quite certain)  
  - `playful`: 80% confidence threshold (moderately certain)
  - `chaotic`: 70% confidence threshold (somewhat certain)

#### Statistical Implementation
```python
# Core termination logic (simplified)
class EventuallyUntilEvaluator:
    def __init__(self, personality):
        self.confidence_threshold = {
            'reliable': 0.95,
            'cautious': 0.90,
            'playful': 0.80,
            'chaotic': 0.70
        }[personality]
        self.evaluations = []
    
    def should_terminate(self, condition_result):
        self.evaluations.append(condition_result)
        if len(self.evaluations) < 3:
            return False  # Need minimum sample size
        
        # Calculate Wilson score confidence interval
        confidence = self.wilson_score_confidence()
        return confidence > self.confidence_threshold
```

#### Test Requirements
```kinda
# Test cases to implement
def test_eventually_until_reliable():
    count = 0
    ~eventually_until count > 10:
        count += random_increment()  # Fuzzy increment
    # Should terminate when statistically confident count > 10 (95% confidence)

def test_eventually_until_chaotic():
    count = 0
    ~eventually_until count > 10:
        count += random_increment()  # Fuzzy increment  
    # Should terminate earlier with lower confidence (70% confidence)
```

## 🧪 Testing Requirements

### Unit Tests
- [ ] `~kinda_repeat(n)` variance testing for all personalities
- [ ] `~kinda_repeat(n)` edge cases (n=0, n=1, large n)
- [ ] `~kinda_repeat(n)` with nested constructs
- [ ] `~eventually_until` termination logic with deterministic conditions
- [ ] `~eventually_until` with probabilistic conditions
- [ ] `~eventually_until` minimum iteration requirements

### Statistical Tests  
- [ ] Validate `~kinda_repeat` distributions match personality specifications
- [ ] Test `~eventually_until` confidence calculations with Wilson score intervals
- [ ] Cross-platform statistical consistency validation
- [ ] Performance testing for long-running repetitions

### Integration Tests
- [ ] Compatibility with Task 1 constructs (`~sometimes_while`, `~maybe_for`)
- [ ] Nested combinations with existing constructs
- [ ] Integration with `~assert_eventually()` statistical framework
- [ ] Memory efficiency for long repetition sequences

## 📖 Documentation Requirements

### Technical Documentation
- [ ] Statistical algorithms explanation (Wilson score intervals)
- [ ] Personality-based variance calculation methods
- [ ] Performance characteristics and optimization notes
- [ ] Integration with existing statistical testing framework

### User Documentation
- [ ] Practical usage examples for both constructs
- [ ] Personality behavior comparison and selection guide
- [ ] Performance recommendations for different use cases
- [ ] Troubleshooting guide for unexpected termination behaviors

## 🎯 Implementation Strategy

### Phase 1: `~kinda_repeat(n)` Implementation (Week 1)
1. **Core Logic**: Implement fuzzy repetition with personality-based variance
2. **Distribution Math**: Normal distribution with personality-specific standard deviation
3. **Parser Integration**: Add syntax recognition and AST transformation
4. **Basic Testing**: Unit tests for all personality modes

### Phase 2: `~eventually_until` Implementation (Week 2)
1. **Statistical Framework**: Implement Wilson score confidence calculations
2. **Termination Logic**: Probability accumulation and threshold checking
3. **Integration**: Link with existing `~assert_eventually()` infrastructure
4. **Advanced Testing**: Statistical validation and edge case handling

### Phase 3: Integration & Optimization (Week 3)
1. **Cross-construct Integration**: Test combinations with Task 1 constructs
2. **Performance Optimization**: Memory efficiency for long-running constructs
3. **Statistical Validation**: Comprehensive statistical testing
4. **Documentation**: Complete technical and user documentation

## 🎯 Success Criteria

### Functional Requirements
- [ ] Both constructs implemented with personality integration
- [ ] Statistical accuracy validated with `~assert_eventually()` framework
- [ ] All edge cases handled (n=0, infinite loops, etc.)
- [ ] 100% backward compatibility maintained

### Performance Requirements
- [ ] `~kinda_repeat` overhead <10% compared to standard loops
- [ ] `~eventually_until` memory usage optimized for long evaluations
- [ ] Statistical calculations efficient for real-time execution
- [ ] Cross-platform performance consistency

### Quality Requirements  
- [ ] >95% test coverage for both constructs
- [ ] All CI tests passing on Ubuntu/macOS/Windows
- [ ] Statistical tests validate probability distributions
- [ ] Code review approved with performance benchmarks

### Documentation Requirements
- [ ] Complete statistical algorithm documentation
- [ ] User guide with real-world examples
- [ ] Performance characteristics and recommendations
- [ ] Integration guide with existing kinda-lang constructs

## 🔗 Dependencies & Coordination

### Task Dependencies
- **Depends on Task 1**: Shared infrastructure and testing patterns
- **Parallel with Epic #124 Tasks 2-3**: Coordination for shared frameworks
- **Feeds into Task 3**: Provides constructs for advanced integration testing

### Technical Dependencies
- Wilson score interval implementation (from `~assert_eventually()`)
- Personality system integration
- Statistical testing framework  
- Parser and AST transformation infrastructure
- Normal distribution sampling (for `~kinda_repeat` variance)

### Epic #124 Coordination
- **Shared Statistical Framework**: Both epics use `~assert_eventually()`
- **Cross-epic Examples**: Epic #124 can demonstrate composition with Epic #125 constructs
- **Documentation Integration**: Unified v0.5.0 documentation structure

## ⏰ Timeline
**Duration**: 3 weeks (15 working days)
- **Week 1**: `~kinda_repeat(n)` implementation and testing
- **Week 2**: `~eventually_until` implementation and statistical integration
- **Week 3**: Integration, optimization, and comprehensive documentation

## 🏷️ Labels
- `epic-125`
- `probabilistic-control-flow`
- `high-priority`
- `v0.5.0`
- `statistical-framework`
- `task-2-repetition`

---
*Created as part of Epic #125 task breakdown - depends on Task 1 infrastructure*