"""Plugin package management."""
import importlib.util
import os
import shutil
import requests
import json

VMAJOR = 0
VMINOR = 4
VPATCH = 0
ID = "com.flench04.pkg"

def meta_data():
    return {
        "name": "pkg",
        "description": "Manage plugins: add, remove, export, info.",
        "file_path": __file__,
    }


def help(data_dir, local_data_dir, config_dir, args):
    return "Usage: pkg add <path> | pkg remove <name> | pkg export <name> | pkg info [names...]"


def add(data_dir, local_data_dir, config_dir, args):
    if not args:
        return "Please provide the path to the plugin file."
    source_path = args[0]
    if not os.path.exists(source_path):
        return f"Plugin file '{source_path}' not found."
    if not source_path.endswith(".py"):
        return "Only .py plugin files can be added."
    destination_path = os.path.join(config_dir,"plugins", os.path.basename(source_path))
    shutil.copy2(source_path, destination_path)
    return f"Added plugin to {destination_path}"


def remove(data_dir, local_data_dir, config_dir, args):
    if not args:
        return "Please provide the plugin name to remove."
    plugin_path = _resolve_plugin_path(config_dir, args[0])
    if not plugin_path:
        return f"Plugin '{args[0]}' not found."
    os.remove(plugin_path)
    return f"Removed plugin {os.path.basename(plugin_path)}"


def export(data_dir, local_data_dir, config_dir, args):
    if not args:
        return "Please provide the plugin name to export."
    plugin_path = _resolve_plugin_path(config_dir, args[0])
    if not plugin_path:
        return f"Plugin '{args[0]}' not found."
    destination_path = os.path.join(os.getcwd(), os.path.basename(plugin_path))
    shutil.copy2(plugin_path, destination_path)
    return f"Exported plugin to {destination_path}"


def info(data_dir, local_data_dir, config_dir, args):
    info_path = _resolve_plugin_path(config_dir, "info")
    if not info_path:
        return "Info plugin not found."
    module = _load_module("info", info_path)
    if module and hasattr(module, "main"):
        return module.main(data_dir, local_data_dir, config_dir, args)
    else:
        return "Info plugin is missing its main entry point."

def _resolve_plugin_path(config_dir, name):
    filename = name if name.endswith(".py") else f"{name}.py"
    plugin_path = os.path.join(config_dir, filename)
    if os.path.exists(plugin_path):
        return plugin_path
    return None


def _load_module(name, plugin_path):
    spec = importlib.util.spec_from_file_location(name, plugin_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore
    return module
def install(data_dir, local_data_dir, config_dir, args):
    '''
    Install a plugin from a given url or the index.json file. Returns a status message.
    '''
    if not args:
        return "Please provide the plugin name or URL to install."
    source = args[0]
    plugins_dir = os.path.join(config_dir, "plugins")
    # Install from direct URL
    if source.startswith("http://") or source.startswith("https://"):
        response = requests.get(source)
        if response.status_code != 200:
            return f"Failed to download plugin from {source}."
        plugin_name = source.split("/")[-1]
        os.makedirs(plugins_dir, exist_ok=True)
        destination_path = os.path.join(plugins_dir, plugin_name)
        with open(destination_path, "wb") as f:
            f.write(response.content)
        return f"Installed plugin from {source} to {destination_path}"

    # Install by name from the index.json file
    index_path = os.path.join(config_dir, "pkg", "index.json")
    if not os.path.exists(index_path):
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        default_index = {
            "hi": {
                "url": "https://raw.githubusercontent.com/Fleench/mem-note/refs/heads/main/src/hub/plugins/hi.py"
            }
        }
        with open(index_path, "w") as f:
            json.dump(default_index, f)
        return "Default index file added."

    with open(index_path, "r") as f:
        index = json.load(f)

    if source not in index:
        return f"Plugin '{source}' not found in index."

    plugin_url = index[source]["url"]
    response = requests.get(plugin_url)
    if response.status_code != 200:
        return f"Failed to download plugin from {plugin_url}."

    os.makedirs(plugins_dir, exist_ok=True)
    destination_path = os.path.join(plugins_dir, f"{source}.py")
    with open(destination_path, "wb") as f:
        f.write(response.content)
    return f"Installed plugin '{source}' from {plugin_url} to {destination_path}"
