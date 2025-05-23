from operator import itemgetter
import tkinter as tk
from vbwise import load

# Store: Data model fulcrum
def store(data):
    listeners = []
    state = {"data": data}
    change_state = lambda new: {'data': new}
    return {
        "get": lambda: state["data"],
        'set': lambda new: [change_state(new), [l(new) for l in listeners]],
        "listen": lambda l: listeners.append(l)
    }

# Widget creators
def _tk(props):
    widget = tk.Tk()
    sync(widget, props)
    widget.bind("<Configure>", lambda e: handle_configure(e, props, store_instance))
    return widget

def frame(props, base):
    widget = tk.Frame(base)
    sync(widget, props)
    widget.pack(fill="both", expand=True)
    for event, action in props.get("bind", {}).items():
        bind(widget, event, action, props, store_instance)
    return widget

# Sync view with model
def sync(widget, props):
    if isinstance(widget, tk.Tk):
        if "title" in props:
            widget.title(props["title"])
        if "geometry" in props:
            widget.geometry(props["geometry"])
    else:
        valid_props = {k: v for k, v in props.items() if k not in ["id", "bind"]}
        if "background" in valid_props:
            widget.configure(bg=valid_props["background"])

# Event handlers
def handle_configure(event, props, store_instance):
    new_geometry = f"{event.width}x{event.height}"
    if props.get("geometry") != new_geometry:
        props["geometry"] = new_geometry
        store_instance["set"](store_instance["get"]())
        print(f"Geometry: {new_geometry}")

def bind(widget, event, action, props, store_instance):
    if action == "change_color":
        widget.bind(event, lambda e: change_color(e, props, store_instance))

def change_color(event, props, store_instance):
    current_bg = props.get("background", "#AA1122")
    props["background"] = "#123ABC" if current_bg == "#AA1122" else "#AA1122"
    store_instance["set"](store_instance["get"]())
    print(f"Background: {props['background']}")

# Build app
def build(node, store_instance):
    widget_map = {}
    def create(node, base=None):
        props = node.get("props", {})
        widget = _tk(props) if node["type"] == "Tk" else frame(props, base)
        widget_map[id(widget)] = node
        store_instance["listen"](lambda data: sync(widget, data["props"]) if data["props"].get("id") == props.get("id") else None)
        for part in node.get("parts", []):
            create(part, widget)
        return widget
    root = create(node)
    return root, widget_map

# Run
tkml_source = '''
Tk {
    id: root
    title: "Elegant Demo"
    geometry: "300x180"
    Frame {
        id: main_frame
        background: "#AA1122"
        bind: { <Button-1>: "change_color" }
    }
}
'''

parsed_tkml = load.tkml_string(tkml_source)
store_instance = store(parsed_tkml)
root_widget, widget_map = build(parsed_tkml, store_instance)

assert widget_map[id(root_widget)]["props"]["id"] == "root"
assert widget_map[id(root_widget.winfo_children()[0])]["props"]["id"] == "main_frame"

root_widget.mainloop()
