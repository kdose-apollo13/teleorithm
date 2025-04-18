"""
    it's like wisp3, but in the style of wisp4
"""
from enum import Enum
from itertools import pairwise
from tkinter import *
from textwrap import dedent

from tkml.grammar import tkml_tree
from tkml.component import comb_for_components as simplify, TKMLFilter

# TDD in reverse -> haven't written the tests yet
# but already importing from them - *time pincer*
from test_wisp5 import first, last, nexx, prev

# style from toml
style = {
    'leaf': {
        'unselected': {
            'background': 'gray',
            'state': DISABLED
        },
        'selected': {
            'background': 'blue',
            'state': DISABLED
        },
        'active': {
            'background': 'green',
            'state': NORMAL
        }
    }
}

class Mode(Enum):
    Normal = 1
    Insert = 2


class Context:
    def __init__(self):
        self.mode = Mode.Normal
        self.leaves = []
        self.focused = None

# --------------------------------------------------------------------



# --------------------------------------------------------------------

def leaf_container(parent):
    f = Frame(parent, bd=1, relief='solid')
    # text box expands
    f.grid_columnconfigure(1, weight=1)
    return f

def leaf_hili(parent):
    hl = Canvas(parent, width=10, bg='gray', highlightthickness=0)
    hl.grid(row=0, column=0, sticky='ns')
    return hl

def leaf_textbox(parent, props):
    t = Text(parent, height=4, width=90, wrap='word', state=DISABLED)
    t.insert('1.0', props.get('text', ''))
    t.grid(row=0, column=1, sticky='ew')
    return t

def create_leaf(spec, parent, context):
    props = spec.get("props", {})
    container = leaf_container(parent)
    hili = leaf_hili(container)
    container.hili_ref = hili
    textbox = leaf_textbox(container, props)
    container.textbox_ref = textbox
    return container

# --------------------------------------------------------------------

def normal_mode_colorize_hilis(context):
    c = context
    for l in c.leaves:
        if l is c.focused:
            l.hili_ref.config(bg='blue')
        else:
            l.hili_ref.config(bg='gray')

def select_next_leaf(context):
    c = context
    n = nexx(c.focused, c.leaves) or last(c.leaves)
    c.focused = n
    print(n)
    return n

def select_prev_leaf(context):
    c = context
    p = prev(c.focused, c.leaves) or first(c.leaves)
    c.focused = p
    print(p)
    return p

def apply_style(context):
    c = context
    for leaf in c.leaves:
        if leaf is c.focused:
            leaf.set_style(focused)
        else:
            leaf.set_style(default)

def enter_focused_leaf(context):
    c = context
    for leaf in c.leaves:
        if leaf is c.focused:
            t = leaf.textbox_ref
            t.config(state=NORMAL)
            t.focus_set()
            leaf.hili_ref.config(bg='green')
        else:
            leaf.hili_ref.config(bg='gray')

def exit_focused_leaf(context):
    c = context
    for leaf in c.leaves:
        if leaf is c.focused:
            t = leaf.textbox_ref
            t.config(state=DISABLED)
            app.focus_set()
            leaf.hili_ref.config(bg='blue')
        else:
            leaf.hili_ref.config(bg='gray')

def capture_widget_tree(parent):
    widget_info = {"type": str(parent)}
    parts_info = []
    for child in parent.winfo_parts():
        parts_info.append(capture_widget_tree(child))
    if parts_info:
        widget_info["parts"] = parts_info

    # Extract specific attributes based on widget type
    # if isinstance(parent, Text):
    #     widget_info["text"] = parent.get("1.0", END)
    # elif isinstance(parent, Label) or isinstance(parent, Button):
    #     widget_info["text"] = parent.cget("text")

    return widget_info

def create_app(spec, context):
    app = Tk()
    props = spec.get('props', {})
    t = props.get('title', 'default')
    app.title(t)
    app.geometry("400x800")
    app.grid_columnconfigure(0, weight=1) # Make the first column expandable
    app.grid_rowconfigure(0, weight=1)    # Make the first row expandable


    def on_key(e):
        if context.mode == Mode.Normal:
            if e.char == 'j':
                l = select_next_leaf(context)
                normal_mode_colorize_hilis(context)
            elif e.char == 'k':
                select_prev_leaf(context)
                normal_mode_colorize_hilis(context)
            elif e.char == 'i':
                context.mode = Mode.Insert
                enter_focused_leaf(context)
            elif e.keysym == 'Return':
                widget_tree_data = capture_widget_tree(app)
                print("Captured Widget Tree:")
                import pprint
                pprint.pprint(widget_tree_data)
        elif context.mode == Mode.Insert:
            if e.keysym == 'Escape':
                context.mode = Mode.Normal
                exit_focused_leaf(context)
                normal_mode_colorize_hilis(context)

    app.bind("<Key>", on_key)

    for i, child in enumerate(spec.get("parts", [])):
        component = create_component(child, app, context)
        if component:
            component.grid(row=i, column=0, sticky="nsew")

    context.focused = first(context.leaves)
    normal_mode_colorize_hilis(context)

    return app

# --------------------------------------------------------------------

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
    for i, child in enumerate(spec.get("parts", [])):
        component = create_component(child, content, context)
        if component:
            component.grid(row=i, column=0, sticky="ew")

def create_scrollable(spec, parent, context):
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

# --------------------------------------------------------------------

# TODO: need something that works with initial and final dicts
# initial dict should permit empty
# final dict is based either on tkml or from widgets - both directions

def create_component(spec, parent, context):
    """
        build active widget tree representation here?
    """
    if spec['type'] == 'App':
        return create_app(spec, context)
    elif spec['type'] == 'Scrollable':
        return create_scrollable(spec, parent, context)
    elif spec['type'] == 'Leaf':
        leaf = create_leaf(spec, parent, context)
        context.leaves.append(leaf)
        return leaf
    else:
        return None


# only the App gets created, everything before just mapped
source = dedent('''
    Tkml {
        meta: 'failure is inevitable'

        Scrollable {
            Frame {
                row_weight: 0: 1
                col_weight: 0: 1 
                
                Canvas {
                    id: viewport
                    row: 0
                    col: 0
                    sticky: 'nesw'
                    scrolled_by: scrollbar

                    Frame {
                        id: content
                        col_weight: 0: 1
                    }
                }

                Scrollbar {
                    id: scrollbar
                    orient: 'vertical'
                    sticky: 'ns'
                    scrolls: viewport
                }
            }

        }

        App {
            script: 'leafapp.py'
            style: 'leafapp.toml'
            comps: 'leafcomps.tkml'
            Scrollable {
                Leaf { id: l1 text: "Leaf One" }
                Leaf { id: l2 text: "Leaf Two" }
                Leaf { id: l3 text: "Leaf Three" }
            }
        }
        
    }
''')

if __name__ == '__main__':
    tree = tkml_tree(source)
    f = TKMLFilter()
    spec = simplify(tree, f)
    context = Context()
    app = create_component(spec, None, context)
    # app.mainloop()

    def viz_spec(spec, indent=0):
        type_info = spec.get('type', '')
        props = spec.get('props', {})
        parts = spec.get('parts', {})
        
        if type_info:
            print(' ' * indent, type_info)
        for k, v in props.items():
            if isinstance(v, dict):
                viz_spec(spec['props'][k])
            else:
                print(' ' * (indent + 2), k, v)
        for part in parts:
            viz_spec(part, indent + 2)

    viz_spec(spec)
    
