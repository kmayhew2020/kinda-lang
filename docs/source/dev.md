# Developer Guide

## Project Structure

```
kinda/
├── cli.py                # CLI entrypoints
├── run.py                # Programmatic interface
├── langs/
│   └── python/
│       ├── transformer.py      # Kinda-to-Python transformer
│       ├── semantics.py        # Core logic transformations
│       ├── runtime_gen.py      # Runtime code generator
│       └── runtime/            # Generated runtime module
├── interpreter/
│   ├── repl.py                 # (stubbed) interactive mode
├── grammar/
│   └── python/
│       └── matchers.py         # Regex-based matchers
tests/
└── python/
    └── ...                     # Full test suite
```

## Run the Tests

To run tests locally:

```bash
pytest
```

To run with coverage:

```bash
pytest --cov=kinda --cov-report=term-missing
```

## Coverage Goals

We aim for **80%+ coverage** for core functionality. Tests should be written for:

- All supported fuzzy constructs (`kinda`, `sorta`, `sometimes`)
- Line passthrough (comments, blank lines, normal Python)
- Runtime generation
- CLI invocation
- Transformer and semantics logic

## CI / GitHub Actions

CI runs on:

- `main`
- branches prefixed with `ci/`
- all pull requests targeting `main`

See `.github/workflows/ci.yml` for details.

## Adding a New Construct

1. Add regex matcher under `grammar/python/matchers.py`
2. Add transformation logic in `semantics.py`
3. Add test inputs under `tests/python/input/`
4. Add tests to `test_runner.py` or `test_transformer.py`
5. Validate with `pytest`

## Logging

Logging is currently minimal. TODO: add structured debug logging for:
- transformations
- interpreter steps
- runtime execution

## Docs

All Markdown docs live in `/docs`. Wiki should mirror this structure where useful.

## Future Dev Tasks

- [ ] Add support for nested fuzzy blocks
- [ ] Add personalities / config injection
- [ ] CLI options for controlling chaos
- [ ] Multi-language scaffold (C, JS)
- [ ] Formal spec + grammar
