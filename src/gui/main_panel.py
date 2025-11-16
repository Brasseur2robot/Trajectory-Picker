# Based on this project: https://github.com/ImagingSolution/PythonImageViewer/

import tkinter as tk  # Window creation
from tkinter import image_names, ttk, StringVar, filedialog, messagebox  # Open file
from PIL import Image, ImageTk  # Image management
import math  # Revolution calculations
import numpy as np  # Affine transformation matrix operations
import os  # Directory operations
import json  # Json operations

import trajectory_manager

from .actions_panel import toggle_actions_panel
from .canvas import create_canvas
from .info_bar import create_info_bar
from .menu_bar import (
    create_menu_bar,
    toggle_wea_checkbutton,
    toggle_export_action_checkbutton,
    toggle_export_action_command,
)
from .shortcuts import create_default_shortcuts
from .trajectory_panel import toggle_trajectory_panel, update_trajectory_panel_content


class GUI(tk.Frame):
    # Import methods from other files (easier to maintain)
    toggle_actions_panel = toggle_actions_panel
    create_canvas = create_canvas
    create_info_bar = create_info_bar
    create_menu_bar = create_menu_bar
    toggle_wea_checkbutton = toggle_wea_checkbutton
    toggle_export_action_checkbutton = toggle_export_action_checkbutton
    toggle_export_action_command = toggle_export_action_command
    create_default_shortcuts = create_default_shortcuts
    toggle_trajectory_panel = toggle_trajectory_panel
    update_trajectory_panel_content = update_trajectory_panel_content

    def __init__(
        self,
        master=None,
        CONFIG_FILE=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../../config.json"
        ),
    ):
        super().__init__(master)

        self.CONFIG_FILE = CONFIG_FILE

        # Config
        self.CONFIG = (
            self.load_json_file(self.CONFIG_FILE)
            if self.load_json_file(self.CONFIG_FILE)
            else {}
        )

        # Set the self.vars to the content of the config
        self.assign_config()

        # Basic window setting
        self.master.geometry("600x400")

        self.pil_image = None  # Image to display
        self.my_title = "Trajectory Picker"

        # Window title
        self.master.title(self.my_title)

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

        # Trajectory panel variable to know if toggle_trajectory_panel have to display the panel or close it
        self.trajectory_panel = None

        # Variable to toggle symmetry
        self.symmetry = False

        # Variable to get which point to delete
        self.checkbox_del_widgets = []

        # Wait for the basic generation of the GUI before loading other widgets
        self.master.update()

        # Window component & shortcuts
        self.create_menu_bar()
        self.create_info_bar()
        self.create_canvas()
        self.create_default_shortcuts()

    # Close the window
    def menu_quit_clicked(self, event=None):
        self.master.destroy()

    # Set image in the canvas
    def set_image(self, filename):
        if not filename:
            return
        # Open with PIL.Image
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

    def save_file(self, event=None, data_type: str | None = None) -> None:
        """Open a file picker to save the trajectory or actions to a file depending of the data_type value

        Args:
            self (GUI): the GUI object that is mainuplated
            event (tkinter.Event): set to None here because not used
            data_type (str | None): define which data is manipulated and how to save it
        """

        if data_type is None:
            return

        if data_type == "trajectory" and not self.image_points:
            messagebox.showwarning("No data", "There is no trajectory to save.")
            return

        elif data_type == "actions" and not self.actions:
            messagebox.showwarning("No data", "There are no actions to save.")
            return

        file_path = filedialog.asksaveasfilename(
            title=f"Save {type} file",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )

        if file_path:
            file_extension = os.path.splitext(file_path)[-1].lower()
            try:
                if file_extension == ".json":
                    if data_type == "trajectory":
                        json_trajectory = trajectory_manager.coordinates_to_json(
                            self.image_points,
                            self.actions,
                            self.angle.get(),
                            self.orientation.get(),
                            self.direction.get(),
                            self.action.get(),
                            self.wea.get(),
                        )
                        self.save_json_file(file_path, json_trajectory)
                        self.save_config("last_opened_trajectory", file_path)

                    elif data_type == "actions":
                        json_actions = trajectory_manager.format_actions_to_json(
                            self.actions
                        )
                        self.save_json_file(file_path, json_actions)
                        self.save_config("last_opened_actions", file_path)

                # elif file_extension == ".csv":
                #     trajectory_manager.coordinates_to_csv(
                #         self.image_points,
                #         file_path,
                #         self.angle.get(),
                #         self.orientation.get(),
                #         self.direction.get(),
                #         self.action.get(),
                #     )
                else:
                    messagebox.showerror("Unsupported File", "File type not supported.")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {e}")

    def load_file(
        self, event=None, file_path: str | None = None, content_type: str = ""
    ):
        """Load the trajectory or the actions file chosen by the user depending of the content_type

        Args:
            self (GUI): the GUI object that is manipulated
            event (tkinter.Event): set to None here because not used
            file_path (str | None): the file_path to open the file, if None the program open a file picker
            content_type (str): a str that represents the type of content to know how to handle the content
        """

        if not self.pil_image and content_type == "trajectory":
            messagebox.showinfo(
                "No image",
                "You don't have any image set so the trajectory won't be rendered, you need to pick an image first",
            )
            return

        if file_path is None:
            file_path = filedialog.askopenfilename(
                filetypes=[
                    # ("JSON & CSV", ".json .csv"),
                    ("JSON", ".json"),
                    # ("CSV", ".csv"),
                ],
                initialdir=os.getcwd(),  # Current directory
            )

        if file_path:
            file_extension = os.path.splitext(file_path)[-1].lower()

            try:
                if file_extension == ".json":
                    json_data = self.load_json_file(file_path)

                    # Actions type file
                    if content_type == "actions":
                        response = "yes"
                        if len(self.actions) != 0:
                            response = messagebox.askquestion(
                                "Actions",
                                "You have already some actions that are defined, would you like to overwrite them ?",
                            )

                        if response == "yes":
                            self.actions = trajectory_manager.format_json_to_actions(
                                json_data
                            )
                            self.save_config("last_opened_actions", file_path)

                    # Trajectory type file (could also have the actions inside the same file)
                    elif content_type == "trajectory":
                        # Actions & trajectory in the same file
                        if isinstance(json_data[1], list):
                            response = "yes"

                            if len(self.actions) != 0 or len(self.image_points) != 0:
                                response = messagebox.askquestion(
                                    "Trajectory & actions",
                                    "You have already some actions or trajectory that are defined, would you like to overwrite them ?",
                                )

                            if response == "yes":
                                self.actions = (
                                    trajectory_manager.format_json_to_actions(
                                        json_data[0]
                                    )
                                )

                                self.image_points = self.reload_config(
                                    trajectory_manager.format_json_to_trajectory(
                                        json_data[1]
                                    )
                                )

                                self.save_config("last_opened_trajectory", file_path)

                        # Only the trajectory inside the file
                        elif isinstance(json_data[0], dict):
                            response = "yes"

                            if len(self.image_points) != 0:
                                response = messagebox.askquestion(
                                    "Trajectory",
                                    "You have already some trajectory that is defined, would you like to overwrite it ?",
                                )

                            if response == "yes":
                                self.image_points = self.reload_config(
                                    trajectory_manager.format_json_to_trajectory(
                                        json_data
                                    )
                                )
                                self.save_config("last_opened_trajectory", file_path)

                        else:
                            messagebox.showerror(
                                "Importing error",
                                "An error has occured during the importation of the file",
                            )
                            return

                    self.redraw_image()
                    if self.trajectory_panel is not None:
                        self.update_trajectory_panel_content()

                # elif file_extension == ".csv":
                #     self.image_points = trajectory_manager.csv_to_coordinates(file_path)
                #     self.redraw_image()

                else:
                    messagebox.showerror("Unsupported File", "File type not supported.")

            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {e}")

    def reload_config(self, trajectory):
        def _reload_menu(menu, menu_index: int):
            # Tricks to reload the checkmark on the menu_index options of the menu
            # Unset the command to not execute it, change the checkmark and reset the command

            cmd = menu.entrycget(menu_index, "command")
            menu.entryconfig(menu_index, command="")
            menu.invoke(menu_index)
            menu.entryconfig(menu_index, command=cmd)

        # Can't pass inside the condition for wea and action two times, or it will break the menu
        action_flag = False

        for point in trajectory:
            if point[2] is not None and not self.angle.get():
                self.save_config("angle", 1)
                _reload_menu(self.trajectory_menu, 2)

            # TODO: check index for last point, don't have to check
            elif point[2] is None and self.angle.get():
                trajectory = trajectory_manager.calculate_angle(trajectory)

            if point[3] is not None and not self.orientation.get():
                self.save_config("orientation", 1)
                _reload_menu(self.trajectory_menu, 3)

            if point[4] is not None and not self.direction.get():
                self.save_config("direction", 1)
                _reload_menu(self.trajectory_menu, 4)

            # if point[6] and not self.wea.get() and not action_flag:
            #     action_flag = True
            #     print("wea")
            #     self.save_config("action", 1)
            #     self.save_config("wea", 1)
            #     _reload_menu(self.action_sub_menu, 0)
            #     _reload_menu(self.action_sub_menu, 1)
            #     self.toggle_wea_checkbutton(True)
            #     self.toggle_export_action_checkbutton(True)
            #
            # elif self.actions and not self.action.get() and not action_flag:
            #     action_flag = True
            #     print("action")
            #     self.save_config("action", 1)
            #     _reload_menu(self.action_sub_menu, 0)
            #     self.toggle_wea_checkbutton(True)
            #     self.toggle_export_action_checkbutton(True)

        return trajectory

    def save_config(self, key, value):
        # Save the config inside .json file based on a key / value system

        json_config = self.load_json_file(self.CONFIG_FILE)

        if json_config is not None:
            # Update with new key / value pair
            json_config[key] = value

            self.save_json_file(self.CONFIG_FILE, json_config)

        else:
            json_config = {key: value}
            self.save_json_file(self.CONFIG_FILE, json_config)

    def assign_config(self) -> None:
        """Set all the differents object vars to the value that are saved in the config

        Args:
            self (GUI): the GUI object that is manipulated
        """

        self.coordinate_system = tk.StringVar(
            value=self.CONFIG.get("coordinate_system", "top-left")
        )
        self.previous_cs = self.coordinate_system.get()

        self.angle = tk.IntVar(value=self.CONFIG.get("angle", 0))
        self.orientation = tk.IntVar(value=self.CONFIG.get("orientation", 0))
        self.direction = tk.IntVar(value=self.CONFIG.get("direction", 0))
        self.action = tk.IntVar(value=self.CONFIG.get("action", 0))
        self.wea = tk.IntVar(value=self.CONFIG.get("wea", 0))
        self.export_action = tk.IntVar(value=self.CONFIG.get("export_action", 0))

        return None

    def load_last_opened_image(self, event=None):
        # Load the last opened image based on the content of the config file
        last_image = self.CONFIG.get("last_opened_image")
        if last_image and os.path.exists(last_image):
            self.set_image(last_image)

            # Render the last opened / saved trajectory
            if self.CONFIG.get("last_opened_trajectory"):
                self.load_file(
                    file_path=self.CONFIG.get("last_opened_trajectory"),
                    content_type="trajectory",
                )

            # Load the last opened / saved actions
            if (
                not self.actions
                and self.CONFIG.get("last_opened_actions")
                and self.action.get()
            ):
                self.load_file(
                    file_path=self.CONFIG.get("last_opened_actions"),
                    content_type="actions",
                )

        self.toggle_trajectory_panel()

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

    def save_json_file(self, file_path, content):
        with open(file_path, mode="w") as file:
            return json.dump(content, file, indent=4)

    def load_json_file(self, file_path) -> None | list:
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(file_path, "r", encoding="utf-8") as json_file:
                    return json.load(json_file)

            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {e}")
                return None

        return None

    def wrapper_options(self, option_name: str, option_tk_var: tk.IntVar):
        """Save the option value inside the config file and update the content of the trajectory_panel

        Args:
            option_name (str): the option the program is manipulating
            option_tk_var (tk.IntVar): the tk object from which the value will be retrieve to save the option value
        """

        response = "yes"

        # As the coordinate_system can change a lot of things there is special treatment for it
        if option_name == "coordinate_system":
            if self.previous_cs == self.coordinate_system.get():
                return

            if self.image_points:
                response = messagebox.askquestion(
                    "Coordinate system",
                    "You already have points in your trajectory set with a specific coordinate system. Setting another one can broke your trajectory. Do you want to continue ?",
                )

            if response == "yes":
                self.previous_cs = self.coordinate_system.get()

            elif self.previous_cs != self.coordinate_system.get():
                self.coordinate_system.set(self.previous_cs)

        # Calculate the angles values if it was not done before
        elif option_name == "angle":
            if self.image_points and self.image_points[0][2] is None:
                self.image_points = trajectory_manager.calculate_angle(
                    self.image_points
                )

        # Rendering the wea_checkbutton & the toggle_export_action_checkbutton only if the action option is used
        elif option_name == "action":
            if option_tk_var.get():
                self.toggle_wea_checkbutton(True)
                self.toggle_export_action_checkbutton(True)

                if self.export_action.get():
                    self.toggle_export_action_command(True)

            else:
                self.toggle_wea_checkbutton(False)
                self.toggle_export_action_checkbutton(False)

                if self.export_action.get():
                    self.toggle_export_action_command(False)

        # Render the export_action commands inside the file_menu
        elif option_name == "export_action":
            if option_tk_var.get():
                self.toggle_export_action_command(True)
            else:
                self.toggle_export_action_command(False)

        # Basic treatment for all options
        if response == "yes":
            self.save_config(option_name, option_tk_var.get())
            self.update_trajectory_panel_content()

    # -------------------------------------------------------------------------------
    # Define mouse & keyboard event
    # -------------------------------------------------------------------------------

    def set_move_image(self, event):
        # Right mouse button pressed / set the current coordinates to move the image
        self.__old_event = event

    def delete_point(self, event=None, selection_mode=False):
        # Middle right mouse button pressed / delete latest point
        if event is None and self.image_points is not None:
            points_to_pop = [
                i
                for i, checkbox_value in enumerate(self.checkbox_del_widgets)
                if checkbox_value.get() == 1
            ]
            points_to_pop.reverse()  # Reverse it to not delete the wrong ones
            for index in points_to_pop:
                self.image_points.pop(index)

            self.update_trajectory_panel_content(
                points_to_pop
            )  # Update the content of the floating panel
            self.redraw_image()  # Update the new trajectory drawing

        else:
            # Delete the selected point
            if self.image_points and self.selected_point_idx is not None:
                self.image_points.pop(self.selected_point_idx)
                self.update_trajectory_panel_content(self.selected_point_idx)
                self.selected_point_idx = None
                self.redraw_image()  # Update the new trajectory drawing

            elif self.image_points and selection_mode is False:
                self.image_points.pop()  # Remove the last point
                self.update_trajectory_panel_content(len(self.image_points))
                self.redraw_image()  # Update the new trajectory drawing

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
        self.update_trajectory_panel_content()
        self.redraw_image()
        self.canvas.unbind("<Motion>", self.preview_motion_bind)
        self.canvas.unbind("<Button-1>", self.preview_button_bind)
        self.master.unbind("<Escape>", self.preview_escape_bind)
        self.select_point_bind = self.master.bind("<Button-1>", self.select_point)

        return

    def leave_preview(self, event):
        self.preview_mode = False
        self.preview_point_coords = None
        self.update_trajectory_panel_content()
        self.redraw_image()
        self.canvas.unbind("<Motion>", self.preview_motion_bind)
        self.canvas.unbind("<Button-1>", self.preview_button_bind)
        self.canvas.unbind("<Escape>", self.preview_escape_bind)

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
    # Data floating panel management -> Point data
    # -------------------------------------------------------------------------------

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

        self.update_trajectory_panel_content()
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
                for x, y, _, _, _, _, _ in self.preview_point_coords
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
                self.to_canvas_point(x, y) for x, y, _, _, _, _, _ in self.image_points
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

    def redraw_image(self):
        # Redraw the image
        if self.pil_image is None:
            return
        self.draw_image(self.pil_image)
