"""Plugin package management."""
import importlib.util
import os
import shutil


def main(data_dir, args):
    if not args:
        _print_usage()
        return

    command = args[0]
    if command == "add":
        _add_plugin(args[1:])
    elif command == "remove":
        _remove_plugin(args[1:])
    elif command == "export":
        _export_plugin(args[1:])
    elif command == "info":
        _run_info(args[1:])
    else:
        print(f"Unknown pkg command '{command}'.")
        _print_usage()


def meta_data():
    return {
        "name": "pkg",
        "description": "Manage plugins: add, remove, export, info.",
        "file_path": __file__,
    }


def _print_usage():
    print("Usage: pkg add <path> | pkg remove <name> | pkg export <name> | pkg info [names...]")


def _add_plugin(args):
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
    config_dir = _get_config_dir()
    destination_path = os.path.join(config_dir, os.path.basename(source_path))
    shutil.move(source_path, destination_path)
    print(f"Added plugin to {destination_path}")


def _remove_plugin(args):
    if not args:
        print("Please provide the plugin name to remove.")
        return
    config_dir = _get_config_dir()
    plugin_path = _resolve_plugin_path(config_dir, args[0])
    if not plugin_path:
        print(f"Plugin '{args[0]}' not found.")
        return
    os.remove(plugin_path)
    print(f"Removed plugin {os.path.basename(plugin_path)}")


def _export_plugin(args):
    if not args:
        print("Please provide the plugin name to export.")
        return
    config_dir = _get_config_dir()
    plugin_path = _resolve_plugin_path(config_dir, args[0])
    if not plugin_path:
        print(f"Plugin '{args[0]}' not found.")
        return
    destination_path = os.path.join(os.getcwd(), os.path.basename(plugin_path))
    shutil.copy2(plugin_path, destination_path)
    print(f"Exported plugin to {destination_path}")


def _run_info(args):
    config_dir = _get_config_dir()
    info_path = _resolve_plugin_path(config_dir, "info")
    if not info_path:
        print("Info plugin not found.")
        return
    module = _load_module("info", info_path)
    if module and hasattr(module, "main"):
        module.main(None, args)
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


def _get_config_dir():
    if os.name == "nt":
        config_root = os.environ.get("APPDATA", os.path.expanduser("~"))
        app_config = os.path.join(config_root, "mem-note")
    else:
        config_root = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        app_config = os.path.join(config_root, "mem-note")
    if not os.path.exists(app_config):
        os.makedirs(app_config)
    return app_config
