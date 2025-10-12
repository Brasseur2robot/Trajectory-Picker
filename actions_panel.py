import tkinter as tk
from tkinter import ttk

MIN_HEIGHT = 300
MIN_WIDTH = 300


def toggle_actions_panel(self, event=None):
    """Create or delete the actions_panel depending if it exist"""

    # Create the panel if it don't exist
    if self.actions_panel is None or not self.actions_panel.winfo_exists():
        # Panel creation
        self.actions_panel = tk.Toplevel(self.master)

        self.actions_panel.title("Actions panel")
        self.actions_panel.overrideredirect(True)
        self.actions_panel.minsize(height=MIN_HEIGHT, width=MIN_WIDTH)
        self.actions_panel.configure(bg="#262626")

        # Main frame (everything is inside it)
        main_frame = ttk.Frame(self.actions_panel)
        main_frame.pack(fill=tk.X)

        # Titlebar
        titlebar_frame = ttk.Frame(main_frame)
        titlebar_frame.pack(fill=tk.X)

        titlebar_frame.pack_propagate(False)  # Disable resizing based on child widgets
        titlebar_frame.config(height=20)

        title_label = ttk.Label(
            titlebar_frame,
            text="Actions Panel",
        )
        title_label.pack(side=tk.LEFT, padx=5)

        # Titlebar / content separator
        separator_frame = ttk.Frame(main_frame, style="primary.TFrame", height=2)
        separator_frame.pack(fill=tk.X)

        # Content inside the panel
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(expand=True, fill=tk.BOTH)

        # A grid is used here to separate the scrollable zone (row 0 - scroll_frame) from the button zone (row 1 - button_frame)
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=1)

        # Defining the frame where scrollable content will be displayed
        scroll_frame = ttk.Frame(content_frame)
        scroll_frame.grid(row=0, column=0, sticky="nsew")

        # Creating a canvas to use ttk.Scrollbar inside
        canvas = tk.Canvas(scroll_frame)
        canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Linking the scrollbar to the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Function and binding to use the mousewheel for scrolling
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        # Need to be tested for windows
        # def _on_mousewheel(event):
        #     canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        #
        # canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Content inside the canvas where the labels and entries will be displayed
        self.form_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.form_frame, anchor="nw")

        # Create the form for each actions that already exist + 1 that is empty
        self.actions_form = []
        for i in range(len(self.actions) + 1):
            if i == len(self.actions):
                _create_form(self)
            else:
                _create_form(self, self.actions[i], i)

        # Frame without scroll for the close button
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=1, column=0, pady=10)

        # Close button
        ttk.Button(
            button_frame,
            text="Close panel",
            command=self.actions_panel.destroy,
        ).pack()

    # Delete the panel if it exist
    else:
        self.actions_panel.destroy()


def _remove_form(self, event=None):
    """Remove the action from the cleared form and recreate all form from the actions list"""

    index_to_del = None

    # Search for the action to remove
    for i in range(len(self.actions_form)):
        if i != len(self.actions_form) - 1:
            if self.actions_form[i][1].get() == "":
                index_to_del = i

    # Remove the action based on the found index and recreate all forms
    if index_to_del is not None:
        self.actions.pop(index_to_del)

        for form in self.actions_form:
            form[0].destroy()
            form[1].destroy()
        self.actions_form = []

        for i in range(len(self.actions) + 1):
            if i == len(self.actions):
                _create_form(self)
            else:
                _create_form(self, self.actions[i], i)

        self.update_fp()


def _entry_change(self, new_action: str, action_index: int):
    """Edit an already existing action or create append a new action and create a new form"""

    if new_action != "":
        # Create a new action and a new form if the last form is completed or update the existing action
        if action_index == len(self.actions_form) - 1:
            self.actions.append(new_action)

            _create_form(self)
            self.update_fp()

        else:
            self.actions[action_index] = new_action
            self.update_fp()


def _create_form(self, action=None, action_index: int = -1):
    """Create a form and insert an action inside if the form previously exist"""

    # Label to show the action number
    label = ttk.Label(
        self.form_frame,
        text=f"Action n°{len(self.actions_form) + 1}:",
    )
    label.grid(row=len(self.actions_form) + 1, column=0, padx=5, pady=5)

    # The entry and his StringVar
    string = tk.StringVar()
    entry = ttk.Entry(self.form_frame, textvariable=string)
    if action is not None:
        entry.insert(0, action)
    entry.grid(row=len(self.actions_form) + 1, column=1, padx=5, pady=5)

    # Trace to update the action
    string.trace_add(
        "write",
        lambda *args,
        new_action=string,
        action_index=action_index
        if action_index != -1
        else len(self.actions): _entry_change(
            self,
            new_action.get(),
            action_index,
        ),
    )
    # Bind to delete form when cleared
    entry.bind(
        "<FocusOut>",
        lambda event=None: _remove_form(self, event),
    )

    # Storing the object
    self.actions_form.append([label, entry])
