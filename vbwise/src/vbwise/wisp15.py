import tkinter as tk

# Sample state (can be modified as needed)
STORED_STATE = {
    'text': 'some_text'
}

class App:
    def __init__(self, state, layout):
        self.state = state
        self.layout = layout
        self.widgets = {}
        self.handlers = {
            "save_text": self.save_text
        }

    def save_text(self, event=None):
        entry = self.widgets.get("entry")
        if entry:
            self.state["text"] = entry.get()
            STORED_STATE = self.state  # Update global state (optional)

    def build(self):
        # Phase 1: Create all widgets recursively
        def create_widgets(parent, name, node):
            kind = node.get("type", "Frame")
            if name == "root" and kind == "Tk":
                widget = tk.Tk()
            else:
                widget_type = getattr(tk, kind)
                widget = widget_type(parent)
            self.widgets[name] = widget
            for child_name, child_node in node.get("parts", {}).items():
                create_widgets(widget, child_name, child_node)

        create_widgets(None, "root", self.layout["root"])

        # Phase 2: Configure all widgets recursively
        def configure_widgets(name, node):
            widget = self.widgets[name]
            props = node.get("props", {})
            
            # Configure root window properties
            if name == "root":
                if "title" in props:
                    widget.title(props["title"])
                if "geometry" in props:
                    widget.geometry(props["geometry"])
            
            # Apply grid placement if specified
            if "grid" in props:
                grid_props = props["grid"].copy()  # Make a copy to avoid modifying original
                # Safely extract 'weight' if it exists, default to empty dict
                weight = grid_props.pop('weight', {})
                widget.grid(**grid_props)
                # Set grid weights on the parent widget if provided
                row = grid_props.get("row", 0)
                column = grid_props.get("column", 0)
                if "row" in weight:
                    widget.master.grid_rowconfigure(row, weight=weight["row"])
                if "column" in weight:
                    widget.master.grid_columnconfigure(column, weight=weight["column"])
            
            # Apply widget-specific configurations
            if "config" in props:
                config = props["config"]
                for key, value in config.items():
                    if isinstance(value, dict) and "widget" in value and "method" in value:
                        ref_widget = self.widgets[value["widget"]]
                        method = getattr(ref_widget, value["method"])
                        widget.config(**{key: method})
                    else:
                        widget.config(**{key: value})
            
            # Bind events if specified
            if "bind" in props:
                for event, cmd in props["bind"].items():
                    widget.bind(event, self.handlers.get(cmd, lambda e: None))
            
            # Handle canvas window creation for content frame
            if "create_window" in props:
                canvas = widget
                content_frame = self.widgets[props["create_window"]["content"]]
                canvas.create_window((0, 0), window=content_frame, anchor="nw")
                # Update scrollregion after content is added
                # is this necessary?
                content_frame.update_idletasks()
                canvas.config(scrollregion=canvas.bbox("all"))
            
            # Recursively configure child widgets
            for child_name, child_node in node.get("parts", {}).items():
                configure_widgets(child_name, child_node)

        configure_widgets("root", self.layout["root"])

    def update(self):
        entry = self.widgets.get("entry")
        if entry:
            entry.delete(0, tk.END)
            entry.insert(0, self.state.get("text", ""))

# Define the layout with a scrollable frame and sample content
layout = {
    "root": {
        "type": "Tk",
        "props": {
            "title": "Scrollable Frame App",
            "geometry": "400x300"
        },
        "parts": {
            "main_frame": {
                "type": "Frame",
                "props": {
                    "grid": {
                        "row": 0,
                        "column": 0,
                        "sticky": "nsew",
                        "weight": {"row": 1, "column": 1}  # Allow resizing
                    }
                },
                "parts": {
                    "canvas": {
                        "type": "Canvas",
                        "props": {
                            "grid": {
                                "row": 0,
                                "column": 0,
                                "sticky": "nsew",
                                "weight": {"row": 1, "column": 1}  # Expand with frame
                            },
                            "config": {
                                "bg": "white",
                                "yscrollcommand": {"widget": "scrollbar", "method": "set"}
                            },
                            "create_window": {"content": "content_frame"}
                        },
                        'parts': {
                            "content_frame": {
                                "type": "Frame",
                                "props": {
                                    "config": {"bg": "lightblue"}
                                },
                                "parts": {
                                    **{f"label{i}": {
                                        "type": "Label",
                                        "props": {
                                            "config": {"text": f"Label {i}", "bg": "lightblue"},
                                            "grid": {"row": i, "column": 0}
                                        }
                                    } for i in range(20)}
                                }
                            }
                        },
                    },
                    "scrollbar": {
                        "type": "Scrollbar",
                        "props": {
                            "grid": {
                                "row": 0,
                                "column": 1,
                                "sticky": "ns"
                            },
                            "config": {
                                "orient": "vertical",
                                "command": {"widget": "canvas", "method": "yview"}
                            }
                        }
                    }
                }
            },

        }
    }
}

# Run the application
state = STORED_STATE
app = App(state, layout)
app.build()
app.update()
app.widgets["root"].mainloop()

