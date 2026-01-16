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
from embed_term.term import EmbedTerminal
DEBUG = True
VMAJOR = 0
VMINOR = 4
VPATCH = 0
API = {}
def main(args = []):
    term = EmbedTerminal()
    term.init_terminal()
    cmd = ""
    if not args:
        args = sys.argv[1:]
    if not args:
        # Embeded terminal
        print("Welcome to hub. Type 'exit' to quit.")
        while not cmd:
            try:
                term.display_input(type="sl")
                if term.tick():
                    cmd = term.read_input().strip()
                    print()
            except:
                term.reset_terminal()
                print("\nExiting hub.")
                sys.exit(0)
        args = cmd.split()

    
    command = args[0]
    
    # Core configuration commands
    if command == "init":
        init()
    elif command == "load":
        load(args[1:])
    elif command == "reset":
        reset(args[1:])
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
    if cmd:
        term.clear_input()
        cmd = ""
        main()

def run_plugin(plugin_name, cmd, args):
    '''
    Load and run a specific plugin
    '''
    config_dir = get_config_dir()
    plugin_path = os.path.join(config_dir, "plugins", plugin_name + ".py")
    # Check if plugin exists in config; if not, try to install it from package
    if not os.path.exists(plugin_path) or DEBUG:
        move_plugins_to_config()
        if not os.path.exists(plugin_path):
            print(f"Plugin '{plugin_name}' not found.")
            return
    if DEBUG:
        move_plugins_to_config()

    plugin_API_register()
    # Load and run the plugin
    manifest = os.path.join(config_dir,"manifest.json")
    if not os.path.exists(manifest):
        with open(manifest,"w") as file:
            file.write("{}")
    with open(manifest, "r") as file:
        manifest_data = json.load(file)
    try:
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        if spec is None or spec.loader is None:
            print(f"Could not load plugin '{plugin_name}'.")
            return
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if plugin_name not in manifest_data:
            try:
                ID = module.ID
                manifest_data[ID] = {}
            except:
                print(f"Plugin '{plugin_name}' is missing an ID attribute.")
                return
            with open(manifest, "w") as file:
                json.dump(manifest_data, file, indent=4)
        global VMAJOR, VMINOR, VPATCH
        if VMAJOR != module.VMAJOR or (VMAJOR == 0 and (VMINOR != module.VMINOR)):
            print(f"Plugin: {plugin_name} version incompatible with hub version.")
            return
        if hasattr(module, cmd):
            cmd = getattr(module, cmd)
            result = cmd(get_API_dict(), args)
            # Plugins should return text (str) or list of lines; printing happens here in main
            if result is None:
                return
            if isinstance(result, list):
                for line in result:
                    print(line)
            else:
                print(result)
        else:
            if cmd == "main":
                print(f"Plugin '{plugin_name}' does not have a main entry point.")
            else:
                print(f"Plugin '{plugin_name}' does not have the command {cmd}.")
            
    except Exception as e:
        print(f"Error executing plugin '{plugin_name}': {e}")


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
    Ensure the data directory exists. Supports local .mem directory if initialized.
    '''
    # 1. Check for local .mem directory
    if os.path.exists(os.path.join(os.getcwd(), ".mem")):
        data_dir = os.path.join(os.getcwd(), ".mem")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir
    else:
        return get_data_dir()
def get_data_dir():
    # 2. Check for configured data directory
    conf = get_config_dir()
    data_dir_file = os.path.join(conf, "data_dir.conf")
    if os.path.exists(data_dir_file):
        with open(data_dir_file, "r") as file:
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
        with open(os.path.join(conf, "data_dir.conf"), "w") as file:
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
    print(f"You are about to reset {args[0]}. This action cannot be undone. Type in {conf} to confirm.")
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
        plugins_dir = os.path.join(config_dir, "plugins")
        move_plugins_to_config()
        print("Bundled plugins reset.")
def get_API_dict() -> dict:
    '''
    Return a dictionary of the hub API commands and variables
    '''
    global API, VMAJOR, VMINOR, VPATCH
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
def plugin_API_register():
    API = get_API_dict()
    config_dir = get_config_dir()
    plugin_path = os.path.join(config_dir, "plugins")
    for filename in os.listdir(plugin_path):
        if not filename.endswith(".py") or filename.startswith("__"):
            continue
        plugin_name = filename[:-3]
        spec = importlib.util.spec_from_file_location(plugin_name, os.path.join(plugin_path, filename))
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
