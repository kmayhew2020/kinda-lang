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
~sorta print("Hello!")   # Maybe prints (80% chance)  
~sometimes (x > 40) {    # Random conditional (50% chance)
    ~sorta print("Probably big!")
    x ~= x + 1           # Fuzzy reassignment
}
~maybe (x > 39) {        # More likely conditional (60% chance)
    ~sorta print("Quite likely big!")
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
| `~sorta print(msg)` | Maybe prints (80% chance) | Sometimes prints, sometimes `[shrug]` |
| `~sometimes (cond) {}` | Random conditional (50%) | Block runs if both random AND condition |
| `~maybe (cond) {}` | Less random conditional (60%) | More likely than ~sometimes but still fuzzy |
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
pytest tests/
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