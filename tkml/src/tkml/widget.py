from tkml.grammar import tkml_tree
from tkml.tkmlvisitor import TKMLVisitor
from tkml.component import rebuild
from tkml import wrapped_methods
from tkml.utils import overwrite_dict
from tkml.errors import TkmlError

import tkinter


def apply_props(comp_props, w):
    """
        comp_props
            : dict
            : {method_name: kwargs_dict, ...}

        w
            : tkinter.Widget
        
        modifies
            ~ widget, calls methods on it, changing who knows what

        raises
            ! TkmlError
    """
    for n, a in comp_props.items():
        if n == 'grid_rowconfigure':
            w.grid_rowconfigure(a['row'], weight=a['weight'])
        elif n == 'grid_columnconfigure':
            w.grid_columnconfigure(a['col'], weight=a['weight'])
        elif n == 'grid':
            w.grid(row=a['row'], column=a['column'], sticky=a['sticky'])
        elif n == 'config':
            w.config(**a)
        elif n == 'bind':
            w.bind(a['event'], a['callback'])
        elif n == 'title':
            w.title(a)
        elif n == 'geometry':
            w.geometry(a)
        elif n == 'text':
            w.delete('1.0', tkinter.END)
            w.insert('1.0', s)
        elif n == 'create_window':
            print(n)
        elif n == 'id':
            # print(n)
            continue
        else:
            # print(n)
            continue


if __name__ == '__main__':
    root_app = {
        'type': 'App',
        'props': {
            # 'title': 'align failure successwise',
            # 'geometry': '400x900'
        },
        'parts': []
    }
    comp_defs = [
        {
            'type': 'App',
            'props': {},
            'parts': [{'type': 'Tk', 'props': {}, 'parts': []}]
        }
    ]
    styles = {'Default': {'App': {'title': 'blah', 'geometry': '600x900'}}}
    style = styles['Default']
    widget = build_widget(root_app, comp_defs, style, None)
    widget.mainloop()

