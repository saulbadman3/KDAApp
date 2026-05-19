class T:
    BG = "#0d0f18"
    PANEL = "#13162b"
    CARD = "#1a1e35"
    BORDER = "#252945"
    ACCENT = "#5b7cf6"
    ACCENT2 = "#7c9dff"
    SUCCESS = "#22c55e"
    DANGER = "#ef4444"
    WARN = "#f59e0b"
    MUTED = "#6b7280"
    TEXT = "#e2e8f0"
    TEXT2 = "#94a3b8"
    GOLD = "#f0c27f"

    @staticmethod
    def hover(hex_color: str) -> str:
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        f = 0.82
        return f"#{int(r*f):02x}{int(g*f):02x}{int(b*f):02x}"

C_BG = T.BG
C_PANEL = T.PANEL
C_CARD = T.CARD
C_BORDER = T.BORDER
C_ACCENT = T.ACCENT
C_ACCENT2 = T.ACCENT2
C_SUCCESS = T.SUCCESS
C_DANGER = T.DANGER
C_WARN = T.WARN
C_MUTED = T.MUTED
C_TEXT = T.TEXT
C_TEXT2 = T.TEXT2
C_GOLD = T.GOLD

__all__ = ["T", "C_BG","C_PANEL","C_CARD","C_BORDER", "C_ACCENT","C_ACCENT2","C_SUCCESS","C_DANGER", "C_WARN","C_MUTED","C_TEXT","C_TEXT2","C_GOLD"]