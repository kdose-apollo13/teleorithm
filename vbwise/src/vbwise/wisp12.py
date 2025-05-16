# wisp12.py
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
        def recurse(parent, name, node):
            kind = node.get("type", "Frame")
            props = node.get("props", {})
            parts = node.get("parts", {})

            widget_type = getattr(tk, kind)
            widget = widget_type(parent)
            self.widgets[name] = widget

            if name == "root":
                if "title" in props:
                    widget.title(props["title"])
                if "geometry" in props:
                    widget.geometry(props["geometry"])

            if "grid" in props:
                widget.grid(**props["grid"])

            if "config" in props:
                widget.config(**props["config"])

            if "bind" in props:
                for event, cmd in props["bind"].items():
                    widget.bind(event, self.handlers.get(cmd, lambda e: None))

            for child_name, child_node in parts.items():
                recurse(widget, child_name, child_node)

        recurse(None, "root", self.layout["root"])

    def update(self):
        entry = self.widgets.get("entry")
        if entry:
            entry.delete(0, tk.END)
            entry.insert(0, self.state.get("text", ""))

# --- sample usage ---

# mock load (eg) json, toml, tkml, gnml
state = STORED_STATE

layout = {
    "root": {
        "type": "Tk",
        "props": {
            "title": "State Sync App",
            "geometry": "300x100"
        },
        "parts": {
            "entry": {
                "type": "Entry",
                "props": {
                    "grid": {"row": 0, "column": 0},
                }
            },
            "button": {
                "type": "Button",
                "props": {
                    "grid": {"row": 0, "column": 1},
                    "config": {"text": "Save"},
                    "bind": {"<Button-1>": "save_text"}
                }
            }
        }
    }
}

app = App(state, layout)
app.build()
app.update()
app.widgets["root"].mainloop()

