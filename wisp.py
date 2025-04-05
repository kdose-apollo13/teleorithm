from unittest import main, TestCase
from klab.lab import measure
from klab.ututils import Spec, Runner

import ast
from tokenize import tokenize

from tkinter import *
from textwrap import dedent

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


# with open('tkml.gram', 'rt') as r:
#     tkml_spec = r.read()

tkml_spec = r'''
tkml        = ws block ws
block       = identifier ws '{' ws item* ws '}'
item        = (binding / property / block) ws
property    = identifier ws ':' ws value
binding     = '|' identifier '|' ws '>>' ws identifier
value       = identifier / color / number
identifier  = ~'[a-zA-Z_][a-zA-Z0-9_]*'
color       = '#' ~'[a-zA-Z0-9]{6}'
number      = ~'[0-9]+'
ws          = ~'\\s*'
'''

grammar = Grammar(tkml_spec)

tkml = '''
Tk {
    location: right_half

    Canvas {
        row: 0
        col: 0
        width: 200
        height: 100
        highlightthickness: 0
        background: #334433
    }

    Canvas { 
        row: 0
        col: 1
        width: 300
        height: 300
        highlightthickness: 0
        background: #DD22FF
    }

    |Tab| >> on_Tab
}
'''

tree = grammar.parse(tkml)
# print(tree)

class Node:
    def __init__(self, name, binds, props, childs):
        self.name = name
        self.binds = binds
        self.props = props
        self.childs = childs

    def __repr__(self):
        return f'Node({self.name}, {self.childs})'


class TKMLVisitor(NodeVisitor):
    def visit_tkml(self, node, visited):
        return visited[1]

    def visit_block(self, node, visited):
        name = visited[0]
        items = visited[4]
        binds = {}
        props = {}
        childs = []
        for item in items:
            match item:
                case 'bind', key, value:
                    binds[key] = value
                case 'prop', key, value:
                    props[key] = value
                case _:
                    childs.append(item)
                    
        return Node(name, binds, props, childs)

    def visit_item(self, node, visited):
        item = visited[0][0]
        return item

    def visit_property(self, node, visited):
        key = visited[0]
        value = visited[4]
        return ('prop', key, value)

    def visit_binding(self, node, visited):
        key = visited[1]
        value = visited[6]
        return ('bind', key, value)

    def visit_value(self, node, visited):
        val = visited[0]
        return val

    def visit_identifier(self, node, visited):
        return node.text

    def visit_color(self, node, visited):
        return node.text

    def visit_number(self, node, visited):
        return int(node.text)

    def generic_visit(self, node, visited):
        return visited or node
        

visitor = TKMLVisitor()
ast = visitor.visit(tree)
# print(ast)


def parse_tkml_ast(buffer, name_it, node, parent):
    """
        buffer
            : io.StringIO

        name_it
            : Iterator
            : some infinite sequence of suffixes for unique widget names

        node:
            : Node

        parent
            : str
            : name of tk parent widget or None for root
    """
    if node.name == 'Tk':
        code = dedent('''
        from tkinter import *
        from queue import Queue

        Q = Queue()
        root = Tk()
        ''')
        buf.write(code)

        if 'location' in node.props:
            code = dedent('''
            w_screen = root.winfo_screenwidth()
            h_screen = root.winfo_screenheight()
            w = w_screen // 2
            h = h_screen - 70
            x = w_screen // 2
            y = 0
            geo = f'{w}x{h}+{x}+{y}'
            root.geometry(geo)
            ''')
            buf.write(code)

        for c in node.childs:
            if isinstance(c, tuple):
                raise Exception('fff')
            parse_tkml_ast(buf, name_it, c, 'root')

        coda = dedent(f'''
        def safe_close():
            print('hellogoodbye!')
            root.destroy()
        root.protocol('WM_DELETE_WINDOW', safe_close)
        
        def on_Tab(e):
            print(e)
        root.bind('<Tab>', on_Tab)
        
        root.mainloop()
        ''')
        buf.write(coda)

        return buf.getvalue()

    elif node.name == 'Canvas':
        suffix = next(name_it)
        name = f'canvas_{suffix}'
        props = node.props
        code = dedent(f'''
        {name} = Canvas({parent})
        {name}.grid(row={props['row']}, column={props['col']})
        {name}.config(
            background="{props['background']}",
            width={props['width']},
            height={props['height']}
        )
        ''')
        buf.write(code)

        for c in node.childs:
            parse_tkml_ast(buf, name_it, c, name)
    
from io import StringIO
from itertools import count

buf = StringIO()
tk_code = parse_tkml_ast(buf, count(start=1), ast, parent=None)
print(tk_code)
exec(tk_code)


if __name__ == '__main__':
    main(testRunner=Runner)


