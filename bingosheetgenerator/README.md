# Bingo Sheet Generator

Cross-platform Python CLI for generating printable bingo sheet PDFs.

## Features
- Standard 5x5 bingo sheets with `FREE` center.
- Configurable number range (`--min-number`, `--max-number`, default `1-75`).
- Configurable total sheets (`--sheets`).
- Configurable sheets per paper page (`--sheets-per-page`, default `4`).
- Configurable paper size (`a4` default, or `letter`).
- Two number placement modes:
  - `segmented` (default): number range split across B/I/N/G/O columns.
    - Values are sorted smallest to largest within each column.
  - `fully-random`: numbers can appear in any column/cell.
- BINGO letter color modes:
  - `black` (default)
  - `random`
  - `custom` via hex colors
- Safety warnings requiring confirmation:
  - Range does not split evenly across B/I/N/G/O in `segmented` mode.
  - Requested sheet count leaves empty card slots on final page.

## Install

```bash
python3 -m pip install -r requirements.txt
```

## Usage

```bash
python3 bingo_generator.py --sheets 40 --output bingo_40.pdf
```

Custom examples:

```bash
# Default behavior: 1-75, segmented columns, sorted per column, A4, 4 sheets/page
python3 bingo_generator.py --sheets 16 --output default.pdf

# US letter, 6 sheets per page
python3 bingo_generator.py --sheets 30 --sheets-per-page 6 --paper-size letter --output letter.pdf

# Fully random number positions
python3 bingo_generator.py --sheets 12 --distribution fully-random --output random_positions.pdf

# Custom BINGO letter colors
python3 bingo_generator.py \
  --sheets 20 \
  --letter-color-mode custom \
  --custom-letter-colors 'B:#1F77B4,I:#D62728,N:#2CA02C,G:#FFBF00,O:#9467BD' \
  --output custom_colors.pdf

# Non-interactive mode (auto-confirm warnings)
python3 bingo_generator.py --sheets 10 --sheets-per-page 4 --assume-yes --output partial_last_page.pdf
```

## Notes
- Works on Linux, macOS, and Windows with Python 3.10+.
- If using `--distribution segmented`, choose ranges that divide well into 5 segments for classic behavior.

## License
MIT. See the repository `LICENSE` file.
