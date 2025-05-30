import os

def tree_builder(path, prefix=""):
    """
    Returns a string representing the directory tree of the given path.
    """
    tree_str = ""
    entries = sorted(os.listdir(path))
    entries_count = len(entries)

    for index, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = "└── " if index == entries_count - 1 else "├── "
        tree_str += prefix + connector + entry + "\n"

        if os.path.isdir(full_path):
            extension = "    " if index == entries_count - 1 else "│   "
            tree_str += tree_builder(full_path, prefix + extension)
    return tree_str
