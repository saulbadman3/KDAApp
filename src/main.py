# src/main.py
import customtkinter as ctk
import os
from src.ui.sidebar import Sidebar
from src.theme import *
from src.ui.shared import *
from src.core.math_model import *
from src.ui.training_page import TrainingPage
from src.ui.auth_page import AuthPage
from src.ui.rocdet_page import RocDetPage
from src.ui.research_page import ResearchPage
from src.config import PROFILE_FILE
from src.core.profile_io import load_profile

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=C_BG)
        self.title("KDA - Keystroke Dynamics Authentication")
        self.geometry("1060x680")
        self.minsize(1060, 680)
        self.profile = None
        self.roc_data = None
        self._build()
        self._auto_load()

    def _build(self):
        self._current = 0
        self.pages = []
        self.sidebar = Sidebar(self, self._switch)
        self.sidebar.pack(side="left", fill="y")
        self.content = ctk.CTkFrame(self, fg_color=C_BG)
        self.content.pack(side="left", fill="both", expand=True)
        self.pages = [
            TrainingPage(self.content, self),
            AuthPage(self.content, self),
            ResearchPage(self.content, self),
            RocDetPage(self.content, self),
        ]
        self.pages[0].pack(fill="both", expand=True, padx=32, pady=28)

    def _switch(self, idx):
        if not self.pages or idx == self._current:
            return
        self.pages[self._current].pack_forget()
        self._current = idx
        self.pages[idx].pack(fill="both", expand=True, padx=32, pady=28)

    def _auto_load(self):
        if os.path.exists(PROFILE_FILE):
            try:
                self.profile = load_profile(PROFILE_FILE)
            except Exception:
                pass

def main():
    app = App()
    app.mainloop()