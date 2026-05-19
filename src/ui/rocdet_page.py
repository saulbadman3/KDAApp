import customtkinter as ctk
import numpy as np
from src.theme import *
from src.ui.shared import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.core.math_model import roc_det
from tkinter import messagebox

class RocDetPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        section_title(self, "ROC & DET Curves").pack(anchor="w", pady=(0, 4))
        lbl(self, "Collect test data in Research tab first, then plot.", color=C_MUTED).pack(anchor="w", pady=(0, 16))
        btn(self, "Plot Curves", self._plot, C_ACCENT).pack(anchor="w", pady=(0, 14))

        pc = card(self)
        pc.pack(fill="both", expand=True)
        self.fig = Figure(figsize=(8,4), dpi=96, facecolor="#1a1e35")
        self.ax_roc = self.fig.add_subplot(1, 2, 1)
        self.ax_det = self.fig.add_subplot(1, 2, 2)
        self._style()
        self.fig.tight_layout(pad=2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=pc)
        self.canvas.get_tk_widget().configure(bg="#1a1e35")
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

    def _style(self):
        for ax, title, xl, yl in [(self.ax_roc,"ROC Curve","FPR","TPR (1 – FRR)"), (self.ax_det,"DET Curve","FAR","FRR")]:
            ax.set_facecolor("#13162b")
            ax.set_title(title, color=C_TEXT, fontsize=11, pad=8, fontweight="bold")
            ax.set_xlabel(xl, color=C_MUTED, fontsize=9)
            ax.set_ylabel(yl, color=C_MUTED, fontsize=9)
            ax.tick_params(colors=C_MUTED, labelsize=8)
            for sp in ax.spines.values():
                sp.set_color(C_BORDER)

    def _plot(self):
        if not self.app.roc_data:
            messagebox.showwarning("No data", "Run Compute FAR/FRR in Research first.")
            return
        
        legit, impost = self.app.roc_data
        thrs, fars, frrs, tprs = roc_det(legit, impost, 50)
        self.ax_roc.cla()
        self.ax_det.cla()
        self._style()
        self.ax_roc.plot(fars, tprs, color=C_ACCENT2, lw=2, marker="o", ms=4, markerfacecolor="#f0c27f", zorder=3)
        self.ax_roc.fill_between(fars, tprs, alpha=0.08, color=C_ACCENT)
        self.ax_roc.plot([0,1],[0,1],"--",color=C_MUTED,lw=1)
        self.ax_roc.set_xlim(0,1)
        self.ax_roc.set_ylim(0,1)
        auc = float(np.trapezoid(tprs, fars))
        self.ax_roc.text(0.55, 0.08, f"AUC = {auc:.3f}", color=C_ACCENT2, fontsize=9, transform=self.ax_roc.transAxes)
        self.ax_det.plot(fars, frrs, color="#4ade80", lw=2, marker="s", ms=4, markerfacecolor="#f87171", zorder=3)
        self.ax_det.plot([0,1],[0,1],"--",color=C_MUTED,lw=1)
        ei = np.argmin(np.abs(fars-frrs))
        eer = (fars[ei]+frrs[ei])/2
        self.ax_det.scatter([fars[ei]],[frrs[ei]],color="#f0c27f",zorder=5,s=70)
        self.ax_det.annotate(f" EER≈{eer:.3f}",(fars[ei],frrs[ei]), color="#f0c27f",fontsize=8)
        self.ax_det.set_xlim(0,1)
        self.ax_det.set_ylim(0,1)
        self.fig.tight_layout(pad=2)
        self.canvas.draw()