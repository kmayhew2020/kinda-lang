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

### Chaos Control
Kinda gives you fine-grained control over randomness intensity:

```bash
# Chaos Level (1-10 scale) - controls all fuzzy behavior
kinda run mycode.py.knda --chaos-level 1   # Minimal chaos (predictable)
kinda run mycode.py.knda --chaos-level 5   # Medium chaos (default)
kinda run mycode.py.knda --chaos-level 10  # Maximum chaos (wild)

# Personality Moods - overall behavior style
kinda run mycode.py.knda --mood reliable   # Conservative, high success rates
kinda run mycode.py.knda --mood cautious   # Moderate uncertainty
kinda run mycode.py.knda --mood playful    # Standard kinda behavior (default)
kinda run mycode.py.knda --mood chaotic    # Embrace the chaos

# Combine both for precise control
kinda run mycode.py.knda --mood reliable --chaos-level 1   # Maximum predictability
kinda run mycode.py.knda --mood chaotic --chaos-level 10   # Absolute chaos
```

**Chaos Level Effects:**
- **Level 1-2**: Minimal chaos - fuzzy constructs behave almost deterministically  
- **Level 3-4**: Low chaos - slight unpredictability, small variance
- **Level 5-6**: Medium chaos - balanced randomness (default behavior)
- **Level 7-8**: High chaos - significant randomness and variance
- **Level 9-10**: Maximum chaos - highly unpredictable, extreme variance

Try the demo to see the difference:
```bash
kinda run examples/python/chaos_level_demo.py.knda --chaos-level 1
kinda run examples/python/chaos_level_demo.py.knda --chaos-level 10
```

### Reproducible Chaos with Seeds

Kinda supports **reproducible randomness** using the `--seed` flag, perfect for testing, debugging, or when you need "deterministic chaos":

```bash
# Same seed = identical output every time
kinda run mycode.py.knda --seed 12345
kinda run mycode.py.knda --seed 12345  # Produces identical results

# Different seed = different but reproducible results  
kinda run mycode.py.knda --seed 99999  # Different output, but consistent

# Environment variable support
export KINDA_SEED=42
kinda run mycode.py.knda              # Uses KINDA_SEED=42
kinda run mycode.py.knda --seed 777   # CLI overrides environment (uses 777)

# Seeds work with all personality combinations
kinda run mycode.py.knda --seed 555 --mood reliable --chaos-level 2
kinda run mycode.py.knda --seed 555 --mood chaotic --chaos-level 8   # Same seed, different personality
```

**Seed Features:**
- **Deterministic**: Same seed + same mood/chaos-level = identical output
- **Cross-run**: Seeds persist across transform/run/interpret commands  
- **Secure**: Automatic bounds checking prevents unsafe seed values
- **Flexible**: Works with environment variables (KINDA_SEED) and CLI flags

Try the seed demonstration:

```bash
kinda run examples/python/seed_demo.py.knda --seed 42
kinda run examples/python/seed_demo.py.knda --seed 42    # Identical output
kinda run examples/python/seed_demo.py.knda --seed 1337  # Different output
```

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
| `~assert_eventually (condition, timeout=5.0, confidence=0.95)` | Statistical assertion for probabilistic conditions | Waits for fuzzy condition to become statistically true |
| `~assert_probability (event, expected_prob=0.5, tolerance=0.1, samples=1000)` | Statistical validation of probability distributions | Validates event probability matches expectations |
| `x ~= x + 1` | Fuzzy assignment | Adds 1 ± random noise |

### Statistical Testing: "Kinda Tests Kinda"

Kinda includes powerful statistical assertions for testing fuzzy and probabilistic behavior:

```kinda
# Test that probabilistic conditions eventually succeed
~assert_eventually (~sometimes True, timeout=5.0, confidence=0.95)

# Validate probability distributions of fuzzy constructs  
~assert_probability (~maybe True, expected_prob=0.6, tolerance=0.1, samples=1000)

# KINDA TESTS KINDA: Use kinda constructs to test other kinda constructs!
~kinda int counter = 0
~sometimes { counter = counter + 1 }
~assert_eventually (counter > 0, timeout=2.0, confidence=0.9)
```

**Statistical Features:**
- **~assert_eventually**: Wait for probabilistic conditions with statistical confidence
- **~assert_probability**: Validate probability distributions of fuzzy events  
- **Seed integration**: Reproducible statistical testing with `--seed` flag
- **Personality-aware**: Error messages match your chosen mood/chaos level
- **Wilson score intervals**: Proper statistical confidence bounds

Try the statistical testing demo:
```bash
kinda run examples/python/statistical_testing_demo.py.knda --seed 42
```

## 🎯 Why Use Kinda?

- **Test code resilience** - See how your logic handles randomness
- **Simulate real-world uncertainty** - Model unreliable systems  
- **Debug by chaos** - Find edge cases through controlled randomness
- **Statistical validation** - Verify fuzzy behavior meets expectations
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

---

## 🏢 Enterprise & Professional Use

**Kinda for Mission-Critical Systems**

While Kinda started as a playful language for uncertainty, it has proven valuable for serious applications where traditional testing falls short:

### **🛰️ Aerospace & Defense Applications**
- **External code analysis** to find edge cases in spacecraft software
- **Physics-based chaos models** for space radiation, EMI, hardware aging
- **Mission-critical system validation** where failure is not an option

### **⚡ Critical Infrastructure**
- **Nuclear power** control system testing
- **Medical device** software validation  
- **Financial trading** platform resilience
- **Industrial automation** fault tolerance

### **💼 Commercial Licensing**
For production systems and proprietary applications:
- ✅ **No copyleft obligations** on your code
- ✅ **Professional support** and custom development
- ✅ **Security clearance** support for classified systems
- ✅ **Certification assistance** for regulatory compliance

📄 **[Enterprise Information](./ENTERPRISE.md)** | 📄 **[Licensing Options](./LICENSE-DUAL.md)**

---

## 📜 License

**Dual Licensed:**
- 🆓 **[Open Source (AGPL v3)](./LICENSE)** - Research, education, open source projects
- 💼 **[Commercial License](./LICENSE-COMMERCIAL.md)** - Production, proprietary, classified systems

**Which license do you need?** See our **[Licensing Guide](./LICENSE-DUAL.md)**

---

*"Sometimes the best way to make software reliable is to admit it was never reliable in the first place."* 🎲

*For mission-critical systems: "Sometimes the best way to find critical bugs is to systematically inject controlled chaos."* 🛰️