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

### `~kinda float` - Fuzzy Floating-Point
Declares a fuzzy floating-point variable with personality-adjusted drift:
```python
~kinda float pi = 3.14159
# pi might be 3.139, 3.141, or 3.642 depending on personality

~kinda float temperature = 98.6
~kinda float pressure = 14.7
# Both get personality-adjusted drift

# Works with scientific notation
~kinda float avogadro = 6.02e23
~kinda float planck = 6.626e-34
```

**Personality Effects on Float Drift:**
- **Reliable**: Minimal drift (±0.0), maintains precision
- **Cautious**: Small drift (±0.2), conservative variance  
- **Playful**: Standard drift (±0.5), balanced randomness
- **Chaotic**: High drift (±2.0), maximum variance

**Use Cases:**
- Simulating sensor noise and measurement uncertainty
- Testing numerical algorithm robustness  
- Modeling real-world floating-point precision issues
- Adding controlled randomness to scientific simulations

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

### `~ish` - Fuzzy Values, Comparisons, and Variable Modification

The `~ish` construct provides three distinct usage patterns that address different fuzzy programming needs:

#### Pattern 1: Fuzzy Value Creation
Creates fuzzy values with ±2 variance from literals:
```python
timeout = 5~ish         # Creates value between 3-7
delay = 100~ish         # Creates value between 98-102
pi_ish = 3.14~ish       # Creates value between ~1.14-5.14
```
**Use cases**: Random delays, approximate values, testing with variance

#### Pattern 2: Fuzzy Comparison 
Performs approximate equality checks with ±2 tolerance:
```python
score = 98
if score ~ish 100:      # True if score is 98-102
    ~sorta print("Close enough!")

health = 75
if health ~ish max_health:  # Compares with tolerance
    ~sorta print("Nearly full health!")
```
**Use cases**: Approximate equality, tolerance-based conditionals, "good enough" checks

#### Pattern 3: Variable Modification
Assigns fuzzy values back to existing variables:
```python
balance = 100
balance ~ish 50         # Assigns value between 48-52 to balance

temperature = 70
temperature ~ish base_temp + variance  # Assigns fuzzy result to temperature
```
**Use cases**: Variable updates with uncertainty, gradual value drift, simulation

#### Context-Aware Behavior
The transformer automatically detects which pattern to use based on context:
- **Value creation**: `literal~ish` (e.g., `42~ish`)
- **Comparison**: `var ~ish target` in conditionals, expressions, function calls
- **Modification**: `var ~ish value` as standalone statements

#### Personality System Integration
All ~ish patterns respect personality settings:
- **Reliable**: Minimal variance (±1.0), tight tolerance (±1.0)
- **Cautious**: Moderate variance (±1.5), relaxed tolerance (±1.5) 
- **Playful**: Standard variance (±2.0), standard tolerance (±2.0)
- **Chaotic**: High variance (±3.0), loose tolerance (±3.0)

#### Common Usage Examples
```python
# Mixed pattern usage
base_score = 100~ish           # Pattern 1: Create fuzzy value
if base_score ~ish 100:        # Pattern 2: Compare with tolerance
    base_score ~ish 95         # Pattern 3: Modify variable
    ~sorta print("Adjusted score:", base_score)
```

### `~kinda bool` - Fuzzy Boolean
Declares fuzzy booleans with personality-adjusted uncertainty that can flip values:
```python
~kinda bool ready ~= True      # Might flip to False sometimes
~kinda bool active = "yes"     # String values converted to booleans
~kinda bool enabled = 1        # Integer values treated as booleans

# Uncertainty varies by personality:
# reliable: <5% chance of flipping
# chaotic: >20% chance of flipping
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

## Time-Based Variable Drift

Variables in kinda-lang can accumulate uncertainty over program lifetime, simulating real-world software degradation like memory leaks, accumulated errors, and thermal drift.

### `~time drift float` - Floating-Point with Time-Based Drift
Creates floating-point variables that become fuzzier with age and usage:
```python
~time drift float temperature = 98.6  # Starts precise
# After 1000 operations: temperature might be ~98.7
# After 10000 operations: temperature might be ~98.2  
# After 100000 operations: temperature might be ~99.1
```

**Drift Accumulation Factors:**
- **Age**: Older variables drift more (logarithmic scaling)
- **Usage**: More frequently accessed variables accumulate drift
- **Recency**: Recent activity causes more immediate drift
- **Personality**: Drift rate controlled by personality profiles

### `~time drift int` - Integer with Time-Based Drift  
Creates integer variables that drift over time:
```python
~time drift int count = 100          # Fresh variable, mostly precise
count~drift                         # Access with current drift applied
# Each access accumulates more uncertainty
```

### Variable Access with Drift: `~drift`
Access variables with accumulated time-based uncertainty:
```python
~time drift float sensor_reading = 25.0
~time drift int packet_count = 1000

# Each access applies accumulated drift
current_reading = sensor_reading~drift    # Gets drifted value
current_count = packet_count~drift        # Integer with accumulated fuzz

# Drift increases with each access and time passage
for i in range(100):
    reading = sensor_reading~drift        # More drift each time
    count = packet_count~drift           # Accumulates uncertainty
```

### Personality Effects on Time Drift
Drift behavior varies significantly by personality:

- **Reliable** (`drift_rate=0.0`): No time-based drift - variables stay precise
- **Cautious** (`drift_rate=0.01`): Very slow drift, minimal degradation
- **Playful** (`drift_rate=0.05`): Moderate drift, balanced uncertainty growth
- **Chaotic** (`drift_rate=0.1`): Fast drift, rapid uncertainty accumulation

### Real-World Simulation Examples
Time drift enables realistic system behavior modeling:

```python
# System monitoring with degradation
~time drift float memory_usage = 256.0
~time drift float cpu_temp = 45.0
~time drift int error_count = 0

# Over time, values become less reliable
for hour in range(100):
    ~maybe (memory_usage~drift > 400.0):
        ~sorta print("Memory leak detected!")
        error_count~drift = error_count~drift + 1
    
    ~sometimes (cpu_temp~drift > 80.0):
        ~sorta print("CPU overheating!")
```

**Use Cases:**
- Modeling sensor degradation and calibration drift
- Simulating memory leaks and resource consumption  
- Testing system resilience to parameter uncertainty
- Representing accumulated floating-point precision errors
- Educational demonstrations of real-world software degradation

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