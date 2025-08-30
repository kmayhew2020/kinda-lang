# Features

Kinda introduces fuzzy behavior into your existing codebase using playful, chaos-infused constructs that embrace uncertainty and add personality to your programs.

## Core Fuzzy Constructs

All kinda constructs use the `~` prefix to indicate fuzzy behavior:

### `~kinda int` - Fuzzy Integers
Declares a variable with controlled randomness (+/-1 variance):
```python
~kinda int x = 42
# x will be 41, 42, or 43
```

### `~sorta print` - Probabilistic Output  
Prints with 80% probability, provides snarky alternatives 20% of the time:
```python
~sorta print("Hello world")
# 80% chance: [print] Hello world
# 20% chance: [shrug] Maybe later? Hello world
```

### `~sometimes` - 50% Conditional Execution
Executes blocks with 50% probability:
```python
~sometimes (condition) {
    ~sorta print("This might happen")
}
```

### `~maybe` - 60% Conditional Execution  
Similar to `~sometimes` but with higher probability:
```python
~maybe (x > 10) {
    ~sorta print("Probably will execute")
}
```

### `~probably` - 70% Conditional Execution
High-confidence conditional that executes most of the time:
```python
~probably (user.is_authenticated()) {
    ~sorta print("Access granted (usually)")
}
```

### `~rarely` - 15% Conditional Execution  
Low-probability conditional that executes infrequently:
```python
~rarely (error_occurred) {
    ~sorta print("This happens rarely - debug mode?")
}
```

### `~ish` - Fuzzy Values and Comparisons
Creates fuzzy values and approximate comparisons:
```python
fuzzy_val = 100 ~ish    # ~98-102
if score ~ish target:   # Within ±2 tolerance
    ~sorta print("Close enough!")
```

### `~kinda binary` - Three-State Logic
Returns 1 (positive), 0 (neutral), or -1 (negative):
```python
~kinda binary decision ~ probabilities(0.4, 0.3, 0.3)
if decision == 1:
    ~sorta print("Yes!")
elif decision == -1:
    ~sorta print("Nope!")
else:
    ~sorta print("I'm not sure...")
```

### `~welp` - Graceful Fallbacks
Provides fallback values when operations fail:
```python
result = ~welp risky_operation() fallback 42
# If risky_operation() fails, result = 42
```

## Language Support

### Current Support
- ✅ **Python** (.py.knda): Complete support with all constructs
- ✅ **Examples**: 12 comprehensive examples from individual to complex scenarios

### Planned Support  
- 🚧 **C** (.c.knda): Planned for v0.4.0 with full compilation pipeline
- 🚧 **JavaScript**: Future consideration
- 🚧 **Java**: Future consideration

## CLI Modes

### Transform Mode
Convert kinda code to target language:
```bash
kinda transform program.py.knda
# Generates build/program.py with fuzzy runtime
```

### Run Mode  
Transform and execute immediately:
```bash
kinda run program.py.knda
# One-step execution with fuzzy behavior
```

### Interpret Mode
Direct interpretation for maximum chaos:
```bash
kinda interpret program.py.knda  
# Maximum fuzziness, no intermediate files
```

## Personality & Chaos

### Error Messages with Attitude
Kinda provides helpful but snarky error messages:
```
[?] Your code transformed fine but crashed during execution
[shrug] Something's broken. The usual suspects:
   • Missing ~ before kinda constructs (very important)
   • General syntax weirdness
```

### Controlled Randomness
- Fuzzy behavior is controlled and predictable in range
- Each run produces different results (embracing uncertainty)
- Errors include helpful debugging tips with personality

### Future Personality Modes
Planned personality configurations:
- **Optimist**: "This will probably work!"
- **Cynic**: "This'll probably break..."  
- **Trickster**: Extra randomness and chaos
- **Pedantic**: Minimal fuzziness, maximum accuracy

## Example Workflows

### Individual Learning
```bash
kinda examples                    # See all available examples
kinda run examples/python/individual/kinda_int_example.py.knda
```

### Comprehensive Scenarios
```bash
kinda run examples/python/comprehensive/fuzzy_calculator.py.knda
kinda run examples/python/comprehensive/chaos_arena_complete.py.knda
```

### Development Workflow
```bash
kinda transform my_program.py.knda  # Check transformation
kinda run my_program.py.knda        # Test execution
kinda syntax                        # Quick reference
```

## Philosophy

Kinda embraces the philosophy that:
- **Uncertainty is normal** - perfect code is suspicious
- **Personality matters** - tools should be fun to use
- **Controlled chaos** - randomness within useful bounds
- **Augmentation over replacement** - enhance existing languages, don't replace them

*"In kinda-lang, even the documentation is kinda comprehensive."* 🎲