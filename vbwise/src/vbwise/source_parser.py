# vbwise/source_parser.py

from typing import Dict, List, Any, Optional

from vbwise.node import Node
from vbwise.gramjam import NodeGrammar, NodeDataVisitor, ParseError # Added ParseError

def parse_source_string_to_nodes(source_string: str) -> Dict[str, Node]:
    """
    Parses a source string using NodeGrammar and NodeDataVisitor,
    then transforms the result into a dictionary of Node objects.

    Args:
        source_string: The string containing node definitions in gramjam format.

    Returns:
        A dictionary where keys are node IDs and values are Node objects.
        Returns an empty dictionary if parsing fails or no nodes are found.
    
    Raises:
        ValueError: If parsing fails due to grammar issues.
    """
    if not source_string.strip():
        return {}

    grammar = NodeGrammar()
    visitor = NodeDataVisitor()
    
    try:
        parse_tree = grammar.parse(source_string)
        raw_nodes_data_list: List[Dict[str, Any]] = visitor.visit(parse_tree)
    except ValueError as e: # Catching specific ValueError from NodeGrammar.parse
        # Re-raise or handle as appropriate for the application
        # For now, let's print and return empty, or re-raise
        print(f"Error parsing source string with gramjam: {e}")
        # raise # Or return {} to indicate failure to the caller
        return {} # Or create a single error node
    except Exception as e_gen: # Catch other potential errors during parsing/visiting
        print(f"An unexpected error occurred during parsing: {e_gen}")
        import traceback
        traceback.print_exc()
        return {}


    nodes_dict: Dict[str, Node] = {}

    if not raw_nodes_data_list:
        return {}

    for raw_node_data in raw_nodes_data_list:
        node_id = raw_node_data.get('id')
        if not node_id:
            print(f"Warning: Found a node structure without an ID. Skipping: {raw_node_data}")
            continue

        title = raw_node_data.get('title') # This can be None if not provided

        # content_lines are already List[Tuple[str, str]] from the updated visitor
        content_lines = raw_node_data.get('content_lines', [])

        # Process links: gramjam provides lists for 'next' and 'prev'.
        # The Node class expects a Dict[str, str] where keys are link types.
        # We'll take the first item from 'next' and 'prev' lists if they exist.
        links: Dict[str, str] = {}
        next_nodes_list: Optional[List[str]] = raw_node_data.get('next')
        if next_nodes_list and len(next_nodes_list) > 0:
            links['next'] = next_nodes_list[0] # Taking the first 'next' link

        prev_nodes_list: Optional[List[str]] = raw_node_data.get('prev')
        if prev_nodes_list and len(prev_nodes_list) > 0:
            links['prev'] = prev_nodes_list[0] # Taking the first 'prev' link
        
        # Potentially, other links could be defined in meta, e.g., meta['link_custom'] = 'node_id'
        # For now, only 'next' and 'prev' from dedicated lines are processed into Node.links.
        # The full meta dictionary is preserved in Node.meta.

        tags: List[str] = raw_node_data.get('tags', [])
        meta: Dict[str, str] = raw_node_data.get('meta', {})

        # Create the Node object
        node_obj = Node(
            id=node_id,
            title=title, # Pass None if not present, Node constructor handles it
            content_lines=content_lines,
            links=links,
            tags=tags,
            meta=meta
        )
        
        if node_id in nodes_dict:
            print(f"Warning: Duplicate node ID '{node_id}' found. Overwriting previous definition.")
        nodes_dict[node_id] = node_obj

    return nodes_dict

# Example usage (can be removed or kept for testing)
if __name__ == '__main__':
    sample_initial_content = """
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
--- id: fourth.node.with.more.parts
T1> def less(big_list, n=100):
T1>     z = zip(* [iter(big_list)] * n )
T1>     for t in z:
T1>         print(*t, sep='\\n')
T1>         if input() == 'q':
T1>             break
--- next:
--- prev:
### ENDNODE

    """
    print("--- Parsing Sample Initial Content ---")
    parsed_nodes = parse_source_string_to_nodes(sample_initial_content)

    if parsed_nodes:
        for node_id, node_instance in parsed_nodes.items():
            print(f"\nSuccessfully parsed Node ID: {node_id}")
            print(f"  Title: {node_instance.title}")
            print(f"  Content Lines ({len(node_instance.content_lines)}):")
            for c_type, c_text in node_instance.content_lines:
                print(f"    {c_type}: {c_text[:50]}{'...' if len(c_text)>50 else ''}")
            print(f"  Links: {node_instance.links}")
            print(f"  Tags: {node_instance.tags}")
            print(f"  Meta: {node_instance.meta}")
    else:
        print("\nNo nodes were parsed from the sample content, or an error occurred.")

    print("\n--- Parsing Empty String ---")
    empty_nodes = parse_source_string_to_nodes("")
    print(f"Parsed from empty string: {empty_nodes}")

    print("\n--- Parsing Malformed String ---")
    malformed_content = """
### NODE
--- id: broken
T1> This node is not properly ended.
    """
    # This will now print an error message from parse_source_string_to_nodes
    # (due to the try-except block there) and return {}
    broken_nodes = parse_source_string_to_nodes(malformed_content)
    print(f"Parsed from malformed string: {broken_nodes}")


