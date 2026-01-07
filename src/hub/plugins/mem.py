"""Notes management plugin."""
import os


def meta_data():
    return {
        "name": "notes",
        "description": "Basic note management: list, new, recall, delete, edit.",
        "file_path": __file__,
    }


def help(data_dir, local_data_dir, config_dir):
    print("Usage: notes <command> [args]")
    print("Commands:")
    print("  list            - List all notes")
    print("  new <name> <body> - Create a new note")
    print("  recall <name>   - Read a note")
    print("  delete <name>   - Delete a note")
    print("  edit <name> <body> - Edit (overwrite) a note")


def recall(data_dir, local_data_dir, config_dir, args):
    if not args:
        print("Please provide the name of the note to recall.")
        return
    note_path = os.path.join(data_dir, args[0])
    if os.path.exists(note_path):
        with open(note_path, "r") as file:
            content = file.read()
            print(content)
    else:
        print(f"Note '{args[0]}' does not exist.")


def delete(data_dir, local_data_dir, config_dir, args):
    if not args:
        print("Please provide the name of the note to delete.")
        return
    note_path = os.path.join(data_dir, args[0])
    if os.path.exists(note_path):
        os.remove(note_path)
        print(f"Note '{args[0]}' deleted.")
    else:
        print(f"Note '{args[0]}' does not exist.")


def new(data_dir, local_data_dir, config_dir, args):
    if len(args) < 2:
        print("Please provide the name and content of the note.")
        return
    with open(os.path.join(data_dir, args[0]), "w") as file:
        file.write(" ".join(args[1:]))
    print(f"Note '{args[0]}' created.")


def list(data_dir, local_data_dir, config_dir, args):
    if not os.path.exists(data_dir):
        print("No data directory found.")
        return
    notes = os.listdir(data_dir)
    for note in notes:
        print(note)


def edit(data_dir, local_data_dir, config_dir, args):
    if not args:
        print("Please provide the name of the note to edit.")
        return
    # Delete the old note and create a new one
    delete(data_dir, local_data_dir, config_dir, [args[0]])
    new(data_dir, local_data_dir, config_dir, args)
