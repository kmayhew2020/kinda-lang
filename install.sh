#!/usr/bin/env bash
set -euo pipefail

# Enhanced install.sh for kinda-lang
# Supports automatic PATH handling and developer mode

echo "🤷 Installing kinda... (this might work)"
echo

# Parse command line arguments
DEV_MODE=false
NO_PATH=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --dev)
      DEV_MODE=true
      shift
      ;;
    --no-path)
      NO_PATH=true
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --dev      Install development dependencies and setup dev environment"
      echo "  --no-path  Skip automatic PATH configuration"
      echo "  -h, --help Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Detect shell configuration file
detect_shell_config() {
    if [[ -n "${ZSH_VERSION:-}" ]] || [[ "$SHELL" == *"zsh"* ]]; then
        echo "$HOME/.zshrc"
    elif [[ -n "${BASH_VERSION:-}" ]] || [[ "$SHELL" == *"bash"* ]]; then
        [[ -f "$HOME/.bashrc" ]] && echo "$HOME/.bashrc" || echo "$HOME/.bash_profile"
    elif [[ "$SHELL" == *"fish"* ]]; then
        mkdir -p "$HOME/.config/fish"
        echo "$HOME/.config/fish/config.fish"
    else
        echo "$HOME/.profile"  # POSIX fallback
    fi
}

# Configure PATH for the user's shell
configure_path() {
    if [[ "$NO_PATH" == true ]]; then
        echo "ℹ️  Skipping PATH configuration (--no-path specified)"
        return 0
    fi

    local shell_config
    shell_config=$(detect_shell_config)

    # Check if ~/.local/bin is already in PATH
    if echo "$PATH" | grep -q "$HOME/.local/bin"; then
        echo "✅ ~/.local/bin already in PATH"
        return 0
    fi

    echo "🔧 Adding ~/.local/bin to PATH in $shell_config"

    # Create backup
    if [[ -f "$shell_config" ]]; then
        cp "$shell_config" "$shell_config.backup.$(date +%s)" || true
    fi

    # Add PATH configuration based on shell
    if [[ "$shell_config" == *"config.fish" ]]; then
        echo 'set -gx PATH "$HOME/.local/bin" $PATH' >> "$shell_config"
    else
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$shell_config"
    fi

    # Update current session
    export PATH="$HOME/.local/bin:$PATH"
    echo "✅ PATH configured for current and future sessions"
}

# Find Python (python3 preferred)
if command -v python3 &>/dev/null; then
  python_cmd="python3"
elif command -v python &>/dev/null; then
  python_cmd="python"
else
  echo "❌ Python not found. Install Python 3.9+ first."
  exit 1
fi

# Enforce >= 3.9 (updated from 3.8)
version="$($python_cmd -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
$python_cmd -c 'import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)' || {
  echo "❌ Python $version found, but 3.9+ is required."
  exit 1
}
echo "✅ Using $python_cmd (Python $version)"

# Installation strategy selection
INSTALLATION_METHOD=""

# 1. Check for pipx (preferred)
if command -v pipx &>/dev/null; then
    echo "✨ Found pipx - using isolated installation"
    pipx install . || {
        echo "💥 pipx install failed. Falling back to pip --user"
        pip install --user . || {
            echo "❌ All installation methods failed"
            exit 1
        }
        INSTALLATION_METHOD="pip_user"
        configure_path
    }
    INSTALLATION_METHOD="pipx"

# 2. Use pip --user with PATH handling (if not in venv)
elif [[ -z "${VIRTUAL_ENV:-}" ]]; then
    echo "📦 Using pip --user installation"
    pip install --user . || {
        echo "💥 pip --user install failed."
        echo "   • Try creating a virtual environment first"
        echo "   • Or install pipx: pip install --user pipx"
        exit 1
    }
    INSTALLATION_METHOD="pip_user"
    configure_path

# 3. Create venv as fallback (existing behavior)
else
    echo "ℹ️ Detected active venv: $VIRTUAL_ENV"
    echo "📦 Installing in virtual environment"

    # Make sure pip is ready
    python -m pip install --upgrade pip setuptools wheel

    # Install kinda (editable)
    echo "📦 Installing kinda-lang via pip (editable)..."
    pip install -e . || {
        echo "💥 Editable install failed."
        echo "   • If this is a system/managed env, try one of:"
        echo "     - pip install --user -e .            # per-user site-packages"
        echo "     - pip install --break-system-packages -e .   # Debian/Ubuntu ONLY, risky"
        exit 1
    }
    INSTALLATION_METHOD="venv"
fi

# Development mode setup
if [[ "$DEV_MODE" == true ]]; then
    echo "🧪 Setting up development environment..."

    # Install dev dependencies
    if [[ "$INSTALLATION_METHOD" == "pipx" ]]; then
        pipx inject kinda-lang pytest pytest-cov black mypy || {
            echo "⚠️  Failed to inject dev dependencies via pipx"
            echo "   Install manually: pipx inject kinda-lang pytest pytest-cov black mypy"
        }
    else
        pip install -e .[dev] || {
            echo "💥 Dev dependencies install failed."
            echo "   Continuing with basic installation..."
        }
    fi

    # Run initial tests to verify setup
    echo "🧪 Running initial test suite..."
    if command -v pytest &>/dev/null; then
        pytest tests/ -v --tb=short || {
            echo "⚠️  Some tests failed - this might be normal for kinda-lang"
        }
    else
        echo "⚠️  pytest not available - skipping test run"
    fi

    echo "✅ Development environment setup complete!"
fi

echo
echo "🎉 Installation complete!"
echo ""
echo "✅ kinda-lang is now available"

# Provide appropriate next steps based on installation method
case "$INSTALLATION_METHOD" in
    "pipx")
        echo "✅ Try: kinda --help"
        echo "✅ Try: kinda examples"
        ;;
    "pip_user")
        echo "✅ Try: kinda --help"
        echo "✅ Try: kinda examples"
        if [[ "$NO_PATH" == false ]]; then
            echo ""
            echo "ℹ️  PATH updated - restart terminal or run:"
            shell_config=$(detect_shell_config)
            echo "   source $shell_config"
        fi
        ;;
    "venv")
        echo "✅ Try: kinda --help"
        echo "✅ Try: kinda examples"
        echo ""
        echo "ℹ️  Note: kinda is available in this virtual environment"
        echo "   Activate with: source .venv/bin/activate"
        ;;
esac

if [[ "$DEV_MODE" == true ]]; then
    echo ""
    echo "🛠️  Development commands:"
    echo "   pytest tests/           # Run test suite"
    echo "   black src/ tests/       # Format code"
    echo "   mypy src/              # Type checking"
fi

echo ""
echo "🤷 Welcome to kinda-lang - where code is honest about its uncertainty!"