
def get_scroll_state(canvas):
    """
    Captures the current scroll state of the canvas.
    Returns a dictionary with pixel offset and percentage offset (vertical).
    """
    # Get the fractional scroll position (0.0 to 1.0 for top edge visibility)
    yview_fraction = canvas.yview()
    scroll_fraction_top = yview_fraction[0]

    # Get the total scrollable area dimensions (bounding box of all items)
    bbox = canvas.bbox("all")
    total_height = bbox[3] - bbox[1] if bbox else 0

    # Calculate pixel offset
    pixel_offset_y = scroll_fraction_top * total_height if total_height > 0 else 0

    # Calculate percentage offset
    percentage_offset_y = scroll_fraction_top * 100

    # Get the visible canvas dimensions (viewport size)
    visible_width = canvas.winfo_width()
    visible_height = canvas.winfo_height()

    state = {
        "scroll_offset": {
            "pixels_y": pixel_offset_y,
            "percentage_y": percentage_offset_y,
        },
        "scrollable_area": {
            "width": bbox[2] - bbox[0] if bbox else 0, # Width from bbox
            "height": total_height,
        },
        "visible_area": {
            "width": visible_width,
            "height": visible_height,
        },
        "yview_fraction": yview_fraction, # Raw yview output for reference
    }
    return state

