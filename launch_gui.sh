#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_PY=".venv/bin/python"

has_tk() {
  "$1" - <<'PY' >/dev/null 2>&1
import tkinter  # noqa: F401
PY
}

pick_python_with_tk() {
  local candidate
  for candidate in "$PYTHON_BIN" python3 python3.13 python3.12 python3.11 python; do
    if command -v "$candidate" >/dev/null 2>&1 && has_tk "$candidate"; then
      command -v "$candidate"
      return 0
    fi
  done
  return 1
}

if ! PY_WITH_TK="$(pick_python_with_tk)"; then
  echo
  echo "No Tk-enabled Python interpreter was found."
  case "$(uname -s)" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then
        read -r -p "Install Tk-enabled Python via Homebrew now? [y/N] " install_reply
        case "${install_reply,,}" in
          y|yes)
            echo "Installing with Homebrew..."
            brew install python@3.12 python-tk@3.12
            ;;
          *)
            echo "Skipped Homebrew install."
            ;;
        esac
      fi
      if ! PY_WITH_TK="$(pick_python_with_tk)"; then
        echo "On macOS, install a Tk-enabled Python (examples):"
        echo "  brew install python@3.12 python-tk@3.12"
        echo "  # or install Python from python.org (includes tkinter)"
        exit 1
      fi
      ;;
    Linux)
      echo "On Debian/Ubuntu, install:"
      echo "  sudo apt-get install python3 python3-tk"
      exit 1
      ;;
    *)
      echo "Install Python 3.10+ with Tk support and rerun this script."
      exit 1
      ;;
  esac
fi

if [ ! -d .venv ]; then
  echo "Creating virtual environment with $PY_WITH_TK..."
  "$PY_WITH_TK" -m venv .venv
elif ! has_tk "$VENV_PY"; then
  echo "Existing .venv Python lacks Tkinter. Recreating virtual environment with $PY_WITH_TK..."
  rm -rf .venv
  "$PY_WITH_TK" -m venv .venv
fi

echo "Installing/updating dependencies..."
"$VENV_PY" -m pip install -r requirements.txt

echo "Starting GUI..."
exec "$VENV_PY" bingo_gui.py
