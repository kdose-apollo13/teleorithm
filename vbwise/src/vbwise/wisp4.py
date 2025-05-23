import tkinter as tk
from vbwise import load

class ReactiveStore:
    def __init__(self, data):
        self.data = data
        self.listeners = []

    def update(self, new_data):
        self.data = new_data
        for listener in self.listeners:
            listener(new_data)

class WidgetNode:
    def __init__(self, node, parent_widget=None, store=None, widget_map=None):
        self.node = node
        self.store = store
        self.widget_map = widget_map
        self.widget = self.create_widget(parent_widget)
        self.children = []  # Store child nodes
        self.bind_properties()
        self.bind_events()
        self.bind_children()
        if store:
            store.listeners.append(self.update)
        if widget_map is not None:
            widget_map[id(self.widget)] = self

    def create_widget(self, parent_widget):
        type_map = {
            "Tk": tk.Tk,
            "Frame": tk.Frame
        }
        widget_class = type_map.get(self.node["type"])
        if not widget_class:
            raise ValueError(f"Unknown widget type: {self.node['type']}")
        return widget_class() if self.node["type"] == "Tk" else widget_class(parent_widget)

    def bind_properties(self):
        props = self.node.get("props", {})
        if self.node["type"] == "Tk":
            if "title" in props:
                self.widget.title(props["title"])
            if "geometry" in props:
                self.widget.geometry(props["geometry"])
        elif self.node["type"] == "Frame":
            # Apply background and other props
            valid_props = {k: v for k, v in props.items() if k != "id"}
            if "background" in valid_props:
                self.widget.configure(bg=valid_props["background"])
            # Make Frame fill the window
            self.widget.pack(fill="both", expand=True)

    def bind_events(self):
        if self.node["type"] == "Tk":
            # Bind <Configure> for root window resize/move
            self.widget.bind("<Configure>", self.handle_configure)

    def handle_configure(self, event):
        # Update geometry in TKML model on resize
        new_geometry = f"{event.width}x{event.height}"
        if self.node["props"].get("geometry") != new_geometry:
            self.node["props"]["geometry"] = new_geometry
            if self.store:
                self.store.update(self.store.data)  # Notify listeners
            print(f"Updated geometry: {new_geometry}")

    def bind_children(self):
        for child_node in self.node.get("parts", []):
            child = WidgetNode(child_node, self.widget, self.store, self.widget_map)
            self.children.append(child)

    def update(self, new_data):
        # Update node if ID matches
        if new_data["props"].get("id") == self.node["props"].get("id"):
            self.node = new_data
            self.bind_properties()
            # Update children (recursive update)
            for child, new_child in zip(self.children, new_data.get("parts", [])):
                child.update(new_child)

# Example TKML
tkml_source = '''
Tk {
    id: root
    title: "Elegant Data-Driven Demo"
    geometry: "300x180"
    Frame {
        id: main_frame
        background: "#AA1122"
    }
}
'''

# Build and run
parsed_tkml = load.tkml_string(tkml_source)
store = ReactiveStore(parsed_tkml)
widget_map = {}
root_node = WidgetNode(parsed_tkml, store=store, widget_map=widget_map)

assert widget_map[id(root_node.widget)] == root_node
assert widget_map[id(root_node.children[0].widget)].node["props"]["id"] == "main_frame"

# Test external update
external_update = lambda: store.update({
    "type": "Tk",
    "props": {
        "id": "root",
        "title": "External Update!",
        "geometry": "400x300"
    },
    "parts": [{
        "type": "Frame",
        "props": {
            "id": "main_frame",
            "background": "#123ABC"  # Change background
        },
        "parts": []
    }]
})

root_node.widget.after(1000, external_update)
root_node.widget.mainloop()
