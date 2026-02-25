#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Tero Halla-aho
"""Desktop GUI for the bingo PDF generator."""

from __future__ import annotations

import os
import sys
from dataclasses import asdict
from typing import Optional

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ModuleNotFoundError:
    print(
        "Tkinter is not available in this Python installation. "
        "Install a Tk-enabled Python (for example: python-tk via Homebrew on macOS, "
        "or python3-tk on Debian/Ubuntu).",
        file=sys.stderr,
    )
    raise SystemExit(1)

from bingo_generator import Config, generate_pdf


class BingoGui(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Bingo Sheet Generator")
        self.geometry("720x610")
        self.minsize(680, 560)

        self.output_path = tk.StringVar(value=os.path.join(os.getcwd(), "bingo_sheets.pdf"))
        self.sheets = tk.StringVar(value="4")
        self.sheets_per_page = tk.StringVar(value="4")
        self.paper_size = tk.StringVar(value="a4")
        self.min_number = tk.StringVar(value="1")
        self.max_number = tk.StringVar(value="75")
        self.distribution = tk.StringVar(value="segmented")
        self.letter_color_mode = tk.StringVar(value="black")
        self.custom_letter_colors = tk.StringVar(
            value="B:#1F77B4,I:#D62728,N:#2CA02C,G:#FFBF00,O:#9467BD"
        )
        self.free_center = tk.BooleanVar(value=True)
        self.free_center_text = tk.StringVar(value="FREE")
        self.seed = tk.StringVar(value="")
        self.status = tk.StringVar(value="Ready")

        self._build_ui()
        self._update_custom_color_state()
        self._update_free_center_state()

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=14)
        root.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(root, text="Bingo Sheet Generator", font=("TkDefaultFont", 13, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        self._add_file_picker(root, 1, "Output PDF", self.output_path, self._select_output)
        self._add_entry(root, 2, "Total sheets", self.sheets)
        self._add_entry(root, 3, "Sheets per page", self.sheets_per_page)
        self._add_combo(root, 4, "Paper size", self.paper_size, ["a4", "letter"])
        self._add_entry(root, 5, "Minimum number", self.min_number)
        self._add_entry(root, 6, "Maximum number", self.max_number)
        self._add_combo(root, 7, "Distribution", self.distribution, ["segmented", "fully-random"])
        self._add_combo(
            root,
            8,
            "Letter colors",
            self.letter_color_mode,
            ["black", "random", "custom"],
            on_change=lambda *_: self._update_custom_color_state(),
        )
        self.custom_color_entry = self._add_entry(
            root,
            9,
            "Custom colors",
            self.custom_letter_colors,
            hint="B:#1F77B4,I:#D62728,N:#2CA02C,G:#FFBF00,O:#9467BD",
        )

        free_center_box = ttk.Checkbutton(
            root,
            text="Use free center cell",
            variable=self.free_center,
            command=self._update_free_center_state,
        )
        free_center_box.grid(row=10, column=0, columnspan=3, sticky="w", pady=(4, 0))

        self.free_center_text_entry = self._add_entry(
            root,
            11,
            "Free center text",
            self.free_center_text,
            hint="Shown only when free center is enabled",
        )

        self._add_entry(root, 12, "Random seed (optional)", self.seed)

        button_row = ttk.Frame(root)
        button_row.grid(row=13, column=0, columnspan=3, sticky="ew", pady=(16, 6))
        button_row.columnconfigure(0, weight=1)
        generate_btn = ttk.Button(button_row, text="Generate PDF", command=self._generate)
        generate_btn.grid(row=0, column=0, sticky="e")

        status = ttk.Label(root, textvariable=self.status, foreground="#0a4")
        status.grid(row=14, column=0, columnspan=3, sticky="w", pady=(4, 0))

        tips = ttk.Label(
            root,
            text=(
                "Tip: Use segmented for classic B-I-N-G-O ranges. "
                "Warnings will ask for confirmation before generating."
            ),
            wraplength=640,
            justify="left",
        )
        tips.grid(row=15, column=0, columnspan=3, sticky="w", pady=(14, 0))

        root.columnconfigure(1, weight=1)

    def _add_entry(
        self,
        root: ttk.Frame,
        row: int,
        label_text: str,
        variable: tk.Variable,
        hint: Optional[str] = None,
    ) -> ttk.Entry:
        ttk.Label(root, text=label_text).grid(row=row, column=0, sticky="w", pady=4)
        entry = ttk.Entry(root, textvariable=variable)
        entry.grid(row=row, column=1, sticky="ew", pady=4)
        if hint:
            ttk.Label(root, text=hint).grid(row=row, column=2, sticky="w", padx=(10, 0), pady=4)
        return entry

    def _add_combo(
        self,
        root: ttk.Frame,
        row: int,
        label_text: str,
        variable: tk.StringVar,
        values: list[str],
        on_change=None,
    ) -> None:
        ttk.Label(root, text=label_text).grid(row=row, column=0, sticky="w", pady=4)
        combo = ttk.Combobox(root, textvariable=variable, values=values, state="readonly")
        combo.grid(row=row, column=1, sticky="ew", pady=4)
        if on_change:
            combo.bind("<<ComboboxSelected>>", on_change)

    def _add_file_picker(
        self,
        root: ttk.Frame,
        row: int,
        label_text: str,
        variable: tk.StringVar,
        browse_cmd,
    ) -> None:
        ttk.Label(root, text=label_text).grid(row=row, column=0, sticky="w", pady=4)
        entry = ttk.Entry(root, textvariable=variable)
        entry.grid(row=row, column=1, sticky="ew", pady=4)
        ttk.Button(root, text="Browse...", command=browse_cmd).grid(row=row, column=2, sticky="w", pady=4)

    def _update_custom_color_state(self) -> None:
        state = "normal" if self.letter_color_mode.get() == "custom" else "disabled"
        self.custom_color_entry.configure(state=state)

    def _update_free_center_state(self) -> None:
        state = "normal" if self.free_center.get() else "disabled"
        self.free_center_text_entry.configure(state=state)

    def _select_output(self) -> None:
        selected = filedialog.asksaveasfilename(
            title="Save Bingo PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=os.path.basename(self.output_path.get() or "bingo_sheets.pdf"),
        )
        if selected:
            self.output_path.set(selected)

    def _int_value(self, field_name: str, raw: str) -> int:
        raw = raw.strip()
        if not raw:
            raise ValueError(f"{field_name} is required")
        return int(raw)

    def _optional_int(self, raw: str) -> Optional[int]:
        raw = raw.strip()
        if not raw:
            return None
        return int(raw)

    def _warning_handler(self, message: str) -> bool:
        return messagebox.askyesno("Configuration warning", f"{message}\n\nContinue anyway?")

    def _build_config(self) -> Config:
        return Config(
            output=self.output_path.get().strip(),
            sheets=self._int_value("Total sheets", self.sheets.get()),
            sheets_per_page=self._int_value("Sheets per page", self.sheets_per_page.get()),
            paper_size=self.paper_size.get(),
            min_number=self._int_value("Minimum number", self.min_number.get()),
            max_number=self._int_value("Maximum number", self.max_number.get()),
            distribution=self.distribution.get(),
            letter_color_mode=self.letter_color_mode.get(),
            custom_letter_colors=self.custom_letter_colors.get().strip() or None,
            free_center=self.free_center.get(),
            free_center_text=self.free_center_text.get().strip() or "FREE",
            seed=self._optional_int(self.seed.get()),
            assume_yes=True,
        )

    def _generate(self) -> None:
        try:
            config = self._build_config()
            if not config.output:
                raise ValueError("Output PDF path is required")

            self.status.set("Generating PDF...")
            self.update_idletasks()
            generate_pdf(config, warning_handler=self._warning_handler)
        except ValueError as err:
            self.status.set("Ready")
            messagebox.showerror("Cannot generate PDF", str(err))
            return
        except Exception as err:  # pragma: no cover
            self.status.set("Ready")
            messagebox.showerror("Unexpected error", str(err))
            return

        self.status.set(f"Generated: {config.output}")
        messagebox.showinfo("Done", f"Bingo PDF generated:\n{config.output}")


def main() -> int:
    app = BingoGui()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
