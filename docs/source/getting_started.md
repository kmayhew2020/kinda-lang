# Getting Started

Welcome to **Kinda** - a programming language for people who aren't totally sure!

Kinda augments existing Python (and eventually C) with fuzzy constructs that embrace uncertainty, personality, and controlled chaos.

## Installation

### From Source (Current)
```bash
git clone https://github.com/kmayhew2020/kinda-lang
cd kinda-lang
./install.sh  # or install.bat on Windows
```

### Package Installation (Future)
```bash
pip install kinda-lang  # Coming soon
```

## Quick Start

### 1. Write Your First Kinda Program

Create a file called `hello.py.knda`:

```python
~kinda int x = 42
~sorta print("Hello,", x)

~sometimes (x > 40) {
    ~sorta print("That's a big number!")
}
```

### 2. Run Your Program

```bash
kinda run hello.py.knda
```

Output (varies each time):
```
[print] Hello, 43
[shrug] Meh... That's a big number!
```

### 3. Explore All Constructs

Try these fuzzy constructs in your code:

- **`~kinda int`**: Fuzzy integers with +/-1 variance
- **`~sorta print`**: Prints 80% of the time, shrugs the rest
- **`~sometimes`**: 50% chance conditional execution  
- **`~maybe`**: 60% chance conditional execution
- **`~ish`**: Fuzzy values and comparisons
- **`~kinda binary`**: Three-state logic (1/0/-1)
- **`~welp`**: Graceful fallback handling

## CLI Commands

```bash
kinda examples     # Show example programs
kinda syntax       # Quick syntax reference
kinda transform    # Transform to Python without running
kinda interpret    # Maximum chaos mode (direct interpretation)
```

## Examples

See comprehensive examples with:
```bash
kinda examples
```

All examples are in the `examples/python/` directory with both individual construct demos and comprehensive scenarios.
