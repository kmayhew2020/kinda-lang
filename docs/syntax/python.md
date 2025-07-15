# 🌀 Kinda Syntax (Python Dialect)

This file defines all supported Kinda constructs in Python-like syntax. This version uses indentation, colons, and no semicolons — suitable for Python source augmentation.

---

## ✅ Declarations

### `x: kinda int = 5`

- Declares a fuzzy integer.
- Adds random noise: value becomes `5 ± 1`.
- Stored in the environment under name `x`.

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