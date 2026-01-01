# File: main.py
# Author: Glenn Sutherland
# Date: 12/31/2025
# Description: A basic memory/note cli tool
import argparse
import os
import sys
import importlib.util
home = os.path.expanduser("~")
def main():
    args = sys.argv[1:]
    if not args:
        print("Please provide a command: list, new, recall, delete, run")
        return
    if args[0] == "list":
        list_notes(args[1:])
    elif args[0] == "new":
        new_note(args[1:])

    elif args[0] == "recall":
        recall_note(args[1:])

    elif args[0] == "delete":
        delete_note(args[1:])
    elif args[0] == "run":
        run(args[1:])
    elif args[0] == "edit":
        edit_note(args[1:])
    elif args[0] == "init":
        init()
    else:
        print(f"Unknown command '{args[0]}'. Available commands: list, new, recall, delete, run, edit, init")
def recall_note(args):
    '''
    Recall a specific note
    '''
    if not args:
        print("Please provide the name of the note to recall.")
        return
    data = get_data_dir()
    note_path = os.path.join(data, args[0])
    if os.path.exists(note_path):
        with open(note_path, "r") as file:
            content = file.read()
            print(content)
    else:
        print(f"Note '{args[0]}' does not exist.")
def delete_note(args):
    '''
    Delete a specific note
    '''
    if not args:
        print("Please provide the name of the note to delete.")
        return
    data = get_data_dir()
    note_path = os.path.join(data, args[0])
    if os.path.exists(note_path):
        os.remove(note_path)
        print(f"Note '{args[0]}' deleted.")
    else:
        print(f"Note '{args[0]}' does not exist.")
def new_note(args):
    '''
    Create a new note
    '''
    if len(args) < 2:
        print("Please provide the name and content of the note.")
        return
    data = get_data_dir()
    with open(os.path.join(data, args[0]), "w") as file:
        file.write(" ".join(args[1:]))
    print(f"Note '{args[0]}' created.")
def list_notes(args):
    '''
    List all notes
    '''
    data = get_data_dir()
    notes = os.listdir(data)
    for note in notes:
        print(note)
def run(args):
    '''
    Run a specific extension command
    '''
    if not args:
        print("Please provide a plugin name.")
        return
    
    config_dir = get_config_dir()
    plugin_path = os.path.join(config_dir, args[0] + ".py")
    
    if not os.path.exists(plugin_path):
        print(f"Plugin '{args[0]}' not found.")
        return
    
    # Load and run the plugin
    # Pass the data directory and remaining args to the plugin
    spec = importlib.util.spec_from_file_location(args[0], plugin_path)
    module = importlib.util.module_from_spec(spec) # type: ignore
    spec.loader.exec_module(module) # type: ignore
    
    # Call the plugin's main function if it exists
    if hasattr(module, 'main'):
        module.main(get_data_dir(), args[1:])
def get_data_dir():
    '''
    Ensure the data directory exists. Supports local .mem directory if initialized.
    '''
    if os.path.exists(os.path.join(os.getcwd(), ".mem")):
        data_dir = os.path.join(os.getcwd(), ".mem")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir
    if os.name == 'nt':  # Windows
        data_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
        app_data = os.path.join(data_dir, "mem-note")
    else:  # Linux/Mac
        data_dir = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        app_data = os.path.join(data_dir, "mem-note")
    
    if not os.path.exists(app_data):
        os.makedirs(app_data)
    return app_data

def get_config_dir():
    '''
    Ensure the config directory exists
    '''
    if os.name == 'nt':  # Windows
        config_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
        app_config = os.path.join(config_dir, "mem-note")
    else:  # Linux/Mac
        config_dir = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        app_config = os.path.join(config_dir, "mem-note")
    
    if not os.path.exists(app_config):
        os.makedirs(app_config)
    return app_config
def edit_note(args):
    '''
    Edit a specific note
    '''
    if not args:
        print("Please provide the name of the note to edit.")
        return
    data = get_data_dir()
    note_path = os.path.join(data, args[0])
    delete_note([args[0]])
    new_note(args)
def init():
    '''
    Allow the current directory to be initialized to store its own memories
    '''
    cwd = os.getcwd()
    data_dir = os.path.join(cwd, ".mem")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Initialized memory directory at {data_dir}")
    else :
        print("This directory is already initialized.")
if __name__ == "__main__":
    main()