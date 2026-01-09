"""Notes management plugin."""
import os


def meta_data():
    return {
        "name": "notes",
        "description": "Basic note management: list, new, recall, delete, edit.",
        "file_path": __file__,
    }


def help(data_dir, local_data_dir, config_dir):
    return [
        "Usage: notes <command> [args]",
        "Commands:",
        "  list            - List all notes",
        "  new <name> <body> - Create a new note",
        "  recall <name>   - Read a note",
        "  delete <name>   - Delete a note",
        "  edit <name> <body> - Edit (overwrite) a note",
    ]


def recall(data_dir, local_data_dir, config_dir, args):
    if not args:
        return "Please provide the name of the note to recall."
    note_path = os.path.join(data_dir, args[0])
    if os.path.exists(note_path):
        with open(note_path, "r") as file:
            content = file.read()
            return content
    else:
        return f"Note '{args[0]}' does not exist."


def delete(data_dir, local_data_dir, config_dir, args):
    if not args:
        return "Please provide the name of the note to delete."
    note_path = os.path.join(data_dir, args[0])
    if os.path.exists(note_path):
        os.remove(note_path)
        return f"Note '{args[0]}' deleted."
    else:
        return f"Note '{args[0]}' does not exist."


def new(data_dir, local_data_dir, config_dir, args):
    if len(args) < 2:
        return "Please provide the name and content of the note."
    with open(os.path.join(data_dir, args[0]), "w") as file:
        file.write(" ".join(args[1:]))
    return f"Note '{args[0]}' created."


def list(data_dir, local_data_dir, config_dir, args):
    if not os.path.exists(data_dir):
        return "No data directory found."
    notes = os.listdir(data_dir)
    return notes


def edit(data_dir, local_data_dir, config_dir, args):
    if not args:
        return "Please provide the name of the note to edit."
    # Delete the old note and create a new one
    out = []
    d = delete(data_dir, local_data_dir, config_dir, [args[0]])
    if d:
        out.append(d)
    n = new(data_dir, local_data_dir, config_dir, args)
    if n:
        out.append(n)
    return out
