from tkml.grammar import tkml_tree
from tkml.tkmlvisitor import TKMLVisitor
from tkml.component import rebuild
from tkml import wrapped_methods

import tkinter


def build_widget(comp, base):
    """
        comp
            : dict
            : {
                'type': _,
                'props': { method_name: kwargs_dict },
                'parts': _
              }

        base
            : tkinter.Widget

        returns
            > tkinter.Widget
    """
    type_name = comp['type']
    tk_class = getattr(tkinter, type_name)
    widget = tk_class(base)

    options = comp['props']
    for name, opt in options.items():
        method = getattr(wrapped_methods, name, None)
        method(widget, opt)

    for part in comp['parts']:
        return build_widget(part, widget)

    return widget


if __name__ == '__main__':
    pass

