"""Notes management plugin."""
import os
VMAJOR = 0
VMINOR = 4
VPATCH = 0
ID = "com.flench04.mem"
def meta_data():
    return {
        "name": "notes",
        "description": "Basic note management: list, new, recall, delete, edit.",
        "file_path": __file__,
    }


def help(api, args):
    return [
        "Usage: notes <command> [args]",
        "Commands:",
        "  list            - List all notes",
        "  new <name> <body> - Create a new note",
        "  recall <name>   - Read a note",
        "  delete <name>   - Delete a note",
        "  edit <name> <body> - Edit (overwrite) a note",
    ]


def recall(api, args):
    if not args:
        return "Please provide the name of the note to recall."
    data_dir = api["get_data_local_dir"]()
    note_path = os.path.join(data_dir, args[0])
    if os.path.exists(note_path):
        with open(note_path, "r") as file:
            content = file.read()
            return content
    else:
        return f"Note '{args[0]}' does not exist."


def delete(api, args):
    if not args:
        return "Please provide the name of the note to delete."
    data_dir = api["get_data_local_dir"]()
    note_path = os.path.join(data_dir, args[0])
    if os.path.exists(note_path):
        os.remove(note_path)
        return f"Note '{args[0]}' deleted."
    else:
        return f"Note '{args[0]}' does not exist."


def new(api, args):
    if len(args) < 2:
        return "Please provide the name and content of the note."
    data_dir = api["get_data_local_dir"]()
    with open(os.path.join(data_dir, args[0]), "w") as file:
        file.write(" ".join(args[1:]))
    return f"Note '{args[0]}' created."


def list(api, args):
    data_dir = api["get_data_local_dir"]()
    if not os.path.exists(data_dir):
        return "No data directory found."
    notes = os.listdir(data_dir)
    return notes


def edit(api, args):
    if not args:
        return "Please provide the name of the note to edit."
    # Delete the old note and create a new one
    out = []
    d = delete(api, [args[0]])
    if d:
        out.append(d)
    n = new(api, args)
    if n:
        out.append(n)
    return out
def main(api, args):
    return help(api, args)