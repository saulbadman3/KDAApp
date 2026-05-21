import customtkinter as ctk
from src.theme import *

NAV = ["Training",  "Auth",  "Research", "ROC / DET"]

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_select):
        super().__init__(master, width=200, fg_color=C_PANEL, corner_radius=0)
        self.pack_propagate(False)
        self._cb   = on_select
        self._btns = []

        ctk.CTkLabel(self, text="KDA", font=ctk.CTkFont("Segoe UI", 30, "bold"), text_color=C_ACCENT2).pack(pady=(36,0))
        ctk.CTkLabel(self, text="Keystroke Dynamics Auth", font=ctk.CTkFont("Segoe UI", 9), text_color=C_MUTED).pack(pady=(2,24))
        ctk.CTkFrame(self, height=1, fg_color=C_BORDER).pack(fill="x", padx=20, pady=(0,20))

        for i, label in enumerate(NAV):
            b = ctk.CTkButton(self, text=f" {label}", anchor="w", height=44, corner_radius=10, fg_color="transparent", hover_color=C_CARD, text_color=C_TEXT2, 
                              font=ctk.CTkFont("Segoe UI", 13), command=lambda i=i: self.select(i))
            b.pack(fill="x", padx=12, pady=3)
            self._btns.append(b)

        self.select(0)

        ctk.CTkFrame(self, height=1, fg_color=C_BORDER).pack(fill="x", padx=20, pady=20, side="bottom")

    def select(self, idx):
        for i, b in enumerate(self._btns):
            if i == idx:
                b.configure(fg_color=C_CARD, text_color=C_ACCENT2, font=ctk.CTkFont("Segoe UI", 13, "bold"))
            else:
                b.configure(fg_color="transparent", text_color=C_TEXT2, font=ctk.CTkFont("Segoe UI", 13))
        self._cb(idx)