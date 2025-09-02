# Kinda-Lang CI Requirements

## Required Dependencies

### Core Development Tools
```bash
pip install -e .[dev]  # Installs: pytest, pytest-cov, black, mypy
pip install isort      # Import sorting
pip install flake8     # Linting
```

### Optional Security Tools
```bash
pip install bandit     # Security scanning
pip install safety     # Dependency vulnerability scanning
pip install pip-audit  # PyPA recommended security tool
```

## Environment Setup

### Required Environment Variables (for testing)
```bash
export KINDA_SEED=42          # Default seed for reproducible testing
export PYTHONPATH="${PWD}"    # Ensure local kinda package is found
```

### Git Hooks Setup (Optional)
```bash
# Install pre-commit hook
ln -sf ../../scripts/pre-commit-hook.sh .git/hooks/pre-commit
```

## CI Script Usage

### Full CI Pipeline
```bash
./scripts/ci-full.sh
```
Runs complete validation suite (~3-5 minutes)

### Quick Pre-commit Check
```bash
./scripts/pre-commit-hook.sh  
```
Fast validation for development (~30 seconds)

### Custom Test Runs
```bash
# Test specific chaos level
KINDA_SEED=123 python -m pytest --chaos-level=5

# Test specific personality
python -m kinda run examples/python/hello.py.knda --mood=chaotic

# Coverage report
python -m pytest --cov=kinda --cov-report=html
```

## Expected CI Results

### Passing Criteria
- ✅ All code formatted with Black
- ✅ Imports sorted with isort  
- ✅ No flake8 linting errors
- ✅ Test coverage ≥75%
- ✅ All example programs execute successfully
- ✅ CLI commands functional
- ✅ Package installs without errors

### Warning Conditions (Non-blocking)
- ⚠️ MyPy type checking issues
- ⚠️ Performance regression detected
- ⚠️ Security scan findings
- ⚠️ Maximum chaos test failures (expected chaos)

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure `pip install -e .` completed successfully
2. **Missing dependencies**: Run `pip install -r requirements-dev.txt`
3. **Path issues**: Ensure running from project root directory
4. **Permission errors**: Make scripts executable with `chmod +x scripts/*.sh`

### Performance Notes
- Full CI suite: ~3-5 minutes on modern hardware
- Pre-commit hook: ~30 seconds
- Network required: Only for security dependency checks (optional)