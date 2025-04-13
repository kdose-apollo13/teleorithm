from tkinter import *


def outer_frame(parent):
    frame = Frame(parent)
    # The canvas shall expand with the frame
    frame.grid_columnconfigure(0, weight=1)
    # Vertically, too, the canvas shall grow
    frame.grid_rowconfigure(0, weight=1)
    return frame

def viewport_canvas(container):
    c = Canvas(container)
    c.grid(row=0, column=0, sticky="nsew")

    sb = Scrollbar(container, orient="vertical", command=c.yview)
    sb.grid(row=0, column=1, sticky="ns")

    # The scrollbar's movement dictates the canvas's view
    c.config(yscrollcommand=sb.set)
    return c
    
def inner_frame(view):
    f = Frame(view)
    f.grid_columnconfigure(0, weight=1)
    return f
    
def populate_frame(content, spec):
    for i, child in enumerate(spec.get("children", [])):
        component = create_component(child, content)
        if component:
            component.grid(row=i, column=0, sticky="ew")

def create_scrollable(spec, parent):
    print(f"Creating Scrollable component, parent: {parent}")

    container = outer_frame(parent)
    view = viewport_canvas(container)
    content = inner_frame(view)
    view.create_window((0, 0), window=content, anchor="nw")

    # When the inner frame shifts, the canvas learns its boundaries
    content.bind(
        "<Configure>",
        lambda e: view.config(scrollregion=view.bbox("all"))
    )
    
    populate_frame(content, spec)

    return container

def create_component(spec, parent):
    if spec.get("type") == "Label":
        return Label(parent, text=spec.get("text", "Default Label"))
    elif spec.get("type") == "Button":
        return Button(parent, text=spec.get("text", "Default Button"))
    return None

if __name__ == '__main__':
    root = Tk()
    root.title("Scrollable Example")

    scrollable_spec = {
        "type": "Scrollable",
        "children": [
            {"type": "Label", "text": f"Label {i}"} for i in range(50)
        ]
    }

    scrollable_widget = create_scrollable(scrollable_spec, root)
    scrollable_widget.grid(row=0, column=0, sticky="nsew") # Let the scrollable widget fill the root

    root.grid_columnconfigure(0, weight=1) # The root shall yield space to its children
    root.grid_rowconfigure(0, weight=1)    # In both dimensions, space shall be given

    root.mainloop()

