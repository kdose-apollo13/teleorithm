import tkinter as tk
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

leaf_widgets = []
focused_index = [0]  # mutable reference
mode = "normal"  # Global variable to track the mode

# 1. Define tkml grammar
tkml_grammar = Grammar(r'''
tkml        = ws block ws
block       = identifier ws "{" ws item* ws "}"
item        = (property / block) ws
property    = identifier ws ":" ws value
value       = string / identifier / color / number
string      = "\"" ~"(?s:(\\\\.|[^\"\\\\])*)" "\""
identifier  = ~"[a-zA-Z_][a-zA-Z0-9_]*"
color       = "#" ~"[a-zA-Z0-9]{6}"
number      = ~"[0-9]+"
ws          = ~"\s*"
''')

# 2. Visitor: transform parse tree into nested dict
class TKMLVisitor(NodeVisitor):
    def visit_tkml(self, node, visited):
        print(f"visit_tkml visited: {visited}")
        return visited[1]

    def visit_block(self, node, visited):
        print(f"visit_block visited: {visited}")
        name = visited[0]
        items = visited[4]  # item*
        props = {}
        children = []
        for item_list in items:
            print(f"  Item list in block {name}: {item_list}")
            if item_list:
                item = item_list[0]
                print(f"  Item in block {name}: {item}")
                if isinstance(item, dict):
                    if "type" in item:
                        children.append(item)
                    else:
                        props.update(item)
        widget = {'type': name, 'props': props, 'children': children}
        print(f"Returning widget from visit_block for {name}: {widget}")
        return widget

    def visit_item(self, node, visited):
        print(f"visit_item visited: {visited}")
        return visited[0]

    def visit_property(self, node, visited):
        print(f"visit_property visited: {visited}")
        return {visited[0]: visited[4]}

    def visit_value(self, node, visited):
        print(f"visit_value visited: {visited}")
        return visited[0]

    def visit_string(self, node, visited):
        return node.text.strip('"')

    def visit_identifier(self, node, visited):
        return node.text

    def visit_color(self, node, visited):
        return node.text

    def visit_number(self, node, visited):
        return int(node.text)

    def generic_visit(self, node, visited):
        return visited or node.text

# 3. Mapping from dict to tkinter components (Refactored)
def create_app(spec, master):
    app = tk.Tk()
    app.title("TKML App")
    app.geometry("400x800")
    app.grid_columnconfigure(0, weight=1) # Make the first column expandable
    app.grid_rowconfigure(0, weight=1)    # Make the first row expandable

    def on_key(event):
        global mode
        if mode == "normal":
            if event.char == "j":
                focused_index[0] = min(focused_index[0] + 1, len(leaf_widgets) - 1)
                update_focus()
                print(f"Normal Mode: Focused index: {focused_index[0]}")
            elif event.char == "k":
                focused_index[0] = max(focused_index[0] - 1, 0)
                update_focus()
                print(f"Normal Mode: Focused index: {focused_index[0]}")
            elif event.char == "i":
                mode = "insert"
                update_focus() # Update highlight for insert mode
                if leaf_widgets:
                    focused_leaf = leaf_widgets[focused_index[0]]
                    # Find the Text widget within the focused Leaf
                    text_widget = focused_leaf.winfo_children()[1] # Assuming Text is the second child
                    text_widget.config(state=tk.NORMAL)
                    text_widget.focus_set()
                print("Switched to Insert Mode")
        elif mode == "insert":
            if event.keysym == "Escape":
                mode = "normal"
                update_focus()
                if leaf_widgets:
                    focused_leaf = leaf_widgets[focused_index[0]]
                    text_widget = focused_leaf.winfo_children()[1]
                    text_widget.config(state=tk.DISABLED)
                    app.focus_set() # Set focus back to the app for normal mode navigation
                print("Switched to Normal Mode")
            else:
                # Let the Text widget handle other key presses in insert mode
                pass

    app.bind("<Key>", on_key)

    for i, child in enumerate(spec.get("children", [])):
        component = create_component(child, app)
        if component:
            component.grid(row=i, column=0, sticky="nsew") # Use grid for top-level children

    app.after(100, update_focus)  # Initial focus

    return app


def create_scrollable(spec, master):
    print(f"Creating Scrollable component, master: {master}")
    frame = tk.Frame(master)
    frame.grid_columnconfigure(0, weight=1) # Make the canvas expandable
    frame.grid_rowconfigure(0, weight=1)    # Make the canvas expandable

    canvas = tk.Canvas(frame)
    canvas.grid(row=0, column=0, sticky="nsew")

    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")

    canvas.configure(yscrollcommand=scrollbar.set)

    inner = tk.Frame(canvas)
    inner.grid_columnconfigure(0, weight=1) # Allow inner frame to expand content
    canvas.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    for i, child in enumerate(spec.get("children", [])):
        component = create_component(child, inner)
        if component:
            component.grid(row=i, column=0, sticky="ew") # Leaf expands horizontally

    return frame


def create_leaf(spec, master):
    props = spec.get("props", {})
    widget = tk.Frame(master, bd=1, relief="solid")
    widget.grid_columnconfigure(1, weight=1) # Make the text area expandable

    # Create highlight canvas and attach to widget.
    highlight = tk.Canvas(widget, width=10, bg="gray",
                            highlightthickness=0)
    highlight.grid(row=0, column=0, sticky="ns")
    widget.highlight = highlight  # attach for later update

    text = tk.Text(widget, height=2, width=90, wrap="word", state=tk.DISABLED)
    text.insert("1.0", props.get("text", ""))
    text.grid(row=0, column=1, sticky="ew") # Text expands horizontally
    widget.text_widget = text # Attach text widget for easier access

    leaf_widgets.append(widget)
    return widget

def update_focus():
    global mode
    for i, leaf in enumerate(leaf_widgets):
        if i == focused_index[0]:
            if mode == "normal":
                leaf.highlight.config(bg="blue")
            elif mode == "insert":
                leaf.highlight.config(bg="green") # Indicate insert mode visually
        else:
            leaf.highlight.config(bg="gray")


component_map = {
    "App": create_app,
    "Scrollable": create_scrollable,
    "Leaf": create_leaf,
}

def create_component(spec, master):
    comp_type = spec.get("type")
    if comp_type in component_map:
        return component_map[comp_type](spec, master)
    else:
        print(f"Unknown component type: {comp_type}")
        return None

# 4. Functional pipeline: parse → AST → dict → tkinter
def build_tk_app(tkml_source):
    tree = tkml_grammar.parse(tkml_source)
    print("Raw parse tree:", tree)
    spec = TKMLVisitor().visit(tree)
    print("Parsed Structure (spec):", spec)
    app = create_component(spec, None)
    return app

# Example tkml source
tkml_source = '''
App {
    Scrollable {
        Leaf { id: l1 text: "Leaf One" }
        Leaf { id: l2 text: "Leaf Two" }
        Leaf { id: l3 text: "Leaf Three" }
    }
}
'''

if __name__ == "__main__":
    app = build_tk_app(tkml_source)
    app.update()
    app.mainloop()
