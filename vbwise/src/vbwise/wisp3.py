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
        self.bind_properties()
        self.bind_events()
        if store:
            store.listeners.append(self.update)
        if widget_map is not None:
            # why id rather than widget itself (ie) its ref?
            widget_map[id(self.widget)] = self  # Map widget to node

    def create_widget(self):
        if self.node["type"] != "Tk":
            raise ValueError("Only Tk root supported for now")
        return tk.Tk()

    def bind_properties(self):
        # calling widget methods with props data...
        props = self.node.get("props", {})
        if "title" in props:
            self.widget.title(props["title"])
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
                # we changed the data model, so push an update from it to widgets
                self.store.update(self.node)  # Notify listeners
            print(f"Updated geometry: {new_geometry}")

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

assert widget_map[id(root_node.widget)] == root_node

# Test external update

external_update = lambda: store.update({
    "type": "Tk",
    "props": {
        "id": "root",
        "title": "External Update!",
        "geometry": "400x300"
    },
    "parts": []
})

root_node.widget.after(1000, external_update) 
root_node.widget.mainloop()

