from tkinter import *


def create_app(spec):
    app = Tk()
    t = spec['props']['title']
    app.title(t)
    app.geometry("400x800")
    app.grid_columnconfigure(0, weight=1) # Make the first column expandable
    app.grid_rowconfigure(0, weight=1)    # Make the first row expandable

    for i, child in enumerate(spec.get("children", [])):
        component = create_component(child, app)
        if component:
            component.grid(row=i, column=0, sticky="nsew")

    return app

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
    container.grid(row=0, column=0, sticky="nsew")

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
    if spec['type'] == 'App':
        return create_app(spec)
    elif spec['type'] == 'Scrollable':
        return create_scrollable(spec, parent)
    elif spec.get("type") == "Label":
        return Label(parent, text=spec.get("text", "Default Label"))
    elif spec.get("type") == "Button":
        return Button(parent, text=spec.get("text", "Default Button"))
    return None


if __name__ == '__main__':
    spec = {
        'type': 'App',
        'props': {'title': 'Some Title for App'},
        'children': [
            {
                'type': 'Scrollable',
                'children': [
                    {"type": "Label", "text": f"Label {i}"} for i in range(50)
                ]
            }
        ]
    }
    app = create_component(spec, None)
    app.mainloop()

