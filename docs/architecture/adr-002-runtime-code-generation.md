# ADR-002: Dynamic Runtime Code Generation

**Status**: Accepted  
**Date**: 2024 (Inferred from implementation)  
**Deciders**: Kinda-Lang Core Team  

## Context

Kinda-Lang needs to provide runtime implementations for fuzzy constructs like `~kinda int`, `~sorta print`, `~sometimes`, etc. The challenge is that different programs use different subsets of constructs, and each construct may need complex runtime behavior including personality integration, error handling, and chaos state tracking.

Static runtime libraries would include unused code, while fully dynamic execution would be too slow.

## Decision

Implement dynamic runtime code generation (`kinda/langs/python/runtime_gen.py`) that:

1. **Tracks Used Constructs**: Transformer records which helpers are needed during parsing
2. **Generates Minimal Runtime**: Only includes functions for constructs actually used
3. **Template-Based Generation**: Construct definitions include full implementation code
4. **Automatic Integration**: Generated runtime includes personality system integration

**Implementation Details**:

**Construct Definition** (`kinda/grammar/python/constructs.py:6-36`):
```python
"kinda_int": {
    "pattern": re.compile(r'~kinda int (\w+)\s*[~=]+\s*([^#;]+?)'),
    "body": (
        "def kinda_int(val):\n"
        "    from kinda.personality import chaos_fuzz_range, update_chaos_state\n"
        "    # ... full implementation\n"
        "    return result"
    ),
}
```

**Usage Tracking** (`kinda/langs/python/transformer.py:235-238`):
```python
if key == "kinda_int":
    var, val = groups
    used_helpers.add("kinda_int")  # Track usage
    transformed_code = f"{var} = kinda_int({val})"
```

**Runtime Generation** (`kinda/langs/python/runtime_gen.py:5-21`):
```python
def generate_runtime_helpers(used_keys, output_path: Path, constructs):
    code = []
    for key in sorted(used_keys):
        construct = constructs.get(key)
        if construct and "body" in construct:
            code.append(construct["body"])
    
    runtime_path = output_path / "fuzzy.py"
    with runtime_path.open("a") as f:
        f.write("\n\n" + "\n\n".join(code) + "\n")
```

## Alternatives Considered

### 1. Static Runtime Library
- **Rejected**: Would include all possible constructs regardless of usage
- **Issue**: Larger generated files, slower imports, unnecessary complexity

### 2. Embedded Inline Code
- **Rejected**: Would duplicate runtime code in every generated file
- **Issue**: Code bloat, difficult to maintain, no shared state

### 3. External Runtime Dependencies
- **Rejected**: Would require separate package installation
- **Issue**: Breaks self-contained transformation goal, deployment complexity

### 4. Just-In-Time Compilation
- **Rejected**: Too complex for current goals, performance overhead
- **Issue**: Requires sophisticated caching and compilation infrastructure

## Consequences

### Positive
- **Minimal Output**: Generated files only include needed functionality
- **Self-Contained**: No external runtime dependencies required
- **Easy Maintenance**: Runtime code lives with construct definitions
- **Performance**: No runtime lookup overhead for unused constructs
- **Flexibility**: Each construct can have arbitrarily complex implementation

### Negative
- **Build Complexity**: Requires two-phase generation (tracking + output)
- **Debugging Harder**: Generated code may be hard to trace back to source
- **Code Duplication**: Shared utilities may be duplicated across constructs

## Evidence from Codebase

**Transform Integration** (`kinda/langs/python/transformer.py:355-361`):
```python
header = ""
if used_helpers:
    helpers = ", ".join(sorted(used_helpers))
    header = f"from kinda.langs.{target_language}.runtime.fuzzy import {helpers}\n\n"
return header + "\n".join(output_lines)
```

**Full Runtime Creation** (`kinda/langs/python/transformer.py:443-448`):
```python
runtime_path = Path(__file__).parent.parent.parent / "langs" / "python" / "runtime"
runtime_path.mkdir(parents=True, exist_ok=True)
generate_runtime_helpers(used_helpers, runtime_path, KindaPythonConstructs)
generate_runtime(runtime_path)
```

**Personality Integration in Generated Code** (`kinda/grammar/python/constructs.py:12-14`):
```python
"def kinda_int(val):\n"
"    from kinda.personality import chaos_fuzz_range, update_chaos_state\n"
"    import random\n"
```

This approach provides the optimal balance between performance, maintainability, and functionality for Kinda-Lang's runtime requirements.