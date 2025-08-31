# 🌀 Kinda Syntax (Python Dialect)

This file defines all supported Kinda constructs in Python-like syntax. This version uses indentation, colons, and no semicolons — suitable for Python source augmentation.

---

## ✅ Declarations

### `x: kinda int = 5`

- Declares a fuzzy integer.
- Adds random noise: value becomes `5 ± 1`.
- Stored in the environment under name `x`.

### `pi: kinda float = 3.14159`

- Declares a fuzzy floating-point variable.
- Adds personality-adjusted drift: value gets random drift within range.
- Supports scientific notation: `avogadro: kinda float = 6.02e23`.
- Drift varies by personality: reliable (±0.0), chaotic (±2.0).
- Stored in the environment under name `pi`.

### `flag: kinda bool = True`

- Declares a fuzzy boolean with personality-adjusted uncertainty.
- Value has a chance to flip based on current personality mode.
- Supports string values: `"true"`, `"false"`, `"yes"`, `"no"`, etc.
- Supports integer values: `1` (truthy), `0` (falsy).
- Uncertainty varies by personality: reliable (<5%), chaotic (>20%).

---

## ✅ Reassignments

### `x ~= 5`

- Fuzzy reassignment of an existing variable.
- New value becomes `5 ± 1`.
- Overwrites `x` in the environment.

---

## ✅ Print

### `sorta print("hello")`

- Probabilistic print.
- 80% chance it prints, 20% chance it silently skips.
- Evaluates the expression before printing.
- Output prefixed with `[print]`.

---

## ✅ Conditional Blocks

### `if sometimes(x > 5):`

```python
if sometimes(x > 5):
    sorta print("yes")
```

- 50% probability execution.
- Condition must evaluate to True AND random chance succeeds.
- Works with any boolean expression.

### `if maybe(condition):`

```python
if maybe(user.authenticated):
    sorta print("Welcome back")
```

- 60% probability execution.
- Higher chance than `sometimes` but still fuzzy.
- Good for "likely but not certain" scenarios.

### `if probably(condition):`

```python  
if probably(connection.stable):
    sorta print("Connection looks good")
```

- 70% probability execution.
- High confidence conditional - executes most of the time.
- Use when operation should usually succeed.

### `if rarely(condition):`

```python
if rarely(debug_mode_enabled):
    sorta print("Debug info: rare execution")
```

- 15% probability execution.
- Lowest probability of all conditionals.
- Perfect for debug statements, exceptional cases, or easter eggs.
- Executes infrequently even when condition is True.

---

## ✅ Fuzzy Values and Comparisons (`~ish`)

The `~ish` construct has **three distinct usage patterns** with different behaviors:

### Pattern 1: Fuzzy Value Creation (`value~ish`)

```python
# Creates fuzzy values from literals
timeout = 5~ish         # Creates value between 3-7
delay = 100~ish         # Creates value between 98-102
factor = 2.5~ish        # Creates value between ~0.5-4.5
```

- **Syntax**: `literal~ish` (number directly followed by ~ish)
- **Behavior**: Creates fuzzy value with ±2 variance from the literal
- **Use cases**: Random delays, approximate constants, test data variation

### Pattern 2: Fuzzy Comparison (`x ~ish target`)

```python
# Approximate equality checks in conditionals
score = 98
if score ~ish 100:                    # True if score is 98-102
    sorta print("Close enough!")

# Works in expressions and function calls
result = max(score ~ish 100, backup_score)
is_close = temperature ~ish ideal_temp
```

- **Syntax**: `variable ~ish target` in conditionals, expressions, function calls
- **Behavior**: Returns True/False based on ±2 tolerance comparison
- **Use cases**: Approximate equality checks, tolerance-based conditions

### Pattern 3: Variable Modification (`var ~ish value`)

```python
# Assigns fuzzy values to existing variables
balance = 100
balance ~ish 50                       # Assigns value between 48-52 to balance

# Works with expressions
temperature = 70
temperature ~ish base_temp + variance # Assigns fuzzy result to temperature

# Standalone assignment statements
health ~ish max_health // 2
score ~ish opponent_score * 1.1
```

- **Syntax**: `variable ~ish expression` as standalone statements
- **Behavior**: Evaluates expression, adds ±2 variance, assigns to variable
- **Use cases**: Variable updates with uncertainty, gradual drift, simulation

### Context-Aware Pattern Detection

The transformer automatically detects which pattern to use:

```python
# Pattern 1: Value creation (literal~ish)
x = 42~ish              # Creates fuzzy value

# Pattern 2: Comparison (in conditionals/expressions)
if x ~ish 40:           # Fuzzy comparison
    result = x ~ish 45 + other_value

# Pattern 3: Modification (standalone assignment)
x ~ish 50               # Modifies x with fuzzy assignment
```

### Personality Integration

All patterns respect current personality settings:
- **Reliable**: ±1.0 variance/tolerance (minimal fuzziness)  
- **Cautious**: ±1.5 variance/tolerance (conservative)
- **Playful**: ±2.0 variance/tolerance (standard behavior)
- **Chaotic**: ±3.0 variance/tolerance (maximum chaos)

---

## ✅ Binary Logic

### `kinda binary variable`

```python
decision: kinda binary = decision
if decision == 1:
    sorta print("Yes")
elif decision == -1:
    sorta print("No")  
else:
    sorta print("Maybe")
```

- Three-state logic: 1 (positive), 0 (neutral), -1 (negative).
- Default probabilities: 40% positive, 40% negative, 20% neutral.