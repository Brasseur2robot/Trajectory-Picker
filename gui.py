# Based on this project: https://github.com/ImagingSolution/PythonImageViewer/

import tkinter as tk  # Window creation
from tkinter import filedialog, messagebox  # Open file
from PIL import Image, ImageTk  # Image management
import math  # Revolution calculations
import numpy as np  # Affine transformation matrix operations
import os  # Directory operations
import json  # Json operations
from trajectory_manager import *
import trajectory_manager


class GUI(tk.Frame):
    def __init__(
        self,
        master=None,
        CONFIG_FILE=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config.json"
        ),
    ):
        super().__init__(master)

        self.CONFIG_FILE = CONFIG_FILE

        # Config
        self.CONFIG = self.load_config()

        coordinate_system = self.CONFIG.get("coordinate_system")
        if coordinate_system:
            self.coordinate_system = tk.StringVar(value=coordinate_system)
        else:
            self.coordinate_system = tk.StringVar(value="top-left")
        self.previous_cs = self.coordinate_system.get()

        # Basic window setting
        self.master.geometry("600x400")

        self.pil_image = None  # Image to display
        self.my_title = "Trajectory Picker"

        # Window title
        self.master.title(self.my_title)

        # Window component
        self.create_menu()  # Menu creation
        self.create_widget()  # Widget creation

        # Trajectory points
        self.image_points = []  # list of (x, y) tuples in image coordinates

        # Initial affine transformation matrix
        self.reset_transform()

        self.master.after(
            100, self.load_last_opened_image
        )  # TODO: Wait 60ms to make sure everything is loaded, if done too fast it won't show the image // Bug

    # Close the window
    def menu_quit_clicked(self, event=None):
        self.master.destroy()

    # create_menu method
    def create_menu(self):
        self.menu_bar = tk.Menu(
            self,
            bg="#1d1d1d",
            fg="#ffffff",
            activebackground="#eeb604",
            bd=0,
            relief=tk.FLAT,
        )  # Create menu_bar instance from Menu class

        # File menu
        self.file_menu = tk.Menu(
            self.menu_bar,
            tearoff=tk.OFF,
            bg="#1d1d1d",
            fg="#ffffff",
            activebackground="#eeb604",
            relief=tk.FLAT,
            bd=0,
        )
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(
            label="Open image", command=self.load_image, accelerator="Ctrl + O"
        )
        self.file_menu.add_command(
            label="Open trajectory", command=self.load_file, accelerator="Ctrl + T"
        )
        self.file_menu.add_command(
            label="Save trajectory", command=self.save_file, accelerator="Ctrl + S"
        )
        self.file_menu.add_separator()  # Add separator
        self.file_menu.add_command(
            label="Exit", command=self.menu_quit_clicked, accelerator="Ctrl + Q"
        )

        self.menu_bar.bind_all(
            "<Control-o>", self.load_image
        )  # Create a bind to open an image to load
        self.menu_bar.bind_all(
            "<Control-t>", self.load_file
        )  # Create a bind to open a trajectory file
        self.menu_bar.bind_all(
            "<Control-s>", self.save_file
        )  # Create a bind to save the current trajectory to a file
        self.menu_bar.bind_all(
            "<Control-q>", self.menu_quit_clicked
        )  # Create a bind to close the app

        # Floating panel menu
        self.fp_menu = tk.Menu(
            self.menu_bar,
            tearoff=tk.OFF,
            bg="#1d1d1d",
            fg="#ffffff",
            activebackground="#eeb604",
            relief=tk.FLAT,
            bd=0,
        )
        self.menu_bar.add_cascade(label="Floating panel", menu=self.fp_menu)

        self.fp_menu.add_command(label="Open", command=self.toggle_panel_open)
        # Old config:
        # self.fp_menu.add_command(label="Resize", command=self.toggle_panel_size)
        self.fp_menu.add_command(label="Close", command=self.toggle_panel_close)

        # Image menu
        self.image_menu = tk.Menu(
            self.menu_bar,
            tearoff=tk.OFF,
            bg="#1d1d1d",
            fg="#ffffff",
            activebackground="#eeb604",
            relief=tk.FLAT,
            bd=0,
        )
        self.menu_bar.add_cascade(label="Image", menu=self.image_menu)

        self.image_menu.add_command(
            label="Zoom-in", command=lambda: self.zoom(None, 1), accelerator="Ctrl + +"
        )
        self.image_menu.add_command(
            label="Zoom-out", command=lambda: self.zoom(None, 0), accelerator="Ctrl + -"
        )
        self.image_menu.add_command(
            label="Recenter",
            command=lambda: self.recenter_image(None),
            accelerator="Double right click",
        )
        self.image_menu.add_command(
            label="Rotate clockwise",
            command=lambda: self.rotate_image(5),
            accelerator="Ctrl + M",
        )
        self.image_menu.add_command(
            label="Rotate counterclockwise",
            command=lambda: self.rotate_image(-5),
            accelerator="Ctrl + L",
        )
        # Trajectory menu
        self.trajectory_menu = tk.Menu(
            self.menu_bar,
            tearoff=tk.OFF,
            bg="#1d1d1d",
            fg="#ffffff",
            activebackground="#eeb604",
            relief=tk.FLAT,
            bd=0,
        )
        self.menu_bar.add_cascade(label="Trajectory", menu=self.trajectory_menu)

        # Coordinate system sub-menu
        self.cs_sub_menu = tk.Menu(
            self.trajectory_menu,
            tearoff=tk.OFF,
            bg="#1d1d1d",
            fg="#ffffff",
            activebackground="#eeb604",
            relief=tk.FLAT,
            bd=0,
        )
        self.trajectory_menu.add_cascade(
            label="Coordinate system", menu=self.cs_sub_menu
        )  # cs means coordinate system here

        self.cs_sub_menu.add_radiobutton(
            label="Top left",
            variable=self.coordinate_system,
            value="top-left",
            command=lambda: self.coordinate_system_wrapper(),
        )
        self.cs_sub_menu.add_radiobutton(
            label="Bottom left",
            variable=self.coordinate_system,
            value="bottom-left",
            command=lambda: self.coordinate_system_wrapper(),
        )

        self.trajectory_menu.add_command(
            label="Add a new point",
            command=lambda: self.create_point(event="Menu"),
            accelerator="Left click",
        )

        self.trajectory_menu.add_command(
            label="Delete last point",
            command=lambda: self.delete_point(event=not None),
            accelerator="Middle click",
        )

        # TODO: Option & help menu
        """self.options_menu = tk.Menu(
            self.menu_bar,
            tearoff=tk.OFF,
            bg="#1d1d1d",
            fg="#ffffff",
            activebackground="#eeb604",
            relief=tk.FLAT,
            bd=0,
        )
        self.menu_bar.add_cascade(label="Options & help", menu=self.options_menu)"""

        self.master.config(menu=self.menu_bar)  # Menu bar arrangement

    # Define create_widget method
    def create_widget(self):
        # Status bar equivalent (added to parent)
        self.frame_statusbar = tk.Frame(self.master, bg="#1d1d1d")
        self.label_image_info = tk.Label(
            self.frame_statusbar,
            text="image info",
            bg="#1d1d1d",
            fg="#ffffff",
            anchor=tk.E,
            padx=5,
        )
        self.label_image_pixel = tk.Label(
            self.frame_statusbar,
            text="(x, y)",
            bg="#1d1d1d",
            fg="#ffffff",
            anchor=tk.W,
            padx=5,
        )
        self.label_image_info.pack(side=tk.RIGHT)
        self.label_image_pixel.pack(side=tk.LEFT)
        self.frame_statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas
        self.canvas = tk.Canvas(
            self.master, background="#262626", bd=0, highlightthickness=0
        )
        self.canvas.pack(
            expand=True, fill=tk.BOTH
        )  # Same as Dock.Fill in both of these

        # Canvas / Menu separator
        self.separator_cm = tk.Frame(self.canvas, bg="#EEB604", height="2")
        self.separator_cm.pack(side="top", fill="x")

        # Canvas / Status bar separator
        self.separator_csb = tk.Frame(self.canvas, bg="#EEB604", height="2")
        self.separator_csb.pack(side="bottom", fill="x")

        # Mouse event
        self.master.bind(
            "<Button-1>", self.create_point
        )  # Left mouse button / create a point
        self.master.bind(
            "<Button-2>", self.delete_point
        )  # Middle mouse button click / delete latest point
        self.master.bind(
            "<Button-3>", self.set_move_image
        )  # Right mouse button / set the current coordinates to move the image
        self.master.bind(
            "<B3-Motion>", self.move_image
        )  # Left mouse button with movement / move the image
        self.master.bind(
            "<Motion>", self.change_coordinates
        )  # Mouse movement / change coordinates
        self.master.bind(
            "<Double-Button-3>", self.recenter_image
        )  # Right mouse button double click / recenter the image
        self.master.bind("<MouseWheel>", self.zoom)  # Mouse wheel / zoom

        # Keyboard event
        self.master.bind(
            "<Control-equal>", lambda event: self.zoom(event, 1)
        )  # Crtl + keys / zoom-in
        self.master.bind(
            "<Control-minus>", lambda event: self.zoom(event, 0)
        )  # Ctrl - keys / zoom-out

        # The following bind didn't worked with leftarrow and rightarrow :(
        self.master.bind(
            "<Control-m>",
            lambda event: self.rotate_image(5.0),
        )  # Ctrl left / rotate clockwise
        self.master.bind(
            "<Control-l>", lambda event: self.rotate_image(-5.0)
        )  # Ctrl right / rotate counterclockwise

        # Create the floating panel
        self.create_floating_panel()

    # Define the floating panel
    def create_floating_panel(self):
        self.floating_panel_minimized = False
        self.floating_panel_width = 200
        # Create a frame inside the canvas
        self.floating_panel = tk.Toplevel(self.master)
        self.floating_panel.minsize(width=self.floating_panel_width, height=300)
        self.floating_panel.overrideredirect(True)  # Remove window decorations
        self.floating_panel.geometry("100x300+100+100")
        self.floating_panel.configure(bg="#262626")

        # Create a title bar
        self.floating_panel_titlebar = tk.Frame(
            self.floating_panel, bg="#1d1d1d", relief=tk.RAISED
        )
        self.floating_panel_titlebar.pack(fill=tk.X)

        self.floating_panel_titlebar.pack_propagate(
            False
        )  # Disable resizing based on child widgets
        self.floating_panel_titlebar.config(
            height=20
        )  # Set the height of the titlebar, can't do it if pack is not desactivate

        self.floating_panel_title_label = tk.Label(
            self.floating_panel_titlebar,
            text="Floating Panel",
            bg="#1d1d1d",
            fg="white",
        )
        self.floating_panel_title_label.pack(side=tk.LEFT, padx=5)
        """
        self.floating_panel_toggle_button = tk.Button(
            self.floating_panel_titlebar,
            text="_",
            command=self.toggle_panel_size,
            width=2,
        )
        self.floating_panel_toggle_button.pack(side=tk.RIGHT)"""

        # Content inside the panel
        self.floating_panel_content = tk.Frame(self.floating_panel, bg="#262626")
        self.floating_panel_content.pack(expand=True, fill=tk.BOTH)

        # Titlebar / Panel content separator
        self.separator_cpc = tk.Frame(
            self.floating_panel_content, bg="#EEB604", height="2"
        )
        self.separator_cpc.pack(side="top", fill="x")

        self.floating_panel_text_widget = tk.Text(
            self.floating_panel_content,
            bg="#262626",
            fg="#ffffff",
            bd=0,
            highlightthickness=0,
            height=13,
            width=40,
        )
        self.floating_panel_text_widget.pack(padx=10, pady=10)

        # Create a list of Entry widgets to edit coordinates
        self.entry_widgets = []

        # Create a list of Checkbox var to update points
        self.checkbox_var_widgets = []

        # Export & delete buttons
        tk.Button(
            self.floating_panel_content,
            text="Delete point(s)",
            command=self.delete_point,
            bg="#3b3b3b",
            fg="white",
            activebackground="#4b4b4b",
            activeforeground="white",
            relief=tk.FLAT,
            overrelief=tk.FLAT,
        ).pack(padx=10, pady=10)
        # Old config:
        """tk.Button(
            self.floating_panel_content,
            text="Export to json or csv",
            command=self.save_file,
            bg="#3b3b3b",
            fg="white",
            activebackground="#4b4b4b",
            activeforeground="white",
            relief=tk.FLAT,
            overrelief=tk.FLAT,
        ).pack(padx=10, pady=10)"""

        # Enable dragging the panel
        # TODO: Need to be tested on Windows to see if it's working without
        """
        for widget in (self.panel_title_label, self.panel_titlebar):
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.do_drag)"""

    # Set image in the canvas
    def set_image(self, filename):
        if not filename:
            return
        # Open with PIL.Image
        self.test = True
        self.pil_image = Image.open(filename)
        # Set the affine transformation matrix to display the entire image
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        # Display the image
        self.draw_image(self.pil_image)

        # Set window title file name
        self.master.title(self.my_title + " - " + os.path.basename(filename))
        # Display image information on the status bar
        self.label_image_info["text"] = (
            f"{self.pil_image.format} : {self.pil_image.width} x {self.pil_image.height} {self.pil_image.mode}"
        )
        """
        # Setting the current directory
        # os.chdir(os.path.dirname(filename))"""

    # -------------------------------------------------------------------------------
    # Save & load file / Config wrapper
    # -------------------------------------------------------------------------------

    def save_file(self, event=None):
        # Open a file picker to save coordinates to a file
        if not self.image_points:
            messagebox.showwarning("No Data", "There are no coordinates to save.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Coordinates File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")],
        )

        if file_path:
            file_extension = os.path.splitext(file_path)[-1].lower()
            try:
                if file_extension == ".json":
                    coordinates_to_json(self.image_points, file_path)
                elif file_extension == ".csv":
                    coordinates_to_csv(self.image_points, file_path)
                else:
                    messagebox.showerror("Unsupported File", "File type not supported.")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {e}")

    def load_file(self, event=None):
        # Load the trajectory file chosen by the user
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("JSON & CSV", ".json .csv"),
                ("JSON", ".json"),
                ("CSV", ".csv"),
            ],
            initialdir=os.getcwd(),  # Current directory
        )

        if file_path:
            file_extension = os.path.splitext(file_path)[-1].lower()
            try:
                if file_extension == ".json":
                    self.image_points = json_to_coordinates(file_path)
                    self.update_fp()
                    self.redraw_image()
                elif file_extension == ".csv":
                    self.image_points = csv_to_coordinates(file_path)
                    self.update_fp()
                    self.redraw_image()
                else:
                    messagebox.showerror("Unsupported File", "File type not supported.")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {e}")

    def save_config(self, key, value):
        # Save the config inside .json file based on a key / value system
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as config_file:
                try:
                    config = json.load(config_file)
                except json.JSONDecodeError:
                    return None

            # Update with new key / value pair
            config[key] = value

            with open(self.CONFIG_FILE, "w") as config_file:
                json.dump(config, config_file, indent=4)

    def load_config(self):
        # Load the configuration to from a .json file if the file doesn't exist, it creates an empty one
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as config_file:
                return json.load(config_file)

        else:
            with open(self.CONFIG_FILE, "w") as config_file:
                json.dump({}, config_file, indent=4)
                return {}

    def load_last_opened_image(self):
        # Load the last opened image based on the content of the config file
        last_image = self.CONFIG.get("last_opened_image")
        if last_image and os.path.exists(last_image):
            self.set_image(last_image)

    def load_image(self, event=None):
        # Load the image chosen by the user
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image file", ".bmp .png .jpg .tif"),
                ("Bitmap", ".bmp"),
                ("PNG", ".png"),
                ("JPEG", ".jpg"),
                ("Tiff", ".tif"),
            ],
            initialdir=os.getcwd(),  # Current directory
        )

        # Set the image to open
        self.set_image(file_path)

        if file_path:
            self.save_config("last_opened_image", file_path)

    def coordinate_system_wrapper(self):
        # Wrapper to save the coordinate_system in the CONFIG_FILE and redraw_image
        response = "yes"
        if self.previous_cs == self.coordinate_system.get():
            return
        if self.image_points:
            response = messagebox.askquestion(
                "Coordinate system",
                "You already have points in your trajectory set with a specific coordinate system. Setting another one can broke your trajectory. Do you want to continue ?",
            )

        if response == "yes":
            self.previous_cs = self.coordinate_system.get()
            self.save_config("coordinate_system", self.coordinate_system.get())
            self.redraw_image()
            print(self.previous_cs)
            print(type(self.coordinate_system.get()))
        elif self.previous_cs != self.coordinate_system.get():
            self.coordinate_system.set(self.previous_cs)

    # -------------------------------------------------------------------------------
    # Define mouse & keyboard event
    # -------------------------------------------------------------------------------

    def set_move_image(self, event):
        # Right mouse button pressed / set the current coordinates to move the image
        self.__old_event = event

    def delete_point(self, event=None):
        # Middle right mouse button pressed / delete latest point
        if event == None:
            points_to_pop = [
                i
                for i, checkbox_value in enumerate(self.checkbox_var_widgets)
                if checkbox_value.get() == 1
            ]
            for index in reversed(
                points_to_pop
            ):  # Reverse it to not delete the wrong ones
                self.image_points.pop(index)
                self.update_fp()  # Update the content of the floating panel
                self.redraw_image()  # Update the canvas
        else:
            if self.image_points:
                self.image_points.pop()  # Remove the last point
                self.update_fp()  # Update the content of the floating panel
                self.redraw_image()  # Update the canvas

    def create_point(self, event):
        # Left mouse button pressed / create a point
        if self.pil_image is None:
            return
        if event == "Menu":
            return
            # TODO:
        else:
            image_point = self.to_image_point(event.x, event.y)
            if image_point is not None:
                self.image_points.append((image_point[0], image_point[1], None))
                self.image_points = trajectory_manager.calculate_angle(
                    self.image_points
                )
                self.update_fp()  # Update the content of the floating panel
                self.redraw_image()

    def move_image(self, event):
        # Drag the mouse with right mouse button pressed / move the image
        if self.pil_image is None:
            return
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.redraw_image()  # Redraw the image
        self.__old_event = event

    def change_coordinates(self, event):
        # Drag the mouse / change coordinates
        if self.pil_image is None:
            return

        image_point = self.to_image_point(event.x, event.y)
        if image_point is not None:
            self.label_image_pixel["text"] = (
                f"({image_point[0]:.0f}, {image_point[1]:.0f})"
            )
        else:
            self.label_image_pixel["text"] = "(--, --)"

    def recenter_image(self, event):
        # Double-click right mouse button / recenter the image
        if self.pil_image is None:
            return
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        self.redraw_image()  # Redraw the image

    def zoom(self, event, isZoomCenter=None):
        # Scrolling | Ctrl + '+' | Ctrl + '-' / zoom
        if self.pil_image is None:
            return

        if isZoomCenter is not None:
            # Center the zoom by setting the scale at current center of the canvas
            half_canvas_width = self.canvas.winfo_width() // 2
            half_canvas_height = self.canvas.winfo_height() // 2
            if isZoomCenter == 1:
                self.scale_at(1.25, half_canvas_width, half_canvas_height)
            else:
                self.scale_at(0.8, half_canvas_width, half_canvas_height)

        elif (
            event.state != 9
        ):  # 9 is for the shift key (probably only working for windows)
            if event.delta < 0:
                # Enlarged when scrolled down
                self.scale_at(1.25, event.x, event.y)
            else:
                # Shrink when scrolled up
                self.scale_at(0.8, event.x, event.y)

        else:
            if event.delta < 0:
                # Rotate counterclockwise when scrolled down
                self.rotate_at(-5, event.x, event.y)
            else:
                # Rotate clockwise when scrolled up
                self.rotate_at(5, event.x, event.y)
        self.redraw_image()  # Redraw the image

    def rotate_image(self, deg: float):
        if self.pil_image is None:
            return

        half_canvas_width = self.canvas.winfo_width() // 2
        half_canvas_height = self.canvas.winfo_height() // 2

        self.rotate_at(deg, half_canvas_width, half_canvas_height)
        self.redraw_image()

    # -------------------------------------------------------------------------------
    # Floating panel management -> Drag, open, close & size
    # -------------------------------------------------------------------------------

    # TODO: Need to be tested on Windows to see if it's working without
    """def start_drag(self, event):
        # Record the initial position
        self._drag_data = {"x": event.x, "y": event.y}

    def do_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]

        # Get current panel position
        x = self.floating_panel.winfo_x() + dx
        y = self.floating_panel.winfo_y() + dy

        self.floating_panel.place(x=x, y=y)"""

    # Old config:
    """def toggle_panel_size(self):
        # Resize the floating_panel based on the button value

        if not self.floating_panel_minimized:
            # Save current width and height before minimizing
            self.last_full_width = self.floating_panel.winfo_width()
            self.last_full_height = self.floating_panel.winfo_height()

            self.floating_panel_content.pack_forget()  # Hide content
            _, _, x, y = self._parse_geometry(self.floating_panel.geometry())
            self.floating_panel.geometry(f"{self.last_full_width}x20+{x}+{y}")
            self.floating_panel_toggle_button.config(text="▭")  # Maximize icon
        else:
            # Resize with save width and height
            self.floating_panel_content.pack(expand=True, fill=tk.BOTH)
            width, _, x, y = self._parse_geometry(self.floating_panel.geometry())
            self.floating_panel.geometry(
                f"{self.last_full_width}x{self.last_full_height}+{x}+{y}"
            )
            self.floating_panel_toggle_button.config(text="_")  # Minimize icon
        self.floating_panel_minimized = not self.floating_panel_minimized"""

    def toggle_panel_close(self):
        # Hide the toggle panel, still exist in the memory

        self.floating_panel.withdraw()

    def toggle_panel_open(self):
        # Make the toggle panel visible

        self.floating_panel.deiconify()

    # Old config:
    """def _parse_geometry(self, geometry_str):
        # Use a regular expression to extract the current geometry values
        # Example input: "200x100+150+200"
    """
    # match = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", geometry_str)
    """ if match:
            width, height, x, y = map(int, match.groups())
            return width, height, x, y
        return 200, 100, 100, 100  # Fallback"""

    # -------------------------------------------------------------------------------
    # Data floating panel management -> Point data
    # -------------------------------------------------------------------------------

    def update_fp(self):
        # Update the floating panel text widget with the current list of coordinates
        # Clear current content
        self.checkbox_var_widgets.clear()
        self.entry_widgets.clear()
        self.floating_panel_text_widget.delete(1.0, tk.END)

        # Insert updated coordinates
        for i, (x, y, angle) in enumerate(self.image_points):
            if i == 0:
                self.floating_panel_text_widget.insert(tk.END, "Point 1:    ")
            else:
                self.floating_panel_text_widget.insert(tk.END, f"\nPoint {i + 1}:    ")

            # Create Checkbox widgets
            check_var = tk.IntVar()
            checkbox = tk.Checkbutton(
                self.floating_panel_text_widget,
                bg="#262626",
                fg="#ffffff",
                selectcolor="#4b4b4b",
                activebackground="#262626",
                bd=0,
                highlightthickness=0,
                variable=check_var,
                relief=tk.FLAT,
            )
            self.checkbox_var_widgets.insert(i, check_var)

            # Adding the checkbox after the point name
            self.floating_panel_text_widget.window_create(tk.END, window=checkbox)

            self.floating_panel_text_widget.insert(tk.END, "\n   x: ")

            # Create Entry widgets for x and y values
            x_entry = tk.Entry(
                self.floating_panel_text_widget,
                width=5,
                bg="#4b4b4b",
                fg="white",
                relief=tk.FLAT,
            )
            x_entry.insert(
                0, format(x, ".0f")
            )  # Set the initial value to the current x rounded
            x_entry.bind(
                "<FocusOut>",
                lambda event, idx=i: self.wrapper_update_coordinate(event, idx),
            )
            self.entry_widgets.append(x_entry)

            y_entry = tk.Entry(
                self.floating_panel_text_widget,
                width=5,
                bg="#4b4b4b",
                fg="white",
                relief=tk.FLAT,
            )
            y_entry.insert(
                0, format(y, ".0f")
            )  # Set the initial value to the current y rounded
            y_entry.bind(
                "<FocusOut>",
                lambda event, idx=i: self.wrapper_update_coordinate(event, idx),
            )
            self.entry_widgets.append(y_entry)

            # Add the Entry widget and the angle to the Text widget
            self.floating_panel_text_widget.window_create(tk.END, window=x_entry)
            self.floating_panel_text_widget.insert(
                tk.END, "\n   y: "
            )  # Separates x and y
            self.floating_panel_text_widget.window_create(tk.END, window=y_entry)

            angle_output = (
                f"\n   angle: {format(angle, '.0f')}°" if angle is not None else ""
            )
            self.floating_panel_text_widget.insert(tk.END, angle_output)
            self.floating_panel_text_widget.insert(
                tk.END, "\n"
            )  # Newline after each Point

    def wrapper_update_coordinate(self, event, idx: int):
        self.image_points = update_coordinates(
            idx, self.image_points, self.entry_widgets
        )
        self.redraw_image()

    # -------------------------------------------------------------------------------
    # Affine transformation for image display
    # -------------------------------------------------------------------------------

    def reset_transform(self):
        # Restore affine transformation to initialization (scale 1, no movement)
        self.mat_affine = np.eye(3)  # 3x3 unit matrix

    def translate(self, offset_x, offset_y):
        # Shift keybinding
        mat = np.eye(3)  # 3x3 unit matrix
        mat[0, 2] = float(offset_x)
        mat[1, 2] = float(offset_y)

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale(self, scale: float):
        # Scaling
        self.scalre_value = scale
        mat = np.eye(3)  # 3x3 unit matrix
        mat[0, 0] = scale
        mat[1, 1] = scale

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale_at(self, scale: float, cx: float, cy: float):
        # Scale around coordinates (cx, cy)

        # Move to origin
        self.translate(-cx, -cy)
        # Scanling
        self.scale(scale)
        # Return something (that has been moved) to previous place
        self.translate(cx, cy)

    def rotate(self, deg: float):
        # Revolution
        mat = np.eye(3)  # Identity matrix
        mat[0, 0] = math.cos(math.pi * deg / 180)
        mat[1, 0] = math.sin(math.pi * deg / 180)
        mat[0, 1] = -mat[1, 0]
        mat[1, 1] = mat[0, 0]

        self.mat_affine = np.dot(mat, self.mat_affine)

    def rotate_at(self, deg: float, cx: float, cy: float):
        # Rotate around coordinates (cx, cy)

        # Move to origin
        self.translate(-cx, -cy)
        # Revolution
        self.rotate(deg)
        # Return something (that has been moved) to previous place
        self.translate(cx, cy)

    def zoom_fit(self, image_width, image_height):
        # Resize the image

        # Canva size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if (image_width * image_height <= 0) or (canvas_width * canvas_height <= 0):
            return

        # Initialization of affine transformations
        self.reset_transform()

        scale = 1.0
        offsetx = 0.0
        offsety = 0.0

        if (canvas_width * image_height) > (image_width * canvas_height):
            # Widget is horizontal (image is aligned vertically)
            scale = canvas_height / image_height
            # Center half of the excess portion
            offsetx = (canvas_width - image_width * scale) / 2
        else:
            # Widget is vertical (image fits horizontally)
            scale = canvas_width / image_width
            # Center half of the excess portion
            offsety = (canvas_height - image_height * scale) / 2

        # Scaling
        self.scale(scale)
        # Center the too much part
        self.translate(offsetx, offsety)

    # -------------------------------------------------------------------------------
    # Convert point coordinates
    # -------------------------------------------------------------------------------

    def to_image_point(self, x, y):
        # Apply the inverse matrix to change from canvas coordinates to image coordinates
        if self.pil_image is None:
            return []

        self.mat_affine_copy = (
            self.mat_affine.copy()
        )  # Use a copy of the mat_affine or the image rendering will have trouble

        # There's two way to change the coordinates system here
        if self.coordinate_system.get() == "bottom-left":
            # A clean way using matrix and flipping the Y axis and translating the origin
            self.mat_affine_copy[1][2] += (
                self.mat_affine_copy[1][1] * self.pil_image.height
            )  # Adding to the default origin (top left) the height of the image multiplied by the current scale_value
            self.mat_affine_copy[1][1] = -self.mat_affine_copy[1][1]  # Flipping axis

            # And a tricky way using a hardwriting of the y value with the result of a subsatraction of the height of the image and the previous y value
            # This will only do the work for rendering the good y value, but not for the future calculations of the points
            # image_point[1] = abs(self.pil_image.height - image_point[1])

        image_point = np.dot(np.linalg.inv(self.mat_affine_copy), (x, y, 1.0))

        if (
            image_point[0] < 0
            or image_point[1] < 0
            or image_point[0] > self.pil_image.width
            or image_point[1] > self.pil_image.height
        ):
            return None

        return image_point

    def to_canvas_point(self, image_x, image_y):
        # Apply the affine matrix to change from image coordinates to canvas coordinates
        if self.pil_image is None:
            return None

        self.mat_affine_copy = (
            self.mat_affine.copy()
        )  # Use a copy of the mat_affine or the image rendering will have trouble

        # There's two way to change the coordinates system here
        if self.coordinate_system.get() == "bottom-left":
            # A clean way using matrix and flipping the Y axis and translating the origin
            self.mat_affine_copy[1][2] += (
                self.mat_affine_copy[1][1] * self.pil_image.height
            )  # Adding to the default origin (top left) the height of the image multiplied by the current scale_value
            self.mat_affine_copy[1][1] = -self.mat_affine_copy[1][1]  # Flipping axis

        canvas_coords = np.dot(self.mat_affine_copy, (image_x, image_y, 1.0))

        return canvas_coords[0], canvas_coords[1]

    # -------------------------------------------------------------------------------
    # Drawing image
    # -------------------------------------------------------------------------------

    def draw_image(self, pil_image):
        if pil_image is None:
            return

        self.pil_image = pil_image

        # Canva size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Find the affine transformation matrix from canvas to image data
        # (Find the inverse of the affine transformation matrix for display)
        mat_inv = np.linalg.inv(self.mat_affine)

        # Convert a numpy array to a tuple for affine transformation
        affine_inv = (
            mat_inv[0, 0],
            mat_inv[0, 1],
            mat_inv[0, 2],
            mat_inv[1, 0],
            mat_inv[1, 1],
            mat_inv[1, 2],
        )

        # Affine transformation of PIL image data
        dst = self.pil_image.transform(
            (canvas_width, canvas_height),  # Output size
            Image.AFFINE,  # Affine transformation
            affine_inv,  # Affine transformation matrix (output to input transformation matrix)
            Image.NEAREST,  # Interpolation method, nearest neighbor
        )

        im = ImageTk.PhotoImage(image=dst)

        # Clear previous drawing
        self.canvas.delete("all")

        # Image rendering
        self.canvas.create_image(
            0,
            0,  # Image display position (upper left coordinate)
            anchor="nw",  # Anchor, origin at upper left
            image=im,  # Display image data
        )

        self.image = im

        # Lines and point drawing
        if len(self.image_points) > 0:
            # Convert all image points to canvas points
            canvas_points = [
                self.to_canvas_point(x, y) for x, y, _ in self.image_points
            ]
            # Draw lines
            for i in range(len(canvas_points) - 1):
                x1, y1 = canvas_points[i]
                x2, y2 = canvas_points[i + 1]
                self.canvas.create_line(x1, y1, x2, y2, fill="white", width=2)

            # Draw points
            for index, (x, y) in enumerate(canvas_points):
                self.canvas.create_oval(
                    x - 7, y - 7, x + 7, y + 7, fill="white", outline="black"
                )
                self.canvas.create_text(
                    x, y, text=str(index + 1), fill="black", font=("Helvetica", 9)
                )

    def redraw_image(self):
        # Redraw the image
        if self.pil_image is None:
            return
        self.draw_image(self.pil_image)
