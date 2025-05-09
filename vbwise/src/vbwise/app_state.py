# vbwise/app_state.py

import sys
import traceback
from typing import Dict, List, Optional, Set, Callable, Self # Use typing_extensions.Self for Python < 3.11

from vbwise.node import Node # Assuming relative import

# Consider moving configuration like this to a dedicated config module/file
VALID_LAYOUTS = ['single', 'split_v_2', 'split_h_2', 'scrolled_list'] # Added 'scrolled_list'
DEFAULT_LAYOUT = 'scrolled_list' # Changed default layout
DEFAULT_DETAIL_LEVEL = 1
MIN_DETAIL_LEVEL = 0 # Example: allow 0 for minimal, 1 for L1, etc.

class AppState:
    """
    Manages the application's data (knowledge graph) and UI/interaction state.

    This class holds core data like nodes, and the current state of the
    application such as selected layout, focused elements, detail levels,
    and active pathways. It uses an observer pattern to notify other
    components (e.g., the GUI) of state changes.
    """

    def __init__(self):
        # --- Core Data ---
        self.all_nodes: Dict[str, Node] = {}

        # --- UI/Interaction State (internal attributes prefixed with '_') ---
        self._layout: str = DEFAULT_LAYOUT 
        self._focused_leaf_id: Optional[str] = None
        self._global_detail_level: int = DEFAULT_DETAIL_LEVEL
        self.leaf_detail_overrides: Dict[str, int] = {} # {node_id: detail_level}
        self.displayed_leaf_ids: List[str] = []
        self.selected_leaf_ids: Set[str] = set()

        # --- Pathway Navigation State ---
        self._active_pathway_link_type: Optional[str] = None
        self._active_pathway_current_node_id: Optional[str] = None

        # --- Observers ---
        self._observers: List[Callable[[AppState, Optional[str], Dict], None]] = []

    # --------------------------------------------------------------------------
    # Observer Pattern
    # --------------------------------------------------------------------------

    def add_observer(
        self, callback: Callable[[Self, Optional[str], Dict], None]
    ) -> None: 
        """Registers a callback function for state change notifications."""
        if callable(callback) and callback not in self._observers:
            self._observers.append(callback)

    def remove_observer(
        self, callback: Callable[[Self, Optional[str], Dict], None]
    ) -> None:
        """Unregisters a callback function."""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self, event_type: Optional[str] = None, **kwargs) -> None:
        """Notifies all registered observers about a state change."""
        for callback in list(self._observers):  # Iterate over a copy
            try:
                callback(self, event_type=event_type, **kwargs)
            except Exception as e:
                print(
                    f"Error in AppState observer {callback.__name__}: {e}",
                    file=sys.stderr
                )
                traceback.print_exc()

    # --------------------------------------------------------------------------
    # Properties for State Attributes
    # --------------------------------------------------------------------------

    @property
    def layout(self) -> str:
        """The current display layout (e.g., 'single', 'scrolled_list')."""
        return self._layout

    @layout.setter
    def layout(self, layout_type: str) -> None:
        if layout_type not in VALID_LAYOUTS:
            raise ValueError(
                f"Invalid layout type: '{layout_type}'. "
                f"Valid types are: {', '.join(VALID_LAYOUTS)}."
            )
        if self._layout != layout_type:
            self._layout = layout_type
            self._notify_observers(event_type="layout_changed")

    @property
    def focused_leaf_id(self) -> Optional[str]:
        """The ID of the leaf widget that currently has input focus."""
        return self._focused_leaf_id

    @focused_leaf_id.setter
    def focused_leaf_id(self, node_id: Optional[str]) -> None:
        if node_id is not None and node_id not in self.all_nodes:
            raise ValueError(
                f"Cannot set focus to non-existent node: '{node_id}'"
            )
        if self._focused_leaf_id != node_id:
            self._focused_leaf_id = node_id
            self._notify_observers(event_type="focused_leaf_changed", node_id=node_id)

    @property
    def global_detail_level(self) -> int:
        """The global default detail level for displaying node content."""
        return self._global_detail_level

    @global_detail_level.setter
    def global_detail_level(self, level: int) -> None:
        if not isinstance(level, int):
            raise TypeError("Global detail level must be an integer.")
        if level < MIN_DETAIL_LEVEL:
            raise ValueError(
                f"Global detail level cannot be less than {MIN_DETAIL_LEVEL}."
            )
        if self._global_detail_level != level:
            self._global_detail_level = level
            if self.leaf_detail_overrides: 
                self.leaf_detail_overrides.clear()
                self._notify_observers(event_type="all_leaf_overrides_cleared")
            self._notify_observers(event_type="global_detail_level_changed")

    # --------------------------------------------------------------------------
    # Methods for Data Loading and Complex State Transformations
    # --------------------------------------------------------------------------

    def load_nodes(self, nodes_data: Dict[str, Node]) -> None:
        """
        Loads a dictionary of Node objects, replacing any existing nodes.
        Resets UI state related to displayed nodes, focus, selection,
        and detail overrides to their defaults.
        """
        self.all_nodes = nodes_data
        self.displayed_leaf_ids = []
        self.focused_leaf_id = None 
        if self.selected_leaf_ids:
            self.selected_leaf_ids.clear()
            self._notify_observers(event_type="selection_changed") 
        if self.leaf_detail_overrides:
            self.leaf_detail_overrides.clear()
            self._notify_observers(event_type="all_leaf_overrides_cleared")

        self._active_pathway_link_type = None
        self._active_pathway_current_node_id = None
        # self.global_detail_level = DEFAULT_DETAIL_LEVEL # Resetting via setter

        self._notify_observers(event_type="data_loaded")

    def update_displayed_leaves(self, node_ids: List[str]) -> None:
        """
        Sets which nodes are currently displayed in the layout, in order.
        """
        valid_ids = [id_ for id_ in node_ids if id_ in self.all_nodes]
        if self.displayed_leaf_ids != valid_ids:
            self.displayed_leaf_ids = valid_ids
            self._notify_observers(event_type="displayed_leaves_changed")

    def set_leaf_detail_override(self, node_id: str, level: int) -> None:
        """
        Sets or updates a specific detail level override for a single leaf.
        """
        if node_id not in self.all_nodes:
            raise ValueError(f"Cannot set override for non-existent node: '{node_id}'")
        if not isinstance(level, int):
            raise TypeError("Detail level override must be an integer.")
        if level < MIN_DETAIL_LEVEL:
            raise ValueError(
                f"Detail level override cannot be less than {MIN_DETAIL_LEVEL}."
            )

        current_override = self.leaf_detail_overrides.get(node_id)
        if current_override != level:
            self.leaf_detail_overrides[node_id] = level
            self._notify_observers(
                event_type="leaf_detail_override_changed", node_id=node_id
            )

    def clear_leaf_detail_override(self, node_id: str) -> None:
        """Removes a detail level override for a single leaf."""
        if node_id in self.leaf_detail_overrides:
            del self.leaf_detail_overrides[node_id]
            self._notify_observers(
                event_type="leaf_detail_override_cleared", node_id=node_id
            )

    def set_selected_leaves_detail_level(self, level: int) -> None:
        """Sets the detail level override for all currently selected leaves."""
        if not self.selected_leaf_ids:
            return 

        if not isinstance(level, int):
            raise TypeError("Detail level for selected must be an integer.")
        if level < MIN_DETAIL_LEVEL:
            raise ValueError(
                f"Detail level for selected cannot be less than {MIN_DETAIL_LEVEL}."
            )

        nodes_changed = []
        for node_id in list(self.selected_leaf_ids): 
            if node_id in self.all_nodes:
                if self.leaf_detail_overrides.get(node_id) != level:
                    self.leaf_detail_overrides[node_id] = level
                    nodes_changed.append(node_id)

        if nodes_changed:
            self._notify_observers(
                event_type="leaf_detail_override_changed_batch",
                node_ids=nodes_changed
            )

    # --------------------------------------------------------------------------
    # Selection Management
    # --------------------------------------------------------------------------

    def select_leaf(self, node_id: str, add_to_selection: bool = False) -> None:
        """
        Selects a leaf. By default, clears existing selection.
        """
        if node_id not in self.all_nodes:
            raise ValueError(f"Cannot select non-existent node: '{node_id}'")

        changed = False
        if not add_to_selection:
            if self.selected_leaf_ids != {node_id}:
                self.selected_leaf_ids.clear()
                self.selected_leaf_ids.add(node_id)
                changed = True
        elif node_id not in self.selected_leaf_ids:
            self.selected_leaf_ids.add(node_id)
            changed = True

        if changed:
            self._notify_observers(event_type="selection_changed")

    def deselect_leaf(self, node_id: str) -> None:
        """Removes a specific node from the current selection."""
        if node_id in self.selected_leaf_ids:
            self.selected_leaf_ids.discard(node_id)
            self._notify_observers(event_type="selection_changed")

    def clear_selection(self) -> None:
        """Clears all currently selected leaves."""
        if self.selected_leaf_ids:
            self.selected_leaf_ids.clear()
            self._notify_observers(event_type="selection_changed")

    def select_all_displayed(self) -> None:
        """Selects all nodes that are currently in `displayed_leaf_ids`."""
        new_selection = {
            node_id for node_id in self.displayed_leaf_ids
            if node_id in self.all_nodes 
        }
        if self.selected_leaf_ids != new_selection:
            self.selected_leaf_ids = new_selection
            self._notify_observers(event_type="selection_changed")

    # --------------------------------------------------------------------------
    # Pathway Navigation
    # --------------------------------------------------------------------------

    @property
    def active_pathway_link_type(self) -> Optional[str]:
        """The link type of the currently active pathway (e.g., 'next')."""
        return self._active_pathway_link_type

    @property
    def active_pathway_current_node_id(self) -> Optional[str]:
        """The ID of the current node within the active pathway."""
        return self._active_pathway_current_node_id

    def start_pathway(
        self, link_type: str, start_node_id: Optional[str] = None
    ) -> None:
        """
        Starts navigating a pathway defined by a link type.
        """
        effective_start_node_id = start_node_id or self._focused_leaf_id
        if not effective_start_node_id or \
           effective_start_node_id not in self.all_nodes:
            raise ValueError(
                f"Cannot start pathway '{link_type}'. "
                f"Invalid start node: '{effective_start_node_id}'."
            )

        self._active_pathway_link_type = link_type
        self._active_pathway_current_node_id = effective_start_node_id

        self.update_displayed_leaves([effective_start_node_id])
        self.focused_leaf_id = effective_start_node_id 
        self.clear_selection() 

        self._notify_observers(
            event_type="pathway_started",
            link_type=link_type,
            start_node_id=effective_start_node_id
        )

    def pathway_next(self) -> None:
        """Moves to the next node in the active pathway, if possible."""
        if not self._active_pathway_link_type or \
           not self._active_pathway_current_node_id:
            self._notify_observers(
                event_type="pathway_navigation_failed",
                direction="next",
                reason="no_active_pathway"
            )
            return

        current_node = self.all_nodes.get(self._active_pathway_current_node_id)
        if not current_node: 
            self.stop_pathway(reason="internal_error_current_node_missing")
            return

        next_node_id = current_node.links.get(self._active_pathway_link_type)
        if next_node_id and next_node_id in self.all_nodes:
            self._active_pathway_current_node_id = next_node_id
            self.update_displayed_leaves([next_node_id])
            self.focused_leaf_id = next_node_id 
            self.clear_selection()
            self._notify_observers(
                event_type="pathway_navigated",
                direction="next",
                new_node_id=next_node_id
            )
        else:
            reason = "broken_link" if next_node_id else "end_of_links"
            self.stop_pathway(reason=reason) 

    def pathway_previous(self) -> None:
        """Moves to the previous node in the active pathway (if implemented)."""
        self._notify_observers(
            event_type="pathway_navigation_failed",
            direction="previous",
            reason="not_implemented"
        )

    def stop_pathway(self, reason: Optional[str] = None) -> None:
        """Stops navigating the current pathway."""
        if self._active_pathway_link_type:
            stopped_link_type = self._active_pathway_link_type
            self._active_pathway_link_type = None
            self._notify_observers(
                event_type="pathway_stopped",
                link_type=stopped_link_type,
                reason=reason
            )

    # --------------------------------------------------------------------------
    # Getter Methods for Querying State
    # --------------------------------------------------------------------------

    def get_node_by_id(self, node_id: str) -> Optional[Node]:
        """Returns a Node object by its ID, or None if not found."""
        return self.all_nodes.get(node_id)

    def get_effective_detail_level(self, node_id: str) -> int:
        """
        Gets the effective detail level for a leaf.
        Returns the node's specific override if it exists, otherwise the
        global default detail level.
        """
        if node_id not in self.all_nodes:
            return self.global_detail_level 
        return self.leaf_detail_overrides.get(node_id, self.global_detail_level)

    @property
    def displayed_leaf_nodes(self) -> List[Node]:
        """Returns a list of Node objects currently displayed, in order."""
        return [
            self.all_nodes[node_id]
            for node_id in self.displayed_leaf_ids
            if node_id in self.all_nodes 
        ]

    @property
    def selected_leaf_nodes(self) -> List[Node]:
        """Returns a list of Node objects currently selected."""
        return [
            self.all_nodes[node_id]
            for node_id in self.selected_leaf_ids
            if node_id in self.all_nodes
        ]

