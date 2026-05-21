import customtkinter as ctk
from src.theme import *
import time

def card(master, **kw):
    return ctk.CTkFrame(master, fg_color=C_CARD, corner_radius=14, border_width=1, border_color=C_BORDER, **kw)

def lbl(master, text, size=13, color=C_TEXT, bold=False, **kw):
    return ctk.CTkLabel(master, text=text, font=ctk.CTkFont("Segoe UI", size, "bold" if bold else "normal"), text_color=color, **kw)

def section_title(master, text):
    return ctk.CTkLabel(master, text=text, font=ctk.CTkFont("Segoe UI", 22, "bold"), text_color=C_ACCENT2)

def btn(master, text, cmd, color=C_ACCENT, w=160, **kw):
    def _hover(h):
        r, g, b = int(h[1:3],16), int(h[3:5],16), int(h[5:7],16)
        f = 0.82
        return f"#{int(r*f):02x}{int(g*f):02x}{int(b*f):02x}"
    return ctk.CTkButton(master, text=text, command=cmd, fg_color=color, hover_color=_hover(color), corner_radius=10, height=38, width=w, 
                         font=ctk.CTkFont("Segoe UI", 13, "bold"), **kw)

class StatusBadge(ctk.CTkLabel):
    def __init__(self, master):
        super().__init__(master, text="", corner_radius=10, font=ctk.CTkFont("Segoe UI", 14, "bold"), height=52)
        self.idle()

    def idle(self):
        self.configure(text="Awaiting input...", fg_color="#241a0e", text_color=C_MUTED)

    def granted(self):
        self.configure(text="ACCESS GRANTED", fg_color="#14532d", text_color="#4ade80")

    def denied(self):
        self.configure(text="ACCESS DENIED", fg_color="#450a0a", text_color="#f87171")

    def wrong(self):
        self.configure(text="WRONG PASSPHRASE", fg_color="#451a03", text_color=C_WARN)

class KeyEntry(ctk.CTkEntry):
    def __init__(self, master, on_submit, **kw):
        super().__init__(master, show="●", height=46, corner_radius=10, border_color=C_BORDER, fg_color=C_PANEL, font=ctk.CTkFont("Segoe UI", 16),
                        placeholder_text="Type passphrase and press Enter...", placeholder_text_color=C_MUTED, **kw)
        self._press = {}
        self.timings = []
        self._callback = on_submit
        self.bind("<KeyPress>", self._kp)
        self.bind("<KeyRelease>", self._kr)
        self.bind("<Return>", lambda _: on_submit())

    def _kp(self, e):
        forbidden = ("BackSpace", "Delete")
        if e.keysym in forbidden:
            self.reset()
            if hasattr(self.master, "status"):
                self.master.status.configure(text="Corrections are not allowed. Start typing again.", text_color=C_DANGER)
            return "break"

        if e.keysym in ("Return", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "CapsLock", "Tab"):
            return
        self._press[e.keysym] = time.perf_counter() * 1000

    def _kr(self, e):
        if e.keysym == "Return":
            return
        k = e.keysym
        if k in self._press:
            pr = self._press.pop(k)
            re = time.perf_counter() * 1000
            self.timings.append({"key":k, "press_time":pr, "release_time":re, "dwell":re-pr})

    def reset(self):
        self.delete(0, "end")
        self.timings.clear()
        self._press.clear()