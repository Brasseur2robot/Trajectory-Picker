import tkinter as tk
from tkinter import ttk


def create_canvas(self):
    """Create a canvas where the image will be displayed and add two separator

    Args:
        self (GUI): the GUI object that is manipulated
    """

    self.canvas = tk.Canvas(self.master)
    self.canvas.pack(expand=True, fill=tk.BOTH)
    self.canvas.bind("<Configure>", self.load_last_opened_image)

    # Canvas / Menu separator
    separator_cm = ttk.Frame(self.canvas, style="primary.TFrame", height="2")
    separator_cm.pack(side="top", fill="x")

    # Canvas / Status bar separator
    separator_csb = ttk.Frame(self.canvas, style="primary.TFrame", height="2")
    separator_csb.pack(side="bottom", fill="x")
