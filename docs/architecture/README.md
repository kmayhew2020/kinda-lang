# Kinda-Lang Architecture Documentation

This directory contains architectural documentation derived from analysis of the Kinda-Lang codebase. All diagrams and decisions are based on the actual implementation as of the analysis date.

## Overview

Kinda-Lang is a fuzzy programming language that transforms uncertainty into executable code through probabilistic constructs and personality-driven behavior. The architecture supports expressing uncertainty naturally while maintaining practical usability through configurable chaos levels.

## Documents

### System Architecture
- **[C4 System/Container Diagram](c4-system-container.md)** - High-level architecture overview showing major components and their relationships

### Architecture Decision Records (ADRs)
- **[ADR-001: Personality-Driven Chaos Control](adr-001-personality-driven-chaos.md)** - Decision to implement configurable behavior profiles that affect all fuzzy constructs
- **[ADR-002: Dynamic Runtime Code Generation](adr-002-runtime-code-generation.md)** - Decision to generate minimal runtime libraries based on actual construct usage
- **[ADR-003: Inline Construct Transformation](adr-003-inline-construct-transformation.md)** - Decision to support complex inline expressions with context-aware transformation

### Sequence Diagrams
- **[Transform Flow](sequence-transform-flow.md)** - Shows the complete transformation from .knda source to executable Python
- **[Construct Execution](sequence-construct-execution.md)** - Shows how fuzzy constructs interact with the personality system during runtime

## Key Architectural Principles

### 1. Personality-Driven Design
Every fuzzy construct queries a global personality system for behavioral parameters. This enables consistent chaos philosophy across the entire program while allowing fine-tuned control through mood selection.

**Source**: `kinda/personality.py:111-272`

### 2. Minimal Runtime Generation  
Only constructs actually used in source code have their runtime implementations included in generated files. This keeps output lean while supporting arbitrary construct complexity.

**Source**: `kinda/langs/python/runtime_gen.py:5-21`

### 3. Context-Aware Transformation
The same syntax can behave differently based on context (e.g., `x ~ish 10` as assignment vs. comparison), enabling natural expression of uncertainty.

**Source**: `kinda/langs/python/transformer.py:140-170`

### 4. Graceful Degradation
All constructs include comprehensive error handling with personality-appropriate messages, ensuring programs continue running even when individual operations fail.

**Source**: `kinda/grammar/python/constructs.py` - all construct definitions

## Component Relationships

```
CLI Interface (kinda/cli.py)
├── Personality System (kinda/personality.py)  
├── Code Transformer (kinda/langs/python/transformer.py)
│   ├── Grammar Engine (kinda/grammar/python/)
│   └── Runtime Generator (kinda/langs/python/runtime_gen.py)
└── Fuzzy Interpreter (kinda/interpreter/repl.py)
```

## Implementation Highlights

### Multi-Pass Transformation
Source code undergoes multiple transformation passes:
1. **Inline constructs**: `~ish` and `~welp` within expressions
2. **Block constructs**: `~sometimes`, `~maybe` with nested code blocks  
3. **Runtime generation**: Dynamic helper function creation
4. **Import injection**: Automatic runtime dependency resolution

### String-Aware Parsing
All construct recognition includes string literal detection to avoid transforming code inside quotes. This enables fuzzy constructs in any expression context without breaking string constants.

### Cascade Effects
The personality system tracks operation failures and applies increasing instability to subsequent operations, creating realistic system degradation patterns.

## Future Considerations

### Planned Extensions
- **C Language Support**: Architecture designed for multiple target languages (`kinda/langs/c/` structure exists)
- **Additional Personalities**: Framework supports arbitrary personality profiles
- **Advanced Cascade Effects**: Time-based drift and cross-construct interactions

### Architectural Scalability
- **Plugin Architecture**: New constructs can be added through grammar definitions
- **Language Agnostic**: Core transformation logic separated from target language specifics
- **Runtime Flexibility**: Generated code has no external dependencies

## Refreshing Documentation

This documentation is designed to be regenerated when the codebase changes. Key files to monitor for architectural changes:

- `kinda/cli.py` - Command interface and flow control
- `kinda/personality.py` - Behavioral system core
- `kinda/langs/python/transformer.py` - Transformation logic
- `kinda/grammar/python/constructs.py` - Language construct definitions

All file references include specific line numbers linking architectural elements back to source code for traceability and maintenance.