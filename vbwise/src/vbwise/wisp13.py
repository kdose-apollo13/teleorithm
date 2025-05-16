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

    def save_text(self, event=None):
        entry = self.widgets.get("entry")
        if entry:
            self.state["text"] = entry.get()
            STORED_STATE = self.state

    def build(self):
        # Phase 1: Create all widgets
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

        # Phase 2: Configure all widgets
        def configure_widgets(name, node):
            widget = self.widgets[name]
            props = node.get("props", {})
            if name == "root":
                if "title" in props:
                    widget.title(props["title"])
                if "geometry" in props:
                    widget.geometry(props["geometry"])
            if "grid" in props:
                widget.grid(**props["grid"])
            if "config" in props:
                config = props["config"]
                for key, value in config.items():
                    if isinstance(value, dict) and "widget" in value and "method" in value:
                        ref_widget = self.widgets[value["widget"]]
                        method = getattr(ref_widget, value["method"])
                        widget.config(**{key: method})
                    else:
                        widget.config(**{key: value})
            if "bind" in props:
                for event, cmd in props["bind"].items():
                    widget.bind(event, self.handlers.get(cmd, lambda e: None))
            for child_name, child_node in node.get("parts", {}).items():
                configure_widgets(child_name, child_node)

        configure_widgets("root", self.layout["root"])

    def update(self):
        entry = self.widgets.get("entry")
        if entry:
            entry.delete(0, tk.END)
            entry.insert(0, self.state.get("text", ""))

# Example layout with composite widgets (canvas and scrollbar)
layout = {
    "root": {
        "type": "Tk",
        "props": {
            "title": "Composite Widget App",
            "geometry": "400x300"
        },
        "parts": {
            "canvas": {
                "type": "Canvas",
                "props": {
                    "grid": {"row": 0, "column": 0, "sticky": "nsew"},
                    "config": {
                        "bg": "white",
                        "scrollregion": "0 0 800 600",
                        "xscrollcommand": {"widget": "scrollbar", "method": "set"}
                    }
                }
            },
            "scrollbar": {
                "type": "Scrollbar",
                "props": {
                    "grid": {"row": 1, "column": 0, "sticky": "ew"},
                    "config": {
                        "orient": "horizontal",
                        "command": {"widget": "canvas", "method": "xview"}
                    }
                }
            }
        }
    }
}

# Sample usage
state = STORED_STATE
app = App(state, layout)
app.build()
app.update()
app.widgets["root"].mainloop()

