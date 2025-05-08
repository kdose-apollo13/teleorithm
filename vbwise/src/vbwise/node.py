# node.py

class Node:
    """Represents a single knowledge unit or 'leaf' in the graph."""
    def __init__(self, id, title="", metadata=None, content_lines=None, links=None):
        if not isinstance(id, str) or not id:
            raise ValueError("Node ID must be a non-empty string.")
        self.id = id  # Unique string identifier

        self.title = title # Human-readable title (string)

        # Metadata as a dictionary. e.g., {'tags': 'linux,cli', 'author': 'me'}
        self.metadata = metadata if metadata is not None else {}

        # Content stored as a list of tuples: (prefix, line_text)
        # e.g., [('L1', 'command arg1'), ('TXT', 'Explanation.'), ('CODE', 'print("hello")')]
        # The prefix determines how the line is displayed based on detail level.
        self.content_lines = content_lines if content_lines is not None else []

        # Links to other nodes. Dictionary: {link_type: target_node_id}
        # e.g., {'next': 'node_002', 'related': 'node_999', 'pathway_basic_linux': 'node_010'}
        self.links = links if links is not None else {}

    def __repr__(self):
        # Provides a developer-friendly string representation
        return f"Node(id='{self.id}', title='{self.title}')"

    def get_content_for_display(self, detail_level):
        """Filters content lines based on the given detail level."""
        displayed_content = []
        for prefix, line_text in self.content_lines:
            display = False
            if prefix == 'TXT':
                display = True # Always display general text
            elif prefix == 'CODE':
                # Example logic: Show code from detail level 2 upwards
                if detail_level >= 2:
                     display = True
            elif prefix.startswith('L'):
                try:
                    # L1, L2, L3... based on integer level
                    level = int(prefix[1:])
                    if detail_level >= level:
                        display = True
                except ValueError:
                    # Ignore malformed prefixes, maybe print a warning
                    print(f"Warning: Malformed content prefix '{prefix}' in node '{self.id}'.")
                    pass # Do not display lines with invalid prefixes

            if display:
                displayed_content.append(line_text)
        return displayed_content

# Example Usage (for testing the class in isolation)
if __name__ == "__main__":
    example_node = Node(
        id="test_node_001",
        title="Example Node",
        metadata={"tags": "example"},
        content_lines=[
            ("L1", "Essential command: do_this"),
            ("TXT", "This explains the command briefly."),
            ("L2", "Detailed flag --verbose"),
            ("CODE", "print('example code')"),
            ("L3", "Internal workings detailed here."),
            ("TXT", "End of explanation."),
            ("CODE", "result = process_data()"),
        ],
        links={"next": "test_node_002"}
    )

    print(example_node)
    print("\nContent at Detail Level 1:")
    for line in example_node.get_content_for_display(1):
        print(line)

    print("\nContent at Detail Level 2:")
    for line in example_node.get_content_for_display(2):
        print(line)

    print("\nContent at Detail Level 3:")
    for line in example_node.get_content_for_display(3):
        print(line)
