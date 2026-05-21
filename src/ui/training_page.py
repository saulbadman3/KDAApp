import customtkinter as ctk
from src.ui.shared import *
from src.core.math_model import *
from src.core.profile_io import *
import src.core.user_store as store
from tkinter import filedialog, messagebox
from src.config import PROFILE_FILE, MIN_TRAIN, MAX_TRAIN
import os

class TrainingPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.attempts = []
        self._target_password = None
        self._build()

    def _build(self):
        section_title(self, "Biometric Training Mode").pack(anchor="w", pady=(0, 4))
        lbl(self, f"Type your password {MIN_TRAIN}-{MAX_TRAIN} times to build a profile.", color=C_MUTED).pack(anchor="w", pady=(0, 10))

        uc = card(self)
        uc.pack(fill="x", pady=(2, 8))
        
        lbl(uc, "Account & Training Profile Setup", 12, C_ACCENT, bold=True).pack(anchor="w", padx=20, pady=(10, 4))

        lbl(uc, "Username", 11, C_MUTED).pack(anchor="w", padx=20, pady=(4, 1))
        self.username_entry = ctk.CTkEntry(uc, height=46, corner_radius=10, border_color=C_BORDER, fg_color=C_PANEL, font=ctk.CTkFont("Segoe UI", 16),
                        placeholder_text="Type username to fetch password...", placeholder_text_color=C_MUTED)
        self.username_entry.pack(fill="x", padx=20, pady=(0, 6))

        lbl(uc, "Type Password Here (Biometric Capture)", 11, C_MUTED).pack(anchor="w", padx=20, pady=(4, 1))
        self.entry = KeyEntry(uc, self._submit)
        self.entry.configure(show="•", placeholder_text="Type password here...")
        self.entry.pack(fill="x", padx=20, pady=(0, 14))

        pc = card(self)
        pc.pack(fill="x", pady=(0, 14))
        row = ctk.CTkFrame(pc, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(6, 6))
        self.cnt_lbl = lbl(row, f"0 / {MIN_TRAIN} attempts", 13, bold=True)
        self.cnt_lbl.pack(side="left")
        self.pct_lbl = lbl(row, "0%", 13, C_ACCENT2, bold=True)
        self.pct_lbl.pack(side="right")
        self.prog = ctk.CTkProgressBar(pc, height=8, corner_radius=4, fg_color=C_BORDER, progress_color=C_ACCENT)
        self.prog.set(0)
        self.prog.pack(fill="x", padx=20, pady=(0, 14))

        opt = ctk.CTkFrame(self, fg_color="transparent")
        opt.pack(fill="x", pady=(0, 14))
        self.clip = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(opt, text="Remove outliers", variable=self.clip, font=ctk.CTkFont("Segoe UI", 12), fg_color=C_ACCENT, hover_color=C_ACCENT2,
                        text_color=C_TEXT2).pack(side="left")

        br = ctk.CTkFrame(self, fg_color="transparent")
        br.pack(fill="x", pady=(0, 10))
        btn(br, "Save Profile", self._save, C_ACCENT).pack(side="left", padx=(0, 10))
        btn(br, "Clear Form", self._clear, C_DANGER, w=110).pack(side="left")

        self.status = lbl(self, "", color=C_SUCCESS)
        self.status.pack(anchor="w", pady=(0, 8))

        lc = card(self)
        lc.pack(fill="both", expand=True)
        lbl(lc, "Training session log", 11, C_MUTED).pack(anchor="w", padx=16, pady=(4, 4))
        self.log = ctk.CTkTextbox(lc, fg_color=C_PANEL, corner_radius=8, font=ctk.CTkFont("Cascadia Code", 11), text_color=C_TEXT2, state="disabled")
        self.log.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _submit(self):
        username = self.username_entry.get().strip()
        typed_password = self.entry.get()

        if not username:
            self.status.configure(text="Please enter username first.", text_color=C_WARN)
            self.entry.reset()
            return

        if not self._target_password:
            if not store.verify(username, typed_password):
                self.status.configure(text="Authentication failed: Invalid username or password.", text_color=C_DANGER)
                self.entry.reset()
                return
            self._target_password = typed_password
            self.username_entry.configure(state="disabled")
            self._log(f"--- Session started for user '{username}' ---")

        if typed_password != self._target_password:
            self.status.configure(text="Wrong password - session pattern mismatch.", text_color=C_DANGER)
            self.entry.reset()
            return

        tims = self.entry.timings[:len(self._target_password)]
        if len(tims) < len(self._target_password):
            self.status.configure(text="Keystroke capture incomplete. Type smoothly.", text_color=C_WARN)
            self.entry.reset()
            return

        n_keys = len(self._target_password)
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

        self._log(f"[{n:02d}] Recorded: mean_dwell = {np.mean(dwell):.1f} ms; mean_flight = {np.mean(flight):.1f} ms")
        self.status.configure(text="Ready to save profile" if n >= MIN_TRAIN else f"{n} attempt recorded", text_color=C_SUCCESS if n >= MIN_TRAIN else C_TEXT2)
        self.entry.reset()

    def _save(self):
        username = self.username_entry.get().strip()
        if len(self.attempts) < MIN_TRAIN:
            messagebox.showwarning("Not enough data", f"Need at least {MIN_TRAIN} attempts (have {len(self.attempts)}).")
            return
            
        prof = build_profile(self.attempts)

        mask = prof["feature_mask"]
        active_features = int(sum(mask))
        total_features = len(mask)
        
        self._log(f"--- FEATURE SELECTION REPORT ---")
        self._log(f"Active stable features (CV < 0.3): {active_features} of {total_features}")
        self._log(f"Feature Mask: {mask}")
        self._log(f"--------------------------------")
        
        suggested_filename = f"{username}.kda" if username else PROFILE_FILE
        path = filedialog.asksaveasfilename(defaultextension=".kda",
            filetypes=[("KDA Profile","*.kda")], initialfile=suggested_filename)
            
        if path:
            save_profile(prof, path)
            self.app.profile = prof
            if username:
                store.set_profile_path(username, path)
            self._log(f"Profile saved -> {os.path.basename(path)}")
            messagebox.showinfo("Saved", f"Profile saved and bound to '{username}':\n{path}")

    def _clear(self):
        self.attempts.clear()
        self._target_password = None
        self.username_entry.configure(state="normal")
        self.username_entry.delete(0, "end")
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