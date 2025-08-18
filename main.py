import tkinter as tk
from gui import GUI

# CONFIG_FILE = "config_file_path"

if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(master=root)  # or gui = GUI(master=root, CONFIG_FILE)
    gui.mainloop()
