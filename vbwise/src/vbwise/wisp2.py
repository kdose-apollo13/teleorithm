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
    def __init__(self, node, store=None, widget_map=None):
        self.node = node
        self.store = store
        self.widget_map = widget_map  # Map widget IDs to nodes
        self.widget = self.create_widget()
        self.vars = {}  # Reactive variables
        self.bind_properties()
        self.bind_events()
        if store:
            store.listeners.append(self.update)
        if widget_map is not None:
            widget_map[id(self.widget)] = self  # Map widget to node

    def create_widget(self):
        if self.node["type"] != "Tk":
            raise ValueError("Only Tk root supported for now")
        return tk.Tk()

    def bind_properties(self):
        props = self.node.get("props", {})
        # Handle title with StringVar for reactivity
        if "title" in props:
            self.vars["title"] = tk.StringVar(value=str(props["title"]))
            self.vars["title"].trace_add("write", lambda *args: self.update_property("title"))
            self.widget.title(self.vars["title"].get())
        # Handle geometry statically (updated via events)
        if "geometry" in props:
            self.widget.geometry(props["geometry"])

    def bind_events(self):
        # Bind <Configure> for resize/move events
        self.widget.bind("<Configure>", self.handle_configure)

    def handle_configure(self, event):
        # Update geometry in TKML model on resize
        new_geometry = f"{event.width}x{event.height}"
        if self.node["props"].get("geometry") != new_geometry:
            self.node["props"]["geometry"] = new_geometry
            if self.store:
                self.store.update(self.node)  # Notify listeners
            print(f"Updated geometry: {new_geometry}")

    def update_property(self, key):
        if key == "title":
            self.widget.title(self.vars["title"].get())

    def update(self, new_data):
        # Update node if ID matches
        if new_data["props"].get("id") == self.node["props"].get("id"):
            self.node = new_data
            self.bind_properties()

# Example TKML
tkml_source = '''
Tk {
    id: root
    title: "Elegant Data-Driven Demo"
    geometry: "300x180"
}
'''

# Build and run
parsed_tkml = load.tkml_string(tkml_source)
store = ReactiveStore(parsed_tkml)
widget_map = {}
root_node = WidgetNode(parsed_tkml, store=store, widget_map=widget_map)

# Test dynamic title update
root_node.vars["title"].set("New Title!")
root_node.widget.mainloop()
