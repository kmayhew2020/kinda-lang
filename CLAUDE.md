# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# ⚠️ CRITICAL: Repository Setup - Fork Workflow

**YOU ARE WORKING ON A FORK**

- **Your Fork (DEVELOPMENT)**: `kinda-lang-dev/kinda-lang` ← USE THIS FOR ALL WORK
- **Upstream (RELEASES ONLY)**: `kmayhew2020/kinda-lang` ← PM ONLY, VERSION RELEASES

## Golden Rules

### Daily Development Work (Coder/Tester/Reviewer/Architect)
1. ✅ ALL feature/bugfix work happens on fork: `kinda-lang-dev/kinda-lang`
2. ✅ ALL `gh` commands use: `--repo kinda-lang-dev/kinda-lang`
3. ✅ ALL PRs target fork's `dev` branch
4. ✅ Iterate on `dev` until milestone complete

### Release Process (PM ONLY)
1. ✅ Create release branch on fork: `release/vX.Y.Z`
2. ✅ PR from fork's release branch → upstream's `main`
3. ✅ Upstream PR created by PM for version releases only

### Never Do This
1. ❌ NEVER push feature branches to upstream
2. ❌ NEVER create feature/bugfix PRs on upstream
3. ❌ NEVER work directly on upstream repo

## Workflow Summary

```
Feature/Bug Work:
  Fork dev ← feature branches ← PRs ← merge to dev
  ↓ (iterate until milestone)

Release Work (PM ONLY):
  Fork release/vX.Y.Z → upstream main (PR for version release)
```

## Pre-Flight Validation

**MANDATORY: Run before ANY agent work**

```bash
bash .claude/preflight/validate.sh
```

This validates:
- ✅ You're on the fork (not upstream)
- ✅ Remotes configured correctly
- ✅ No prohibited .md status files
- ✅ Local CI script exists
- ✅ Not accidentally creating PRs on upstream

**If validation fails, STOP and fix issues before proceeding.**

## Verify Your Setup

```bash
git remote -v
# Should show:
# origin    https://github.com/kinda-lang-dev/kinda-lang.git
# upstream  https://github.com/kmayhew2020/kinda-lang.git
```

**If wrong**:
```bash
git remote set-url origin https://github.com/kinda-lang-dev/kinda-lang.git
git remote add upstream https://github.com/kmayhew2020/kinda-lang.git
```

---

## Quick Reference Card

**Most Common Commands:**
```bash
make dev                    # Install dev environment
pytest tests/               # Run all tests
pytest tests/python/ -v     # Run specific test category
black kinda/ tests/         # Format code
kinda run examples/hello.py.knda  # Test installation
bash .claude/preflight/validate.sh  # Validate setup
```

**Common Workflows:**
- **Fix failing test**: `pytest tests/test_file.py::test_name -vvs` → edit code → repeat
- **Add new construct**: Edit `kinda/grammar/python/constructs.py` → add tests → `pytest tests/python/`
- **Format before commit**: `black --check --diff .` → `black kinda/ tests/`
- **Check CI locally**: `pytest --cov=kinda --cov-report=term-missing tests/ --tb=short && black --check --diff .`

---

## 🤖 5-Agent Development Workflow

This project uses a **5-agent workflow** for structured development. When working on tasks, you may be invoked as one of these agents:

1. **PROJECT MANAGER** (`.claude/agents/kinda-pm.md`) - Backlog management, issue assignment, PR merging
2. **ARCHITECT** (`.claude/agents/kinda-architect.md`) - Technical design, architecture specs
3. **CODER** (`.claude/agents/kinda-coder.md`) - Implementation, unit tests
4. **TESTER** (`.claude/agents/kinda-tester.md`) - Testing, CI validation, quality assurance
5. **REVIEWER** (`.claude/agents/kinda-pr-reviewer.md`) - PR review, final approval

**Workflow:** User → PM → Architect → Coder → Tester → Reviewer → PM (merge) → Complete

See `docs/agents/WORKFLOW.md` for complete workflow documentation including quality gates, feedback loops, and agent coordination.

### For Claude Code Agents

If you're an agent:
- **FIRST**: Run preflight validation: `bash .claude/preflight/validate.sh`
- Check your agent definition file in `.claude/agents/` to understand your role
- Follow the workflow chain: complete your work and hand off to the next agent
- Use the appropriate tools for your role (see workflow doc)
- Update ROADMAP.md and issue tracking as you progress
- Always use `--repo kinda-lang-dev/kinda-lang` for all `gh` commands (see fork workflow above)

### Optional: MCP Server Enhancement

The repository includes an **optional MCP (Model Context Protocol) server** that provides programmatic workflow enforcement and GitHub integration.

**⚠️ IMPORTANT: Build Required on Fresh Clone**

The MCP server build files (`.mcp-server/build/`) are **not** version controlled. After cloning this repository, you **must** build the server before use:

```bash
cd .mcp-server
npm install && npm run build
```

**Setup (one-time per machine):**

1. **Get a GitHub Token** (if you don't have one):
   - Visit: https://github.com/settings/tokens/new
   - Name: `kinda-lang MCP Server`
   - Scopes: Select `repo` (full control) and `workflow`
   - Generate token and copy it (starts with `ghp_`)

2. **Build and Configure:**

   **For Claude Code CLI (Terminal):**
   ```bash
   # Easy way: Use the setup script
   cd .mcp-server
   ./setup-cli.sh your_github_token_here

   # OR manual setup:
   npm install && npm run build
   claude mcp add kinda-agent-workflow node $(pwd)/build/mcp-agent-server.js --scope user \
     -e GITHUB_TOKEN=your_token_here \
     -e GITHUB_OWNER=kinda-lang-dev \
     -e GITHUB_REPO=kinda-lang \
     -e WORKING_DIR=$(dirname $(pwd))

   # Verify: claude mcp list (should show ✓ Connected)
   # Exit and restart Claude Code session to load tools
   ```

   **For Claude Code Desktop (GUI):**
   ```bash
   cd .mcp-server
   ./install.sh  # Interactive installer handles build + config
   # Enter your GitHub token when prompted
   # Choose 'y' to auto-configure Claude Code
   # Restart Claude Code Desktop when complete
   ```

**For Agents Using MCP Tools:**

Once configured, these MCP tools are available in your Claude Code session:
- `start_task` - Initialize agent task tracking
- `run_tests` - Automated test execution with coverage
- `run_local_ci` - Full CI validation
- `save_context` - Agent state preservation
- `complete_task` - Task completion with validation
- `github_issue` - GitHub integration (uses your configured token)

**Note:** MCP server is **optional**. The `.claude/` bash scripts work independently and do not require tokens. See `.mcp-server/SETUP.md` for details.

## Project Overview

**Kinda** is a fuzzy programming language that adds uncertainty and personality to code. It introduces the `~` (tilde) prefix for fuzzy constructs that behave probabilistically and uses `.knda` file extensions for source files.

### Core Concepts

- **Fuzzy constructs**: All fuzzy features use `~` prefix (e.g., `~kinda int`, `~sometimes`, `~sorta print`)
- **Personality system**: Four moods (reliable, cautious, playful, chaotic) that affect all fuzzy behavior
- **Chaos control**: `--chaos-level` (1-10) and `--seed` flags for fine-grained randomness control
- **Statistical testing**: `~assert_eventually()` and `~assert_probability()` for testing probabilistic code
- **File extension**: Kinda source files use `.py.knda` suffix for Python-like syntax

## Directory Structure (High-Level)

```
kinda-lang/
├── kinda/                      # Core package
│   ├── grammar/python/         # Python transformation (constructs.py, matchers.py)
│   ├── personality.py          # Chaos/personality system (CRITICAL - all RNG goes here)
│   ├── security/               # Sandboxing (Issue #109)
│   ├── injection/              # Epic #127 Python enhancement bridge
│   ├── composition/            # Epic #126 construct composition
│   ├── transpiler/             # Multi-language support
│   ├── cli.py                  # CLI entry point
│   └── langs/python/runtime/   # Auto-generated runtime (fuzzy.py - excluded from mypy)
├── tests/                      # Test suite organized by category
├── examples/                   # Example .knda programs
├── .claude/                    # Agent workflow & scripts
│   ├── agents/                 # 5-agent definitions
│   └── preflight/              # Validation scripts
└── .mcp-server/                # Optional MCP server (requires build)
```

## Development Commands

### Installation & Setup

```bash
# Install with pipx (recommended for users)
pipx install kinda-lang

# Developer setup with all dependencies
./install.sh --dev    # Unix/Linux/macOS
install.bat           # Windows
# OR
pip install -e .[dev]

# Regular installation
pip install -e .
```

### Quick Commands (via Makefile)

```bash
make help      # Show all available commands
make install   # Install kinda (pip install -e .)
make dev       # Install with dev dependencies
make test      # Run full test suite
make clean     # Clean build artifacts
make examples  # Show kinda examples
make docs      # Build Sphinx documentation
```

### Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=kinda tests/

# Run specific test category
pytest tests/python/          # Python transformer tests
pytest tests/security/        # Security sandbox tests
pytest tests/performance/     # Performance tests (many skip in CI)

# Run single test file
pytest tests/test_cli.py -v

# Run single test
pytest tests/python/test_fuzzy_constructs.py::test_kinda_int -v
```

### Code Quality

```bash
# Format code with Black
black kinda/ tests/

# Check formatting (CI-style)
black --check --diff .

# Type checking (excludes fuzzy.py runtime)
mypy kinda/

# Run linting
make test
```

### Debugging & Troubleshooting

```bash
# Debug transformation issues - see generated Python
kinda transform file.py.knda > file_transformed.py
cat file_transformed.py  # Inspect the output

# Verify installation
python -c "import kinda; print(kinda.__version__)"
which kinda  # Unix
where kinda  # Windows

# Check encoding issues (important for cross-platform)
file -i file.py.knda  # Check file encoding on Unix
# Windows: Check with Notepad++ or VSCode encoding display

# Test specific construct behavior with verbose output
pytest tests/python/test_fuzzy_constructs.py::test_specific_construct -vvs

# Debug failing tests with full output
pytest tests/test_file.py -vvs --tb=long

# Run single test file with detailed output
pytest tests/test_cli.py -v --tb=short
```

### Environment Variables

```bash
# Seed for reproducible randomness
export KINDA_SEED=42

# Override personality mood (if supported)
export KINDA_MOOD=chaotic

# Override chaos level (if supported)
export KINDA_CHAOS_LEVEL=8

# All environment variables work with CLI flags
kinda run file.knda --seed 42      # CLI overrides environment
kinda run file.knda --mood reliable
kinda run file.knda --chaos-level 5
```

### Local Testing & Validation

```bash
# Preflight validation (checks remotes, files, etc.)
bash .claude/preflight/validate.sh

# Run full local CI equivalent
pytest --cov=kinda --cov-report=term-missing tests/ --tb=short
black --check --diff .

# Run performance tests (skipped in CI by default)
pytest -m performance
```

### GitHub Actions CI

```bash
# CI runs on push/PR to main, dev, feature/*, bugfix/*, ci/* branches
# Tests run on: Ubuntu, macOS, Windows × Python 3.8-3.12

# Local CI validation
pytest --cov=kinda --cov-report=term-missing tests/ --tb=short
black --check --diff .

# CI skips performance tests by default (marked with @pytest.mark.performance)
# Run performance tests locally: pytest -m performance
```

**CI Platform Matrix:**
- **OS**: ubuntu-latest, macos-latest, windows-latest
- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Workflows**: `.github/workflows/main.yml` (main CI), `.github/workflows/docs.yml`, `.github/workflows/demo-validation.yml`

### Running Kinda Programs

```bash
# Transform and execute
kinda run examples/hello.py.knda

# Run with personality and chaos control
kinda run file.py.knda --mood reliable --chaos-level 1
kinda run file.py.knda --mood chaotic --chaos-level 10

# Reproducible execution with seed
kinda run file.py.knda --seed 42

# Just transform (don't execute)
kinda transform file.py.knda

# Interpret mode (max chaos runtime)
kinda interpret file.py.knda

# Show examples and syntax
kinda examples
kinda syntax
```

## Architecture

### Pipeline Overview

1. **Parsing**: `.knda` files → AST via `kinda/grammar/python/matchers.py`
2. **Transformation**: AST → Python code via `kinda/grammar/python/constructs.py`
3. **Runtime injection**: Fuzzy runtime functions added to transformed code
4. **Execution**: Transformed Python runs with `kinda.personality` and security sandbox

### Key Modules

#### Core Transformation (`kinda/grammar/python/`)
- **`constructs.py`**: Defines all fuzzy constructs (70+ constructs including loops, conditionals, types)
- **`matchers.py`**: Regex-based pattern matching for construct detection
- Contains the construct definitions that power the entire transformation system

#### Personality & Chaos System (`kinda/personality.py`)
- **`PersonalityContext`**: Global singleton managing chaos state and RNG
- **`ChaosProfile`**: Configuration for probability modifiers and variance
- **Seeded RNG**: All randomness flows through centralized `chaos_random()`, `chaos_randint()`, etc.
- **Personality modes**:
  - `reliable`: Conservative, high success rates, minimal variance
  - `cautious`: Moderate uncertainty
  - `playful`: Standard kinda behavior (default)
  - `chaotic`: Maximum chaos and variance

#### Security System (`kinda/security/`)
- **`sandbox.py`**: Comprehensive sandboxing for code execution (Issue #109)
- **`execution.py`**: Safe execution context and resource limits
- **`filesystem.py`**: Filesystem access controls and path validation
- Security features include imports filtering, dangerous function blocking, and resource limits

#### Injection System (`kinda/injection/`)
- **`injection_engine.py`**: Python enhancement bridge for injecting kinda constructs into pure Python
- **`ast_analyzer.py`**: AST analysis for safe injection points
- **`patterns.py`**: Injection pattern definitions
- Part of Epic #127 Python Enhancement Bridge

#### Composition Framework (`kinda/composition/`)
- **`framework.py`**: Framework for building constructs from other constructs
- **`patterns.py`**: High-level construct composition patterns
- Part of Epic #126 "Kinda builds Kinda" self-hosting vision

#### Transpiler Infrastructure (`kinda/transpiler/`)
- **`engine.py`**: Multi-language transpiler foundation
- **`targets/`**: Language-specific backends (Python Enhanced, C, MATLAB planned)
- Part of Epic #127 multi-language support architecture

#### Runtime (`kinda/langs/python/runtime/fuzzy.py`)
- Auto-generated fuzzy runtime functions injected into transformed code
- Provides `assert_eventually()`, `assert_probability()`, and helper functions
- Uses centralized personality system for all RNG
- **Note**: Excluded from mypy type checking (see pyproject.toml)

### Construct Types

The system supports these construct categories (all in `constructs.py`):

1. **Declarations**: `~kinda int`, `~kinda float`, `~kinda bool`, `~kinda binary`
2. **Time-based drift**: `~time drift float`, `~time drift int`, `var~drift`
3. **Conditionals**: `~sometimes`, `~maybe`, `~probably`, `~rarely`
4. **Loops**: `~sometimes_while`, `~maybe_for`, `~kinda_repeat`, `~eventually_until`
5. **Operators**: `~ish` (value creation, comparison, modification), fuzzy assignment `~=`
6. **Output**: `~sorta print()`
7. **Testing**: `~assert_eventually()`, `~assert_probability()`

### Statistical Testing Framework

The system includes statistical assertions for testing fuzzy code:

- **`~assert_eventually(condition, timeout=5.0, confidence=0.95)`**: Wait for probabilistic conditions
- **`~assert_probability(event, expected_prob=0.5, tolerance=0.1, samples=1000)`**: Validate probability distributions
- Uses Wilson score intervals for confidence bounds
- Integrated with personality system for error messages

## Important Implementation Details

### Personality Integration

**All fuzzy constructs must use centralized RNG** from `PersonalityContext`:

```python
from kinda.personality import chaos_randint, chaos_random, chaos_choice, update_chaos_state

# CORRECT - uses personality-aware RNG
result = chaos_randint(0, 10)

# WRONG - bypasses personality system
import random
result = random.randint(0, 10)  # Don't do this!
```

Key personality functions:
- `chaos_random()`, `chaos_randint()`, `chaos_uniform()`, `chaos_choice()` - RNG functions
- `chaos_fuzz_range()`, `chaos_float_drift_range()` - Get personality-adjusted ranges
- `update_chaos_state(failed=bool)` - Track failures for cascade effects
- `get_personality()` - Access current personality context

### Security Constraints (Issue #109)

The security sandbox (in `kinda/security/`) enforces:

- **Import filtering**: Only safe imports allowed (no `os`, `subprocess`, etc.)
- **Function blocking**: Dangerous built-ins blocked (`eval`, `exec`, `__import__`)
- **Filesystem restrictions**: Paths must be within allowed directories
- **Resource limits**: CPU time, memory, file operations tracked
- **Condition validation**: All conditions checked via `secure_condition_check()`

When adding new constructs, ensure they use `secure_condition_check()` for any user-provided conditions.

### Test Structure

Tests are organized by category:
- `tests/python/` - Core Python transformer tests
- `tests/security/` - Security sandbox tests
- `tests/performance/` - Performance benchmarks (many skip in CI)
- `tests/epic_127/` - Python enhancement bridge tests
- `tests/migration/` - Migration framework tests
- `tests/control/` - Control flow tests

**Performance test markers**:
- `@pytest.mark.performance` - Performance tests (run locally, skip in CI)
- `@pytest.mark.ci_unstable` - Tests that may be flaky in CI
- `@pytest.mark.slow` - Long-running tests

### Performance Testing

```bash
# Run performance tests (skipped in CI by default)
pytest -m performance

# Run with specific performance parameters
pytest tests/performance/ --iterations=1000

# Check performance cache
ls -la .performance-cache/

# Performance test configuration in pyproject.toml:
# - cache_directory: .performance-cache
# - baseline_retention_days: 30
# - confidence_level: 0.95
# - default_iterations: 100
```

**Performance markers:**
- `@pytest.mark.performance` - Skip in CI, run locally for benchmarks
- `@pytest.mark.ci_unstable` - May be flaky in CI environments
- `@pytest.mark.slow` - Long-running tests (>5s typically)

### Windows-Specific Notes

- **Emoji handling**: `safe_print()` in `kinda/cli.py` handles cp1252 encoding fallbacks
- **Install script**: Use `install.bat` instead of `install.sh`
- **CI examples**: Some emoji-heavy examples skipped on Windows (see `.github/workflows/main.yml:59-64`)
- **Path separators**: Code uses `pathlib.Path` for cross-platform compatibility
- **Line endings**: Git should auto-convert (check `.gitattributes` if issues)
- **Shell commands**: Use `bash` in Git Bash or WSL for Unix-style commands

### Adding New Constructs

To add a new fuzzy construct:

1. **Define in `kinda/grammar/python/constructs.py`**:
   ```python
   "new_construct": {
       "type": "statement",  # or "declaration", "expression"
       "pattern": re.compile(r"~new_pattern ..."),
       "description": "What it does",
       "body": "def new_construct_impl():\n    ..."
   }
   ```

2. **Use personality-aware RNG**:
   - Import from `kinda.personality`
   - Use `chaos_*()` functions
   - Call `update_chaos_state(failed=bool)` to track state

3. **Add security checks** if construct evaluates conditions:
   ```python
   from kinda.security import secure_condition_check
   should_proceed, result = secure_condition_check(condition, 'construct_name')
   ```

4. **Write tests** in `tests/python/test_fuzzy_constructs.py`:
   - Test basic functionality
   - Test with different personality modes
   - Test with different chaos levels
   - Test reproducibility with seeds

### CLI Entry Point

Main CLI is in `kinda/cli.py`:
- Handles `run`, `transform`, `interpret`, `examples`, `syntax` commands
- Manages `--seed`, `--chaos-level`, `--mood` flags
- Safe file encoding detection (supports chardet)
- Windows-safe emoji fallbacks in `safe_print()`

## Project Status & Licensing

### Current Version
**v0.5.0** - "Complete Probabilistic Programming"

Recent completions:
- ✅ **Epic #127**: Python Enhancement Bridge (injection framework, 100% complete)
- ✅ **Epic #126**: Construct Composition Framework ("Kinda builds Kinda")
- ✅ **Epic #125**: Probabilistic Control Flow (loops, repetition constructs)
- ✅ **Issue #109**: Comprehensive Security Sandboxing

Active development:
- Multi-language transpiler (C support planned)
- Advanced composition patterns
- Performance optimizations

See `ROADMAP.md` for detailed development timeline and Epic status.

### Licensing Model

**Dual License** - Choose based on your use case:

1. **Open Source (AGPL v3)** - For research, education, and open source projects
   - Free to use and modify
   - Must share source code changes
   - Network use triggers disclosure obligations

2. **Commercial License** - For production, proprietary, and enterprise systems
   - No copyleft obligations on your code
   - Professional support with SLAs
   - Custom chaos models and certification assistance
   - Aerospace/Defense/Medical device compliance support

See `LICENSE-DUAL.md` and `ENTERPRISE.md` for details.

### Performance Characteristics

From `PERFORMANCE.md`:
- **Transformation speed**: 8.1 lines/ms (445-line file in ~55ms)
- **Excellent linear scaling**: O(n) complexity maintained
- **Minimal overhead**: <15% for probabilistic constructs vs standard Python
- **Pre-compiled regex patterns**: Module-level compilation for speed
- Coverage: 78% maintained across 101 passing tests

### Record/Replay System (Debugging)

The system includes debugging capabilities via `kinda.record_replay`:

```bash
# Record execution session
kinda record run file.py.knda

# Session files are saved as JSON
# Location: Project root or .kinda-sessions/ directory

# Replay recorded session (verify actual CLI command)
kinda replay <session-id>

# Analyze recorded decisions manually
# Session files are JSON - can be inspected
cat .kinda-sessions/session_*.json | jq  # If jq available
python -m json.tool .kinda-sessions/session_*.json  # Built-in formatter
```

**Capabilities:**
- Record all random decisions to JSON session files
- Exact reproduction of program execution
- Thread-safe operation with minimal overhead
- Stack trace analysis and construct context inference
- Useful for debugging non-deterministic behavior

## Epic #127 - Python Enhancement Bridge

The injection framework allows gradual adoption of kinda constructs in existing Python:

```python
from kinda import inject

@inject.probabilistic
def my_function():
    ~kinda int counter = 0
    ~sometimes { risky_operation() }
    return counter
```

**Key capabilities**:
- Decorator-based injection (`@inject.probabilistic`)
- AST analysis for safe injection points
- CLI: `kinda inject analyze`, `kinda inject convert`, `kinda inject run`
- Security scanning and automatic backups

See `EPIC_127_PYTHON_ENHANCEMENT_BRIDGE_ARCHITECTURE.md` and `docs/EPIC_127_OVERVIEW.md` for full specs.

## Documentation Structure

### Root-Level Docs (Architecture & Specs)
- **`ROADMAP.md`**: Development timeline, Epic status, strategic priorities
- **`CHANGELOG.md`**: Version history and feature releases
- **`SECURITY.md`**: Security policy, vulnerability reporting
- **`ENTERPRISE.md`**: Commercial use cases, licensing, professional services
- **`PERFORMANCE.md`**: Performance benchmarks and optimization details
- **`EPIC_127_PYTHON_ENHANCEMENT_BRIDGE_ARCHITECTURE.md`**: Python injection framework architecture

### User Documentation (`docs/`)
- **`docs/source/`**: Sphinx docs (getting_started, features, architecture, etc.)
- **`docs/PROBABILISTIC_CONTROL_FLOW.md`**: Complete reference for loop constructs
- **`docs/composition/`**: Composition framework guides and examples
- **`docs/META_PROGRAMMING_TESTING.md`**: Statistical testing with "Kinda tests Kinda"

### Developer Documentation (`docs/specifications/`, `docs/architecture/`)
- Implementation specs for Epic #125, #126, #127
- Performance testing framework architecture
- Statistical testing implementation details
- CI integration and example ecosystem specs

## Special Files & Conventions

- **`conftest.py`**: Pytest configuration, imports `kinda.testing.pytest_plugin`
- **`pyproject.toml`**: Build config, dev dependencies, excludes `fuzzy.py` from mypy
- **`.knda` files**: Kinda source files (`.py.knda` for Python-like syntax)
- **Performance tests**: Use `@pytest.mark.performance` marker, many skip in CI
- **Windows compatibility**: `safe_print()` in CLI for emoji fallbacks
