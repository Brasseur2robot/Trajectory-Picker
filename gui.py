# Based on this project: https://github.com/ImagingSolution/PythonImageViewer/

import tkinter as tk  # Window creation
from tkinter import ttk, StringVar, filedialog, messagebox  # Open file
from PIL import Image, ImageTk  # Image management
import math  # Revolution calculations
import numpy as np  # Affine transformation matrix operations
import os  # Directory operations
import json  # Json operations

from trajectory_manager import *
import trajectory_manager
from actions_panel import toggle_actions_panel
from menu_bar import create_menu_bar
from info_bar import create_info_bar
from shortcuts import create_default_shortcuts


class GUI(tk.Frame):
    # Import methods from other files (easier to maintain)
    create_menu_bar = create_menu_bar
    create_info_bar = create_info_bar
    toggle_actions_panel = toggle_actions_panel
    create_default_shortcuts = create_default_shortcuts

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

        # Set the coordinate_system based on the existent config
        coordinate_system = self.CONFIG.get("coordinate_system")
        if coordinate_system:
            self.coordinate_system = tk.StringVar(value=coordinate_system)
        else:
            self.coordinate_system = tk.StringVar(value="top-left")
        self.previous_cs = self.coordinate_system.get()

        # Set the angle based on the existent config
        angle = self.CONFIG.get("angle")
        if angle:
            self.angle = tk.IntVar(value=angle)
        else:
            self.angle = tk.IntVar(value=0)

        # Set the orientation based on the existent config
        orientation = self.CONFIG.get("orientation")
        if orientation:
            self.orientation = tk.IntVar(value=orientation)
        else:
            self.orientation = tk.IntVar(value=0)

        # Set the direction based on the existent config and his possible values
        direction = self.CONFIG.get("direction")
        if direction:
            self.direction = tk.IntVar(value=direction)
        else:
            self.direction = tk.IntVar(value=0)

        # Set the action based on the existent config and his possible values
        action = self.CONFIG.get("action")
        if action:
            self.action = tk.IntVar(value=action)
        else:
            self.action = tk.IntVar(value=0)

        # Basic window setting
        self.master.geometry("600x400")

        self.pil_image = None  # Image to display
        self.my_title = "Trajectory Picker"

        # Window title
        self.master.title(self.my_title)

        # Window component & shortcuts
        self.create_menu_bar()
        self.create_info_bar()
        self.create_widget()
        self.create_default_shortcuts()

        # Trajectory points
        self.image_points = []  # list of (x, y) tuples in image coordinates

        # Selected point index
        self.selected_point_idx = None
        self.min_distance = None

        # Preview point
        self.preview_mode = False  # True while we’re waiting for a click
        self.preview_point_coords = (
            None  # Canvas point used for the “transparent” preview
        )

        # Actions panel variable to know if toggle_actions_panel have to display the panel or close it
        # self.actions is the list of possible actions for a point
        self.actions_panel = None
        self.actions = []

        # Variable to toggle symmetry
        self.symmetry = False

        # Initial affine transformation matrix
        self.reset_transform()

        # Render the last opened image
        self.master.after(
            100, self.load_last_opened_image
        )  # TODO: Wait 60ms to make sure everything is loaded, if done too fast it won't show the image // Bug

        # Render the last opened trajectory
        if self.CONFIG.get("last_opened_trajectory"):
            self.load_file(file_path=self.CONFIG.get("last_opened_trajectory"))

    # Close the window
    def menu_quit_clicked(self, event=None):
        self.master.destroy()

    # Define create_widget method
    def create_widget(self):
        # Canvas
        self.canvas = tk.Canvas(
            self.master, background="#262626", bd=0, highlightthickness=0
        )
        self.canvas.pack(
            expand=True, fill=tk.BOTH
        )  # Same as Dock.Fill in both of these

        # Canvas / Menu separator
        self.separator_cm = ttk.Frame(self.canvas, style="primary.TFrame", height="2")
        self.separator_cm.pack(side="top", fill="x")

        # Canvas / Status bar separator
        self.separator_csb = ttk.Frame(self.canvas, style="primary.TFrame", height="2")
        self.separator_csb.pack(side="bottom", fill="x")

        # Create the floating panel
        self.create_floating_panel()

    # Define the floating panel
    def create_floating_panel(self):
        self.floating_panel_width = 250
        # Create a frame inside the canvas
        self.floating_panel = tk.Toplevel(self.master)
        self.floating_panel.minsize(width=self.floating_panel_width, height=300)
        self.floating_panel.overrideredirect(True)  # Remove window decorations
        self.floating_panel.geometry("100x300+100+100")
        self.floating_panel.configure(bg="#262626")

        # Create a title bar
        self.floating_panel_titlebar = ttk.Frame(self.floating_panel)
        self.floating_panel_titlebar.pack(fill=tk.X)

        self.floating_panel_titlebar.pack_propagate(
            False
        )  # Disable resizing based on child widgets
        self.floating_panel_titlebar.config(
            height=20
        )  # Set the height of the titlebar, can't do it if pack is not desactivate

        self.floating_panel_title_label = ttk.Label(
            self.floating_panel_titlebar,
            text="Floating Panel",
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
        self.floating_panel_content = ttk.Frame(self.floating_panel)
        self.floating_panel_content.pack(expand=True, fill=tk.BOTH)

        # Titlebar / Panel content separator
        self.separator_cpc = ttk.Frame(
            self.floating_panel_content, style="primary.TFrame", height="2"
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

        """ Old config
        # Create a list of Entry widgets to edit coordinates
        self.entry_widgets = []"""

        # Create a list of Checkbox var to delete points
        self.checkbox_del_widgets = []

        # Export & delete buttons
        ttk.Button(
            self.floating_panel_content,
            text="Delete point(s)",
            command=self.delete_point,
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
                    trajectory_manager.coordinates_to_json(
                        self.image_points,
                        self.actions,
                        file_path,
                        self.angle.get(),
                        self.orientation.get(),
                        self.direction.get(),
                        self.action.get(),
                    )
                    self.save_config("last_opened_trajectory", file_path)

                elif file_extension == ".csv":
                    trajectory_manager.coordinates_to_csv(
                        self.image_points,
                        file_path,
                        self.angle.get(),
                        self.orientation.get(),
                        self.direction.get(),
                        self.action.get(),
                    )
                else:
                    messagebox.showerror("Unsupported File", "File type not supported.")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {e}")

    def load_file(self, event=None, file_path=None):
        # Load the trajectory file chosen by the user

        if file_path is None:
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
                    loaded_content = trajectory_manager.json_to_coordinates(file_path)
                    if loaded_content is not None:
                        self.image_points, self.actions = (
                            loaded_content[0],
                            loaded_content[1],
                        )

                    else:
                        return

                    self.update_fp()
                    self.redraw_image()

                elif file_extension == ".csv":
                    self.image_points = trajectory_manager.csv_to_coordinates(file_path)
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

    def wrapper_coordinate_system(self):
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

        elif self.previous_cs != self.coordinate_system.get():
            self.coordinate_system.set(self.previous_cs)

    def wrapper_angle(self):
        # Wrapper to save the angle value in the CONFIG_FILE and update_fp
        self.save_config("angle", self.angle.get())
        self.update_fp()

    def wrapper_orientation(self):
        # Wrapper to save the orientation value in the CONFIG_FILE and update_fp
        self.save_config("orientation", self.orientation.get())
        self.update_fp()

    def wrapper_direction(self):
        """Wrapper to save the orientation value in the CONFIG_FILE and update_fp"""

        self.save_config("direction", self.direction.get())
        self.update_fp()

    def wrapper_action(self):
        """Wrapper to save the action value in the CONFIG_FILE and update_fp"""

        self.save_config("action", self.action.get())
        self.update_fp()

    # -------------------------------------------------------------------------------
    # Define mouse & keyboard event
    # -------------------------------------------------------------------------------

    def set_move_image(self, event):
        # Right mouse button pressed / set the current coordinates to move the image
        self.__old_event = event

    def delete_point(self, event=None, selection_mode=False):
        # Middle right mouse button pressed / delete latest point
        if event is None:
            points_to_pop = [
                i
                for i, checkbox_value in enumerate(self.checkbox_del_widgets)
                if checkbox_value.get() == 1
            ]
            for index in reversed(
                points_to_pop
            ):  # Reverse it to not delete the wrong ones
                self.image_points.pop(index)
                self.update_fp()  # Update the content of the floating panel
                self.redraw_image()  # Update the canvas

        else:
            if self.image_points and self.selected_point_idx is not None:
                self.image_points.pop(self.selected_point_idx)
                self.selected_point_idx = None
                self.update_fp()
                self.redraw_image()

            elif self.image_points and selection_mode is False:
                self.image_points.pop()  # Remove the last point
                self.update_fp()  # Update the content of the floating panel
                self.redraw_image()  # Update the canvas

    def select_point(self, event):
        selection_radius = 30

        self.selected_point_idx = None

        if self.image_points is not None:
            for idx, point in enumerate(self.image_points):
                x, y = point[0], point[1]
                image_point = self.to_image_point(event.x, event.y)
                if image_point is not None:
                    x_clicked, y_cliked = image_point[0], image_point[1]
                else:
                    return

                distance = math.sqrt((x_clicked - x) ** 2 + (y_cliked - y) ** 2)

                if distance <= selection_radius:
                    if self.min_distance is None or distance < self.min_distance:
                        self.min_distance = distance
                        self.selected_point_idx = idx

            self.redraw_image()
            self.min_distance = None

    """ Old config
    def create_point(self, event=None):
        # Control p keys pressed / create a point
        if self.pil_image is None:
            return
        self.preview_point()
        else:
            image_point = self.to_image_point(event.x, event.y)
            if image_point is not None:
                self.image_points.append((image_point[0], image_point[1], None))
                self.image_points = trajectory_manager.calculate_angle(
                    self.image_points
                )
                self.update_fp()  # Update the content of the floating panel
                self.redraw_image()"""

    def create_preview(self, event=None):
        # Control p keys pressed / create a preview point that can be added to the canva on click
        # "Preview" the point that will be created

        if self.pil_image is None:
            return

        if self.preview_mode:  # If preview is already active exit the function
            return

        self.preview_mode = True

        self.preview_motion_bind = self.canvas.bind("<Motion>", self.move_preview)
        self.preview_button_bind = self.canvas.bind("<Button-1>", self.create_point)
        self.preview_escape_bind = self.master.bind("<Escape>", self.leave_preview)

        self.move_preview(event)

    def move_preview(self, event):
        # Create and (re)draw the transparent preview point
        if not self.preview_mode:
            return

        preview_point_coords = self.to_image_point(event.x, event.y)
        if preview_point_coords is not None:
            self.preview_point_coords = [
                [
                    preview_point_coords[0],
                    preview_point_coords[1],
                    None,
                    None,
                    None,
                    None,
                ]
            ]
            self.preview_point_coords = trajectory_manager.coordinates_to_float64(
                self.preview_point_coords
            )
            self.redraw_image()

    def create_point(self, event):
        self.image_points.append(self.preview_point_coords[0])
        self.image_points = trajectory_manager.calculate_angle(self.image_points)
        self.preview_mode = False
        self.preview_point_coords = None
        self.master.unbind("<Button-1>", self.select_point_bind)
        self.update_fp()
        self.redraw_image()
        self.canvas.unbind("<Motion>", self.preview_motion_bind)
        self.canvas.unbind("<Button-1>", self.preview_button_bind)
        self.master.unbind("<Escape>", self.preview_escape_bind)
        self.select_point_bind = self.master.bind("<Button-1>", self.select_point)
        self.master.bind(
            "<Escape>",
            lambda event, selection_mode=True: self.delete_point(event, selection_mode),
        )
        return

    def leave_preview(self, event):
        self.preview_mode = False
        self.preview_point_coords = None
        self.update_fp()
        self.redraw_image()
        self.canvas.unbind("<Motion>", self.preview_motion_bind)
        self.canvas.unbind("<Button-1>", self.preview_button_bind)
        self.canvas.unbind("<Escape>", self.preview_escape_bind)
        self.master.bind(
            "<Escape>",
            lambda event, selection_mode=True: self.delete_point(event, selection_mode),
        )
        return

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
        self.checkbox_del_widgets.clear()
        # self.entry_widgets.clear()
        self.floating_panel_text_widget.delete(1.0, tk.END)

        # Insert updated coordinates
        for i, (x, y, angle, orientation, direction, action) in enumerate(
            self.image_points
        ):
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
            self.checkbox_del_widgets.insert(i, check_var)

            # Adding the checkbox after the point name
            self.floating_panel_text_widget.window_create(tk.END, window=checkbox)

            self.floating_panel_text_widget.insert(tk.END, "\n   x: ")

            # Create Entry widgets for x and y values
            x_string = StringVar()
            x_entry = tk.Entry(
                self.floating_panel_text_widget,
                width=5,
                bg="#4b4b4b",
                fg="white",
                relief=tk.FLAT,
                textvariable=x_string,
            )
            x_entry.insert(
                0, format(x, ".0f") if x else ""
            )  # Set the initial value to the current x rounded
            x_string.trace_add(
                "write",
                lambda *args, new_x=x_string, idx=i: self.coordinate_entry_change(
                    new_x=new_x.get(), idx=idx
                ),
            )
            # self.entry_widgets.append(x_entry)

            y_string = StringVar()
            y_entry = tk.Entry(
                self.floating_panel_text_widget,
                width=5,
                bg="#4b4b4b",
                fg="white",
                relief=tk.FLAT,
                textvariable=y_string,
            )
            y_entry.insert(
                0, format(y, ".0f") if y else ""
            )  # Set the initial value to the current y rounded
            y_string.trace_add(
                "write",
                lambda *args, new_y=y_string, idx=i: self.coordinate_entry_change(
                    new_y=new_y.get(), idx=idx
                ),
            )
            # self.entry_widgets.append(y_entry)

            # Add the Entry widget (x, y and orientation), direction drop-down menu and the angle to the Text widget
            self.floating_panel_text_widget.window_create(tk.END, window=x_entry)
            self.floating_panel_text_widget.insert(
                tk.END, "\n   y: "
            )  # Separates x and y
            self.floating_panel_text_widget.window_create(tk.END, window=y_entry)

            if self.orientation.get():
                orientation_string = StringVar()
                orientation_entry = tk.Entry(
                    self.floating_panel_text_widget,
                    width=5,
                    bg="#4b4b4b",
                    fg="white",
                    relief=tk.FLAT,
                    textvariable=orientation_string,
                )
                orientation_string.trace_add(
                    "write",
                    lambda *args,
                    new_orientation=orientation_string,
                    idx=i: self.orientation_entry_change(new_orientation.get(), idx),
                )
                orientation_entry.insert(
                    0, format(orientation, ".0f") if orientation else ""
                )  # Set the initial orientation, empty if not set

                # self.entry_widgets.append(orientation_entry)
                self.floating_panel_text_widget.insert(tk.END, "\n   orientation: ")
                self.floating_panel_text_widget.window_create(
                    tk.END, window=orientation_entry
                )

            if self.direction.get():
                direction_string = StringVar()
                direction_entry = tk.Entry(
                    self.floating_panel_text_widget,
                    width=5,
                    bg="#4b4b4b",
                    fg="white",
                    relief=tk.FLAT,
                    textvariable=direction_string,
                )
                direction_string.trace_add(
                    "write",
                    lambda *args,
                    new_direction=direction_string,
                    idx=i: self.direction_entry_change(new_direction.get(), idx),
                )
                """Old config
                direction_entry.bind(
                    "<FocusOut>",
                    lambda event, idx=i: self.wrapper_update_direction(event, idx),
                )"""
                direction_entry.insert(
                    0, direction if direction else ""
                )  # Set the initial direction, empty if not set

                # self.entry_widgets.append(direction_entry)
                self.floating_panel_text_widget.insert(tk.END, "\n   direction: ")
                self.floating_panel_text_widget.window_create(
                    tk.END, window=direction_entry
                )

            if self.action.get():
                action_menubutton = ttk.Menubutton(
                    self.floating_panel_text_widget,
                    text="Choose action",
                )
                action_menu = tk.Menu(
                    action_menubutton,
                )
                action_menubutton.configure(menu=action_menu)

                choices = {}

                for action in self.actions:
                    if self.image_points is None:
                        return

                    if (
                        self.image_points[i][5] is not None
                        and action in self.image_points[i][5]
                    ):
                        choices[action] = tk.IntVar(value=1)
                        label = (
                            f"({self.image_points[i][5].index(action) + 1}): {action}"
                        )

                    else:
                        choices[action] = tk.IntVar(value=0)
                        label = action

                    action_menu.add_checkbutton(
                        label=label,
                        variable=choices[action],
                        onvalue=1,
                        offvalue=0,
                        command=lambda new_choices=choices,
                        idx=i: self.action_checkbutton_change(new_choices, idx),
                    )

                self.floating_panel_text_widget.insert(tk.END, "\n   action(s): ")
                self.floating_panel_text_widget.window_create(
                    tk.END, window=action_menubutton
                )

            if self.angle.get():
                angle_output = (
                    f"\n   angle: {format(angle, '.0f')}°" if angle is not None else ""
                )
                self.floating_panel_text_widget.insert(tk.END, angle_output)

            self.floating_panel_text_widget.insert(
                tk.END, "\n"
            )  # Newline after each Point

    def coordinate_entry_change(self, new_x=None, new_y=None, idx: int = -1):
        """Update the x or y coordinate based on the content of the x_entry and the y_entry widgets"""

        new_coordinate = (
            [0, new_x]
            if new_x is not None
            else ([1, new_y] if new_y is not None else None)
        )

        if idx == -1 or new_coordinate is None:
            return

        if new_coordinate[1] == "":
            self.image_points = trajectory_manager.update_trajectory(
                self.image_points, idx, new_coordinate[0], new_coordinate[1]
            )
            self.update_fp()
            return

        try:
            new_coordinate[1] = np.float64(new_coordinate[1])
        except Exception as e:
            messagebox.showerror("Error", "New coordinate must be number")
            self.update_fp()
            return

        if (
            new_coordinate[0] == 0
            and not (0 <= new_coordinate[1] <= self.pil_image.width)
        ) or (
            new_coordinate[0] == 1
            and not (0 <= new_coordinate[1] <= self.pil_image.height)
        ):
            messagebox.showerror(
                "Error", "Coordinates cannot be outside the dimensions of the image"
            )
            self.update_fp()
            return

        if not isinstance(new_coordinate[1], np.float64):
            return

        self.image_points = trajectory_manager.update_trajectory(
            self.image_points, idx, new_coordinate[0], new_coordinate[1]
        )

        self.redraw_image()

    def orientation_entry_change(self, new_orientation, idx: int):
        """Update the orientation based on the content of the orientation entry widget"""

        if new_orientation == "" or new_orientation == "-":
            self.image_points = trajectory_manager.update_trajectory(
                self.image_points, idx, 3, None
            )
            return

        try:
            new_orientation = float(new_orientation)
        except Exception as e:
            messagebox.showerror("Error", "Orientation must be number")
            self.update_fp()
            return

        if not (-180 <= new_orientation <= 180):
            messagebox.showerror(
                "Error", "Orientation must be a value between -180 and 180"
            )
            self.update_fp()
            return

        self.image_points = trajectory_manager.update_trajectory(
            self.image_points, idx, 3, new_orientation
        )
        # self.redraw_image()

    def direction_entry_change(self, new_direction, idx):
        """Update the direction based on the content of the orientation entry widget"""

        self.image_points = trajectory_manager.update_trajectory(
            self.image_points, idx, 4, new_direction
        )
        self.redraw_image()

    def action_checkbutton_change(self, choices: dict, idx: int = -1):
        """Update the actions of a point based on the content of checkbutton widget"""

        if self.image_points is None:
            return
        current_actions = self.image_points[idx][5]

        for name, var in choices.items():
            if current_actions is None:
                current_actions = []

            if var.get() == 1:
                if name not in current_actions:
                    current_actions.append(name)
                    new_actions = current_actions
                    self.image_points = trajectory_manager.update_trajectory(
                        self.image_points, idx, 5, new_actions
                    )
                    self.update_fp()

            elif var.get() == 0:
                if name in current_actions:
                    current_actions.remove(name)
                    new_actions = current_actions
                    if len(new_actions) == 0:
                        new_actions = None
                    self.image_points = trajectory_manager.update_trajectory(
                        self.image_points, idx, 5, new_actions
                    )
                    self.update_fp()

    def toggle_symmetry(self):
        """Change the symmetry based on the value of the checkbutton from the trajectory menu"""
        if self.image_points is None:
            return

        for idx, point in enumerate(self.image_points):
            old_x = point[0]
            new_x = np.float64(self.pil_image.width - old_x)
            if isinstance(new_x, np.float64):
                self.image_points = trajectory_manager.update_trajectory(
                    self.image_points, idx, 0, new_x
                )
            else:
                return

        self.update_fp()
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

        # Preview point drawing
        if self.preview_point_coords:
            index = len(self.image_points)
            preview_point_coords = [
                self.to_canvas_point(x, y)
                for x, y, _, _, _, _ in self.preview_point_coords
            ]
            for x, y in preview_point_coords:
                self.canvas.create_oval(
                    x - 7,
                    y - 7,
                    x + 7,
                    y + 7,
                    fill="white",
                    outline="black",
                    stipple="gray50",
                )
                self.canvas.create_text(
                    x, y, text=str(index + 1), fill="black", font=("Helvetica", 9)
                )

        # Lines and point drawing
        if len(self.image_points) > 0:
            # Convert all image points to canvas points
            canvas_points = [
                self.to_canvas_point(x, y) for x, y, _, _, _, _ in self.image_points
            ]
            # Draw lines
            for i in range(len(canvas_points) - 1):
                x1, y1 = canvas_points[i]
                x2, y2 = canvas_points[i + 1]
                self.canvas.create_line(x1, y1, x2, y2, fill="white", width=2)

            # Draw points
            for index, (x, y) in enumerate(canvas_points):
                if index == self.selected_point_idx:
                    self.canvas.create_oval(
                        x - 7,
                        y - 7,
                        x + 7,
                        y + 7,
                        fill="red",
                        outline="black",
                        tags=("point",),
                    )
                else:
                    self.canvas.create_oval(
                        x - 7,
                        y - 7,
                        x + 7,
                        y + 7,
                        fill="white",
                        outline="black",
                        tags=("point",),
                    )
                self.canvas.create_text(
                    x, y, text=str(index + 1), fill="black", font=("Helvetica", 9)
                )
                # TODO: self.points.append(point)

    def redraw_image(self):
        # Redraw the image
        if self.pil_image is None:
            return
        self.draw_image(self.pil_image)
