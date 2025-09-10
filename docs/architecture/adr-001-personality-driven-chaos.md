# ADR-001: Personality-Driven Chaos Control System

**Status**: Accepted  
**Date**: 2024 (Inferred from implementation)  
**Deciders**: Kinda-Lang Core Team  

## Context

Kinda-Lang aims to express uncertainty in programming through fuzzy constructs. However, different use cases require different levels of chaos and unpredictability. A research prototype might want maximum chaos for exploring edge cases, while a production application might prefer more reliable behavior with subtle uncertainty.

## Decision

Implement a personality-driven chaos control system (`kinda/personality.py`) that provides:

1. **Four Personality Profiles**: reliable, cautious, playful, chaotic
2. **Global Singleton Context**: `PersonalityContext` manages behavior across all constructs
3. **Dynamic Parameter Adjustment**: Probabilities, variances, and error styles adapt to personality
4. **Cascade Effects**: System instability affects subsequent operations
5. **Consistent Interface**: All fuzzy constructs query personality for parameters

**Implementation Details** (`kinda/personality.py:15-107`):
```python
@dataclass
class ChaosProfile:
    sometimes_base: float = 0.5        # ~sometimes probability
    maybe_base: float = 0.6            # ~maybe probability  
    int_fuzz_range: Tuple[int, int] = (-1, 1)  # kinda int variance
    chaos_amplifier: float = 1.0       # Global chaos multiplier
    error_snark_level: float = 0.5     # Error message personality
```

## Alternatives Considered

### 1. Per-Construct Configuration
- **Rejected**: Would require complex configuration syntax in .knda files
- **Issue**: Breaks the simplicity goal of fuzzy programming

### 2. Static Randomness Levels
- **Rejected**: Doesn't provide fine-grained control over different aspects
- **Issue**: Can't adjust error handling personality independently from chaos level

### 3. Environment Variables
- **Rejected**: Less discoverable and harder to integrate with CLI
- **Issue**: Doesn't support dynamic adjustment during execution

## Consequences

### Positive
- **User Control**: Developers can tune chaos level to their needs via `--mood` flag
- **Consistent Behavior**: All constructs share the same chaos philosophy
- **Emergent Complexity**: Cascade effects create realistic system degradation
- **Debugging Friendly**: "reliable" mode provides near-deterministic behavior

### Negative
- **Added Complexity**: Every construct must query personality system
- **Performance Overhead**: Singleton pattern and parameter lookup on each operation
- **Testing Challenges**: Non-deterministic behavior harder to test systematically

## Evidence from Codebase

**CLI Integration** (`kinda/cli.py:206-218`):
```python
def setup_personality(mood: str) -> None:
    if mood and mood.lower() not in PERSONALITY_PROFILES:
        safe_print(f"[?] Unknown mood '{mood}'")
        mood = "playful"
    PersonalityContext.set_mood(mood or "playful")
```

**Construct Integration** (`kinda/grammar/python/constructs.py:82-100`):
```python
def sometimes(condition=True):
    from kinda.personality import chaos_probability, update_chaos_state
    prob = chaos_probability('sometimes', condition)
    result = random.random() < prob and bool(condition)
    update_chaos_state(failed=not result)
    return result
```

**Error Message Adaptation** (`kinda/grammar/python/constructs.py:302-313`):
```python
personality = get_personality()
style = personality.get_error_message_style()
if style == 'professional':
    print(f"[welp] Expression returned None, using fallback")
elif style == 'chaotic':
    print(f"[welp] *shrugs* That didn't work, whatever")
```

This decision enables Kinda-Lang to serve both experimental chaos-driven development and more practical applications requiring controlled uncertainty.