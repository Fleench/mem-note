# File: main.py
# Description: Plugin manager and entry point for mem-note
import os
import sys
import importlib.util
import shutil

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: hub <plugin_name> [args] | init | load <path>")
        return
    
    command = args[0]
    
    # Core configuration commands
    if command == "init":
        init()
    elif command == "load":
        load(args[1:])
    else:
        # Treat command as a plugin name
        split_command = command.split(".")
        if len(split_command) < 2:
            print("Error: Command must be formated like <plugin>.<command>")
            return
        run_plugin(split_command[0], split_command[1],args[1:])


def run_plugin(plugin_name, cmd, args):
    '''
    Load and run a specific plugin
    '''
    config_dir = get_config_dir()
    plugin_path = os.path.join(config_dir, plugin_name + ".py")
    
    # Check if plugin exists in config; if not, try to install it from package
    if not os.path.exists(plugin_path):
        move_plugins_to_config()
        plugin_path = os.path.join(config_dir, plugin_name + ".py")
        if not os.path.exists(plugin_path):
            print(f"Plugin '{plugin_name}' not found.")
            return
    
    # Load and run the plugin
    try:
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        if spec is None or spec.loader is None:
            print(f"Could not load plugin '{plugin_name}'.")
            return
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Call the plugin's main function if it exists
        if hasattr(module, cmd):
            module.cmd(get_data_dir(), get_data_local_dir(), args)
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
        destination_path = os.path.join(config_dir, filename)
        if not os.path.exists(destination_path):
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
        app_config = os.path.join(config_dir, "hub")
    
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


if __name__ == "__main__":
    main()
