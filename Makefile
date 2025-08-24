# Kinda Makefile - for people who like shortcuts

.PHONY: install test clean dev help examples

# Install kinda
install:
	@echo "🤷 Installing kinda..."
	pip install -e .
	@echo "✅ Installation complete! (probably)"
	@echo "Try: kinda --help"

# Install with dev dependencies
dev:
	@echo "📦 Installing kinda with dev tools..."
	pip install -e .[dev]
	@echo "✅ Dev setup complete!"

# Run tests
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v
	@echo "🎉 Tests complete! (assuming they passed)"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning up build artifacts..."
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	@echo "✨ Clean as a whistle!"

# Show examples
examples:
	@echo "🎲 Running kinda examples..."
	kinda examples

# Quick help
help:
	@echo "🤷 Kinda Makefile commands:"
	@echo "  make install  - Install kinda"
	@echo "  make dev      - Install with dev dependencies"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Clean build artifacts"
	@echo "  make examples - Show kinda examples"
	@echo ""
	@echo "After install, try:"
	@echo "  kinda --help"
	@echo "  kinda examples"
	@echo "  kinda syntax"

# Default target
.DEFAULT_GOAL := help