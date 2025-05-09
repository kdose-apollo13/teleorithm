# vbwise/node.py

from typing import Dict, List, Tuple, Optional

class Node:
    """
    Represents a single node in the knowledge graph.
    """
    def __init__(self,
                 id: str,
                 title: Optional[str] = None,
                 content_lines: Optional[List[Tuple[str, str]]] = None,
                 links: Optional[Dict[str, str]] = None,
                 tags: Optional[List[str]] = None,
                 meta: Optional[Dict[str, str]] = None):
        """
        Initializes a Node object.

        Args:
            id: The unique identifier for the node.
            title: An optional title for the node. If None, might default to ID.
            content_lines: A list of tuples, where each tuple is (TYPE, TEXT).
                           TYPE can be 'T1', 'T2', 'T3' for text, 'C1', 'C2', 'C3' for code.
                           Example: [('T1', 'This is a text line.'), ('C1', 'print("Hello")')]
            links: A dictionary of outbound links from this node.
                   Keys are link types (e.g., 'next', 'prev', 'related'),
                   Values are target node IDs. Example: {'next': 'node_id_2'}
            tags: A list of string tags associated with the node.
            meta: A dictionary for any other metadata (key-value string pairs).
        """
        self.id: str = id
        self.title: str = title if title is not None else ""
        self.content_lines: List[Tuple[str, str]] = content_lines if content_lines is not None else []
        self.links: Dict[str, str] = links if links is not None else {}
        self.tags: List[str] = tags if tags is not None else []
        self.meta: Dict[str, str] = meta if meta is not None else {}

    def __repr__(self) -> str:
        return f"Node(id='{self.id}', title='{self.title}', " \
               f"content_lines={len(self.content_lines)}, links={len(self.links)}, " \
               f"tags={len(self.tags)}, meta={len(self.meta)})"


