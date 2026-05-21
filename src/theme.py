class T:
    BG = "#0f0a07"
    PANEL = "#1a1208"
    CARD = "#241a0e"
    BORDER = "#3d2e1a"
    ACCENT = "#c27d3a"
    ACCENT2 = "#e8a85f"
    SUCCESS = "#7fb96b"
    DANGER = "#d94f3a"
    WARN = "#e8c53a"
    MUTED = "#7a6555"
    TEXT = "#f0e6d8"
    TEXT2 = "#c4a882"
    GOLD = "#f5c842"

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