# Python Injection Framework - CLI Interface Specification

## 📋 Document Overview
**Epic**: #127 Python Injection Framework
**Target Release**: v0.5.5 "Python Enhancement Bridge"
**CLI Design Date**: 2025-09-15
**Status**: Design Phase

This document defines the command-line interface for the Python Injection Framework, extending the existing `kinda` CLI with injection-specific commands and workflows.

## 🎯 CLI Design Goals

### User Experience Objectives
1. **Intuitive Discovery**: Natural extension of existing `kinda` command patterns
2. **Progressive Complexity**: Simple commands for basic use, advanced options for power users
3. **Consistent Behavior**: Maintain existing CLI personality and error handling patterns
4. **Clear Feedback**: Comprehensive status reporting and guidance for users
5. **Safety First**: Built-in safeguards and backup mechanisms

### Integration Requirements
- Extend existing `kinda/cli.py` without breaking changes
- Leverage existing personality system (`--mood`, `--chaos-level`, `--seed`)
- Integrate with current security framework and validation
- Maintain consistent error handling and user messaging patterns

## 🛠️ Command Structure Overview

### New Command Hierarchy
```
kinda inject                    # Main injection command group
├── run <file>                  # Inject and execute Python file
├── analyze <file>              # Analyze injection opportunities
├── convert <file>              # Convert to injected version
├── validate <file>             # Validate injection compatibility
└── examples                    # Show injection examples
```

### Existing Command Extensions
```
kinda run <file.py>            # Auto-detect injection if decorators present
kinda transform <file.py>      # Support Python injection transformation
```

## 📝 Detailed Command Specifications

### 1. `kinda inject run` - Inject and Execute

**Purpose**: Inject probabilistic constructs into Python file and execute immediately

**Syntax**:
```bash
kinda inject run <file> [options]
```

**Arguments**:
- `<file>`: Python file to inject and run (`.py` or `.py.knda`)

**Options**:
```bash
--level {basic,intermediate,advanced}     # Injection complexity level (default: basic)
--patterns <pattern1,pattern2,...>       # Specific patterns to inject
--inplace                                 # Modify original file (with backup)
--backup                                  # Force backup creation (default: true)
--dry-run                                 # Show what would be injected without executing
--output <file>                          # Write injected code to specific file
--debug-injection                        # Show detailed injection process
--safety-mode {strict,normal,permissive} # Safety level for injection validation
```

**Personality Integration**:
```bash
--mood {reliable,cautious,playful,chaotic}  # Injection personality
--chaos-level {1-10}                       # Control randomness intensity
--seed <number>                             # Reproducible injection behavior
```

**Examples**:
```bash
# Basic injection and execution
kinda inject run my_script.py

# Advanced injection with specific patterns
kinda inject run my_script.py --level advanced --patterns "sometimes,maybe,kinda_int"

# Dry run to preview injection
kinda inject run my_script.py --dry-run --debug-injection

# Inject with playful personality and backup
kinda inject run my_script.py --mood playful --backup --output enhanced_script.py
```

**Expected Output**:
```
🎲 Analyzing 'my_script.py' for injection opportunities...
📊 Found 12 injection points:
   • 3 variable assignments (kinda_int candidates)
   • 2 conditional statements (sometimes/maybe candidates)
   • 1 print statement (sorta_print candidate)
   • 6 function calls (welp fallback candidates)

🔧 Injecting probabilistic constructs (level: basic)...
   ✅ Injected kinda_int for variable 'counter'
   ✅ Added sometimes conditional to main loop
   ✅ Enhanced print statement with sorta_print

💾 Created backup: my_script.py.bak
🎮 Running enhanced Python code...
[Script output with probabilistic behavior]
🎉 Injection and execution complete!
```

---

### 2. `kinda inject analyze` - Analyze Injection Opportunities

**Purpose**: Analyze Python file for injection opportunities without modification

**Syntax**:
```bash
kinda inject analyze <file> [options]
```

**Arguments**:
- `<file>`: Python file to analyze

**Options**:
```bash
--patterns <pattern1,pattern2,...>       # Focus on specific patterns
--level {basic,intermediate,advanced}    # Analysis depth level
--report {summary,detailed,json}         # Report format
--export <file>                          # Export analysis to file
--show-code                              # Show code snippets for each opportunity
--estimate-impact                        # Estimate performance impact
--security-check                         # Include security analysis
```

**Examples**:
```bash
# Basic analysis
kinda inject analyze my_script.py

# Detailed analysis with code snippets
kinda inject analyze my_script.py --report detailed --show-code

# Focus on specific patterns
kinda inject analyze my_script.py --patterns "sometimes,kinda_int" --export analysis.json

# Security-focused analysis
kinda inject analyze my_script.py --security-check --level advanced
```

**Expected Output**:
```
📊 Injection Analysis Report for 'my_script.py'
=====================================

📈 Summary:
   • File size: 234 lines, 45 functions
   • Injection opportunities: 18 found
   • Estimated performance impact: <5%
   • Security status: ✅ Safe for injection

🎯 Injection Opportunities by Pattern:

   1. Variable Assignments (8 opportunities)
      • Line 12: counter = 0              → ~kinda int counter = 0
      • Line 25: result = calculate()     → result = ~welp calculate() 42
      • Line 33: threshold = 10           → ~kinda int threshold = 10
      [Show more with --show-code]

   2. Conditional Statements (4 opportunities)
      • Line 45: if user_input:           → ~sometimes (user_input) {
      • Line 78: if result > threshold:   → ~maybe (result > threshold) {
      [Show more with --show-code]

   3. Loop Constructs (3 opportunities)
      • Line 56: for item in items:       → ~maybe_for item in items:
      • Line 89: while processing:        → ~sometimes_while (processing):
      [Show more with --show-code]

   4. Print Statements (3 opportunities)
      • Line 67: print(f"Result: {r}")    → ~sorta print(f"Result: {r}")
      [Show more with --show-code]

💡 Recommendations:
   • Start with 'basic' level injection for gradual adoption
   • Focus on non-critical paths for initial experimentation
   • Consider 'sometimes' patterns for optional features

🔒 Security Analysis:
   • No dangerous patterns detected
   • All injection points are safe for enhancement
   • Recommended safety mode: normal
```

---

### 3. `kinda inject convert` - Convert to Injected Version

**Purpose**: Create an enhanced version with probabilistic constructs injected

**Syntax**:
```bash
kinda inject convert <file> [options]
```

**Arguments**:
- `<file>`: Python file to convert

**Options**:
```bash
--output <file>                          # Output file (default: <file>_enhanced.py)
--level {basic,intermediate,advanced}    # Conversion complexity level
--gradual                                # Gradual conversion mode (minimal changes)
--functions <func1,func2,...>            # Convert specific functions only
--classes <class1,class2,...>            # Convert specific classes only
--patterns <pattern1,pattern2,...>       # Use specific patterns only
--preserve-behavior                      # Minimize behavioral changes
--aggressive                             # Maximum injection opportunities
--interactive                            # Interactive conversion with choices
```

**Examples**:
```bash
# Basic conversion
kinda inject convert my_script.py

# Gradual conversion of specific functions
kinda inject convert my_script.py --gradual --functions "main,process_data"

# Interactive conversion with user choices
kinda inject convert my_script.py --interactive --level intermediate

# Aggressive conversion to output file
kinda inject convert my_script.py --aggressive --output chaos_script.py
```

**Expected Output**:
```
🔄 Converting 'my_script.py' to enhanced version...

🎯 Conversion Plan (level: basic):
   • Target functions: main, process_data, calculate_result
   • Patterns to apply: kinda_int, sometimes, sorta_print
   • Estimated changes: 12 enhancements

🛠️ Applying conversions:
   ✅ Enhanced variable 'counter' with kinda_int (line 12)
   ✅ Added sometimes conditional to user input check (line 45)
   ✅ Converted print statement to sorta_print (line 67)
   ✅ Added welp fallback to API call (line 89)
   [... 8 more changes]

📝 Generated enhanced version: my_script_enhanced.py
📊 Conversion Summary:
   • Original lines: 234
   • Enhanced lines: 251
   • Injection points used: 12/18 available
   • Estimated behavioral change: Minimal (preserves core logic)

💡 Next Steps:
   • Test enhanced version: kinda run my_script_enhanced.py
   • Compare behaviors: python my_script.py vs kinda run my_script_enhanced.py
   • Gradually increase injection level for more chaos!
```

---

### 4. `kinda inject validate` - Validate Injection Compatibility

**Purpose**: Validate that a Python file is compatible with injection framework

**Syntax**:
```bash
kinda inject validate <file> [options]
```

**Arguments**:
- `<file>`: Python file to validate

**Options**:
```bash
--strict                                 # Strict validation mode
--report {summary,detailed,json}         # Validation report format
--check-dependencies                     # Validate library compatibility
--security-scan                          # Comprehensive security scan
--performance-check                      # Analyze performance implications
```

**Examples**:
```bash
# Basic validation
kinda inject validate my_script.py

# Strict validation with dependency check
kinda inject validate my_script.py --strict --check-dependencies

# Comprehensive validation
kinda inject validate my_script.py --security-scan --performance-check --report detailed
```

**Expected Output**:
```
🔍 Validating 'my_script.py' for injection compatibility...

✅ Syntax Validation: PASSED
   • Valid Python syntax detected
   • No parsing errors found

✅ Security Validation: PASSED
   • No dangerous patterns detected
   • No security vulnerabilities found
   • Safe for probabilistic injection

✅ Dependency Validation: PASSED
   • Compatible libraries: numpy, pandas, requests
   • No conflicting imports detected
   • Runtime integration: Compatible

⚠️  Performance Validation: WARNING
   • Large loops detected (lines 45-89)
   • Recommendation: Use selective injection for performance-critical sections
   • Estimated overhead with full injection: 8-12%

📊 Validation Summary:
   • Overall compatibility: ✅ EXCELLENT
   • Injection readiness: ✅ READY
   • Recommended injection level: basic → intermediate
   • Security risk: None
   • Performance risk: Low

💡 Recommendations:
   • Start with basic injection level
   • Focus on non-critical code paths initially
   • Monitor performance with gradual enhancement
```

---

### 5. `kinda inject examples` - Show Injection Examples

**Purpose**: Display example injection patterns and use cases

**Syntax**:
```bash
kinda inject examples [options]
```

**Options**:
```bash
--pattern <pattern_name>                 # Show examples for specific pattern
--level {basic,intermediate,advanced}    # Show examples for injection level
--use-case <use_case>                    # Show examples for specific use case
--interactive                            # Interactive example explorer
```

**Examples**:
```bash
# Show all injection examples
kinda inject examples

# Show examples for specific pattern
kinda inject examples --pattern sometimes

# Show advanced level examples
kinda inject examples --level advanced

# Interactive example explorer
kinda inject examples --interactive
```

**Expected Output**:
```
🎲 Kinda-Lang Injection Examples

📚 Basic Injection Patterns:

1. Variable Enhancement:
   Before: counter = 0
   After:  ~kinda int counter = 0
   Effect: Adds ±1 fuzzy noise to variable

2. Conditional Enhancement:
   Before: if user_ready:
   After:  ~sometimes (user_ready) {
   Effect: 50% probability of execution

3. Print Enhancement:
   Before: print("Processing...")
   After:  ~sorta print("Processing...")
   Effect: 80% probability of output

4. Function Call Safety:
   Before: result = risky_api_call()
   After:  result = ~welp risky_api_call() "default_value"
   Effect: Graceful fallback on failure

📈 Real-World Use Cases:

🎮 Game Development:
   # Add uncertainty to game mechanics
   damage = ~kinda int base_damage
   ~sometimes (critical_hit) {
       damage *= 2
   }

🧪 Scientific Simulation:
   # Add measurement uncertainty
   temperature = ~kinda float sensor_reading
   ~maybe (calibration_needed) {
       temperature = calibrate(temperature)
   }

📊 Data Processing:
   # Graceful degradation for missing data
   processed = ~welp process_data(raw_data) []
   ~sorta print(f"Processed {len(processed)} items")

💡 Try these examples:
   • kinda inject convert examples/basic_game.py
   • kinda inject run examples/scientific_sim.py --level intermediate
   • kinda inject analyze examples/data_pipeline.py --patterns "welp,sorta_print"
```

---

## 🔧 Integration with Existing CLI

### Extension Points in `kinda/cli.py`

**Main Parser Extension**:
```python
def add_injection_commands(parser: argparse.ArgumentParser):
    """
    Add injection command group to existing kinda CLI
    """
    # Create injection subcommand group
    inject_parser = parser.add_subparsers(dest='inject_command')
    inject_main = inject_parser.add_parser('inject',
                                         help='Python injection framework commands')

    # Add injection-specific subcommands
    inject_sub = inject_main.add_subparsers(dest='inject_action', required=True)

    # inject run
    run_parser = inject_sub.add_parser('run', help='Inject and execute Python file')
    setup_inject_run_parser(run_parser)

    # inject analyze
    analyze_parser = inject_sub.add_parser('analyze', help='Analyze injection opportunities')
    setup_inject_analyze_parser(analyze_parser)

    # inject convert
    convert_parser = inject_sub.add_parser('convert', help='Convert to injected version')
    setup_inject_convert_parser(convert_parser)

    # inject validate
    validate_parser = inject_sub.add_parser('validate', help='Validate injection compatibility')
    setup_inject_validate_parser(validate_parser)

    # inject examples
    examples_parser = inject_sub.add_parser('examples', help='Show injection examples')
    setup_inject_examples_parser(examples_parser)
```

**Enhanced Command Detection**:
```python
def enhanced_detect_language(path: Path, forced: str = None) -> str:
    """
    Enhanced language detection supporting injection syntax
    """
    if forced:
        return forced.lower()

    # Check for injection decorators in Python files
    if path.suffix == '.py':
        content = safe_read_file(path)
        if has_injection_decorators(content):
            return "python-injection"

    # Existing detection logic
    return detect_language(path, forced)

def has_injection_decorators(content: str) -> bool:
    """
    Check if Python file contains injection decorators
    """
    injection_patterns = [
        r'@inject\.',
        r'from kinda import inject',
        r'import kinda.inject',
        r'~sometimes\s*\{',
        r'~maybe\s*\{',
        r'~kinda\s+\w+'
    ]

    for pattern in injection_patterns:
        if re.search(pattern, content):
            return True
    return False
```

**Personality System Integration**:
```python
def setup_injection_personality(args) -> InjectionPersonality:
    """
    Setup personality system for injection operations
    """
    # Leverage existing personality setup
    setup_personality(
        getattr(args, 'mood', None),
        getattr(args, 'chaos_level', 5),
        getattr(args, 'seed', None)
    )

    # Create injection-specific personality configuration
    return InjectionPersonality(
        base_personality=PersonalityContext.current(),
        injection_aggressiveness=get_injection_aggressiveness(args),
        safety_preference=get_safety_preference(args),
        user_experience_level=get_user_experience_level(args)
    )
```

### Error Handling Integration

**Consistent Error Patterns**:
```python
def handle_injection_error(error: Exception, operation: str, file_path: str) -> int:
    """
    Handle injection-specific errors with consistent messaging
    """
    if isinstance(error, InjectionSecurityError):
        safe_print(f"🔒 [security] Injection blocked for safety: {error.reason}")
        safe_print("[tip] Check your code for potentially dangerous patterns")
        return 1

    elif isinstance(error, InjectionParseError):
        safe_print(f"💥 [parse] Failed to analyze '{file_path}': {error.message}")
        safe_print(f"[?] Error at line {error.line_number}: {error.line_content}")
        safe_print("[tip] Check Python syntax and try again")
        return 1

    elif isinstance(error, InjectionCompatibilityError):
        safe_print(f"🤨 [compatibility] Can't inject into '{file_path}': {error.reason}")
        safe_print("[tip] Try 'kinda inject validate' to check compatibility")
        safe_print("[tip] Some libraries may not be compatible with injection")
        return 1

    else:
        # Fallback to existing error handling
        safe_print(f"💥 Injection {operation} failed: {error}")
        safe_print(f"[tip] Try 'kinda inject validate {file_path}' to check for issues")
        return 1
```

## 📊 CLI Configuration and Defaults

### Configuration File Support

**Configuration Structure** (`~/.kinda/injection.toml`):
```toml
[injection]
default_level = "basic"
default_safety_mode = "normal"
auto_backup = true
show_injection_summary = true

[injection.patterns]
default_enabled = ["kinda_int", "sometimes", "sorta_print"]
advanced_enabled = ["welp", "drift", "kinda_binary", "assert_probability"]

[injection.security]
strict_validation = false
allow_dangerous_patterns = false
security_scan_timeout = 30

[injection.performance]
max_injection_overhead = 0.10  # 10%
performance_monitoring = true
cache_ast_analysis = true

[injection.ui]
show_progress_bars = true
verbose_output = false
color_output = true
```

**CLI Configuration Commands**:
```bash
# Show current configuration
kinda inject config show

# Set default injection level
kinda inject config set injection.default_level intermediate

# Enable performance monitoring
kinda inject config set injection.performance.performance_monitoring true

# Reset to defaults
kinda inject config reset
```

### Environment Variable Support

**Injection-Specific Environment Variables**:
```bash
# Injection behavior
export KINDA_INJECTION_LEVEL=basic
export KINDA_INJECTION_SAFETY_MODE=strict
export KINDA_INJECTION_AUTO_BACKUP=true

# Performance tuning
export KINDA_INJECTION_CACHE_SIZE=100
export KINDA_INJECTION_MAX_OVERHEAD=0.15

# Security settings
export KINDA_INJECTION_SECURITY_STRICT=false
export KINDA_INJECTION_ALLOW_DANGEROUS=false

# UI preferences
export KINDA_INJECTION_VERBOSE=false
export KINDA_INJECTION_PROGRESS=true
```

## 🎯 User Experience Enhancements

### Progressive Disclosure Interface

**Beginner-Friendly Defaults**:
```bash
# Simple command for beginners
kinda inject run my_script.py
# Equivalent to: kinda inject run my_script.py --level basic --safety-mode normal --backup

# Guided experience
kinda inject
# Shows: Available commands with descriptions and examples
```

**Power User Shortcuts**:
```bash
# Advanced users can access full power
kinda inject run script.py -l advanced -p "all" --no-backup --aggressive

# Aliasing support in configuration
kinda inject quick script.py    # Predefined alias for common workflow
kinda inject safe script.py     # Predefined alias for safe operation
```

### Interactive Mode Support

**Interactive Injection Workflow**:
```bash
kinda inject convert script.py --interactive
```

**Interactive Output**:
```
🎯 Interactive Injection for 'script.py'

Found 15 injection opportunities. Let's go through them:

1/15: Variable assignment at line 12
      counter = 0

      Suggested injection: ~kinda int counter = 0
      Effect: Adds ±1 fuzzy noise to counter

      [y]es / [n]o / [s]kip remaining / [q]uit: y
      ✅ Applied kinda_int injection

2/15: Conditional statement at line 25
      if user_input:

      Suggested injection: ~sometimes (user_input) {
      Effect: 50% probability of execution

      [y]es / [n]o / [s]kip remaining / [q]uit: n
      ⏭️ Skipped sometimes injection

[Continue through all opportunities...]

📊 Interactive Session Summary:
   • Reviewed: 15 opportunities
   • Applied: 8 injections
   • Skipped: 7 opportunities
   • Generated: script_enhanced.py

🎉 Interactive injection complete!
```

## 🚀 Advanced CLI Features

### Batch Processing Support

**Batch Operations**:
```bash
# Process multiple files
kinda inject run *.py --batch

# Process entire directory
kinda inject convert src/ --recursive --output enhanced_src/

# Pipeline processing
find . -name "*.py" | xargs kinda inject validate --report summary
```

**Batch Output**:
```
🔄 Batch injection processing...

Processing 12 Python files:
  ✅ script1.py         (8 injections applied)
  ✅ script2.py         (3 injections applied)
  ⚠️  script3.py         (2 warnings, 5 injections applied)
  ❌ script4.py         (validation failed)
  ✅ script5.py         (12 injections applied)
  [... remaining files]

📊 Batch Summary:
   • Files processed: 12
   • Successful: 10
   • Warnings: 1
   • Failed: 1
   • Total injections: 67
   • Average per file: 6.7 injections
```

### Integration with Development Workflows

**Git Integration**:
```bash
# Inject changes and create commit
kinda inject convert script.py --git-commit "Add probabilistic enhancements"

# Show diff before applying
kinda inject convert script.py --show-diff --confirm

# Branch-based workflow
kinda inject convert script.py --git-branch "feature/probabilistic-enhancements"
```

**IDE Integration Preparation**:
```bash
# Generate IDE-compatible metadata
kinda inject analyze script.py --export-ide-metadata ide_hints.json

# LSP server support preparation
kinda inject validate script.py --lsp-mode --json-output
```

---

## 📋 CLI Implementation Checklist

### Phase 1: Core Commands (Weeks 1-2)
- [ ] `kinda inject run` basic implementation
- [ ] `kinda inject analyze` basic implementation
- [ ] Integration with existing CLI framework
- [ ] Basic error handling and user feedback
- [ ] Configuration system setup

### Phase 2: Enhanced Features (Weeks 3-4)
- [ ] `kinda inject convert` implementation
- [ ] `kinda inject validate` implementation
- [ ] Interactive mode support
- [ ] Batch processing capabilities
- [ ] Advanced configuration options

### Phase 3: Polish and Integration (Weeks 5-6)
- [ ] `kinda inject examples` implementation
- [ ] Performance optimization for CLI operations
- [ ] Comprehensive error handling and recovery
- [ ] Git workflow integration
- [ ] Documentation and help system completion

### Phase 4: Production Readiness (Weeks 7-8)
- [ ] Security hardening of CLI operations
- [ ] Performance benchmarking and optimization
- [ ] User experience testing and refinement
- [ ] Integration testing with existing CLI
- [ ] Release preparation and documentation

---

**Document Version**: 1.0
**Last Updated**: 2025-09-15
**Next Review**: Implementation Phase Start
**CLI Approval**: Epic #127 Team Review Required

This CLI specification provides a comprehensive interface for the Python Injection Framework, enabling users to seamlessly integrate probabilistic programming constructs into existing Python codebases while maintaining the familiar kinda-lang CLI experience.