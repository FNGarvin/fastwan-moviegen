from .nodes import MovieGenBatchRunner

# A dictionary that maps the node class name to the class itself.
NODE_CLASS_MAPPINGS = {
    "MovieGenBatchRunner": MovieGenBatchRunner,
}

# A dictionary that maps the class name to a display name.
NODE_DISPLAY_NAME_MAPPINGS = {
    "MovieGenBatchRunner": "FastWan Batch Runner",
}

print("[FastWan-MovieGen] Loaded Custom Nodes")
#END OF __init__.py
