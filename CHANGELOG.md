# Changelog

All notable changes to kinda-lang will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-09-04

### 🎉 Major Features

- **Record/Replay System**: Complete recording infrastructure for debugging kinda programs with exact execution reproduction
  - `kinda record run` CLI command for capturing all random decisions
  - JSON session files with rich metadata and RNG call sequences
  - Construct context inference and stack trace analysis
  - Thread-safe operation with minimal performance overhead
- **Meta-Programming Testing Framework**: "Kinda Tests Kinda" philosophy implementation
  - Statistical assertions: `~assert_eventually()` and `~assert_probability()`
  - Self-validating test framework with fuzzy success criteria
  - Recursive meta-testing capabilities for framework validation
- **Enhanced Language Constructs**: New probabilistic programming primitives
  - `~kinda_bool`: Fuzzy boolean with configurable true/false probabilities
  - `~kinda_float`: Fuzzy floating-point with controlled precision variance
  - `~probably`: 70% probability construct for common likely events
  - `~rarely`: 15% probability construct for uncommon events
- **Advanced CLI Features**: Professional development workflow enhancements
  - `--chaos-level` parameter (1-10 scale) for fine-tuned randomness control
  - `--seed` flag for reproducible chaos and deterministic debugging
  - Enhanced error messages with kinda personality and debugging hints

### 🚀 Performance & Infrastructure

- **Epic #124 Self-Definition**: Construct self-definition system for meta-programming
- **Comprehensive CI Pipeline**: Cross-platform testing with automated example validation
- **Development Dependencies**: Automatic installation of pytest, black, mypy for contributors
- **Security Enhancements**: Case-insensitive pattern matching and extended manipulation detection
- **Time-Based Drift**: Variable value changes over time with configurable drift patterns

### 🐛 Bug Fixes & Stability

- **Critical ~ish Construct Crisis Resolved**: Fixed Issues #80, #82, #83, #105, #106, #107
  - Proper handling of negative numbers and complex arithmetic
  - Enhanced parentheses matching with string-aware parsing
  - Resolved nested construct interaction problems
- **Block Else Syntax**: Fixed Issues #79 and #81 with proper conditional fallback support
- **Cross-Platform Unicode**: Windows-compatible emoji handling with ASCII fallbacks
- **Runtime Generation**: Improved error handling and graceful fallback mechanisms
- **Transformer Stability**: Resolved critical transformer bugs affecting complex constructs

### 🛠️ Developer Experience

- **Enhanced Documentation**: 
  - Advanced Usage Patterns guide with real-world examples
  - Meta-programming testing documentation
  - Construct usage clarifications and best practices
- **Improved Build Process**: Streamlined development workflow with automatic dependency management
- **Better Error Reporting**: Context-aware error messages with helpful suggestions
- **Example Reorganization**: Individual construct examples with comprehensive demonstrations

### 📚 Documentation & Examples

- **20+ New Examples**: Individual construct demonstrations and complex integrations
- **Meta-Programming Guide**: Complete coverage of statistical testing patterns
- **Advanced Patterns Documentation**: Real-world usage scenarios and best practices
- **Record/Replay Documentation**: Comprehensive debugging workflow guide
- **Time Drift Examples**: Personality-driven variable evolution demonstrations

### 🔧 Technical Improvements

- **Personality System Integration**: Enhanced chaos-personality interaction across all constructs
- **Runtime Module Management**: Improved fuzzy.py generation and lifecycle management  
- **Pattern Matching**: Pre-compiled regex optimization for better parsing performance
- **Memory Management**: Efficient session recording with lazy serialization
- **Thread Safety**: Complete multi-threaded kinda program support

### 📦 Breaking Changes

- Version bump from 0.3.0 to 0.4.0 due to significant architectural changes
- Enhanced CLI parameter structure may require minor command updates
- New construct syntax additions extend the language surface area
- Statistical assertion integration changes test framework expectations

### 🎪 What's New for Users

- **Professional Debugging**: Record/replay system for reproducible bug hunting
- **Enhanced Chaos Control**: Fine-tuned randomness with --chaos-level and --seed
- **More Expressive Constructs**: ~probably, ~rarely, ~kinda_bool, ~kinda_float
- **Better Development Experience**: Automated dependency management and improved testing
- **Meta-Programming Power**: "Kinda Tests Kinda" framework for advanced applications
- **Production Stability**: Major bug fixes and enhanced error handling

### 🎲 Chaos Evolution

- **Reproducible Chaos**: --seed parameter enables deterministic debugging
- **Controlled Randomness**: --chaos-level provides 1-10 scale chaos tuning  
- **Time-Based Variance**: Variables drift over time with personality-driven patterns
- **Statistical Validation**: Assert probabilistic behaviors with confidence intervals
- **Meta-Chaos**: Framework tests itself using kinda constructs recursively

---

## [0.3.0] - 2025-08-28

### 🎉 Major Features
- **~welp Construct**: Re-enabled with full test coverage and graceful fallback support
- **~ish Integration**: Enhanced syntax integration with ~maybe and ~sometimes constructs  
- **~kinda binary**: Three-state logic construct (positive, negative, neutral) with configurable probabilities
- **Comprehensive Example Suite**: All constructs working together in complex chaos simulations

### 🚀 Performance & Infrastructure
- **Performance Optimizations**: Major improvements to parsing and transformation speed
- **Enhanced CI Pipeline**: Added cross-platform example smoke tests (Ubuntu/macOS/Windows × Python 3.8-3.12)
- **Test Coverage**: Improved from 87% to 94% with comprehensive construct testing
- **Documentation Infrastructure**: Complete docs rebuild with better architecture coverage

### 🐛 Bug Fixes
- **Syntax Error Resolution**: Fixed complex example syntax issues preventing execution
- **Unicode Compatibility**: Windows encoding support with emoji fallbacks  
- **~ish Arithmetic**: Enhanced handling of negative numbers and function calls
- **CLI Error Messages**: Added kinda personality to error reporting with helpful suggestions
- **Example Organization**: Restructured examples with proper categorization and working examples

### 🛠️ Developer Experience
- **Enhanced CLI**: Better error messages with debugging hints and kinda attitude
- **Cross-Platform Testing**: Automatic example verification across all supported platforms
- **GitFlow CI Support**: Proper branch-based CI triggers for dev and feature branches
- **Robust Parsing**: Improved string-aware parentheses matching for complex constructs

### 📚 Documentation
- **Architecture Guide**: Comprehensive overview of transformation pipeline and design principles
- **Feature Documentation**: Complete coverage of all 6+ kinda constructs with examples  
- **Developer Guide**: Testing, contribution guidelines, and development workflow
- **Example Showcase**: 20+ working examples demonstrating all constructs individually and combined

### 🔧 Technical Improvements
- **Regex Optimization**: Pre-compiled patterns for better performance
- **Error Handling**: Graceful fallbacks and improved error context
- **Runtime Generation**: More robust fuzzy runtime with better exception handling
- **Cross-Language Support**: Enhanced C language foundation (experimental)

### 📦 Breaking Changes
- Version bump from 0.2.0 to 0.3.0 due to significant feature additions
- Enhanced construct syntax may require minor updates to existing code
- Improved error messages may change expected error output in tests

### 🎪 What's New for Users
- **All Constructs Working**: Every kinda construct now works reliably in complex scenarios
- **Better Examples**: Comprehensive chaos simulations showcasing real-world fuzzy programming
- **Cross-Platform**: Reliable execution on Windows, macOS, and Linux
- **Enhanced Personality**: More kinda attitude in CLI interactions and error messages

---

## [0.2.0] - Previous Release
- Initial public release with core fuzzy constructs
- Basic CLI functionality and transformation pipeline
- Foundation Python and C language support

---

*"In kinda-lang, even the changelog is kinda sure about what changed."* 🎲