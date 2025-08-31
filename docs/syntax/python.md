# 🌀 Kinda Syntax (Python Dialect)

This file defines all supported Kinda constructs in Python-like syntax. This version uses indentation, colons, and no semicolons — suitable for Python source augmentation.

---

## ✅ Declarations

### `x: kinda int = 5`

- Declares a fuzzy integer.
- Adds random noise: value becomes `5 ± 1`.
- Stored in the environment under name `x`.

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

## ✅ Fuzzy Values

### `value~ish`

```python
fuzzy_number = 100~ish
```

- Creates fuzzy value with ±2 variance.
- `100~ish` returns value between ~98-102.

### `x ~ish target`

```python
if score ~ish 100:
    sorta print("Close enough!")
```

- Fuzzy comparison with ±2 tolerance.
- Returns True if values are within tolerance range.

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