from collections import defaultdict
from graphlib import TopologicalSorter
from itertools import count
import tkinter as tk
from vbwise import load

# Data and style
model = {"title": "choomin' with baba yaga"}
style = {"geometry": "400x300", "bg": "#112233"}

# Store: Data model fulcrum
def store(data):
    listeners = []
    state = {"data": data}
    def change_state(new):
        state["data"] = new
    return {
        "get": lambda: state["data"],
        "set": lambda new: [change_state(new), [l(new) for l in listeners]],
        "listen": lambda l: listeners.append(l)
    }

# Widget ID generator
class WidgetIDs:
    def __init__(self, sep="_"):
        self.sep = sep
        self.counter = count(start=1)

    def new_id(self, node):
        props = node.get("props", {})
        return props.get("_id", f"{node['type']}{self.sep}{next(self.counter)}")

# TKML processing
def widget_specs_by_id(node, flat=defaultdict(dict), widget_ids=WidgetIDs()):
    _id = widget_ids.new_id(node)
    flat[_id].update({"_type": node["type"], **node.get("props", {})})
    for part in node.get("parts", []):
        part_id = widget_ids.new_id(part)
        flat[part_id]["_base"] = _id
        widget_specs_by_id(part, flat, widget_ids)
    return flat

def widget_creation_order(specs_by_id):
    bases = {k: [v["_base"]] for k, v in specs_by_id.items() if "_base" in v}
    return list(TopologicalSorter(bases).static_order())

# Widget creation and config
def create_widget(_id, spec, runtime):
    _class = getattr(tk, spec["_type"], None)
    if not _class:
        raise ValueError(f"Invalid widget type: {spec['_type']}")
    base_id = spec.get("_base")
    base_widget = runtime[base_id]["widget"] if base_id else None
    widget = _class(base_widget)
    runtime[_id] = {"widget": widget, "spec": spec}

def configure_widget(_id, runtime, store_instance, model, style):
    widget = runtime[_id]["widget"]
    spec = runtime[_id]["spec"]
    for key, value in spec.items():
        if key.startswith("_"):
            continue
        if isinstance(value, str) and "." in value:
            thing, attr = value.split(".")
            value = model.get(attr) if thing == "model" else style.get(attr)
        if key == "config":
            # nasty line...
            widget.configure(**{k: style.get(v) if k == "background" and v == style["bg"] else v for k, v in value.items()})
        elif key == "grid":
            widget.grid(**value)
        elif key == "grid_rowconfigure":
            widget.grid_rowconfigure(value["row"], weight=value["weight"])
        elif key == "grid_columnconfigure":
            widget.grid_columnconfigure(value["column"], weight=value["weight"])
        elif key == "title" and isinstance(widget, tk.Tk):
            widget.title(value)
        elif key == "geometry" and isinstance(widget, tk.Tk):
            widget.geometry(value)

# Event handlers
actions = {
    "change_color": lambda props: {
        **props,
        "config": {
            **props.get("config", {}),
            "background": "#123ABC" if props.get("config", {}).get("background", "#112233") == "#112233" else "#112233"
        }
    }
}

def update_node(store_instance, _id, action):
    def update_tree(tree):
        if tree.get("props", {}).get("_id") == _id:
            return {**tree, "props": action(tree["props"])}
        return {**tree, "parts": [update_tree(part) for part in tree.get("parts", [])]}
    root = store_instance["get"]()
    new_root = update_tree(root)
    store_instance["set"](new_root)

def bind_events(_id, runtime, store_instance):
    widget = runtime[_id]["widget"]
    spec = runtime[_id]["spec"]
    for event, action in spec.get("bind", {}).items():
        if action in actions:
            widget.bind(event, lambda e: update_node(store_instance, _id, actions[action]))

# Main
tkml_source = '''
Tk {
    _id: root
    title: model.title
    geometry: style.geometry
    grid_rowconfigure: { row: 0, weight: 1 }
    grid_columnconfigure: { column: 0, weight: 1}
    Frame {
        _id: frame
        config: { background: style.bg }
        grid: { row: 0, column: 0, sticky: nesw }
        bind: { <Button-1>: change_color }
    }
}
'''

t = load.tkml_string(tkml_source)
specs_by_id = widget_specs_by_id(t)
order = widget_creation_order(specs_by_id)
runtime = {}
store_instance = store(t)

# Create and configure
for _id in order:
    create_widget(_id, specs_by_id[_id], runtime)
    configure_widget(_id, runtime, store_instance, model, style)
    bind_events(_id, runtime, store_instance)
    store_instance["listen"](
        lambda data: configure_widget(_id, runtime, store_instance, model, style)
        if find_node_by_id(data, _id) else None
    )

# Configure geometry listener
runtime["root"]["widget"].bind("<Configure>", lambda e: handle_configure(e, runtime["root"]["spec"], store_instance))

def handle_configure(event, spec, store_instance):
    new_geometry = f"{event.width}x{event.height}"
    if spec.get("geometry") != new_geometry:
        spec["geometry"] = new_geometry
        store_instance["set"](store_instance["get"]())
        print(f"Geometry: {new_geometry}")

def find_node_by_id(tree, _id):
    if tree.get("props", {}).get("_id") == _id:
        return tree
    for part in tree.get("parts", []):
        found = find_node_by_id(part, _id)
        if found:
            return found
    return None

root = runtime["root"]["widget"]
root.mainloop()
