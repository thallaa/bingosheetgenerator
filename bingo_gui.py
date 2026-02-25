#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Tero Halla-aho
"""Desktop GUI for the bingo PDF generator."""

from __future__ import annotations

import locale
import os
import sys
from typing import Dict, Optional

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

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "app_title": "Bingo Sheet Generator",
        "title": "Bingo Sheet Generator",
        "language": "Language",
        "output_pdf": "Output PDF",
        "total_sheets": "Total sheets",
        "sheets_per_page": "Sheets per page",
        "paper_size": "Paper size",
        "minimum_number": "Minimum number",
        "maximum_number": "Maximum number",
        "distribution": "Distribution",
        "letter_colors": "Letter colors",
        "custom_colors": "Custom colors",
        "custom_colors_hint": "B:#1F77B4,I:#D62728,N:#2CA02C,G:#FFBF00,O:#9467BD",
        "use_free_center": "Use free center cell",
        "free_center_text": "Free center text",
        "free_center_hint": "Shown only when free center is enabled",
        "seed_optional": "Random seed (optional)",
        "seed_hint": "Use same value to regenerate identical cards; leave empty for new random cards.",
        "generate_pdf": "Generate PDF",
        "ready": "Ready",
        "generating": "Generating PDF...",
        "tip": "Tip: Use segmented for classic B-I-N-G-O ranges. Warnings will ask for confirmation before generating.",
        "browse": "Browse...",
        "save_pdf": "Save Bingo PDF",
        "pdf_files": "PDF files",
        "all_files": "All files",
        "config_warning": "Configuration warning",
        "continue_anyway": "Continue anyway?",
        "cannot_generate": "Cannot generate PDF",
        "unexpected_error": "Unexpected error",
        "output_required": "Output PDF path is required",
        "generated": "Generated: {path}",
        "done": "Done",
        "generated_message": "Bingo PDF generated:\n{path}",
        "field_required": "{field} is required",
        "dist_segmented": "Segmented",
        "dist_fully-random": "Fully random",
        "color_black": "Black",
        "color_random": "Random",
        "color_custom": "Custom",
    },
    "fi": {
        "app_title": "Bingolappugeneraattori",
        "title": "Bingolappugeneraattori",
        "language": "Kieli",
        "output_pdf": "PDF-tiedosto",
        "total_sheets": "Lappujen määrä",
        "sheets_per_page": "Lappuja per sivu",
        "paper_size": "Paperikoko",
        "minimum_number": "Pienin numero",
        "maximum_number": "Suurin numero",
        "distribution": "Numerojako",
        "letter_colors": "Kirjainten väri",
        "custom_colors": "Omat värit",
        "custom_colors_hint": "B:#1F77B4,I:#D62728,N:#2CA02C,G:#FFBF00,O:#9467BD",
        "use_free_center": "Käytä vapaata keskiruutua",
        "free_center_text": "Keskiruudun teksti",
        "free_center_hint": "Näytetään vain, kun vapaa keskikohta on käytössä",
        "seed_optional": "Satunnaissiemen (valinnainen)",
        "seed_hint": "Sama arvo tuottaa samat laput uudelleen; tyhjä kenttä luo aina uudet satunnaiset laput.",
        "generate_pdf": "Luo PDF",
        "ready": "Valmis",
        "generating": "Luodaan PDF...",
        "tip": "Vinkki: segmented vastaa klassista B-I-N-G-O-jakoa. Varoituksissa pyydetään vahvistus ennen luontia.",
        "browse": "Selaa...",
        "save_pdf": "Tallenna bingo-PDF",
        "pdf_files": "PDF-tiedostot",
        "all_files": "Kaikki tiedostot",
        "config_warning": "Asetusvaroitus",
        "continue_anyway": "Jatketaanko silti?",
        "cannot_generate": "PDF:n luonti ei onnistunut",
        "unexpected_error": "Odottamaton virhe",
        "output_required": "PDF-tiedoston polku vaaditaan",
        "generated": "Luotu: {path}",
        "done": "Valmis",
        "generated_message": "Bingo-PDF luotu:\n{path}",
        "field_required": "Kenttä '{field}' on pakollinen",
        "dist_segmented": "Segmentoitu",
        "dist_fully-random": "Täysin satunnainen",
        "color_black": "Musta",
        "color_random": "Satunnainen",
        "color_custom": "Oma",
    },
}

LANGUAGE_LABELS = {
    "en": "English",
    "fi": "Suomi",
}

SUPPORTED_LANGUAGES = set(TRANSLATIONS.keys())


def detect_language() -> str:
    env_candidates = [os.environ.get("LC_ALL"), os.environ.get("LC_MESSAGES"), os.environ.get("LANG")]
    for raw in env_candidates:
        if raw:
            code = raw.split(".", 1)[0].split("_", 1)[0].lower()
            if code in SUPPORTED_LANGUAGES:
                return code

    locale_info = locale.getlocale()
    if locale_info and locale_info[0]:
        code = locale_info[0].split("_", 1)[0].lower()
        if code in SUPPORTED_LANGUAGES:
            return code

    return "en"


class BingoGui(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.language_code = tk.StringVar(value=detect_language())
        self.title(self.tr("app_title"))
        self.geometry("720x640")
        self.minsize(680, 580)

        self.output_path = tk.StringVar(value=os.path.join(os.getcwd(), "bingo_sheets.pdf"))
        self.sheets = tk.StringVar(value="4")
        self.sheets_per_page = tk.StringVar(value="4")
        self.paper_size = tk.StringVar(value="a4")
        self.min_number = tk.StringVar(value="1")
        self.max_number = tk.StringVar(value="75")
        self.distribution = tk.StringVar(value="segmented")
        self.distribution_display = tk.StringVar(value="")
        self.letter_color_mode = tk.StringVar(value="black")
        self.letter_color_display = tk.StringVar(value="")
        self.custom_letter_colors = tk.StringVar(
            value="B:#1F77B4,I:#D62728,N:#2CA02C,G:#FFBF00,O:#9467BD"
        )
        self.free_center = tk.BooleanVar(value=True)
        self.free_center_text = tk.StringVar(value="FREE")
        self.seed = tk.StringVar(value="")
        self.status = tk.StringVar(value=self.tr("ready"))
        self._root_frame: Optional[ttk.Frame] = None

        self._build_ui()
        self._update_custom_color_state()
        self._update_free_center_state()

    def tr(self, key: str, **kwargs: str) -> str:
        lang = self.language_code.get()
        table = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
        template = table.get(key, TRANSLATIONS["en"].get(key, key))
        return template.format(**kwargs) if kwargs else template

    def _build_ui(self) -> None:
        if self._root_frame is not None:
            self._root_frame.destroy()

        root = ttk.Frame(self, padding=14)
        root.pack(fill=tk.BOTH, expand=True)
        self._root_frame = root

        self.title(self.tr("app_title"))

        title = ttk.Label(root, text=self.tr("title"), font=("TkDefaultFont", 13, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        self._add_language_selector(root, 1)
        self._add_file_picker(root, 2, self.tr("output_pdf"), self.output_path, self._select_output)
        self._add_entry(root, 3, self.tr("total_sheets"), self.sheets)
        self._add_entry(root, 4, self.tr("sheets_per_page"), self.sheets_per_page)
        self._add_combo(root, 5, self.tr("paper_size"), self.paper_size, ["a4", "letter"])
        self._add_entry(root, 6, self.tr("minimum_number"), self.min_number)
        self._add_entry(root, 7, self.tr("maximum_number"), self.max_number)
        self._add_localized_combo(
            root,
            8,
            self.tr("distribution"),
            self.distribution,
            self.distribution_display,
            ["segmented", "fully-random"],
            "dist_",
        )
        self._add_localized_combo(
            root,
            9,
            self.tr("letter_colors"),
            self.letter_color_mode,
            self.letter_color_display,
            ["black", "random", "custom"],
            "color_",
            on_change=lambda *_: self._update_custom_color_state(),
        )

        self.custom_color_entry = self._add_entry(
            root,
            10,
            self.tr("custom_colors"),
            self.custom_letter_colors,
            hint=self.tr("custom_colors_hint"),
        )

        free_center_box = ttk.Checkbutton(
            root,
            text=self.tr("use_free_center"),
            variable=self.free_center,
            command=self._update_free_center_state,
        )
        free_center_box.grid(row=11, column=0, columnspan=3, sticky="w", pady=(4, 0))

        self.free_center_text_entry = self._add_entry(
            root,
            12,
            self.tr("free_center_text"),
            self.free_center_text,
            hint=self.tr("free_center_hint"),
        )

        self._add_entry(root, 13, self.tr("seed_optional"), self.seed, hint=self.tr("seed_hint"))

        button_row = ttk.Frame(root)
        button_row.grid(row=14, column=0, columnspan=3, sticky="ew", pady=(16, 6))
        button_row.columnconfigure(0, weight=1)
        generate_btn = ttk.Button(button_row, text=self.tr("generate_pdf"), command=self._generate)
        generate_btn.grid(row=0, column=0, sticky="e")

        status = ttk.Label(root, textvariable=self.status, foreground="#0a4")
        status.grid(row=15, column=0, columnspan=3, sticky="w", pady=(4, 0))

        tips = ttk.Label(root, text=self.tr("tip"), wraplength=640, justify="left")
        tips.grid(row=16, column=0, columnspan=3, sticky="w", pady=(14, 0))

        root.columnconfigure(1, weight=1)

    def _add_language_selector(self, root: ttk.Frame, row: int) -> None:
        ttk.Label(root, text=self.tr("language")).grid(row=row, column=0, sticky="w", pady=4)
        labels = [LANGUAGE_LABELS[code] for code in sorted(SUPPORTED_LANGUAGES)]
        selected_label = LANGUAGE_LABELS.get(self.language_code.get(), LANGUAGE_LABELS["en"])
        self.language_display = tk.StringVar(value=selected_label)
        combo = ttk.Combobox(root, textvariable=self.language_display, values=labels, state="readonly")
        combo.grid(row=row, column=1, sticky="ew", pady=4)
        combo.bind("<<ComboboxSelected>>", self._on_language_change)

    def _on_language_change(self, *_args) -> None:
        selected = self.language_display.get()
        for code, label in LANGUAGE_LABELS.items():
            if label == selected:
                self.language_code.set(code)
                break
        self.status.set(self.tr("ready"))
        self._build_ui()
        self._update_custom_color_state()
        self._update_free_center_state()

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

    def _add_localized_combo(
        self,
        root: ttk.Frame,
        row: int,
        label_text: str,
        key_variable: tk.StringVar,
        display_variable: tk.StringVar,
        keys: list[str],
        prefix: str,
        on_change=None,
    ) -> None:
        ttk.Label(root, text=label_text).grid(row=row, column=0, sticky="w", pady=4)
        labels = [self.tr(f"{prefix}{key}") for key in keys]
        label_by_key = {key: self.tr(f"{prefix}{key}") for key in keys}
        key_by_label = {label: key for key, label in label_by_key.items()}
        display_variable.set(label_by_key.get(key_variable.get(), labels[0]))

        combo = ttk.Combobox(root, textvariable=display_variable, values=labels, state="readonly")
        combo.grid(row=row, column=1, sticky="ew", pady=4)

        def on_select(_event):
            selected_label = display_variable.get()
            selected_key = key_by_label.get(selected_label)
            if selected_key:
                key_variable.set(selected_key)
            if on_change:
                on_change(_event)

        combo.bind("<<ComboboxSelected>>", on_select)

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
        ttk.Button(root, text=self.tr("browse"), command=browse_cmd).grid(row=row, column=2, sticky="w", pady=4)

    def _update_custom_color_state(self) -> None:
        state = "normal" if self.letter_color_mode.get() == "custom" else "disabled"
        self.custom_color_entry.configure(state=state)

    def _update_free_center_state(self) -> None:
        state = "normal" if self.free_center.get() else "disabled"
        self.free_center_text_entry.configure(state=state)

    def _select_output(self) -> None:
        selected = filedialog.asksaveasfilename(
            title=self.tr("save_pdf"),
            defaultextension=".pdf",
            filetypes=[(self.tr("pdf_files"), "*.pdf"), (self.tr("all_files"), "*.*")],
            initialfile=os.path.basename(self.output_path.get() or "bingo_sheets.pdf"),
        )
        if selected:
            self.output_path.set(selected)

    def _int_value(self, field_name: str, raw: str) -> int:
        raw = raw.strip()
        if not raw:
            raise ValueError(self.tr("field_required", field=field_name))
        return int(raw)

    def _optional_int(self, raw: str) -> Optional[int]:
        raw = raw.strip()
        if not raw:
            return None
        return int(raw)

    def _warning_handler(self, message: str) -> bool:
        return messagebox.askyesno(
            self.tr("config_warning"),
            f"{message}\n\n{self.tr('continue_anyway')}",
        )

    def _build_config(self) -> Config:
        return Config(
            output=self.output_path.get().strip(),
            sheets=self._int_value(self.tr("total_sheets"), self.sheets.get()),
            sheets_per_page=self._int_value(self.tr("sheets_per_page"), self.sheets_per_page.get()),
            paper_size=self.paper_size.get(),
            min_number=self._int_value(self.tr("minimum_number"), self.min_number.get()),
            max_number=self._int_value(self.tr("maximum_number"), self.max_number.get()),
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
                raise ValueError(self.tr("output_required"))

            self.status.set(self.tr("generating"))
            self.update_idletasks()
            generate_pdf(config, warning_handler=self._warning_handler)
        except ValueError as err:
            self.status.set(self.tr("ready"))
            messagebox.showerror(self.tr("cannot_generate"), str(err))
            return
        except Exception as err:  # pragma: no cover
            self.status.set(self.tr("ready"))
            messagebox.showerror(self.tr("unexpected_error"), str(err))
            return

        self.status.set(self.tr("generated", path=config.output))
        messagebox.showinfo(self.tr("done"), self.tr("generated_message", path=config.output))


def main() -> int:
    app = BingoGui()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
