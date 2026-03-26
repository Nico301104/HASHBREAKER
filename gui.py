import string
import threading
from datetime import timedelta

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

from constants import CHARSETS, ATTACK_MODES
from engine import CrackEngine
from hash_utils import detect_hash_type


class HashBreakerGUI:
    BG      = "#0d0f14"
    PANEL   = "#13161e"
    ACCENT  = "#00ff9d"
    DANGER  = "#ff3c6e"
    FG      = "#e2e8f0"
    MUTED   = "#64748b"
    BORDER  = "#1e2535"
    MONO    = ("Courier New", 10)
    BODY    = ("Segoe UI", 10)
    TITLE   = ("Courier New", 18, "bold")

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("HashBreaker")
        self.root.configure(bg=self.BG)
        self.root.geometry("900x720")
        self.root.resizable(True, True)
        self._engine = None
        self._thread = None
        self._setup()

    def _setup(self):
        bar = tk.Frame(self.root, bg=self.BG)
        bar.pack(fill="x", padx=20, pady=(16, 4))
        tk.Label(bar, text="⬡ HASHBREAKER", font=self.TITLE, bg=self.BG, fg=self.ACCENT).pack(side="left")
        tk.Label(bar, text="md5 · sha1 · sha256 · sha512",
                 font=("Segoe UI", 9), bg=self.BG, fg=self.MUTED).pack(side="left", padx=14)
        tk.Frame(self.root, height=1, bg=self.ACCENT).pack(fill="x", padx=20, pady=(0, 12))

        body = tk.Frame(self.root, bg=self.BG)
        body.pack(fill="both", expand=True, padx=20)

        left = tk.Frame(body, bg=self.BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._build_hash_panel(left)
        self._build_options_panel(left)

        right = tk.Frame(body, bg=self.BG)
        right.pack(side="left", fill="both", expand=True)
        self._build_stats_panel(right)
        self._build_log_panel(right)

        btns = tk.Frame(self.root, bg=self.BG)
        btns.pack(fill="x", padx=20, pady=12)
        self._btn_start = self._btn(btns, "▶  START CRACKING", self._start, self.ACCENT, self.BG)
        self._btn_start.pack(side="left", padx=(0, 8))
        self._btn_stop = self._btn(btns, "■  STOP", self._stop, self.DANGER, self.BG)
        self._btn_stop.pack(side="left")
        self._btn_stop.configure(state="disabled")
    def _section(self, parent, title):
        f = tk.LabelFrame(parent, text=f"  {title}  ", bg=self.PANEL, fg=self.ACCENT,
                          font=("Courier New", 9, "bold"), bd=1, relief="solid", labelanchor="nw")
        f.pack(fill="x", pady=(0, 10))
        return f

    def _row(self, parent, label):
        row = tk.Frame(parent, bg=self.PANEL)
        row.pack(fill="x", padx=10, pady=3)
        tk.Label(row, text=label, font=self.BODY, bg=self.PANEL, fg=self.MUTED,
                 width=14, anchor="w").pack(side="left")
        return row

    def _entry(self, parent, var=None, width=None):
        kw = dict(font=self.MONO, bg="#0a0c11", fg=self.FG, insertbackground=self.ACCENT, relief="flat", bd=3)
        if var: kw["textvariable"] = var
        if width: kw["width"] = width
        return tk.Entry(parent, **kw)

    def _btn(self, parent, text, cmd, fg, bg):
        return tk.Button(parent, text=text, command=cmd,
                         font=("Courier New", 10, "bold"), bg=bg, fg=fg,
                         activebackground=fg, activeforeground=bg,
                         relief="solid", bd=1, highlightbackground=fg,
                         padx=16, pady=7, cursor="hand2")

    def _build_hash_panel(self, parent):
        sec = self._section(parent, "TARGET HASH")
        self._hash_var = tk.StringVar()
        tk.Entry(sec, textvariable=self._hash_var, font=self.MONO,
                 bg="#0a0c11", fg=self.ACCENT, insertbackground=self.ACCENT,
                 relief="flat", bd=4).pack(fill="x", padx=10, pady=6)
        row = tk.Frame(sec, bg=self.PANEL)
        row.pack(fill="x", padx=10, pady=(0, 8))
        tk.Label(row, text="Hash type:", font=self.BODY, bg=self.PANEL, fg=self.MUTED).pack(side="left")
        self._hash_type = ttk.Combobox(row, values=["auto-detect", "md5", "sha1", "sha256", "sha512"],
                                       state="readonly", width=14, font=self.BODY)
        self._hash_type.set("auto-detect")
        self._hash_type.pack(side="left", padx=6)

    def _build_options_panel(self, parent):
        sec = self._section(parent, "ATTACK OPTIONS")

        row = self._row(sec, "Mode:")
        self._mode = ttk.Combobox(row, values=ATTACK_MODES, state="readonly", width=14, font=self.BODY)
        self._mode.set("dictionary")
        self._mode.pack(side="left")
        self._mode.bind("<<ComboboxSelected>>", self._on_mode_change)

        wl_row = self._row(sec, "Wordlist:")
        self._wl_var = tk.StringVar(value="wordlist.txt")
        self._wl_entry = self._entry(wl_row, var=self._wl_var, width=22)
        self._wl_entry.pack(side="left", padx=(0, 4))
        tk.Button(wl_row, text="Browse", command=self._browse,
                  font=("Segoe UI", 9), bg=self.BORDER, fg=self.FG,
                  relief="flat", bd=0, padx=6, cursor="hand2").pack(side="left")

        cs_row = self._row(sec, "Charset:")
        self._charset = ttk.Combobox(cs_row, values=list(CHARSETS.keys()) + ["custom"],
                                     state="readonly", width=14, font=self.BODY)
        self._charset.set("alphanumeric")
        self._charset.pack(side="left")

        cc_row = self._row(sec, "Custom chars:")
        self._custom = self._entry(cc_row, width=22)
        self._custom.pack(side="left")
        self._custom.insert(0, "abc123!@#")

        lr_row = self._row(sec, "Length range:")
        self._min_len = tk.Spinbox(lr_row, from_=1, to=12, width=4, font=self.BODY,
                                   bg="#0a0c11", fg=self.ACCENT, relief="flat", bd=3)
        self._min_len.pack(side="left")
        self._min_len.delete(0, "end"); self._min_len.insert(0, "1")
        tk.Label(lr_row, text=" → ", font=self.BODY, bg=self.PANEL, fg=self.MUTED).pack(side="left")
        self._max_len = tk.Spinbox(lr_row, from_=1, to=12, width=4, font=self.BODY,
                                   bg="#0a0c11", fg=self.ACCENT, relief="flat", bd=3)
        self._max_len.pack(side="left")
        self._max_len.delete(0, "end"); self._max_len.insert(0, "6")

        th_row = self._row(sec, "Threads:")
        self._threads = tk.Spinbox(th_row, from_=1, to=32, width=4, font=self.BODY,
                                   bg="#0a0c11", fg=self.ACCENT, relief="flat", bd=3)
        self._threads.pack(side="left")
        self._threads.delete(0, "end"); self._threads.insert(0, "4")

    def _build_stats_panel(self, parent):
        sec = self._section(parent, "LIVE STATISTICS")
        grid = tk.Frame(sec, bg=self.PANEL)
        grid.pack(fill="x", padx=10, pady=8)

        def stat_box(r, c, title):
            f = tk.Frame(grid, bg=self.BG)
            f.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            grid.columnconfigure(c, weight=1)
            tk.Label(f, text=title, font=("Segoe UI", 8), bg=self.BG, fg=self.MUTED).pack(pady=(6, 0))
            v = tk.Label(f, text="—", font=("Courier New", 14, "bold"), bg=self.BG, fg=self.ACCENT)
            v.pack(pady=(0, 6))
            return v

        self._lbl_attempts = stat_box(0, 0, "ATTEMPTS")
        self._lbl_speed    = stat_box(0, 1, "H/S")
        self._lbl_eta      = stat_box(0, 2, "ETA")
        self._lbl_elapsed  = stat_box(1, 0, "ELAPSED")
        self._lbl_pct      = stat_box(1, 1, "PROGRESS %")
        self._lbl_mode     = stat_box(1, 2, "MODE")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Crack.Horizontal.TProgressbar",
                        troughcolor=self.BG, background=self.ACCENT, bordercolor=self.BORDER)
        self._progress = ttk.Progressbar(sec, style="Crack.Horizontal.TProgressbar",
                                         orient="horizontal", mode="determinate")
        self._progress.pack(fill="x", padx=10, pady=(0, 6))

        res = tk.Frame(sec, bg=self.PANEL)
        res.pack(fill="x", padx=10, pady=(0, 8))
        tk.Label(res, text="RESULT:", font=("Courier New", 9, "bold"), bg=self.PANEL, fg=self.MUTED).pack(side="left")
        self._lbl_result = tk.Label(res, text="not cracked yet",
                                    font=("Courier New", 14, "bold"), bg=self.PANEL, fg=self.MUTED)
        self._lbl_result.pack(side="left", padx=8)

    def _build_log_panel(self, parent):
        sec = self._section(parent, "ACTIVITY LOG")
        self._log_widget = scrolledtext.ScrolledText(sec, height=12, font=self.MONO,
                                                     bg="#070910", fg="#94a3b8",
                                                     insertbackground=self.ACCENT,
                                                     relief="flat", bd=0)
        self._log_widget.pack(fill="both", expand=True, padx=6, pady=6)
        self._log_widget.tag_config("found",  foreground=self.ACCENT, font=("Courier New", 10, "bold"))
        self._log_widget.tag_config("error",  foreground=self.DANGER)
        self._log_widget.tag_config("info",   foreground="#64748b")
        self._log_widget.tag_config("header", foreground="#e2e8f0", font=("Courier New", 10, "bold"))

    def _log(self, text, tag="info"):
        self._log_widget.insert("end", text + "\n", tag)
        self._log_widget.see("end")

    def _browse(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self._wl_var.set(path)

    def _on_mode_change(self, _=None):
        state = "normal" if self._mode.get() in ("dictionary", "combo") else "disabled"
        self._wl_entry.configure(state=state)

    def _resolve_charset(self):
        name = self._charset.get()
        if name == "custom":
            return self._custom.get() or string.ascii_lowercase
        return CHARSETS.get(name, string.ascii_letters + string.digits)

    def _resolve_hash_type(self, target):
        ht = self._hash_type.get()
        if ht == "auto-detect":
            ht = detect_hash_type(target)
            if ht == "unknown":
                messagebox.showerror("Eroare", "Nu pot detecta tipul hash-ului. Selectează manual.")
                return None
            self._log(f"[auto-detect] {ht.upper()}", "info")
        return ht

    def _start(self):
        target = self._hash_var.get().strip()
        if not target:
            messagebox.showerror("Eroare", "Introduceți un hash.")
            return

        ht = self._resolve_hash_type(target)
        if not ht:
            return

        mode    = self._mode.get()
        threads = int(self._threads.get())
        min_l   = int(self._min_len.get())
        max_l   = int(self._max_len.get())
        charset = self._resolve_charset()
        wordlist = self._wl_var.get()

        self._progress["value"] = 0
        self._lbl_result.configure(text="cracking…", fg=self.MUTED)
        self._lbl_mode.configure(text=mode)
        self._log_widget.delete("1.0", "end")
        self._log(f"Target : {target}", "header")
        self._log(f"Tip    : {ht.upper()}", "header")
        self._log(f"Mod    : {mode} | threads={threads}", "header")
        self._log("─" * 50, "info")

        self._btn_start.configure(state="disabled")
        self._btn_stop.configure(state="normal")

        self._engine = CrackEngine(target, ht, callback=self._on_event)

        def run():
            if mode == "dictionary":
                self._engine.dictionary_attack(wordlist, threads)
            elif mode == "brute-force":
                self._engine.brute_force(charset, min_l, max_l, threads)
            else:
                self._engine.combo_attack(wordlist, charset, 2, threads)

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def _stop(self):
        if self._engine:
            self._engine.stop()
        self._btn_start.configure(state="normal")
        self._btn_stop.configure(state="disabled")
        self._log("── Oprit ──", "error")

    def _on_event(self, event, data):
        self.root.after(0, self._handle, event, data)

    def _handle(self, event, data):
        if event == "stats":
            self._lbl_attempts.configure(text=f"{data['attempts']:,}")
            self._lbl_speed.configure(text=f"{data['speed']:,.0f}")
            self._lbl_eta.configure(text=data["eta"])
            self._lbl_elapsed.configure(text=str(timedelta(seconds=int(data["elapsed"]))))
            self._lbl_pct.configure(text=f"{data['pct']:.2f}%")
            self._progress["value"] = min(data["pct"], 100)

        elif event == "found":
            self._lbl_result.configure(text=f"✓  {data}", fg=self.ACCENT)
            self._log(f"\n🔓 PAROLĂ GĂSITĂ: {data}", "found")
            self._btn_start.configure(state="normal")
            self._btn_stop.configure(state="disabled")

        elif event == "done":
            if not data:
                self._lbl_result.configure(text="✗  negăsit", fg=self.DANGER)
                self._log("✗  Hash-ul nu a putut fi spart cu setările curente.", "error")
            self._btn_start.configure(state="normal")
            self._btn_stop.configure(state="disabled")

        elif event == "error":
            self._log(f"EROARE: {data}", "error")
            self._btn_start.configure(state="normal")
            self._btn_stop.configure(state="disabled")

        elif event == "start":
            self._log(f"Mod: {data['mode']} | candidați: {data['total']:,}", "info")
