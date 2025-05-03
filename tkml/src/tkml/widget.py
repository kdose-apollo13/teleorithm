from tkml.grammar import tkml_tree
from tkml.tkmlvisitor import TKMLVisitor
from tkml.component import rebuild
from tkml import wrapped_methods

import tkinter


class TkmlException(Exception):
    pass


def unconfigured_widget(comp_type, base):
    """
        comp_type
            : str
            : 'Frame'

        base
            : tkinter.Widget

        returns
            > tkinter.Widget

        raises
            ! TkmlException
    """
    try:
        tk_class = getattr(tkinter, comp_type)
    except AttributeError as e:
        raise TkmlException(f'tk class not found -> {comp_type}') from e
    else:
        widget = tk_class(base)
        return widget


def apply_props(comp_props, widget):
    """
        comp_props
            : dict
            : {method_name: kwargs_dict, ...}

        widget
            : tkinter.Widget
        
        modifies
            ~ widget, calls methods on it, changing who knows what

        raises
            ! TkmlException
    """
    for name, kwargs in comp_props.items():
        try:
            method = getattr(wrapped_methods, name, None)
        except AttributeError as e:
            raise TkmlException(f'could not find method {name}') from e
        else:
            method(widget, kwargs)


def build_widget(comp, base):
    widget = unconfigured_widget(comp['type'], base)
    apply_props(comp['props'], widget)
    for part in comp['parts']:
        return build_widget(part, widget)

    return widget


if __name__ == '__main__':
    root = tkinter.Tk()
    comp = {'type': 'Frame', 'props': {'config': {'bg': '#123123'}}, 'parts': []}
    build_widget(comp, root)
    # root.mainloop()

