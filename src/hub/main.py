'''
File: main.py
Description: Plugin manager and entry point for mem-note
'''
import os
import sys
import importlib.util
import shutil
import random
import json
from embed_term.term import EmbedTerminal # pylint: disable=import-error
DEBUG = True
VMAJOR = 0
VMINOR = 4
VPATCH = 0
API = {}
def main(args = []): #pylint: disable=dangerous-default-value
    '''
    Main entry point for hub application
    1. Parse command line arguments
    2. If no args, launch embedded terminal
    3. Handle core commands: init, load, reset
    4. Otherwise treat first arg as plugin name to load and run
    5. Loop back to embedded terminal if needed
    '''
    term = EmbedTerminal()
    term.init_terminal()
    cmd = ""
    if not args:
        args = sys.argv[1:]
        # Embeded terminal
        print("Welcome to hub. Type 'exit' to quit.")
        cmd = " ".join(args)
        while not cmd:
            try:
                term.display_input(type="sl")
                if term.tick():
                    cmd = term.read_input().strip()
                    print()
            except KeyboardInterrupt:
                term.reset_terminal()
                print("\nExiting hub.")
                sys.exit(0)
        args = cmd.split()
    command = args[0]
    # Core configuration commands
    commands = {
        "init": init,
        "load": load,
        "reset": reset,
    }
    if command in commands:
        commands[command](args[1:])
    elif command.lower() == "exit":
        term.clear_input()
        print()
        term.reset_terminal()
        sys.exit(0)
    else:
        # Treat command as a plugin name
        split_command = command.split(":")
        if len(split_command) < 2:
            run_plugin(command, "main", args[1:])
        else:
            run_plugin(split_command[0], split_command[1],args[1:])
    if cmd and len(sys.argv) == 1:
        term.clear_input()
        cmd = ""
        main()

def run_plugin(plugin_name, cmd, args):
    '''
    Load and run a specific plugin
    '''
    plugin_API_register()
    if ensure_plugin_exists(plugin_name):
        register_plugin_to_manifest(plugin_name)
        execute_plugin_command(plugin_name, cmd, args)

def ensure_plugin_exists(plugin_name):
    '''
    Ensure that a plugin exists in the config directory; if not, copy it from packaged plugins
    '''
    config_dir = get_config_dir()
    plugin_path = os.path.join(config_dir, "plugins", plugin_name + ".py")
    if not os.path.exists(plugin_path) or DEBUG:
        move_plugins_to_config()
def register_plugin_to_manifest(plugin_name):
    '''
    Register a plugin in the manifest file
    '''
    config_dir = get_config_dir()
    manifest = os.path.join(config_dir,"manifest.json")
    if not os.path.exists(manifest):
        with open(manifest,"w", encoding="UTF-8") as file:
            file.write("{}")
    with open(manifest, "r", encoding="UTF-8") as file:
        manifest_data = json.load(file)
        plugin_path = os.path.join(config_dir, "plugins", plugin_name + ".py")
    try:
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        if spec is None or spec.loader is None:
            print(f"Could not load plugin '{plugin_name}'.")
            return
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if plugin_name not in manifest_data:
            try:
                ID = module.ID # pylint: disable=C0103
                manifest_data[ID] = {}
            except AttributeError:
                print(f"Plugin '{plugin_name}' is missing an ID attribute.")
                return
            with open(manifest, "w",encoding="UTF-8") as file:
                json.dump(manifest_data, file, indent=4)
    except Exception as e: # pylint: disable=broad-except
        print(f"Error registering plugin '{plugin_name}': {e}")
def execute_plugin_command(plugin_name, command, args):
    '''
    Execute a specific command of a plugin
    '''
    config_dir = get_config_dir()
    plugin_path = os.path.join(config_dir, "plugins", plugin_name + ".py")
    spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
    if spec is None or spec.loader is None:
        print(f"Could not load plugin '{plugin_name}'.")
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, command):
        cmd = getattr(module, command)
        result = cmd(get_API_dict(), args)
        if result is None:
            return
        if isinstance(result, list):
            for line in result:
                print(line)
        else:
            print(result)
    else:
        print(f"Plugin '{plugin_name}' does not have the command {command}.")

def move_plugins_to_config():
    '''
    Copy packaged plugins into the config directory if they are missing.
    '''
    config_dir = get_config_dir()
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    if not os.path.exists(plugins_dir):
        return
    for filename in os.listdir(plugins_dir):
        if not filename.endswith(".py") or filename.startswith("__"):
            continue
        source_path = os.path.join(plugins_dir, filename)
        destination_path = os.path.join(config_dir,"plugins",filename)
        os.makedirs(os.path.join(config_dir,"plugins"), exist_ok=True)
        if not os.path.exists(destination_path) or DEBUG:
            shutil.copy2(source_path, destination_path)


def get_data_local_dir():
    '''
    Ensure the data directory exists. Supports local .mem directory if initialized. Return it.
    '''
    # 1. Check for local .mem directory
    if os.path.exists(os.path.join(os.getcwd(), ".mem")):
        data_dir = os.path.join(os.getcwd(), ".mem")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir
    return get_data_dir()
def get_data_dir():
    '''
    Ensure the data directory exists and return it
    '''
    # 2. Check for configured data directory
    conf = get_config_dir()
    data_dir_file = os.path.join(conf, "data_dir.conf")
    if os.path.exists(data_dir_file):
        with open(data_dir_file, "r", encoding="UTF-8") as file:
            data_dir = file.read().strip()
            if os.path.exists(data_dir) and os.path.isdir(data_dir):
                return data_dir

    # 3. Fallback to default system data directory
    if os.name == 'nt':  # Windows
        data_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
        app_data = os.path.join(data_dir, "mem-note")
    else:  # Linux/Mac
        data_dir = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        app_data = os.path.join(data_dir, "hub")
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
        app_config = os.path.join(config_dir, "hub")
        if DEBUG:
            app_config = os.path.join(config_dir, "hub-debug")
    if not os.path.exists(app_config):
        os.makedirs(app_config)
    return app_config


def init():
    '''
    Allow the current directory to be initialized to store its own local data
    '''
    cwd = os.getcwd()
    data_dir = os.path.join(cwd, ".mem")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Initialized memory directory at {data_dir}")
    else :
        print("This directory is already initialized.")


def load(args):
    '''
    load a folder as the data directory
    '''
    if not args:
        print("Please provide the path to load as data directory.")
        return
    data_dir = args[0]
    if os.path.exists(data_dir) and os.path.isdir(data_dir):
        conf = get_config_dir()
        with open(os.path.join(conf, "data_dir.conf"), "w", encoding="UTF-8") as file:
            file.write(data_dir)
        print(f"Loaded {data_dir} as data directory.")
    elif data_dir == "default":
        conf = get_config_dir()
        data_dir_file = os.path.join(conf, "data_dir.conf")
        if os.path.exists(data_dir_file):
            os.remove(data_dir_file)
        print("Reverted to default data directory.")
    else:
        print(f"Path '{data_dir}' does not exist or is not a directory.")
def reset(args):
    '''
    Reset the configuration  by deleting the config directory
    '''
    if not args or args[0] not in ["config", "data", "bundled-plugins"]:
        print("Usage: hub reset <config|data|bundled-plugins>")
        return
    conf = random.randint(1000000,9999999)
    print(f"You are about to reset {args[0]}. This action cannot be undone. Type in {conf} to confirm.") # pylint: disable=line-too-long
    if input("Confirmation: ") != f"{conf}":
        print("Reset cancelled.")
        return
    if args[0] == "config":
        config_dir = get_config_dir()
        if os.path.exists(config_dir):
            shutil.rmtree(config_dir)
            print("Configuration reset.")
        else:
            print("No configuration found to reset.")
    elif args[0] == "data":
        data_dir = get_data_dir()
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)
            print("Data directory reset.")
        else:
            print("No data directory found to reset.")
    elif args[0] == "bundled-plugins":
        config_dir = get_config_dir()
        #plugins_dir = os.path.join(config_dir, "plugins")
        move_plugins_to_config()
        print("Bundled plugins reset.")
def get_API_dict() -> dict: #pylint: disable=invalid-name
    '''
    Return a dictionary of the hub API commands and variables
    '''
    global API # pylint: disable=global-statement
    if not API:
        API =  {
            "VMAJOR": VMAJOR,
            "VMINOR": VMINOR,
            "VPATCH": VPATCH,
            "get_data_dir": get_data_dir,
            "get_data_local_dir": get_data_local_dir,
            "get_config_dir": get_config_dir,
        }
    return API
def plugin_API_register(): #pylint: disable=invalid-name
    '''
    Register plugin APIs into the global API dictionary
    '''
    global API # pylint: disable=global-statement
    API = get_API_dict()
    config_dir = get_config_dir()
    plugin_path = os.path.join(config_dir, "plugins")
    for filename in os.listdir(plugin_path):
        if not filename.endswith(".py") or filename.startswith("__"):
            continue
        plugin_name = filename[:-3]
        spec = importlib.util.spec_from_file_location(plugin_name, os.path.join(plugin_path, filename)) # pylint: disable=line-too-long
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        if module is None:
            continue
        spec.loader.exec_module(module)
        if not hasattr(module, "ID"):
            continue
        if hasattr(module, "hub_add_api"):
            plugin_api = module.hub_add_api()
            API[module.ID] = {}
            for key in plugin_api:
                API[module.ID][key] = plugin_api[key]
if __name__ == "__main__":
    main()
