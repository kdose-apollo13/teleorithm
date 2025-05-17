import tkinter as tk


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

    def _title(self, widget, props):
        widget.title(props["title"])

    def _geometry(self, widget, props):
        widget.geometry(props["geometry"])

    def _grid(self, widget, props):
        grid_props = props["grid"].copy()
        weight = grid_props.pop('weight', {})
        widget.grid(**grid_props)

        row = grid_props.get("row", 0)
        column = grid_props.get("column", 0)

        if "row" in weight and hasattr(widget.master, 'grid_rowconfigure'):
            widget.master.grid_rowconfigure(row, weight=weight["row"])
        if "column" in weight and hasattr(widget.master, 'grid_columnconfigure'):
            widget.master.grid_columnconfigure(column, weight=weight["column"])

    def _config(self, widget, props):
        config_props = props["config"]
        # TODO: temp dict to avoid issues if value is a dict being iterated ???
        configs_to_apply = {}
        for key, value in config_props.items():
            if isinstance(value, dict) and "widget" in value and "method" in value:
                if value["widget"] in self.widgets:
                    ref_widget = self.widgets[value["widget"]]
                    method = getattr(ref_widget, value["method"], None)
                    if callable(method):
                        configs_to_apply[key] = method
                    else:
                        print(
                            f"Warning: Method '{value['method']}' "
                            "not found or not callable for widget "
                            f"'{value['widget']}'."
                        )
                else:
                    print(
                        f"Warning: Referenced widget '{value['widget']}' "
                        f"not found for config key '{key}'."
                    )
            else:
                configs_to_apply[key] = value

        if configs_to_apply:
            widget.config(**configs_to_apply)

    def _bind(self, widget, props):
        for event, cmd in props["bind"].items():
            widget.bind(event, self.handlers.get(cmd, lambda e: None))

    def _create_window(self, widget, props):
        canvas = widget
        content_frame_name = props["create_window"]["content"]
        
        if content_frame_name in self.widgets:
            content_frame = self.widgets[content_frame_name]
            
            canvas.create_window(
                (0, 0),
                window=content_frame,
                anchor="nw",
                tags="content_window"
            )
            
            # ensure content_frame's geometry is calculated based on its partren
            content_frame.update_idletasks()
            
            # Set the scrollregion for the canvas.
            bbox = canvas.bbox("all") 
            if bbox:
                canvas.config(scrollregion=bbox)
            else:
                # Fallback or if content_frame is empty, use its requested size
                req_width = content_frame.winfo_reqwidth()
                req_height = content_frame.winfo_reqheight()
                canvas.config(scrollregion=(0, 0, req_width, req_height))
                if req_width == 1 and req_height == 1:
                     print(
                        f"Warning: content_frame '{content_frame_name}' "
                        "has minimal size. Scrollregion might be incorrect.")
        else:
            print(
                f"Warning: Content frame '{content_frame_name}' "
                f"not found in widgets for canvas '{name}'."
            )

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
                for part_name, part_node in node.get("parts", {}).items():
                    create_widgets(widget, part_name, part_node)

            create_widgets(None, "root", self.layout["root"])

            # Phase 2: Configure all widgets recursively
            def configure_widgets(name, node):
                widget = self.widgets[name]
                props = node.get("props", {})
                
                if "title" in props:
                    self._title(widget, props)
                if "geometry" in props:
                    self._geometry(widget, props)
                if "grid" in props:
                    self._grid(widget, props)
                if "config" in props:
                    self._config(widget, props)
                if "bind" in props:
                    self._bind(widget, props)
                
                # configure parts before processing parent props that depend on them
                for part_name, part_node in node.get("parts", {}).items():
                    configure_widgets(part_name, part_node)

                if "create_window" in props:
                    self._create_window(widget, props)

            configure_widgets("root", self.layout["root"])

    def save_text(self, event=None):
        entry = self.widgets.get("entry")
        if entry:
            self.state["text"] = entry.get()
            STORED_STATE = self.state  # Update global state (optional)


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

from wisp17 import App
# Run the application
state = STORED_STATE
app = App(state, layout)
app.build()
app.update()
app.widgets["root"].mainloop()

