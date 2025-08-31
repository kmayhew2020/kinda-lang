# 🤷 Kinda

> A programming language for people who aren't totally sure.

**Kinda** adds fuzzy logic and personality to your code. It's for developers who write code like _"I mean… this should work, right?"_

## ⚡ Quick Start

```bash
# Install
pip install kinda-lang

# Try it out 
kinda examples
kinda syntax
kinda run examples/hello.py.knda
```

## 🎲 What Makes Kinda Special?

Kinda introduces **uncertainty as a first-class concept** with the `~` (tilde) prefix:

```kinda
~kinda int x ~= 42       # Fuzzy integer (adds ±1 noise)
~kinda bool ready ~= True # Fuzzy boolean (might flip to False)

# Time-based drift - variables get fuzzier over program lifetime
~time drift float temp ~= 98.6  # Starts precise, drifts with age/usage
~time drift int count ~= 100    # Accumulates uncertainty over time

# ~ish construct - three distinct usage patterns:
timeout = 5~ish          # 1. Value creation: creates fuzzy value (3-7 range)
score = 98
if score ~ish 100 {     # 2. Comparison: fuzzy equality check (98-102 tolerance)  
    ~sorta print("Close enough!")
}
score ~ish 85           # 3. Variable modification: assigns fuzzy value (83-87 range) to score

~sorta print("Hello!")   # Maybe prints (80% chance)  
~sometimes (x > 40) {    # Random conditional (50% chance)
    ~sorta print("Probably big!")
    x ~= x + 1           # Fuzzy reassignment
} {                      # Else block - runs when condition fails
    ~sorta print("Not so big...")
}
~probably (ready) {      # Use the fuzzy boolean 
    ~sorta print("System ready!")
} {                      # Else block for ~probably too
    ~sorta print("Not ready yet...")
}

# Access drift variables - uncertainty grows with each access
for i in range(10) {
    reading = temp~drift    # Gets increasingly fuzzy value
    ~sorta print("Reading:", reading)
}
```

**Every time you run this, it behaves differently.** That's the point.

## 🚀 Installation

### Option 1: pip (recommended)
```bash
pip install kinda-lang
```

### Option 2: From source  
```bash
git clone https://github.com/kmayhew2020/kinda-lang.git
cd kinda-lang
pip install -e .
```

### Verify installation
```bash
kinda --help    # Should show snarky help messages
kinda examples  # Try some examples
```

**Supports:** Linux, macOS, Windows • Python 3.8+

## 📖 Usage

### Commands
- `kinda run file.py.knda` - Transform and execute 
- `kinda interpret file.py.knda` - Run in fuzzy runtime (max chaos)
- `kinda transform file.py.knda` - Just transform to regular Python
- `kinda examples` - See example programs
- `kinda syntax` - Quick syntax reference

### Syntax Reference

| Kinda Construct | What It Does | Example |
|-----------------|--------------|---------|
| `~kinda int x ~= 42` | Fuzzy integer (±1 noise) | `x` might be 41, 42, or 43 |
| `~kinda float pi ~= 3.14` | Fuzzy floating-point (drift) | `pi` might be 3.139, 3.141, or 3.642 with personality-adjusted drift |
| `~kinda bool flag ~= True` | Fuzzy boolean (uncertainty flip) | Sometimes flips True/False based on personality |
| `42~ish` | Fuzzy value creation (±2 variance) | Returns 40-44 randomly |  
| `score ~ish 100` | Fuzzy comparison (±2 tolerance) | True if score is 98-102 |
| `var ~ish 50` | Fuzzy variable modification | Assigns 48-52 randomly to `var` |
| `~kinda binary decision` | Three-state binary | Returns 1 (yes), -1 (no), or 0 (undecided) |
| `~sorta print(msg)` | Maybe prints (80% chance) | Sometimes prints, sometimes `[shrug]` |
| `~sometimes (cond) {} {}` | Random conditional (50%) | Block runs if both random AND condition, optional else |
| `~maybe (cond) {} {}` | Less random conditional (60%) | More likely than ~sometimes but still fuzzy, optional else |
| `~probably (cond) {} {}` | Confident conditional (70%) | Higher confidence than ~maybe, optional else |
| `~rarely (cond) {} {}` | Low-probability conditional (15%) | Executes infrequently, lowest chance of all conditionals |
| `x ~= x + 1` | Fuzzy assignment | Adds 1 ± random noise |

## 🎯 Why Use Kinda?

- **Test code resilience** - See how your logic handles randomness
- **Simulate real-world uncertainty** - Model unreliable systems  
- **Debug by chaos** - Find edge cases through controlled randomness
- **Have fun** - Your compiler has personality and attitude

## 🔧 Development

```bash
git clone https://github.com/kmayhew2020/kinda-lang.git
cd kinda-lang
pip install -e .[dev]
pytest tests/                  # Run test suite
pytest --cov=kinda tests/      # Run with coverage report (94% coverage)
```

## 🤝 Contributing

Pull requests welcome! Kinda is chaos, but organized chaos.

- File issues for bugs or feature requests
- Add more fuzzy constructs
- Improve the snark level
- Help with other language support (C is next!)

## 📜 License

AGPL v3 - Use it, break it, fix it, but share the fixes. We're not responsible if kinda makes your code too honest about what it actually does.

---

*"Sometimes the best way to make software reliable is to admit it was never reliable in the first place."* 🎲