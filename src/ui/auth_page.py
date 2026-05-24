# src/ui/auth_page.py
import customtkinter as ctk
from src.ui.shared import *
import src.core.user_store as store
from src.core.profile_io import load_profile
from src.core.math_model import *
from tkinter import messagebox, filedialog
from datetime import datetime
import numpy as np
import os

class AuthPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        section_title(self, "Biometric Authentication").pack(anchor="w", pady=(0, 4))

        uc = card(self)
        uc.pack(fill="x", pady=(2, 8))
        
        lbl(uc, "Account & Typing Biometrics", 12, C_ACCENT, bold=True).pack(anchor="w", padx=20, pady=(10, 4))

        lbl(uc, "Username", 11, C_MUTED).pack(anchor="w", padx=20, pady=(4, 1))
        self.username_entry = ctk.CTkEntry(uc, height=46, corner_radius=10, border_color=C_BORDER, fg_color=C_PANEL, font=ctk.CTkFont("Segoe UI", 16),
                                            placeholder_text="Type username here...", placeholder_text_color=C_MUTED)
        self.username_entry.pack(fill="x", padx=20, pady=(0, 6))

        lbl(uc, "Password", 11, C_MUTED).pack(anchor="w", padx=20, pady=(4, 1))
        
        # KeyEntry customized to capture raw keypress and release timestamps
        self.password_entry = KeyEntry(uc, self._handle_login)
        self.password_entry.configure(show="•", placeholder_text="Type password here...", placeholder_text_color=C_MUTED)
        self.password_entry.pack(fill="x", padx=20, pady=(0, 14))

        br = ctk.CTkFrame(uc, fg_color="transparent")
        br.pack(fill="x", padx=20, pady=(0, 14))
        
        btn(br, "Login", self._handle_login, C_ACCENT).pack(side="left", padx=(0, 4), expand=True, fill="x")
        btn(br, "Register", self._handle_register, C_SUCCESS).pack(side="left", padx=(0, 4), expand=True, fill="x")
        btn(br, "Load Profile", self._handle_load_profile, "#7f5af0").pack(side="left", padx=(0, 4), expand=True, fill="x")
        btn(br, "Clear", self._clear, C_DANGER).pack(side="left", expand=True, fill="x")

        self.user_lbl = lbl(self, "Status: Not authenticated", 12, C_MUTED, bold=True)
        self.user_lbl.pack(anchor="w", pady=(2, 6))

        cfg = card(self)
        cfg.pack(fill="x", pady=(2, 8))

        ar = ctk.CTkFrame(cfg, fg_color="transparent")
        ar.pack(fill="x", padx=20, pady=(6, 6))
        lbl(ar, "Significance α:", color=C_TEXT2).pack(side="left")
        self.alpha_var = ctk.DoubleVar(value=0.05)
        ctk.CTkSlider(ar, from_=0.01, to=0.20, number_of_steps=19, variable=self.alpha_var, width=150, fg_color=C_BORDER, progress_color=C_ACCENT,
                    command=self._upd_alpha).pack(side="left", padx=10)
        self.alpha_lbl = lbl(ar, "α = 0.05", color=C_ACCENT2, bold=True)
        self.alpha_lbl.pack(side="left")

        self.clip = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(cfg, text="Remove outliers before comparing", variable=self.clip, font=ctk.CTkFont("Segoe UI", 11), fg_color=C_ACCENT, hover_color=C_ACCENT2,
            text_color=C_TEXT2).pack(anchor="w", padx=20, pady=(2, 4))

        self.unusual_time = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(cfg, text="Simulate unusual/night access time",
            variable=self.unusual_time, font=ctk.CTkFont("Segoe UI", 11),
            fg_color=C_ACCENT, hover_color=C_ACCENT2,
            text_color=C_TEXT2).pack(anchor="w", padx=20, pady=(0, 8))

        self.badge = StatusBadge(self)
        self.badge.pack(fill="x", pady=(4, 2))

        self.detail = lbl(self, "Ready. Enter credentials to register or login.", 11, C_MUTED)
        self.detail.pack(anchor="w", pady=(0, 4))

    def _upd_alpha(self, _=None):
        self.alpha_lbl.configure(text=f"α = {self.alpha_var.get():.2f}")

    def _get_credentials(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        return username, password

    def _clear(self):
        self.username_entry.delete(0, "end")
        self.password_entry.reset()
        self.app.current_user = None
        self.app.profile = None
        self.user_lbl.configure(text="Status: Not authenticated", text_color=C_MUTED)
        self.badge.idle()
        self.detail.configure(text="Form cleared.", text_color=C_MUTED)

    def _handle_register(self):
        """Validates credentials and persists them to the user storage system."""
        username, password = self._get_credentials()
        if not username or not password:
            self.badge.deny_register()
            self.detail.configure(text="Fields cannot be empty.", text_color=C_DANGER)
            return
        if len(password) < 4:
            self.badge.deny_register()
            self.detail.configure(text="Password must be >= 4 chars.", text_color=C_WARN)
            return
        if not store.register_user(username, password):
            self.badge.deny_register()
            self.detail.configure(text=f"Username '{username}' is already taken.", text_color=C_DANGER)
            return
            
        self.badge.registered()
        self.detail.configure(text=f"Success! User '{username}' registered in database.", text_color=C_SUCCESS)

    def _handle_load_profile(self):
        """Opens a dialog to manually import a specific pre-trained .kda typing profile."""
        path = filedialog.askopenfilename(title="Select .kda profile file", filetypes=[("Keystroke Profile Data", "*.kda")])
        if not path:
            return

        try:
            self.app.profile = load_profile(path)
            filename = os.path.basename(path)
            self.badge.idle()
            self.detail.configure(text=f"Profile '{filename}' loaded into session memory!", text_color=C_SUCCESS)
        except Exception as e:
            self.badge.idle()
            self.detail.configure(text=f"Failed to load profile: {str(e)}", text_color=C_DANGER)
            
    def _handle_login(self):
        """Verifies password correctness first, then processes keystroke biometrics for final authentication."""
        username, password = self._get_credentials()
        
        if not username or not password:
            self.badge.denied()
            self.detail.configure(text="Credentials fields are empty.", text_color=C_DANGER)
            self.password_entry.reset()
            return

        # Traditional verification step before running biometric analysis
        if not store.verify(username, password):
            self.badge.denied()
            self.detail.configure(text="Invalid username or password.", text_color=C_DANGER)
            self.password_entry.reset()
            return

        # Attempt to load local template file if profile isn't already active in session memory
        if self.app.profile is None:
            default_path = f"{username}.kda"
            if os.path.exists(default_path):
                try:
                    self.app.profile = load_profile(default_path)
                except Exception as e:
                    self.badge.idle()
                    self.detail.configure(text=f"Error reading biometrical profile: {str(e)}", text_color=C_DANGER)
                    self.password_entry.reset()
                    return

        if self.app.profile is None:
            self.badge.idle()
            self.detail.configure(text=f"Password OK. But no biometrical profile found for '{username}'. Go to Training tab.", text_color=C_WARN)
            messagebox.showwarning("No Profile", f"Password verified!\nHowever, user '{username}' has no trained profile. Please record it via the Training tab or click 'Load Profile'.")
            self.password_entry.reset()
            return

        # Calculate exact number of dimensions (N keystrokes + N-1 intervals between them)
        tims = self.password_entry.timings[:len(password)]
        n_keys = len(password)
        expected_features = n_keys + (n_keys - 1)

        if len(tims) < n_keys:
            self.badge.idle()
            self.detail.configure(text="Keystroke capture incomplete. Please type your password smoothly.", text_color=C_WARN)
            self.password_entry.reset()
            return

        # Dwell Time: Key hold duration | Flight Time: Gap between release (i-1) and press (i)
        dwell = np.array([t["dwell"] for t in tims], dtype=float)
        flight = np.array([tims[i]["press_time"] - tims[i-1]["release_time"] for i in range(1, len(tims))], dtype=float)
        flight = np.maximum(flight, 0) # Normalizes negative flight times caused by overlapping keypresses
        feats = np.concatenate([dwell, flight])

        if len(feats) != expected_features:
            self.badge.idle()
            self.detail.configure(text=f"Data length mismatch ({len(feats)}/{expected_features}). Try again.", text_color=C_WARN)
            self.password_entry.reset()
            return

        # Computes Mahalanobis distance D^2 using the user's covariance matrix template
        try:
            score = score_attempt(feats, self.app.profile, clip_outliers=self.clip.get())
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            self.password_entry.reset()
            return

        alpha = float(self.alpha_var.get())
        current_hour = datetime.now().hour
        is_night = current_hour >= 22 or current_hour < 6

        # Adaptive security layer: shifts alpha higher during high-risk hours to tighten the threshold criteria
        if self.unusual_time.get() or is_night:
            alpha = min(alpha * 2.0, 0.40)
            security_alert = " [STRICT MODE]"
        else:
            security_alert = ""

        # Evaluates distance score against the critical value from Chi-Square distribution
        tau = threshold(len(self.app.profile["means"]), alpha)
        accepted = score <= tau

        if accepted:
            self.badge.granted()
            self.app.current_user = username
            self.user_lbl.configure(text=f"Status: Logged in as {username}", text_color=C_SUCCESS)
            self.detail.configure(
                text=f"AUTHORIZED! D^2={score:.4f} <= Threshold={tau:.4f} | α={alpha:.2f}{security_alert}",
                text_color=C_SUCCESS
            )
        else:
            self.badge.denied()
            self.detail.configure(
                text=f"REJECTED BIOMETRICS! D^2={score:.4f} > Threshold={tau:.4f} | α={alpha:.2f}{security_alert}",
                text_color=C_DANGER
            )

        self.password_entry.reset()