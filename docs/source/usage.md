# Usage Guide

Comprehensive guide to using kinda-lang effectively, from basic commands to advanced workflows.

## Basic Commands

### Run Kinda Programs
Transform and execute a kinda file immediately:
```bash
kinda run program.py.knda
```

### Transform Only  
Convert kinda code to target language without executing:
```bash
kinda transform program.py.knda
# Generates build/program.py with fuzzy runtime included
```

### Direct Interpretation
Run in maximum chaos mode without intermediate files:
```bash
kinda interpret program.py.knda
# Direct interpretation with full fuzzy behavior
```

### Get Help and Examples
```bash
kinda examples     # Show all available example programs
kinda syntax       # Quick syntax reference
kinda --help       # Full CLI help
```

## File Organization

### Supported File Extensions
- **`.py.knda`**: Python kinda files (fully supported)
- **`.c.knda`**: C kinda files (planned for v0.4.0)

### Directory Structure
```
your-project/
├── src/
│   ├── main.py.knda        # Your kinda programs
│   └── utils.py.knda       # 
├── examples/               # Copy examples here if desired
└── build/                  # Generated files (auto-created)
```

## Writing Kinda Programs

### Basic Syntax Rules

1. **All fuzzy constructs use `~` prefix**
2. **File extensions must include target language: `.py.knda`**
3. **Conditional blocks use `{}` syntax**
4. **Regular language syntax works normally**

### Example Program Structure

```python
# Simple kinda program: calculator.py.knda

~kinda int num1 = 10
~kinda int num2 = 5

~sorta print("Starting fuzzy calculation...")

~sometimes (num1 > num2) {
    result = num1 + num2
    ~sorta print("Sum:", result)
}

~maybe (num1 ~ish 10) {
    ~sorta print("num1 is approximately 10")
}

~kinda binary choice ~ probabilities(0.5, 0.3, 0.2)
if choice == 1:
    ~sorta print("Positive choice!")
elif choice == -1:
    ~sorta print("Negative choice!")
else:
    ~sorta print("Neutral choice!")
```

## Advanced Usage

For complex patterns and construct combinations, see the [Advanced Patterns Guide](advanced_patterns.md) which covers:
- Complex construct combinations
- Edge cases and error handling
- Production-ready fuzzy systems
- Performance optimization techniques

### Working with Examples

Copy examples to explore locally:
```bash
# View available examples
kinda examples

# Run individual construct examples
kinda run examples/python/individual/kinda_int_example.py.knda
kinda run examples/python/individual/ish_example.py.knda

# Run comprehensive scenarios
kinda run examples/python/comprehensive/fuzzy_calculator.py.knda
kinda run examples/python/comprehensive/chaos_arena_complete.py.knda
```

### Understanding Output

Kinda programs produce different output each time:

```bash
$ kinda run my_program.py.knda
[print] Starting program...
[shrug] Maybe later? Debug info
[print] Result: 42

$ kinda run my_program.py.knda  # Different output
[print] Starting program...
[print] Debug info
[shrug] *waves hand dismissively* Result: 41
```

### Debugging Kinda Programs

1. **Check transformation first:**
   ```bash
   kinda transform my_program.py.knda
   cat build/my_program.py  # See generated Python
   ```

2. **Common issues and fixes:**
   - Missing `~` prefix: `kinda int` → `~kinda int`
   - Wrong file extension: `.knda` → `.py.knda`
   - Invalid construct combinations: See Issue #59

3. **Error messages include helpful tips:**
   ```
   [?] Your code transformed fine but crashed during execution
   [shrug] Something's broken. The usual suspects:
      • Missing ~ before kinda constructs (very important)
      • General syntax weirdness
   ```

### Development Workflow

Recommended development process:

1. **Write and test incrementally:**
   ```bash
   # Start simple
   echo "~sorta print('Hello world')" > test.py.knda
   kinda run test.py.knda
   ```

2. **Check transformation when debugging:**
   ```bash
   kinda transform test.py.knda
   # Review generated build/test.py
   ```

3. **Use examples for reference:**
   ```bash
   kinda examples  # See all patterns
   # Copy and modify example patterns
   ```

4. **Test edge cases:**
   ```bash
   # Run multiple times to see fuzzy behavior
   for i in {1..5}; do kinda run test.py.knda; done
   ```

## Integration with Existing Projects

### Adding Kinda to Python Projects

1. **Identify files for fuzzification**
2. **Rename to `.py.knda` extension** 
3. **Add fuzzy constructs where desired**
4. **Use `kinda transform` in build process**

### CI/CD Integration

Example GitHub Actions workflow:
```yaml
- name: Install kinda-lang
  run: |
    git clone https://github.com/kmayhew2020/kinda-lang
    cd kinda-lang && ./install.sh

- name: Transform kinda files
  run: |
    find src -name "*.py.knda" | xargs -I {} kinda transform {}
    
- name: Test transformed files
  run: |
    python -m pytest build/
```

## Troubleshooting

### Common Issues

**"Command not found: kinda"**
```bash
# Ensure installation completed
./install.sh
# Check PATH includes kinda-lang bin directory
```

**"Cannot find source directory"**
```bash
# Ensure you're in correct directory
cd /path/to/kinda-lang
kinda run examples/python/hello.py.knda
```

**"Invalid syntax" errors**
- Check for missing `~` prefixes
- Ensure proper `{}` syntax for blocks
- Verify file has `.py.knda` extension

### Performance Considerations

- **Transform mode**: Faster for repeated runs (caches transformed files)
- **Interpret mode**: Slower but maximum fuzziness
- **Build files**: Generated in `build/` directory, can be version controlled

### Version Compatibility

- **Python**: 3.8-3.12 supported and tested
- **Operating Systems**: Ubuntu, macOS, Windows
- **Dependencies**: Automatically handled by install scripts

## Future Features

Planned improvements:
- **Package manager installation** (`pip install kinda-lang`)
- **IDE integrations** with syntax highlighting
- **Debugging tools** with fuzzy execution tracing
- **Configuration files** for personality modes
- **C language support** in v0.4.0

*"In kinda-lang, even the usage guide is kinda thorough but definitely unclear in places."* 🎲