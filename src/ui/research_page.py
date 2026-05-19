import customtkinter as ctk
from src.theme import *
from src.config import PASSPHRASE, MIN_TRAIN, MAX_TRAIN
from src.ui.shared import *
from tkinter import messagebox
from src.core.math_model import *
import numpy as np

class ResearchPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.legit_scores = []
        self.impostor_scores = []
        self._build()

    def _build(self):
        section_title(self, "Research").pack(anchor="w", pady=(0,4))
        lbl(self, f"Collect {MIN_TRAIN}-{MAX_TRAIN} legitimate and impostor samples for FAR/FRR analysis.", color=C_MUTED).pack(anchor="w", pady=(0,10))

        c = card(self)
        c.pack(fill="x", pady=(10, 10))
        lbl(c, "Passphrase", 11, C_MUTED).pack(anchor="w", padx=20, pady=(7, 2))
        lbl(c, f'"{PASSPHRASE}"', 18, "#f0c27f", bold=True).pack(anchor="w", padx=20, pady=(0, 14))

        self.entry = KeyEntry(self, self._submit)
        self.entry.pack(fill="x", pady=(0, 10))

        cfg = card(self)
        cfg.pack(fill="x", pady=(0, 14))

        r1 = ctk.CTkFrame(cfg, fg_color="transparent")
        r1.pack(fill="x", padx=20, pady=(6, 6))
        lbl(r1, "Record as:", color=C_TEXT2).pack(side="left")
        self.mode_var = ctk.StringVar(value="Legitimate")
        ctk.CTkSegmentedButton(r1, values=["Legitimate","Impostor"], variable=self.mode_var, selected_color=C_ACCENT, selected_hover_color=C_ACCENT2,
                               unselected_color=C_PANEL, font=ctk.CTkFont("Segoe UI", 12)).pack(side="left", padx=14)

        r2 = ctk.CTkFrame(cfg, fg_color="transparent")
        r2.pack(fill="x", padx=20, pady=(0,14))
        lbl(r2, "Significance α:", color=C_TEXT2).pack(side="left")
        self.alpha_var = ctk.DoubleVar(value=0.05)
        ctk.CTkSlider(r2, from_=0.01, to=0.20, number_of_steps=19, variable=self.alpha_var, width=140, fg_color=C_BORDER, progress_color=C_ACCENT,
                      command=self._upd_alpha).pack(side="left", padx=10)
        
        self.alpha_lbl = lbl(r2, "α = 0.05", color=C_ACCENT2, bold=True)
        self.alpha_lbl.pack(side="left")

        cnt = ctk.CTkFrame(self, fg_color="transparent")
        cnt.pack(fill="x", pady=(0,12))

        self.legit_badge = ctk.CTkLabel(cnt, text="Legit: 0", width=140, height=42, corner_radius=10, fg_color="#14532d", text_color="#4ade80",
                                        font=ctk.CTkFont("Segoe UI", 14, "bold"))
        self.legit_badge.pack(side="left", padx=(0,10))

        self.imp_badge = ctk.CTkLabel(cnt, text="Impostor: 0", width=150, height=42, corner_radius=10, fg_color="#450a0a", text_color="#f87171",
                                      font=ctk.CTkFont("Segoe UI", 14, "bold"))
        self.imp_badge.pack(side="left")

        self.status = lbl(self, "", color=C_SUCCESS)
        self.status.pack(anchor="w", pady=(0,8))

        br = ctk.CTkFrame(self, fg_color="transparent")
        br.pack(fill="x", pady=(0,10))
        btn(br, "Compute FAR/FRR", self._compute, C_ACCENT).pack(side="left", padx=(0,10))
        btn(br, "Clear", self._clear, C_DANGER, w=100).pack(side="left")

        lc = card(self)
        lc.pack(fill="both", expand=True)
        lbl(lc, "Results", 11, C_MUTED).pack(anchor="w", padx=16, pady=(12,4))
        self.log = ctk.CTkTextbox(lc, fg_color=C_PANEL, corner_radius=8, font=ctk.CTkFont("Cascadia Code", 11), text_color=C_TEXT2, state="disabled")
        self.log.pack(fill="both", expand=True, padx=12, pady=(0,12))

    def _upd_alpha(self, _=None):
        self.alpha_lbl.configure(text=f"α = {self.alpha_var.get():.2f}")

    def _submit(self):
        typed = self.entry.get()
        if typed != PASSPHRASE:
            self.status.configure(text="Wrong passphrase — ignored.", text_color=C_DANGER)
            self.entry.reset()
            return
            
        if self.app.profile is None:
            messagebox.showwarning("No Profile", "Train or load a profile first.")
            self.entry.reset()
            return

        tims = self.entry.timings[:len(PASSPHRASE)]
        n_keys = len(PASSPHRASE)
        expected_features = n_keys + (n_keys - 1)

        if len(tims) < n_keys:
            self.status.configure(text="Keystroke capture incomplete. Type smoothly.", text_color=C_WARN)
            self.entry.reset()
            return

        dwell = np.array([t["dwell"] for t in tims], dtype=float)
        flight = np.array([tims[i]["press_time"] - tims[i-1]["release_time"] for i in range(1, len(tims))], dtype=float)
        flight = np.maximum(flight, 0)
        
        feats = np.concatenate([dwell, flight])

        if len(feats) != expected_features:
            self.status.configure(text=f"Data mismatch (Captured {len(feats)} of {expected_features}). Try again.", text_color=C_WARN)
            self.entry.reset()
            return

        try:
            sc = score_attempt(feats, self.app.profile, clip_outliers=True)
        except Exception as e:
            self.status.configure(text=f"Model error: {str(e)}", text_color=C_DANGER)
            self.entry.reset()
            return

        if self.mode_var.get() == "Legitimate":
            self.legit_scores.append(sc)
            self.legit_badge.configure(text=f"Legit: {len(self.legit_scores)}")
            self.status.configure(text=f"Legit score: {sc:.4f}", text_color=C_SUCCESS)
        else:
            self.impostor_scores.append(sc)
            self.imp_badge.configure(text=f"Impostor: {len(self.impostor_scores)}")
            self.status.configure(text=f"Impostor score: {sc:.4f}", text_color="#f87171")
            
        self.entry.reset()

    def _compute(self):
        n_legit = len(self.legit_scores)
        n_imp = len(self.impostor_scores)

        if n_legit < MIN_TRAIN or n_imp < MIN_TRAIN:
            messagebox.showwarning(
                "Insufficient Data", 
                f"For stable FAR/FRR analysis you need at least {MIN_TRAIN} samples for EACH group.\n\n"
                f"Currently collected:\n"
                f"Legitimate: {n_legit} / {MIN_TRAIN}\n"
                f"Impostor: {n_imp} / {MIN_TRAIN}"
            )
            return
        
        alpha = self.alpha_var.get()
        nf = len(self.app.profile["means"]) if self.app.profile else MIN_TRAIN
        thr = threshold(nf, alpha)

        far = sum(1 for s in self.impostor_scores if s <= thr) / len(self.impostor_scores)
        frr = sum(1 for s in self.legit_scores if s > thr) / len(self.legit_scores)

        thrs, fars, frrs, _ = roc_det(self.legit_scores, self.impostor_scores, 100)
        self.app.roc_data = (self.legit_scores[:], self.impostor_scores[:])
        lines = ["─"*48,
                 f"α = {alpha:.3f} -> Threshold = {thr:.4f}",
                 f"Legit attempts: {len(self.legit_scores)}",
                 f"Impostor attempts: {len(self.impostor_scores)}",
                 f"FAR = {far:.4f} ({far*100:.2f}%)",
                 f"FRR = {frr:.4f} ({frr*100:.2f}%)"]
        
        valid_odd  = [(t,f) for t,f,r in zip(thrs,fars,frrs) if r <= 0.07]
        if valid_odd:
            bt, bf = min(valid_odd, key=lambda x: x[1])
            lines.append(f"\n[Odd] min FAR, FRR<=7%:   thr={bt:.4f}   FAR={bf:.4f}")

        ei = np.argmin(np.abs(fars-frrs))
        lines.append(f"EER = {(fars[ei]+frrs[ei])/2:.4f}")
        
        self.log.configure(state="normal")
        for l in lines:
            self.log.insert("end", l+"\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear(self):
        self.legit_scores.clear()
        self.impostor_scores.clear()
        self.legit_badge.configure(text="Legit: 0")
        self.imp_badge.configure(text="Impostor: 0")
        self.status.configure(text="")
        self.log.configure(state="normal")
        self.log.delete("1.0","end")
        self.log.configure(state="disabled")
        self.app.roc_data = None