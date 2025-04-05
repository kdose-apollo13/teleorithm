import ast
from io import BytesIO
import token
from tokenize import tokenize


code = '''\
x = 2
@decorated
def billowize():
    def inside():
        return 23
    return inside
limbo = lambda: print('nothing')
class Thing:
    type = 5
t = Thing()
t.type.whatever = 4
'''

t = ast.parse(code)
nodes = list(ast.walk(t))
# print(*nodes, sep='\n')

def valid_nodes():
    no = ['AST', 'Index', 'ExtSlice', 'Num', 'Str', 'Bytes', '_ast_Ellipsis']
    for name in filter(lambda n: n not in no, dir(ast)):
        attr = getattr(ast, name)
        try:
            if issubclass(attr, ast.AST):
                yield attr
        except TypeError:
            continue

# nodes = list(valid_nodes())

# sa = set(dir(ast.AST()))
# so = set(dir(object()))
# diffs = set()

def node_span(node):
    try:
        offset_a = getattr(node, 'col_offset')
        offset_b = getattr(node, 'end_col_offset')
        line_a = getattr(node, 'lineno')
        line_b = getattr(node, 'end_lineno')
    except AttributeError:
        return
    else:
        return (node, (line_a, offset_a), (line_b, offset_b))

def token_span(t):
    return (token.tok_name[t.type], t.start, t.end)

reader = BytesIO(code.encode()).readline
tokens = list(tokenize(reader))
# print(*tokens, sep='\n')
# tok = tokens[12]

# spans = [find_span(n) for n in nodes if find_span(n) is not None]
node_spans = [s for n in nodes if (s := node_span(n))]
# print(*node_spans, sep='\n')

token_spans = [token_span(t) for t in tokens]
# print(*token_spans, sep='\n')

# func_node_spans = [s for s in node_spans if isinstance(s[0], ast.FunctionDef)]
# func_names = [s[0].name for s in func_node_spans]
# print(func_node_spans)
# print(func_names)
# func_name_starts = [(s[1][0], s[1][1] + 4) for s in func_node_spans]
# print(func_name_starts)
# func_name_tokens = [t for t in token_spans if t[1] in func_name_starts]
# print(func_name_tokens)
# func_name_locations = [
#     (f'{t[1][0]}.{t[1][1]}', f'{t[2][0]}.{t[2][1]}') for t in func_name_tokens
# ]
# print(func_name_locations)

attribute_spans = [s for s in node_spans if isinstance(s[0], ast.Attribute)]
print(attribute_spans)

