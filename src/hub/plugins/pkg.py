"""Plugin package management."""
import importlib.util
import os
import shutil
import requests
import json

def meta_data():
    return {
        "name": "pkg",
        "description": "Manage plugins: add, remove, export, info.",
        "file_path": __file__,
    }


def help(data_dir, local_data_dir, config_dir, args):
    print("Usage: pkg add <path> | pkg remove <name> | pkg export <name> | pkg info [names...]")


def add(data_dir, local_data_dir, config_dir, args):
    if not args:
        print("Please provide the path to the plugin file.")
        return
    source_path = args[0]
    if not os.path.exists(source_path):
        print(f"Plugin file '{source_path}' not found.")
        return
    if not source_path.endswith(".py"):
        print("Only .py plugin files can be added.")
        return
    destination_path = os.path.join(config_dir,"plugins", os.path.basename(source_path))
    shutil.copy2(source_path, destination_path)
    print(f"Added plugin to {destination_path}")


def remove(data_dir, local_data_dir, config_dir, args):
    if not args:
        print("Please provide the plugin name to remove.")
        return
    plugin_path = _resolve_plugin_path(config_dir, args[0])
    if not plugin_path:
        print(f"Plugin '{args[0]}' not found.")
        return
    os.remove(plugin_path)
    print(f"Removed plugin {os.path.basename(plugin_path)}")


def export(data_dir, local_data_dir, config_dir, args):
    if not args:
        print("Please provide the plugin name to export.")
        return
    plugin_path = _resolve_plugin_path(config_dir, args[0])
    if not plugin_path:
        print(f"Plugin '{args[0]}' not found.")
        return
    destination_path = os.path.join(os.getcwd(), os.path.basename(plugin_path))
    shutil.copy2(plugin_path, destination_path)
    print(f"Exported plugin to {destination_path}")


def info(data_dir, local_data_dir, config_dir, args):
    info_path = _resolve_plugin_path(config_dir, "info")
    if not info_path:
        print("Info plugin not found.")
        return
    module = _load_module("info", info_path)
    if module and hasattr(module, "main"):
        module.main(data_dir, local_data_dir, config_dir, args)
    else:
        print("Info plugin is missing its main entry point.")


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
    Install a plugin from a given url or the index.json file.
    '''
    if not args:
        print("Please provide the plugin name or URL to install.")
        return
    source = args[0]
    if source.startswith("http://") or source.startswith("https://"):
        response = requests.get(source)
        if response.status_code != 200:
            print(f"Failed to download plugin from {source}.")
            return
        plugin_name = source.split("/")[-1]
        destination_path = os.path.join(config_dir + "plugins", plugin_name)
        with open(destination_path, "wb") as f:
            f.write(response.content)
        print(f"Installed plugin from {source} to {destination_path}")
    else:
        index_path = os.path.join(config_dir, "pkg", "index.json")
        if not os.path.exists(index_path):
            print("Index file not found. Adding the defualt index file.")
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
            defualt_index = {
                "hi": {
                "url": "https://raw.githubusercontent.com/Fleench/mem-note/refs/heads/main/src/hub/plugins/hi.py"
                }
            }
            with open(index_path, "w") as f:
                json.dump(defualt_index, f)
                print("Defualt index file added.")
            return
        with open(index_path, "r") as f:
            index = json.load(f)
        if source not in index:
            print(f"Plugin '{source}' not found in index.")
            return
        plugin_url = index[source]["url"]
        response = requests.get(plugin_url)
        if response.status_code != 200:
            print(f"Failed to download plugin from {plugin_url}.")
            return
        destination_path = os.path.join(config_dir + "plugins", f"{source}.py")
        if not os.path.exists(os.path.dirname(destination_path)):
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        with open(destination_path, "wb") as f:
            f.write(response.content)
        print(f"Installed plugin '{source}' from {plugin_url} to {destination_path}")