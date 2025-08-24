#!/bin/bash
# Kinda installation script - because life's too short for complex setups

set -e

echo "🤷 Installing kinda... (this might work)"
echo

# Check Python version
python_cmd=""
if command -v python3 &> /dev/null; then
    python_cmd="python3"
elif command -v python &> /dev/null; then 
    python_cmd="python"
else
    echo "❌ Python not found. Install Python 3.8+ first."
    exit 1
fi

# Check Python version is adequate
version=$($python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ $(echo "$version < 3.8" | bc -l 2>/dev/null || echo "0") == "1" ]]; then
    echo "❌ Python $version found, but kinda needs Python 3.8+."
    echo "🤷 Your Python is... vintage. Upgrade maybe?"
    exit 1
fi

echo "✅ Found Python $version (good enough)"

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