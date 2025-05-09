from parsimonious.grammar import Grammar
from parsimonious.exceptions import ParseError
from parsimonious.nodes import NodeVisitor

NODE_GRAMMAR = r'''
file = ws (node_def ws)*
node_def = node_start sp id_line sp content_lines sp node_end
node_start = "### NODE" sp newline
id_line = "---" sp "id" sp ":" sp complex_identifier sp newline
node_end = "### ENDNODE" sp newline
content_lines = content_line*
content_line = meta_line / tags_line / next_line / prev_line / text_line / code_line
meta_line = "---" sp "meta" sp ":" sp key_value_list* sp newline
tags_line = "---" sp "tags" sp ":" sp identifier_list* sp newline
next_line = "---" sp "next" sp ":" sp complex_identifier_list* sp newline
prev_line = "---" sp "prev" sp ":" sp complex_identifier_list* sp newline

text_line = text_level ">" sp text_content sp newline
text_level = "T" ~r"[1-3]"
text_content = ~r"[^\n]*"

code_line = code_level ">" sp code_content sp newline
code_level = "C" ~r"[1-3]"
code_content = ~r"[^\n]*"

identifier_list = identifier (sp "," sp identifier)*
key_value_list = key_value (sp "," sp key_value)*
key_value = identifier sp "=" sp identifier
complex_identifier_list = complex_identifier (sp "," sp complex_identifier)*
complex_identifier = identifier ( "." identifier )*
identifier = ~r"[a-zA-Z0-9_]+"
ws = ~r"[\r\n\t ]*"
sp = ~r"[ \t]*"
newline = "\n"
'''

class NodeGrammar(Grammar):
    def __init__(self):
        super().__init__(NODE_GRAMMAR)

    def parse(self, text: str):
        try:
            return super().parse(text)
        except ParseError as e:
            pos = e.pos
            ctx = text[max(0, pos-20):pos+20]
            raise ValueError(f'invalid spec at {pos}. Context: ...{ctx}...')

class NodeDataVisitor(NodeVisitor):
    def visit_file(self, node, visited_children):
        nodes = []
        if len(visited_children) > 1 and visited_children[1]:
            for node_def_result, _ in visited_children[1]:
                if node_def_result is not None:
                    nodes.append(node_def_result)
        return nodes

    def visit_node_def(self, node, visited_children):
        id_data = visited_children[2]
        content_data = visited_children[4]
        return {
            'id': id_data,
            'meta': content_data.get('meta', {}),
            'tags': content_data.get('tags', []),
            'next': content_data.get('next', []),
            'prev': content_data.get('prev', []),
            'text_lines': content_data.get('text_lines', []),
            'code_lines': content_data.get('code_lines', [])
        }

    def visit_node_start(self, node, visited_children):
        return None

    def visit_id_line(self, node, visited_children):
        return visited_children[6]

    def visit_content_lines(self, node, visited_children):
        content_data = {'meta': {}, 'tags': [], 'next': [], 'prev': [], 'text_lines': [], 'code_lines': []}
        for line_data in visited_children:
            if line_data:
                for key, value in line_data.items():
                    if isinstance(value, list):
                        content_data[key].extend(value)
                    else:
                        content_data[key].update(value)
        return content_data

    def visit_content_line(self, node, visited_children):
        return visited_children[0]

    def visit_meta_line(self, node, visited_children):
        kv_list_result = visited_children[6][0] if len(visited_children) > 6 and visited_children[6] else {}
        return {'meta': kv_list_result}

    def visit_tags_line(self, node, visited_children):
        id_list_result = visited_children[6][0] if len(visited_children) > 6 and visited_children[6] else []
        return {'tags': id_list_result}

    def visit_next_line(self, node, visited_children):
        complex_id_list_result = visited_children[6][0] if len(visited_children) > 6 and visited_children[6] else []
        return {'next': complex_id_list_result}

    def visit_prev_line(self, node, visited_children):
        complex_id_list_result = visited_children[6][0] if len(visited_children) > 6 and visited_children[6] else []
        return {'prev': complex_id_list_result}

    def visit_text_line(self, node, visited_children):
        level = visited_children[0]
        content = visited_children[3]
        return {'text_lines': [{'level': level, 'content': content}]}

    def visit_text_level(self, node, visited_children):
        return node.text

    def visit_text_content(self, node, visited_children):
        return node.text


    def visit_code_line(self, node, visited_children):
        level = visited_children[0]
        content = visited_children[3]
        return {'code_lines': [{'level': level, 'content': content}]}

    def visit_code_level(self, node, visited_children):
        return node.text

    def visit_code_content(self, node, visited_children):
        return node.text



    def visit_identifier_list(self, node, visited_children):
        identifiers = [visited_children[0]] if visited_children[0] is not None else []
        if len(visited_children) > 1 and visited_children[1]:
            for _, _, _, id_result in visited_children[1]:
                if id_result is not None:
                    identifiers.append(id_result)
        return identifiers

    def visit_key_value_list(self, node, visited_children):
        kv_dict = visited_children[0] or {}
        if len(visited_children) > 1 and visited_children[1]:
            for _, _, _, kv_result in visited_children[1]:
                if kv_result:
                    kv_dict.update(kv_result)
        return kv_dict

    def visit_key_value(self, node, visited_children):
        return {visited_children[0]: visited_children[4]}

    def visit_complex_identifier_list(self, node, visited_children):
        complex_identifiers = [visited_children[0]] if visited_children[0] is not None else []
        if len(visited_children) > 1 and visited_children[1]:
            for _, _, _, complex_id_result in visited_children[1]:
                if complex_id_result is not None:
                    complex_identifiers.append(complex_id_result)
        return complex_identifiers

    def visit_complex_identifier(self, node, visited_children):
        full_id = visited_children[0]
        if len(visited_children) > 1 and visited_children[1]:
            for _, id_result in visited_children[1]:
                if id_result is not None:
                    full_id += "." + id_result
        return full_id

    def visit_identifier(self, node, visited_children):
        return node.text

    def generic_visit(self, node, visited_children):
        return visited_children or node.text

if __name__ == '__main__':
    sample = '''
### NODE
--- id: first.node.id
--- meta: key1=value1, key2=value2
--- tags: tag1, tag2, another_tag
T3> a truth
T1> fukyah
T3> between two lies
--- next: second_node.part1, third.node
--- prev: previous.node
### ENDNODE

### NODE
--- id: second_node
--- tags: single_tag
--- meta:
--- next:
--- prev: first.node.id
### ENDNODE

### NODE
--- id: third.node.with.more.parts
T1> some text line of level 1
T2> another line of level 2..
T3> a line of level 3
T1> lines can be toggled in some editor by flags eg v111 means all shown
--- next:
--- prev:
### ENDNODE

### NODE
--- id: third.node.with.more.parts
T1> def less(big_list, n=100):
T1>     z = zip(* [iter(big_list)] * n )
T1>     for t in z:
T1>         print(*t, sep='\\n')
T1>         if input() == 'q':
T1>             break
--- next:
--- prev:
### ENDNODE

'''
    try:
        print("Parsing sample...")
        parse_tree = NodeGrammar().parse(sample)
        print("Parse successful!")
        visitor = NodeDataVisitor()
        node_data_list = visitor.visit(parse_tree)
        import json
        print("\nExtracted Node Data:")
        print(json.dumps(node_data_list, indent=2))
    except ValueError as e:
        print("Parse failed:", e)

