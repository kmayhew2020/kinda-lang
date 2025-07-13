# Kinda Language – Syntax Reference

This file defines all supported Kinda constructs, their syntax, and their behavior. This is the *source of truth* for how Kinda transforms or interprets fuzzy code.

---

## ✅ Declarations

### `kinda int x = 5;`

- Declares a fuzzy integer.
- Adds random noise: value becomes `5 ± 1`.
- Stored in the environment under name `x`.

---

## ✅ Reassignments

### `x ~= 5;`

- Fuzzy reassignment of existing variable.
- New value becomes `5 ± 1`.
- Overwrites `x` in the environment.

---

## ✅ Print

### `sorta print("hello");`

- Probabilistic print.
- 80% chance it prints, 20% chance it silently skips.
- Evaluates the expression before printing.
- Output prefixed with `[print]`.

---

## ✅ Conditional Blocks

### `sometimes (x > 5) { ... }`

- Fuzzy conditional block.
- 70% chance to evaluate condition at all.
- If evaluated: block runs if condition is true.
- Otherwise: logs why it skipped.

---

## ❌ Not Yet Implemented

These are placeholder constructs reserved for future support:

- `maybe (...) { ... }`
- `meh x = ...;` – shrug assignment
- `returnish ...;`
- `whileish (...) { ... }`
- `orMaybe ...`
- `believeStrongly(...)`
- `#pragma kinda personality = "chaotic good"`
- etc.

---

## 🧪 Expression Notes

- Semicolons (`;`) are currently **required**.
- Variable names must be valid Python identifiers.
- Expressions are evaluated in Python syntax.

---

## 📜 Naming Conventions

| Standard Concept | Kinda Equivalent   |
|------------------|--------------------|
| `int`            | `kinda int`        |
| `=`              | `~=`               |
| `print(...)`     | `sorta print(...)` |
| `if (...)`       | `sometimes (...)`  |

---

