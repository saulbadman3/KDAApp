#src.ui.training_page.py
import customtkinter as ctk
from src.ui.shared import *
from src.core.math_model import *
from src.core.profile_io import *
from tkinter import filedialog, messagebox
from src.config import PASSPHRASE, PROFILE_FILE, MIN_TRAIN, MAX_TRAIN
import os

class TrainingPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.attempts = []
        self._build()

    def _build(self):
        section_title(self, "Training Mode").pack(anchor="w", pady=(0,4))
        lbl(self, f'Type "{PASSPHRASE}" {MIN_TRAIN}-{MAX_TRAIN} times, then save.', color=C_MUTED).pack(anchor="w", pady=(0,10))

        c = card(self)
        c.pack(fill="x", pady=(10, 10))
        lbl(c, "Passphrase", 11, C_MUTED).pack(anchor="w", padx=20, pady=(7,2))
        lbl(c, f'"{PASSPHRASE}"', 18, "#f0c27f", bold=True).pack(anchor="w", padx=20, pady=(0,14))

        self.entry = KeyEntry(self, self._submit)
        self.entry.pack(fill="x", pady=(0,10))

        pc = card(self)
        pc.pack(fill="x", pady=(0,14))
        row = ctk.CTkFrame(pc, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(6,6))
        self.cnt_lbl = lbl(row, f"0 / {MIN_TRAIN} attempts", 13, bold=True)
        self.cnt_lbl.pack(side="left")
        self.pct_lbl = lbl(row, "0%", 13, C_ACCENT2, bold=True)
        self.pct_lbl.pack(side="right")
        self.prog = ctk.CTkProgressBar(pc, height=8, corner_radius=4, fg_color=C_BORDER, progress_color=C_ACCENT)
        self.prog.set(0)
        self.prog.pack(fill="x", padx=20, pady=(0,14))

        opt = ctk.CTkFrame(self, fg_color="transparent")
        opt.pack(fill="x", pady=(0,14))
        self.clip = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(opt, text="Remove outliers", variable=self.clip, font=ctk.CTkFont("Segoe UI", 12), fg_color=C_ACCENT, hover_color=C_ACCENT2,
                        text_color=C_TEXT2).pack(side="left")

        br = ctk.CTkFrame(self, fg_color="transparent")
        br.pack(fill="x", pady=(0,10))
        btn(br, "Save Profile", self._save, C_ACCENT).pack(side="left", padx=(0,10))
        btn(br, "Clear", self._clear, C_DANGER, w=110).pack(side="left")

        self.status = lbl(self, "", color=C_SUCCESS)
        self.status.pack(anchor="w", pady=(0,8))

        lc = card(self)
        lc.pack(fill="both", expand=True)
        lbl(lc, "Attempt log", 11, C_MUTED).pack(anchor="w", padx=16, pady=(4,4))
        self.log = ctk.CTkTextbox(lc, fg_color=C_PANEL, corner_radius=8, font=ctk.CTkFont("Cascadia Code", 11), text_color=C_TEXT2, state="disabled")
        self.log.pack(fill="both", expand=True, padx=12, pady=(0,12))

    def _submit(self):
        typed = self.entry.get()

        if typed != PASSPHRASE:
            self.status.configure(text="Wrong passphrase - not recorded.", text_color=C_DANGER)
            self.entry.reset()
            return

        tims = self.entry.timings[:len(PASSPHRASE)]

        if len(tims) < len(PASSPHRASE) - 1:
            self.status.configure(text="Too few keystrokes, try again.", text_color=C_WARN)
            self.entry.reset()
            return

        n_keys = len(PASSPHRASE)

        dwell = np.array([t["dwell"] for t in tims], dtype=float)
        flight = np.array([tims[i]["press_time"] - tims[i-1]["release_time"] for i in range(1, len(tims))], dtype=float)
        flight = np.maximum(flight, 0)

        feats = np.concatenate([dwell, flight])

        expected = n_keys + (n_keys - 1)
        if len(feats) != expected:
            self.status.configure(text=f"Feature mismatch ({len(feats)} != {expected})", text_color=C_WARN)
            self.entry.reset()
            return

        self.attempts.append(feats)

        n = len(self.attempts)
        pct = min(n / MIN_TRAIN, 1.0)

        self.prog.set(pct)
        self.cnt_lbl.configure(text=f"{n} / {MIN_TRAIN} attempts")
        self.pct_lbl.configure(text=f"{int(pct*100)}%")

        self._log(f"[{n:02d}] dwell = {len(dwell)}; flight = {len(flight)}; mean_dwell = {np.mean(dwell):.1f} ms; mean_flight = {np.mean(flight):.1f} ms")

        self.status.configure(text="Ready to save" if n >= MIN_TRAIN else f"{n} attempt recorded", text_color=C_SUCCESS if n >= MIN_TRAIN else C_TEXT2)

        self.entry.reset()

    def _save(self):
        if len(self.attempts) < MIN_TRAIN:
            messagebox.showwarning("Not enough data", f"Need at least {MIN_TRAIN} attempts (have {len(self.attempts)}).")
            return
        prof = build_profile(self.attempts)
        print(prof)
        path = filedialog.asksaveasfilename(defaultextension=".kda",
            filetypes=[("KDA Profile","*.kda")], initialfile=PROFILE_FILE)
        if path:
            save_profile(prof, path)
            self.app.profile = prof
            self._log(f"Profile saved -> {os.path.basename(path)}")
            messagebox.showinfo("Saved", f"Profile saved:\n{path}")

    def _clear(self):
        self.attempts.clear()
        self.prog.set(0)
        self.cnt_lbl.configure(text=f"0 / {MIN_TRAIN} attempts")
        self.pct_lbl.configure(text="0%")
        self.status.configure(text="")
        self.entry.reset()

    def _log(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg+"\n")
        self.log.see("end")
        self.log.configure(state="disabled")