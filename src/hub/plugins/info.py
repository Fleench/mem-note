"""Plugin info helper."""
import importlib.util
import os
import sys


def main(data_dir, args):
    config_dir = _get_config_dir()
    if not os.path.exists(config_dir):
        print("No plugin configuration directory found.")
        return

    plugins = _list_plugins(config_dir)
    if not plugins:
        print("No plugins found.")
        return

    if not args:
        _print_all_plugins(config_dir, plugins)
        return

    for name in args:
        plugin_path = _resolve_plugin_path(config_dir, name)
        if not plugin_path:
            print(f"Plugin '{name}' not found.")
            continue
        _print_plugin_info(name, plugin_path)


def meta_data():
    return {
        "name": "info",
        "description": "Display available plugins and metadata.",
        "file_path": __file__,
    }


def _print_all_plugins(config_dir, plugins):
    for plugin in plugins:
        plugin_path = os.path.join(config_dir, plugin)
        module = _load_module(plugin, plugin_path)
        if module and hasattr(module, "meta_data"):
            meta = module.meta_data()
            name = meta.get("name", plugin[:-3])
            description = meta.get("description", "No description.")
            print(f"{name}: {description}")
        else:
            print(plugin[:-3])


def _print_plugin_info(name, plugin_path):
    module = _load_module(name, plugin_path)
    if module and hasattr(module, "meta_data"):
        meta = module.meta_data()
        print(f"Name: {meta.get('name', name)}")
        print(f"Description: {meta.get('description', 'No description.')}")
        print(f"File: {meta.get('file_path', plugin_path)}")
        return
    print(f"Plugin '{name}' has no metadata.")


def _resolve_plugin_path(config_dir, name):
    filename = name if name.endswith(".py") else f"{name}.py"
    plugin_path = os.path.join(config_dir, filename)
    if os.path.exists(plugin_path):
        return plugin_path
    return None


def _list_plugins(config_dir):
    return [
        filename
        for filename in os.listdir(config_dir)
        if filename.endswith(".py") and not filename.startswith("__")
    ]


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
