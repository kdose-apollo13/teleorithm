"""
    | teleorithm |

    in grammar, ( x / y ) induces a list
    that is why [0] in some visit methods
"""
from parsimonious.nodes import NodeVisitor
from parsimonious.exceptions import VisitationError

from vbwise.tkmlgrammar import tkml_tree


class TKMLVisitor(NodeVisitor):
    """
        walks Node (tree) for components
    """
    def visit_tkml(self, node, visited):
        return visited[1]

    def visit_block(self, node, visited):
        # block = identifier _ LBRACE _ block_member_list _ RBRACE
        block_type_name = visited[0]  # Result of visit_identifier
        member_results = visited[4]   # Result of visit_block_member_list

        props = {}
        parts = []
        for member in member_results:
            if isinstance(member, dict):
                # Check for our canonical block structure
                if 'type' in member and 'props' in member and 'parts' in member:
                    # Check if the 'type' came from a identifier visit (is a string)
                    if isinstance(member.get('type'), str):
                         parts.append(member)
                    else: # Should not happen if grammar & identifier visitor are correct
                         props.update(member) # Treat as prop if type is not a string
                else: # It's a property {key: value}
                    props.update(member)
        return {'type': block_type_name, 'props': props, 'parts': parts}

    def visit_block_member_list(self, node, visited):
        return visited

    def visit_block_member_entry(self, node, visited):
        return visited[0]

    def visit_block_member(self, node, visited):
        return visited[0]

    def visit_prop(self, node, visited):
        # prop = identifier _ COLON _ value
        key = visited[0]    # Result of visit_identifier
        value = visited[4]  # Result of visit_value
        return {key: value}

    def visit_value(self, node, visited):
        # value = prop_group / string / number / color / identifier
        return visited[0]

    def visit_prop_group(self, node, visited):
        # prop_group = LBRACE _ prop_entry_list _ RBRACE
        entry_results = visited[2] # Result of visit_prop_entry_list
        props_dict = {}
        for entry in entry_results:
            props_dict.update(entry)
        return props_dict

    def visit_prop_entry_list(self, node, visited):
        return visited

    def visit_prop_entry_item(self, node, visited):
        return visited[0]

    def visit_prop_entry(self, node, visited):
        # prop_entry = identifier _ COLON _ value
        key = visited[0]    # Result of visit_identifier
        value = visited[4]  # Result of visit_value
        return {key: value}

    def visit_identifier(self, node, visited): # For simple values that are identifiers
        t = node.text
        try:
            n = int(t)
        except ValueError:
            pass
        else:
            return n

        try:
            n = float(t)
        except ValueError:
            pass
        else:
            return n

        return t

    def visit_string(self, node, visited):
        t = node.text
        # Strip quotes and handle basic escapes
        if t.startswith('"') and t.endswith('"'):
            return t[1:-1].replace(r'\"', '"').replace(r'\\', '\\')
        elif t.startswith("'") and t.endswith("'"):
            return t[1:-1].replace(r"\'", "'").replace(r'\\', '\\')
        return t # Should not happen

    def visit_number(self, node, visited):
        t = node.text
        if '.' in t:
            return float(t)
        else:
            return int(t)

    def visit_color(self, node, visited):
        return node.text
        
    def generic_visit(self, node, visited):
        # unhandled -> LBRACE, _ etc...
        # if len(visited) == 1 and \
        #    not isinstance(visited[0], list) and \
        #    not isinstance(visited[0], Node):
        #     return visited[0]
        return visited or node.text

    def visit(self, tree):
        """
            tree
                : parsimonious.nodes.Node

            returns
                > dict
                > root component - may contain nested components

            raises
                ! parsimonious.exceptions.VisitationError if catastrophic
                ! may succeed despite retrieving bad values
        """
        try:
            root = super().visit(tree)
        except VisitationError as e:
            raise e
        else:
            return root


if __name__ == '__main__':
    # source = 'Block {bind: {<Return>: some.func, x: 2}}'
    source = '''
    Block {
        # comment line
        NestedBlock {}  # with trailing comment

        string: 'a "string" value'
        escaped: "what about \\"this\\" huh?"
        number: 31
        float: 23.529
        color: #AA1122
        dotted.property: 'yeah'

        multi_prop: { v: #123ABC q: 1000.xyz }
        comma_prop: { v: #123ABC, q: 1000, z: X.2 }
        multi_line_prop: {
            foo: 1.2.A.B
            bar: { 0: 1 },
        }

        bind: { <Return>: 'yeah' }

        nested_block {
            0: "digit identifier"
            one.two: "dotted identifier"
            bind: { <Button-1>: callback }
        }
    }
    '''
    source = '''
    Tk {
        id: root
        title: "Elegant Data-Driven Demo"
        geometry: "300x180"
        Frame {
            id: mainFrame
            layout_style: "main_frame_layout"
            Label {
                id: myLabel
                data_bind: { text: "text" }
                style: "label_style"
                layout_style: "label_layout"
            }
            Button {
                id: myButton
                text: "Change Text"
                style: "button_style"
                layout_style: "button_layout"
                bind: { <Button-1>: "toggle_label_state" }
            }
        }
    }
    '''
    tree = tkml_tree(source)
    comps = TKMLVisitor().visit(tree)
    import json
    s = json.dumps(comps, indent=2)
    print(s)

