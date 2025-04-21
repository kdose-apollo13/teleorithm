"""
    it's like wisp3, but in the style of wisp4
"""
from enum import Enum
from functools import partial
from itertools import pairwise
from operator import methodcaller
from tkinter import *
from textwrap import dedent

from tkml.grammar import tkml_tree
from tkml.component import comb_for_components as simplify, TKMLFilter

# TDD in reverse -> haven't written the tests yet
# but already importing from them - *time pincer*
from test_wisp5 import first, last, nexx, prev

# TDD the opposite way -> forwards, from the test to the usage
from test_leafstyle import style_file_to_dict as loadstyle

import tkinter as tk


class Mode(Enum):
    Normal = 1
    Insert = 2


class Context:
    def __init__(self):
        self.mode = Mode.Normal
        self.leaves = []
        self.focused = None


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


def create_app2(spec, context):
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

# only the App gets created, everything before just mapped
source = dedent('''
    Tkml {
        script: 'leafapp.py'
        style: 'leafstyle.toml'
        comps: 'leafcomps.tkml'

        Scrollable {
            Frame {
                id: container

                Canvas {
                    id: viewport
                    Frame { id: content }
                }

                Scrollbar { id: scrollbar }
            }
        }

        Tk {
            Scrollable {
                Leaf { id: l1 text: "Leaf One" }
                Leaf { id: l2 text: "Leaf Two" }
                Leaf { id: l3 text: "Leaf Three" }
            }
        }

    }
''')

def capture_widget_tree(parent):
    widget_info = {"type": str(parent)}
    parts_info = []
    for child in parent.winfo_children():
        parts_info.append(capture_widget_tree(child))
    if parts_info:
        widget_info["parts"] = parts_info

    # Extract specific attributes based on widget type
    # if isinstance(parent, Text): widget_info["text"] = parent.get("1.0", END)
    # elif isinstance(parent, Label) or isinstance(parent, Button):
    #     widget_info["text"] = parent.cget("text")

    return widget_info


def create_widget(spec, base, style, comps):
    t = spec['type']

    if t in comps:
        for pspec in comps[t]['parts']:
            s = style[t]
            w = create_widget(pspec, base, s, comps)
            return w
    else:
        tk_class = getattr(tk, t, None)
        widget = tk_class(base)
        # print(style[t])
        for name, value in spec['props'].items():
            if name == 'id': continue
            print(name, value)
            methodcaller(name, value)(widget)
        for part in spec['parts']:
            subwidget = create_widget(part, widget, style, comps)
        return widget
        


def create_tkml(spec):
    # load files
    # create components
    # run app
    props = spec.get('props', {})
    script_file = props.get('script', '')
    style_file = props.get('style', '')
    comps_file = props.get('comps', '')

    style = loadstyle(style_file)
    parts = spec.get('parts', [])

    def centrifuge(tkml_parts):
        yield from (s for s in tkml_parts if s['type'] == 'Tk')
        yield from (s for s in tkml_parts if s['type'] != 'Tk')
            
    app, *comps = centrifuge(parts)
    compdict = {c['type']: c for c in comps}
    # print(compdict)
    
    # associate widget, state, style

    root = create_widget(app, None, style, compdict)
    # root.mainloop()

    # wtree = capture_widget_tree(root)
    # print(wtree)

    # root_widget.bind('<Key>', lambda e: print(capture_widget_tree(root_widget)))
    # now associate it with styles depending on state



if __name__ == '__main__':
    tree = tkml_tree(source)
    f = TKMLFilter()
    spec = simplify(tree, f)
    # viz_spec(spec)
    create_tkml(spec)
    # print(widget_tree)
    # widget_tree = capture_widget_tree(root_widget)
    # print(widget_tree)

    # context = Context()

    # F(Frame, style) -> widget

    
