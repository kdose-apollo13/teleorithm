# vbwise/source_parser.py

import re # Import regular expressions for more robust parsing
import sys # For stderr

from vbwise.node import Node

def parse_source_string_to_nodes(source_string: str) -> dict[str, Node]:
    """
    Parses the custom source string format into a dictionary of Node objects.

    Source format:
    ### NODE: <unique_node_id>
    # <Optional Node Title>
    --- metadata: key=value, ... ---
    L# > Line content... (# is digit)
    TXT> Line content...
    CODE> Line content...
    --- links: link_type=target_id, ... ---
    ### ENDNODE
    ... (next node) ...
    """
    print("Parsing source string...")
    nodes = {} # type: dict[str, Node]
    current_node_id = None
    current_title = ""
    current_metadata = {}
    current_content_lines = []
    current_links = {}
    in_node = False

    # Use regex to find node boundaries and extract ID
    node_start_pattern = re.compile(r"### NODE:\s*(\S+)") # Capture one or more non-whitespace chars as ID

    lines = source_string.splitlines()

    for i, line in enumerate(lines):
        stripped_line = line.strip() # Process stripped line, keep original for content potentially

        # --- Check for Node Boundaries ---
        start_match = node_start_pattern.match(stripped_line)
        if start_match:
            if in_node and current_node_id:
                # Found a new node marker before the end of the previous one
                print(f"Warning: Node start marker found before ENDNODE at line {i+1}. Saving previous node '{current_node_id}'.", file=sys.stderr)
                # Save the previous node
                nodes[current_node_id] = Node(
                    id=current_node_id,
                    title=current_title,
                    metadata=current_metadata,
                    content_lines=current_content_lines,
                    links=current_links
                )

            # Reset for the new node and extract ID
            current_node_id = start_match.group(1) # This captures the ID correctly
            current_title = ""
            current_metadata = {}
            current_content_lines = []
            current_links = {}
            in_node = True
            print(f"Starting parse of node: {current_node_id}")
            continue # Move to the next line after processing the start marker

        elif stripped_line == "### ENDNODE":
            if in_node and current_node_id:
                print(f"Ending parse of node: {current_node_id}")
                # Save the completed node
                nodes[current_node_id] = Node(
                    id=current_node_id,
                    title=current_title,
                    metadata=current_metadata,
                    content_lines=current_content_lines,
                    links=current_links
                )
                # Reset for the next potential node
                current_node_id = None
                current_title = ""
                current_metadata = {}
                current_content_lines = []
                current_links = {}
                in_node = False
                continue # Move to the next line

            elif in_node:
                 print(f"Warning: ENDNODE found at line {i+1} but no current node ID was set. Likely previous parse error.", file=sys.stderr)
                 # Reset anyway just in case
                 current_node_id = None
                 current_title = ""
                 current_metadata = {}
                 current_content_lines = []
                 current_links = {}
                 in_node = False
                 continue # Move to the next line

            else:
                print(f"Warning: ENDNODE found at line {i+1} outside of a node block. Ignoring.", file=sys.stderr)
                continue # Ignore line

        # --- Parse Content and Metadata within a Node ---
        if in_node:
            if stripped_line.startswith("# "): # Title line
                 current_title = stripped_line[2:].strip()
                 continue # Move to the next line

            elif stripped_line.startswith("--- metadata:"): # Metadata line
                 meta_str = stripped_line[len("--- metadata:"):].strip().rstrip("---").strip()
                 if meta_str:
                      try:
                         # Split by comma, then by the first equals sign
                         meta_pairs = [pair.strip() for pair in meta_str.split(',')]
                         for pair in meta_pairs:
                             if '=' in pair:
                                 key, value = pair.split('=', 1)
                                 key = key.strip()
                                 value = value.strip()
                                 if key:
                                     current_metadata[key] = value
                             else:
                                 # Handle cases like just "tag1" or malformed pairs
                                 if pair: # If not just empty string after strip
                                     print(f"Warning: Malformed metadata pair '{pair}' in node '{current_node_id}' at line {i+1}. Ignoring.", file=sys.stderr)
                      except Exception as e:
                         print(f"Error parsing metadata in node '{current_node_id}' at line {i+1}: {e}", file=sys.stderr)
                 continue # Move to the next line

            elif stripped_line.startswith("--- links:"): # Links line
                 links_str = stripped_line[len("--- links:"):].strip().rstrip("---").strip()
                 if links_str:
                      try:
                         # Split by comma, then by the first equals sign
                         link_pairs = [pair.strip() for pair in links_str.split(',')]
                         for pair in link_pairs:
                             if '=' in pair:
                                 link_type, target_id = pair.split('=', 1)
                                 link_type = link_type.strip()
                                 target_id = target_id.strip()
                                 if link_type and target_id:
                                     current_links[link_type] = target_id
                             else:
                                  if pair:
                                      print(f"Warning: Malformed link pair '{pair}' in node '{current_node_id}' at line {i+1}. Ignoring.", file=sys.stderr)
                      except Exception as e:
                         print(f"Error parsing links in node '{current_node_id}' at line {i+1}: {e}", file=sys.stderr)
                 continue # Move to the next line

            elif stripped_line: # Treat any other non-empty line as content
                # Robust prefix detection (L#, TXT, CODE) followed by optional space and >
                prefix_match = re.match(r"^(L\d+|TXT|CODE)\s*>", stripped_line, re.IGNORECASE) # Case-insensitive match for prefix

                prefix = "TXT" # Default prefix if none matched
                content = line # Use original line content to preserve leading/trailing spaces if needed (or use stripped_line)

                if prefix_match:
                    matched_prefix_raw = prefix_match.group(1)
                    prefix = matched_prefix_raw.upper() # Store prefix as uppercase standard
                    # Content is the rest of the line after the prefix and '>'
                    content_start_index = prefix_match.end() # Index right after the '>'
                    content = line[content_start_index:].lstrip() # Get rest of original line, strip leading space

                current_content_lines.append((prefix, content))
                # Do NOT continue here, process this line as content and then loop to next line

            # Ignore empty lines if in_node


    # Handle case where the last node doesn't have an ENDNODE marker (optional but good practice)
    if in_node and current_node_id:
         print(f"Warning: Source ended while parsing node '{current_node_id}'. Saving it.", file=sys.stderr)
         nodes[current_node_id] = Node(
             id=current_node_id,
             title=current_title,
             metadata=current_metadata,
             content_lines=current_content_lines,
             links=current_links
         )

    print(f"Finished parsing. Found {len(nodes)} nodes.")
    return nodes


# Example Usage (for testing the parser in isolation)
if __name__ == "__main__":
    example_source = """
### NODE: first_node
# Getting Started
--- metadata: version=1.0, status=draft, tags=example ---
TXT> Welcome to the first node.
L1> This is essential point 1.
L2> Here's more detail for point 1.
CODE> print("Hello world!")
--- links: next=second_node, related=intro_topic ---
### ENDNODE

### NODE: second_node
# Next Steps
TXT> Now that you've seen the first node, let's look at the next steps.
L1> Point 2.
L2> More detail on point 2.
--- links: prev=first_node ---
### ENDNODE

### NODE: another_node
# Just another node
TXT> This node has no specific links or metadata.
L1> A point here.
L3> Very detailed point.
CODE> def my_func():
CODE>     pass
### ENDNODE

# This line should be ignored
    """

    parsed_nodes = parse_source_string_to_nodes(example_source)

    print("\n--- Parsed Nodes Summary ---")
    if parsed_nodes:
        for node_id, node in parsed_nodes.items():
            print(f"\nNode ID: {node.id}")
            print(f"  Title: {node.title}")
            print(f"  Metadata: {node.metadata}")
            print(f"  Links: {node.links}")
            print(f"  Content Lines ({len(node.content_lines)}):")
            # Print content lines including their parsed prefixes
            for prefix, line_text in node.content_lines:
                print(f"    [{prefix}] {line_text}")
    else:
        print("No nodes were parsed.")

