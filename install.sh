#!/usr/bin/env bash
set -euo pipefail

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

# Enforce >= 3.8
version="$($python_cmd -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
$python_cmd -c 'import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)' || {
  echo "❌ Python $version found, but 3.8+ is required."
  exit 1
}
echo "✅ Using $python_cmd (Python $version)"

# Prefer a venv to avoid PEP 668 managed-env errors
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  venv_dir=".venv"
  echo "🧪 Creating virtual environment at $venv_dir"
  $python_cmd -m venv "$venv_dir"
  # shellcheck disable=SC1090
  source "$venv_dir/bin/activate"
  echo "✅ Activated venv: $venv_dir"
else
  echo "ℹ️ Detected active venv: $VIRTUAL_ENV"
fi

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

echo
echo "🎉 Installation complete!"
echo "Try:"
echo "  source .venv/bin/activate   # activate env (Mac/Linux)"
echo "  kinda --help                # see help"
