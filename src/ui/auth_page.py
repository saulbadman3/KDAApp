# src.ui.auth_page.py
import customtkinter as ctk
from src.ui.shared import *
from src.config import PASSPHRASE
from src.core.math_model import *
from tkinter import messagebox, filedialog
from src.core.profile_io import load_profile

class AuthPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        section_title(self, "Authentication").pack(anchor="w", pady=(0,4))
        lbl(self, "Type the passphrase and press Enter.", color=C_MUTED).pack(anchor="w", pady=(0,10))

        c = card(self)
        c.pack(fill="x", pady=(10,10))
        lbl(c, "Passphrase", 11, C_MUTED).pack(anchor="w", padx=20, pady=(7,2))
        lbl(c, f'"{PASSPHRASE}"', 18, "#f0c27f", bold=True).pack(anchor="w", padx=20, pady=(0,14))

        self.entry = KeyEntry(self, self._submit)
        self.entry.pack(fill="x", pady=(0,10))

        cfg = card(self)
        cfg.pack(fill="x", pady=(0,14))
        ar = ctk.CTkFrame(cfg, fg_color="transparent")
        ar.pack(fill="x", padx=20, pady=(6,6))
        lbl(ar, "Significance α:", color=C_TEXT2).pack(side="left")
        self.alpha_var = ctk.DoubleVar(value=0.05)
        ctk.CTkSlider(ar, from_=0.01, to=0.20, number_of_steps=19, variable=self.alpha_var, width=160, fg_color=C_BORDER, progress_color=C_ACCENT, 
                      command=self._upd_alpha).pack(side="left", padx=12)
        self.alpha_lbl = lbl(ar, "α = 0.05", color=C_ACCENT2, bold=True)
        self.alpha_lbl.pack(side="left")
        self.clip = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(cfg, text="Remove outliers before comparing", variable=self.clip, font=ctk.CTkFont("Segoe UI", 12), fg_color=C_ACCENT, hover_color=C_ACCENT2,
                        text_color=C_TEXT2).pack(anchor="w", padx=20, pady=(0,14))

        self.badge = StatusBadge(self)
        self.badge.pack(fill="x", pady=(0,8))

        self.detail = lbl(self, "", 11, C_MUTED)
        self.detail.pack(anchor="w")

        btn(self, "Load Profile", self._load, "#8b5cf6").pack(anchor="w", pady=0)

    def _upd_alpha(self, _=None):
        self.alpha_lbl.configure(text=f"α = {self.alpha_var.get():.2f}")

    def _submit(self):
        typed = self.entry.get()

        if typed != PASSPHRASE:
            self.badge.wrong()
            self.detail.configure(text="")
            self.entry.reset()
            return

        if self.app.profile is None:
            messagebox.showwarning("No Profile", "Load or train a profile first.")
            self.entry.reset()
            return

        tims = self.entry.timings[:len(PASSPHRASE)]
        n_keys = len(PASSPHRASE)
        expected_features = n_keys + (n_keys - 1)

        if len(tims) < n_keys:
            self.badge.idle()
            self.detail.configure(text="Keystroke capture incomplete. Type smoothly.", text_color=C_WARN)
            self.entry.reset()
            return

        dwell = np.array([t["dwell"] for t in tims], dtype=float)
        flight = np.array([tims[i]["press_time"] - tims[i-1]["release_time"] for i in range(1, len(tims))], dtype=float)
        flight = np.maximum(flight, 0)
        feats = np.concatenate([dwell, flight])

        if len(feats) != expected_features:
            self.badge.idle()
            self.detail.configure(text=f"Data mismatch (Captured {len(feats)} of {expected_features}). Try again.")
            self.entry.reset()
            return

        try:
            score = score_attempt(feats, self.app.profile, clip_outliers=self.clip.get())
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            self.entry.reset()
            return

        alpha = float(self.alpha_var.get())
        n_feat = len(self.app.profile["means"])

        tau = threshold(n_feat, alpha)

        accepted = score <= tau

        if accepted:
            self.badge.granted()
        else:
            self.badge.denied()

        self.detail.configure(
            text=(
                f"Score (D): {score:.4f} | "
                f"Threshold: {tau:.4f} | "
                f"α={alpha:.2f}"
            )
        )

        self.entry.reset()

    def _load(self):
        path = filedialog.askopenfilename(filetypes=[("KDA Profile" ,"*.kda")])
        if path:
            try:
                self.app.profile = load_profile(path)
                messagebox.showinfo("Loaded", f"Profile loaded:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))