import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


def get_files_by_extension(folder, from_ext):
    """Return list of files matching the given extension in folder."""
    from_ext = from_ext.lstrip(".").lower()
    matched = []
    for filename in os.listdir(folder):
        name, ext = os.path.splitext(filename)
        if ext.lstrip(".").lower() == from_ext:
            matched.append(filename)
    return matched


def convert_extensions(folder, from_ext, to_ext, rename_only=True):
    """
    Rename (or copy) files from one extension to another.
    rename_only=True  → renames in-place (original is gone)
    rename_only=False → copies, keeping the original
    Returns (success_list, error_list)
    """
    from_ext = from_ext.lstrip(".")
    to_ext   = to_ext.lstrip(".")
    files    = get_files_by_extension(folder, from_ext)

    success, errors = [], []
    for filename in files:
        src  = os.path.join(folder, filename)
        name = os.path.splitext(filename)[0]
        dst  = os.path.join(folder, f"{name}.{to_ext}")

        try:
            if rename_only:
                os.rename(src, dst)
            else:
                shutil.copy2(src, dst)
            success.append(f"{filename}  →  {name}.{to_ext}")
        except Exception as e:
            errors.append(f"{filename}: {e}")

    return success, errors


# ──────────────────────────────────────────────
#  GUI
# ──────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Extension Converter")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")
        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        PAD = 14
        BG  = "#1e1e2e"
        CARD = "#2a2a3e"
        ACC  = "#7c6af7"
        FG   = "#cdd6f4"
        MUTED = "#585b70"

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame",       background=BG)
        style.configure("Card.TFrame",  background=CARD)
        style.configure("TLabel",       background=BG, foreground=FG,
                         font=("Segoe UI", 10))
        style.configure("Head.TLabel",  background=BG, foreground=FG,
                         font=("Segoe UI", 16, "bold"))
        style.configure("Sub.TLabel",   background=BG, foreground=MUTED,
                         font=("Segoe UI", 9))
        style.configure("Card.TLabel",  background=CARD, foreground=FG,
                         font=("Segoe UI", 10))
        style.configure("TEntry",       fieldbackground=CARD, foreground=FG,
                         insertcolor=FG, bordercolor=MUTED, font=("Segoe UI", 10))
        style.configure("Accent.TButton",
                         background=ACC, foreground="#ffffff",
                         font=("Segoe UI", 10, "bold"),
                         borderwidth=0, focusthickness=0)
        style.map("Accent.TButton",
                  background=[("active", "#6a59e0"), ("pressed", "#5848c0")])
        style.configure("Ghost.TButton",
                         background=CARD, foreground=FG,
                         font=("Segoe UI", 10),
                         borderwidth=0)
        style.map("Ghost.TButton",
                  background=[("active", "#35354f")])
        style.configure("TCheckbutton",
                         background=BG, foreground=FG,
                         font=("Segoe UI", 10))

        root = ttk.Frame(self, padding=PAD)
        root.pack(fill="both", expand=True)

        # Header
        ttk.Label(root, text="Extension Converter", style="Head.TLabel").pack(anchor="w")
        ttk.Label(root, text="Batch-rename files in a folder to a new extension",
                  style="Sub.TLabel").pack(anchor="w", pady=(2, PAD))

        # Folder row
        folder_frame = ttk.Frame(root)
        folder_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(folder_frame, text="Folder").pack(anchor="w")
        row = ttk.Frame(folder_frame)
        row.pack(fill="x", pady=2)
        self.folder_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.folder_var, width=46).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse…", style="Ghost.TButton",
                   command=self._browse).pack(side="left", padx=(6, 0))

        # Extension row
        ext_frame = ttk.Frame(root)
        ext_frame.pack(fill="x", pady=(0, 8))
        cols = ttk.Frame(ext_frame)
        cols.pack(fill="x")

        left = ttk.Frame(cols)
        left.pack(side="left", fill="x", expand=True)
        ttk.Label(left, text="From extension").pack(anchor="w")
        self.from_var = tk.StringVar(value="dwg")
        ttk.Entry(left, textvariable=self.from_var, width=18).pack(anchor="w", pady=2)

        arrow = ttk.Label(cols, text="→", font=("Segoe UI", 14), background="#1e1e2e",
                          foreground=ACC)
        arrow.pack(side="left", padx=12, pady=(16, 0))

        right = ttk.Frame(cols)
        right.pack(side="left", fill="x", expand=True)
        ttk.Label(right, text="To extension").pack(anchor="w")
        self.to_var = tk.StringVar(value="txt")
        ttk.Entry(right, textvariable=self.to_var, width=18).pack(anchor="w", pady=2)

        # Options
        self.copy_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(root, text="Keep originals (copy instead of rename)",
                         variable=self.copy_var).pack(anchor="w", pady=(4, 12))

        # Preview & Convert buttons
        btn_row = ttk.Frame(root)
        btn_row.pack(fill="x", pady=(0, 10))
        ttk.Button(btn_row, text="Preview", style="Ghost.TButton",
                   command=self._preview).pack(side="left")
        ttk.Button(btn_row, text="Convert", style="Accent.TButton",
                   command=self._convert).pack(side="left", padx=(8, 0))

        # Log box
        ttk.Label(root, text="Log").pack(anchor="w")
        log_frame = ttk.Frame(root, style="Card.TFrame")
        log_frame.pack(fill="both", expand=True, pady=(2, 0))

        self.log = tk.Text(log_frame, height=12, bg=CARD, fg=FG,
                           font=("Consolas", 9), relief="flat",
                           bd=6, state="disabled", wrap="none")
        self.log.pack(fill="both", expand=True)

        # Text tags
        self.log.tag_configure("ok",    foreground="#a6e3a1")
        self.log.tag_configure("err",   foreground="#f38ba8")
        self.log.tag_configure("info",  foreground="#89dceb")
        self.log.tag_configure("warn",  foreground="#f9e2af")

    # ---------- helpers ----------
    def _browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def _log(self, text, tag="info"):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _validate(self):
        folder   = self.folder_var.get().strip()
        from_ext = self.from_var.get().strip()
        to_ext   = self.to_var.get().strip()
        if not folder:
            messagebox.showerror("Error", "Please select a folder."); return None
        if not os.path.isdir(folder):
            messagebox.showerror("Error", "Folder does not exist."); return None
        if not from_ext:
            messagebox.showerror("Error", "Enter the source extension."); return None
        if not to_ext:
            messagebox.showerror("Error", "Enter the target extension."); return None
        return folder, from_ext, to_ext

    # ---------- actions ----------
    def _preview(self):
        result = self._validate()
        if not result: return
        folder, from_ext, to_ext = result
        self._clear_log()
        files = get_files_by_extension(folder, from_ext)
        if not files:
            self._log(f"No .{from_ext} files found in:\n  {folder}", "warn")
            return
        self._log(f"Found {len(files)} file(s) to rename in:\n  {folder}\n", "info")
        for f in files:
            name = os.path.splitext(f)[0]
            self._log(f"  {f}  →  {name}.{to_ext}", "ok")

    def _convert(self):
        result = self._validate()
        if not result: return
        folder, from_ext, to_ext = result
        files = get_files_by_extension(folder, from_ext)
        if not files:
            self._clear_log()
            self._log(f"No .{from_ext} files found in:\n  {folder}", "warn")
            return

        action = "copy" if self.copy_var.get() else "rename"
        msg = (f"About to {action} {len(files)} .{from_ext} file(s) to .{to_ext}\n"
               f"in: {folder}\n\nProceed?")
        if not messagebox.askyesno("Confirm", msg):
            return

        self._clear_log()
        success, errors = convert_extensions(
            folder, from_ext, to_ext, rename_only=not self.copy_var.get()
        )

        for line in success:
            self._log("  ✓  " + line, "ok")
        for line in errors:
            self._log("  ✗  " + line, "err")

        self._log(
            f"\nDone: {len(success)} succeeded, {len(errors)} failed.",
            "info" if not errors else "warn"
        )


# ──────────────────────────────────────────────
#  CLI fallback  (python file_converter.py <folder> <from> <to>)
# ──────────────────────────────────────────────
def cli():
    if len(sys.argv) != 4:
        print("Usage: python file_converter.py <folder> <from_ext> <to_ext>")
        print("Example: python file_converter.py C:/MyFiles dwg txt")
        sys.exit(1)

    folder, from_ext, to_ext = sys.argv[1], sys.argv[2], sys.argv[3]
    if not os.path.isdir(folder):
        print(f"Error: '{folder}' is not a valid directory."); sys.exit(1)

    files = get_files_by_extension(folder, from_ext)
    if not files:
        print(f"No .{from_ext} files found in {folder}"); sys.exit(0)

    print(f"Renaming {len(files)} file(s): .{from_ext} → .{to_ext}")
    success, errors = convert_extensions(folder, from_ext, to_ext)
    for line in success: print("  ✓", line)
    for line in errors:  print("  ✗", line)
    print(f"\nDone: {len(success)} succeeded, {len(errors)} failed.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli()
    else:
        app = App()
        app.mainloop()
