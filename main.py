from ttkbootstrap import Window
from ttkbootstrap.style import ThemeDefinition
from gui import GUI

# CONFIG_FILE = "config_file_path"
THEME = ThemeDefinition(
    name="custom",
    themetype="light",
    colors={
        "primary": "#eeb604",
        "secondary": "#444444",
        "success": "#00bc8c",
        "info": "#3498db",
        "warning": "#f39c12",
        "danger": "#e74c3c",
        "light": "#ADB5BD",
        "dark": "#303030",
        "bg": "#222222",
        "fg": "#ffffff",
        "selectbg": "#555555",
        "selectfg": "#ffffff",
        "border": "#222222",
        "inputfg": "#ffffff",
        "inputbg": "#2f2f2f",
        "active": "#1F1F1F",
    },
)

if __name__ == "__main__":
    root = Window()
    root.style.load_user_theme(THEME)
    root.style.theme_use("custom")
    gui = GUI(master=root)  # or gui = GUI(master=root, CONFIG_FILE)
    gui.mainloop()
