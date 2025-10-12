import tkinter as tk
from tkinter import ttk


def create_info_bar(self):
    """Create the info bar and his"""

    frame_statusbar = ttk.Frame(self.master)
    self.label_image_info = tk.Label(
        frame_statusbar,
        text="image info",
    )
    self.label_image_pixel = ttk.Label(
        frame_statusbar,
        text="(x, y)",
    )
    self.label_image_info.pack(side=tk.RIGHT)
    self.label_image_pixel.pack(side=tk.LEFT)
    frame_statusbar.pack(side=tk.BOTTOM, fill=tk.X)
