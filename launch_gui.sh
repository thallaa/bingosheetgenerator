#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python not found. Install Python 3.10+ and run again." >&2
  exit 1
fi

if [ ! -d .venv ]; then
  echo "Creating virtual environment..."
  "$PYTHON_BIN" -m venv .venv
fi

VENV_PY=".venv/bin/python"

echo "Installing/updating dependencies..."
"$VENV_PY" -m pip install -r requirements.txt

if ! "$VENV_PY" - <<'PY'
import tkinter  # noqa: F401
PY
then
  echo
  echo "Tkinter is not available in this Python installation."
  case "$(uname -s)" in
    Darwin)
      echo "On macOS, install a Tk-enabled Python, for example:"
      echo "  brew install python-tk@3.12"
      echo "Then rerun ./launch_gui.sh"
      ;;
    Linux)
      echo "On Debian/Ubuntu, install:"
      echo "  sudo apt-get install python3-tk"
      ;;
    *)
      echo "Install Tk support for your Python version, then rerun this script."
      ;;
  esac
  exit 1
fi

echo "Starting GUI..."
exec "$VENV_PY" bingo_gui.py
