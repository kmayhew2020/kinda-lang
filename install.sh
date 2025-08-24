#!/bin/bash
# Kinda installation script - because life's too short for complex setups

set -e

echo "🤷 Installing kinda... (this might work)"
echo

# Find Python (python3 preferred)
if command -v python3 &>/dev/null; then
  python_cmd="python3"
elif command -v python &>/dev/null; then
  python_cmd="python"
else
  echo "❌ Python not found. Install Python 3.8+ first."
  exit 1
fi

# Capture major.minor and enforce >= 3.8 using real tuple compare
version="$($python_cmd -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
$python_cmd -c 'import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)' || {
  echo "❌ Python $version found, but 3.8+ is required."
  exit 1
}

echo "✅ Using $python_cmd (Python $version)"

# Install kinda
echo "📦 Installing kinda-lang via pip..."
$python_cmd -m pip install -e . || {
    echo "💥 Installation failed. Classic."
    echo "🤷 Try: pip install --user -e ."
    exit 1
}

echo
echo "🎉 Installation complete! (probably)"
echo
echo "Try these commands:"
echo "  kinda --help      # See snarky help"  
echo "  kinda examples    # View examples"
echo "  kinda syntax      # Syntax reference"
echo
echo "🎲 Welcome to the chaos!"