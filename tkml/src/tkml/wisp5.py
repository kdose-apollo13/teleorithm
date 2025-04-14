"""
    it's like wisp3, but in the style of wisp4
"""
from itertools import pairwise
from tkinter import *
from textwrap import dedent

from tkml.grammar import tkml_tree
from tkml.component import comb_for_components as simplify, TKMLFilter

# from kdose import linked_list as kll
import k_linked_list as kll

from enum import Enum

from test_wisp5 import consume, first, last, nexx, prev


class Mode(Enum):
    Normal = 1
    Insert = 2


class Context:
    def __init__(self):
        self.mode = Mode.Normal
        self.leaves = []
        self.focused = None
    

def update_focus():

    global mode

    for i, leaf in enumerate(leaves):
        if i == focused_index[0]:
            if mode == "normal":
                leaf.hili_ref.config(bg="blue")
            elif mode == "insert":
                leaf.hili_ref.config(bg="green")
        else:
            leaf.hili_ref.config(bg="gray")

# --------------------------------------------------------------------

def leaf_container(parent):
    f = Frame(parent, bd=1, relief='solid')
    # text box expands
    f.grid_columnconfigure(1, weight=1)
    return f

def leaf_hili(parent):
    hl = Canvas(parent, width=10, bg='gray', highlightthickness=0)
    hl.grid(row=0, column=0, sticky='ns')

# def leaf_textbox(parent):
    
    

def create_leaf(spec, parent, context):
    props = spec.get("props", {})
    container = leaf_container(parent) 
    hili = leaf_hili(container)
    container.hili_ref = hili

    textbox = Text(container, height=2, width=90, wrap='word', state=DISABLED)
    textbox.insert('1.0', props.get('text', ''))
    textbox.grid(row=0, column=1, sticky='ew')
    container.text_ref = textbox

    return container

# --------------------------------------------------------------------

def select_next_leaf(context):
    c = context
    n = nexx(c.focused, c.leaves) or last(c.leaves)
    c.focused = n
    return n


def select_prev_leaf(context):
    c = context
    p = prev(c.focused, c.leaves) or first(c.leaves)
    c.focused = p
    return p
        
    
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
                select_next_leaf(context)
            elif e.char == 'k':
                select_prev_leaf(context)
            elif e.char == 'i':
                mode = 'insert'
                print('oh crah')

    def on_key2(event):
        global mode
        if mode == "normal":
            if event.char == "j":
                focused_index[0] = min(focused_index[0] + 1, len(leaves) - 1)
                update_focus()
                print(f"Normal Mode: Focused index: {focused_index[0]}")
            elif event.char == "k":
                focused_index[0] = max(focused_index[0] - 1, 0)
                update_focus()
                print(f"Normal Mode: Focused index: {focused_index[0]}")
            elif event.char == "i":
                mode = "insert"
                update_focus() # Update highlight for insert mode
                if leaves:
                    focused_leaf = leaves[focused_index[0]]
                    # Find the Text widget within the focused Leaf
                    text_widget = focused_leaf.winfo_children()[1] # Assuming Text is the second child
                    text_widget.config(state=NORMAL)
                    text_widget.focus_set()
                print("Switched to Insert Mode")
        elif mode == "insert":
            if event.keysym == "Escape":
                mode = "normal"
                update_focus()
                if leaves:
                    focused_leaf = leaves[focused_index[0]]
                    text_widget = focused_leaf.winfo_children()[1]
                    text_widget.config(state=DISABLED)
                    app.focus_set() # Set focus back to the app for normal mode navigation
                print("Switched to Normal Mode")
            else:
                # Let the Text widget handle other key presses in insert mode
                pass

    app.bind("<Key>", on_key)

    for i, child in enumerate(spec.get("children", [])):
        component = create_component(child, app, context)
        if component:
            component.grid(row=i, column=0, sticky="nsew")

    # app.after(100, update_focus)  # Initial focus
    context.focused = first(context.leaves)
    print(context.focused)
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
    for i, child in enumerate(spec.get("children", [])):
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

def create_component(spec, parent, context):
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


if __name__ == '__main__':
    source = dedent('''
    App {
        Scrollable {
            Leaf { id: l1 text: "Leaf One" }
            Leaf { id: l2 text: "Leaf Two" }
            Leaf { id: l3 text: "Leaf Three" }
        }
    }
    ''')
    tree = tkml_tree(source)
    f = TKMLFilter()
    spec = simplify(tree, f)
    context = Context()
    app = create_component(spec, None, context)
    app.mainloop()


