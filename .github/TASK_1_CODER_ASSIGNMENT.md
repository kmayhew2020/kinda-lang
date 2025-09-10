# 🚀 CODER ASSIGNMENT: Epic #124 - Task 1

## 📋 Assignment Overview
**Task**: Core ~sorta Conditional Implementation using Construct Composition
**Epic**: #124 Construct Self-definition  
**Priority**: HIGH
**Estimated Timeline**: 2 weeks (~10 working days)
**Assigned**: Ready for assignment

## 🎯 Mission Statement
Implement the `~sorta` construct using composition of existing basic constructs (`~sometimes`, `~maybe`, personality system) to demonstrate the "Kinda builds Kinda" principle. This is the foundation task that proves higher-level constructs can be elegantly built from simpler ones.

## 🔧 Technical Specification

### Core Requirements
1. **Rebuild `~sorta`** using only existing basic constructs:
   - `~sometimes` for probabilistic execution
   - `~maybe` for conditional uncertainty  
   - Personality system for behavioral variations
   - Standard Python logic for composition

2. **Maintain Full Compatibility**:
   - All existing `~sorta` functionality preserved
   - All existing tests continue to pass
   - Same API and usage patterns
   - Same personality integration

3. **Demonstrate Composition Pattern**:
   - Clear code showing basic constructs being combined
   - Comments explaining how composition works
   - Example showing equivalence to original implementation

### Implementation Pattern
```python
# Target composition approach (example):
def sorta_conditional_implementation(condition, action, personality_mode):
    """
    Implement ~sorta using construct composition:
    1. Use ~sometimes for probabilistic execution
    2. Use ~maybe for conditional uncertainty  
    3. Integrate personality for behavior variation
    """
    
    # Personality influences probability thresholds
    base_probability = get_personality_probability(personality_mode)
    
    # Compose ~sorta behavior from basic constructs
    if condition:
        ~sometimes (
            ~maybe (action, probability=base_probability * 0.8)
        )
    else:
        ~rarely (action)  # Lower probability when condition false
```

## 🧪 Testing Requirements

### Existing Test Compatibility
- [ ] Run full existing ~sorta test suite - **ALL MUST PASS**
- [ ] No changes to existing test files required
- [ ] Same behavior across all personality modes
- [ ] Same error handling and edge cases

### New Composition Tests  
- [ ] Test showing ~sometimes usage in composition
- [ ] Test showing ~maybe usage in composition
- [ ] Test personality integration through basic constructs
- [ ] Test composition equivalence to original implementation

### Success Validation
```bash
# These commands must pass:
pytest tests/ -k sorta  # All existing tests pass
python -m kinda_lang examples/sorta_example.knda  # Examples work
kinda run --test-composition  # New composition tests pass
```

## 📂 File Locations to Modify

### Primary Implementation Files
- `/home/kevin/kinda-lang/kinda_lang/transformer.py` - Update ~sorta transformation
- `/home/kevin/kinda-lang/kinda_lang/runtime.py` - Update ~sorta runtime logic
- `/home/kevin/kinda-lang/kinda_lang/constructs/` - If construct-specific modules exist

### Testing Files
- `/home/kevin/kinda-lang/tests/test_constructs.py` - Add composition tests
- `/home/kevin/kinda-lang/tests/test_sorta.py` - If dedicated ~sorta tests exist
- New file: `/home/kevin/kinda-lang/tests/test_composition.py` - Composition-specific tests

## 🏗️ Development Approach

### Phase 1: Analysis (Day 1)
1. Study existing `~sorta` implementation thoroughly
2. Identify all current functionality and behaviors
3. Map out how basic constructs can replicate each behavior
4. Design composition architecture

### Phase 2: Implementation (Days 2-7)
1. Implement composition logic using basic constructs
2. Ensure personality integration works through composition
3. Maintain all existing API compatibility
4. Add comprehensive logging/comments explaining composition

### Phase 3: Testing (Days 8-10)
1. Run existing test suite - ensure 100% pass rate
2. Create composition-specific tests
3. Performance testing (composition vs original)
4. Edge case validation

## 🎯 Definition of Done

### Required Deliverables
- [ ] `~sorta` implemented via construct composition
- [ ] All existing `~sorta` tests pass (100% success rate)
- [ ] New composition tests created and passing
- [ ] Code comments explain composition pattern clearly
- [ ] Performance impact documented (< 20% slowdown acceptable)

### Quality Gates
- [ ] Code review by PM/Architect agent
- [ ] All CI tests passing 
- [ ] No breaking changes introduced
- [ ] Clean, readable code with proper documentation

### Handoff Requirements
- [ ] Working implementation ready for Task 2 framework integration
- [ ] Clear documentation of composition pattern used
- [ ] Performance benchmarks and analysis
- [ ] Recommendations for Task 2 framework design

## 🔗 Resources & Context

### Previous Work
- See ROADMAP.md Epic #124 context
- Review existing ~sorta implementation patterns
- Study ~sometimes and ~maybe construct implementations

### Related Tasks
- **Task 2**: Framework will generalize this composition pattern
- **Task 3**: ~ish implementation will follow similar approach
- **Task 4**: Documentation will showcase this implementation

## ⚠️ Critical Notes
1. **Backward Compatibility**: Must maintain 100% compatibility with existing code
2. **Performance**: Monitor performance impact - composition should not significantly slow execution  
3. **Code Quality**: This implementation will be showcased as example of "Kinda builds Kinda"
4. **Testing**: Existing test suite is the ultimate validation - all must pass

---

## 🚀 Ready for Assignment

**Status**: ✅ **READY FOR CODER ASSIGNMENT**  
**Next Action**: Assign to kinda-lang coder agent  
**Command**: `"Use the kinda-lang coder agent to implement Epic #124 Task 1"`

---
*Created: 2025-09-04 by Kinda-Lang Project Manager*  
*Epic #124 Task 1 - Foundation of construct composition implementation*