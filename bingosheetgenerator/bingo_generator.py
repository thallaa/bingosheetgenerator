#!/usr/bin/env python3
"""Cross-platform bingo sheet PDF generator."""

from __future__ import annotations

import argparse
import math
import random
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, LETTER
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
except ModuleNotFoundError as err:
    missing_module = err.name or "reportlab"
    print(
        f"Missing dependency '{missing_module}'. Install with: python3 -m pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(1)

LETTERS = "BINGO"
PRESET_COLORFUL = {
    "B": "#1F77B4",
    "I": "#D62728",
    "N": "#2CA02C",
    "G": "#FFBF00",
    "O": "#9467BD",
}


@dataclass
class Config:
    output: str
    sheets: int
    sheets_per_page: int
    paper_size: str
    min_number: int
    max_number: int
    distribution: str
    letter_color_mode: str
    custom_letter_colors: Optional[str]
    seed: Optional[int]
    assume_yes: bool


def parse_args(argv: Sequence[str]) -> Config:
    parser = argparse.ArgumentParser(
        description="Generate printable bingo sheet PDFs (A4/Letter)."
    )
    parser.add_argument("--output", default="bingo_sheets.pdf", help="Output PDF path")
    parser.add_argument(
        "--sheets",
        type=int,
        default=4,
        help="Total number of bingo sheets/cards to generate (default: 4)",
    )
    parser.add_argument(
        "--sheets-per-page",
        type=int,
        default=4,
        help="How many sheets/cards to place on each paper page (default: 4)",
    )
    parser.add_argument(
        "--paper-size",
        choices=["a4", "letter"],
        default="a4",
        help="Paper size for output PDF (default: a4)",
    )
    parser.add_argument(
        "--min-number",
        type=int,
        default=1,
        help="Lowest number in the bingo pool (default: 1)",
    )
    parser.add_argument(
        "--max-number",
        type=int,
        default=75,
        help="Highest number in the bingo pool (default: 75)",
    )
    parser.add_argument(
        "--distribution",
        choices=["segmented", "fully-random"],
        default="segmented",
        help=(
            "'segmented': each B/I/N/G/O column maps to a numeric range segment. "
            "'fully-random': any number can appear in any column."
        ),
    )
    parser.add_argument(
        "--letter-color-mode",
        choices=["black", "random", "custom"],
        default="black",
        help="BINGO letter coloring mode (default: black)",
    )
    parser.add_argument(
        "--custom-letter-colors",
        help=(
            "Required when --letter-color-mode custom. "
            "Format: B:#1F77B4,I:#D62728,N:#2CA02C,G:#FFBF00,O:#9467BD"
        ),
    )
    parser.add_argument("--seed", type=int, help="Optional random seed for repeatable output")
    parser.add_argument(
        "--assume-yes",
        action="store_true",
        help="Skip interactive warning confirmations",
    )

    args = parser.parse_args(argv)
    return Config(**vars(args))


def parse_hex_color(value: str) -> colors.Color:
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
        raise ValueError(f"Invalid color '{value}', expected #RRGGBB")
    return colors.HexColor(value)


def parse_custom_letter_colors(spec: Optional[str]) -> Dict[str, colors.Color]:
    if not spec:
        raise ValueError("--custom-letter-colors is required when --letter-color-mode custom")

    result: Dict[str, colors.Color] = {}
    for item in spec.split(","):
        if ":" not in item:
            raise ValueError(f"Invalid custom color entry '{item}', expected KEY:#RRGGBB")
        key, raw_color = item.split(":", 1)
        letter = key.strip().upper()
        if letter not in LETTERS:
            raise ValueError(f"Invalid letter '{letter}', allowed letters are B,I,N,G,O")
        result[letter] = parse_hex_color(raw_color.strip())

    missing = [letter for letter in LETTERS if letter not in result]
    if missing:
        missing_str = ", ".join(missing)
        raise ValueError(f"Missing custom colors for: {missing_str}")
    return result


def random_letter_colors(rng: random.Random) -> Dict[str, colors.Color]:
    mapping: Dict[str, colors.Color] = {}
    for letter in LETTERS:
        # Keep colors bright enough for printing readability.
        r = rng.randint(40, 220)
        g = rng.randint(40, 220)
        b = rng.randint(40, 220)
        mapping[letter] = colors.Color(r / 255.0, g / 255.0, b / 255.0)
    return mapping


def segment_ranges(min_number: int, max_number: int, parts: int = 5) -> List[List[int]]:
    numbers = list(range(min_number, max_number + 1))
    total = len(numbers)
    base = total // parts
    remainder = total % parts

    segments: List[List[int]] = []
    idx = 0
    for i in range(parts):
        size = base + (1 if i < remainder else 0)
        segments.append(numbers[idx : idx + size])
        idx += size
    return segments


def confirm_or_exit(message: str, assume_yes: bool) -> None:
    print(f"WARNING: {message}")
    if assume_yes:
        print("Continuing because --assume-yes was provided.")
        return

    answer = input("Continue anyway? [y/N]: ").strip().lower()
    if answer not in {"y", "yes"}:
        print("Aborted.")
        sys.exit(1)


def validate_config(config: Config) -> List[List[int]]:
    if config.sheets <= 0:
        raise ValueError("--sheets must be greater than 0")
    if config.sheets_per_page <= 0:
        raise ValueError("--sheets-per-page must be greater than 0")
    if config.max_number < config.min_number:
        raise ValueError("--max-number must be >= --min-number")

    all_numbers_count = config.max_number - config.min_number + 1
    if all_numbers_count < 24:
        raise ValueError("Number range must include at least 24 values for a 5x5 card with free center")

    if config.sheets % config.sheets_per_page != 0:
        pages_needed = math.ceil(config.sheets / config.sheets_per_page)
        capacity = pages_needed * config.sheets_per_page
        empty_slots = capacity - config.sheets
        confirm_or_exit(
            (
                f"Requested {config.sheets} sheet(s) with {config.sheets_per_page} per page. "
                f"This creates {pages_needed} page(s) with {empty_slots} empty slot(s)."
            ),
            config.assume_yes,
        )

    segments: List[List[int]] = []
    if config.distribution == "segmented":
        segments = segment_ranges(config.min_number, config.max_number, parts=5)
        lengths = [len(x) for x in segments]
        if len(set(lengths)) != 1:
            confirm_or_exit(
                (
                    "Number range does not split evenly across B/I/N/G/O columns "
                    f"({lengths}). This is unusual for segmented bingo."
                ),
                config.assume_yes,
            )

        required_per_col = [5, 5, 4, 5, 5]
        for letter, bucket, need in zip(LETTERS, segments, required_per_col):
            if len(bucket) < need:
                raise ValueError(
                    f"Not enough numbers in column {letter} range: need {need}, got {len(bucket)}"
                )

    return segments


def generate_card(
    rng: random.Random,
    min_number: int,
    max_number: int,
    distribution: str,
    segments: List[List[int]],
) -> List[List[Optional[int]]]:
    card: List[List[Optional[int]]] = [[None for _ in range(5)] for _ in range(5)]

    if distribution == "segmented":
        for col in range(5):
            need = 4 if col == 2 else 5
            chosen = sorted(rng.sample(segments[col], need))
            row_indices = [0, 1, 2, 3, 4]
            if col == 2:
                row_indices.remove(2)
            for row, value in zip(row_indices, chosen):
                card[row][col] = value
    else:
        pool = list(range(min_number, max_number + 1))
        chosen = rng.sample(pool, 24)
        rng.shuffle(chosen)
        i = 0
        for row in range(5):
            for col in range(5):
                if row == 2 and col == 2:
                    continue
                card[row][col] = chosen[i]
                i += 1

    return card


def choose_grid(sheets_per_page: int, page_w: float, page_h: float) -> Tuple[int, int]:
    best_cols = 1
    best_rows = sheets_per_page
    best_score = -1.0

    for cols in range(1, sheets_per_page + 1):
        rows = math.ceil(sheets_per_page / cols)
        cell_w = page_w / cols
        cell_h = page_h / rows
        score = min(cell_w, cell_h)
        if score > best_score:
            best_score = score
            best_cols = cols
            best_rows = rows

    return best_cols, best_rows


def draw_card(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    card: List[List[Optional[int]]],
    letter_colors: Dict[str, colors.Color],
) -> None:
    padding = 4 * mm
    inner_x = x + padding
    inner_y = y + padding
    inner_w = w - 2 * padding
    inner_h = h - 2 * padding

    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(x, y, w, h)

    title_h = inner_h * 0.18
    grid_h = inner_h - title_h - (2 * mm)
    col_w = inner_w / 5.0
    cell_h = grid_h / 5.0

    # Header letters B I N G O.
    header_font_size = max(10, min(26, title_h * 0.45))
    c.setFont("Helvetica-Bold", header_font_size)
    for col, letter in enumerate(LETTERS):
        c.setFillColor(letter_colors.get(letter, colors.black))
        cx = inner_x + (col + 0.5) * col_w
        cy = inner_y + grid_h + title_h * 0.35
        c.drawCentredString(cx, cy, letter)

    # Grid and values.
    c.setFillColor(colors.black)
    c.setFont("Helvetica", max(8, min(18, cell_h * 0.4)))

    grid_y = inner_y
    for r in range(6):
        yy = grid_y + r * cell_h
        c.line(inner_x, yy, inner_x + inner_w, yy)
    for col in range(6):
        xx = inner_x + col * col_w
        c.line(xx, grid_y, xx, grid_y + grid_h)

    for row in range(5):
        for col in range(5):
            cx = inner_x + (col + 0.5) * col_w
            cy = grid_y + (4 - row + 0.5) * cell_h
            if row == 2 and col == 2:
                c.setFont("Helvetica-Bold", max(7, min(14, cell_h * 0.3)))
                c.drawCentredString(cx, cy, "FREE")
                c.setFont("Helvetica", max(8, min(18, cell_h * 0.4)))
            else:
                value = card[row][col]
                c.drawCentredString(cx, cy, str(value))


def generate_pdf(config: Config) -> None:
    rng = random.Random(config.seed)
    paper_size = A4 if config.paper_size == "a4" else LETTER
    page_w, page_h = paper_size

    if config.letter_color_mode == "black":
        letter_colors = {letter: colors.black for letter in LETTERS}
    elif config.letter_color_mode == "random":
        # Start from recognizable colorfulness, then randomize shades.
        letter_colors = {letter: parse_hex_color(hex_code) for letter, hex_code in PRESET_COLORFUL.items()}
        letter_colors.update(random_letter_colors(rng))
    else:
        letter_colors = parse_custom_letter_colors(config.custom_letter_colors)

    segments = validate_config(config)

    pdf = canvas.Canvas(config.output, pagesize=paper_size)
    cols, rows = choose_grid(config.sheets_per_page, page_w, page_h)

    margin = 8 * mm
    gap = 4 * mm
    usable_w = page_w - 2 * margin - (cols - 1) * gap
    usable_h = page_h - 2 * margin - (rows - 1) * gap
    card_w = usable_w / cols
    card_h = usable_h / rows

    for sheet_idx in range(config.sheets):
        idx_on_page = sheet_idx % config.sheets_per_page
        if idx_on_page == 0 and sheet_idx > 0:
            pdf.showPage()

        row = idx_on_page // cols
        col = idx_on_page % cols

        x = margin + col * (card_w + gap)
        y_top = page_h - margin - row * (card_h + gap)
        y = y_top - card_h

        card = generate_card(
            rng=rng,
            min_number=config.min_number,
            max_number=config.max_number,
            distribution=config.distribution,
            segments=segments,
        )
        draw_card(pdf, x, y, card_w, card_h, card, letter_colors)

    pdf.save()


def main(argv: Sequence[str]) -> int:
    try:
        config = parse_args(argv)
        generate_pdf(config)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130

    print(f"Generated: {config.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
