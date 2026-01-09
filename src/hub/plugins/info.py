"""Plugin info helper.

Public commands:
- `catalog` (aliases: `list`, `ls`) – list available plugins and short descriptions
- `info` (aliases: `show`) – show metadata for one or more plugins

All public commands return either a `str` or `list[str]`. They do not print directly; printing is handled by `main`.
"""
import importlib.util
import os


def main(data_dir, local_data_dir, config_dir, args):
    """Entry point: if no args, list plugins. Supports explicit subcommands:
    - catalog / list / ls
    - info / show <plugin> [<plugin>...]
    Otherwise treats args as plugin names to show info for.
    """
    plugins_dir = os.path.join(config_dir, "plugins")
    if not os.path.exists(plugins_dir):
        return ["No plugin configuration directory found."]

    plugins = _list_plugins(plugins_dir)
    if not plugins:
        return ["No plugins found."]

    if not args:
        return _get_all_plugins_info(plugins_dir, plugins)

    # Recognize explicit subcommands
    cmd = args[0].lower()
    if cmd in ("catalog", "list", "ls"):
        return _get_all_plugins_info(plugins_dir, plugins)
    if cmd in ("info", "show"):
        return info(data_dir, local_data_dir, config_dir, args[1:])

    # Otherwise treat the provided args as plugin names
    return info(data_dir, local_data_dir, config_dir, args)


def catalog(data_dir, local_data_dir, config_dir, args):
    """Public command to list plugins."""
    plugins_dir = os.path.join(config_dir, "plugins")
    if not os.path.exists(plugins_dir):
        return ["No plugin configuration directory found."]
    plugins = _list_plugins(plugins_dir)
    if not plugins:
        return ["No plugins found."]
    return _get_all_plugins_info(plugins_dir, plugins)


def info(data_dir, local_data_dir, config_dir, args):
    """Public command to return metadata for one or more plugins.

    args: list of plugin names (without ".py" or with). Returns list of lines.
    """
    if not args:
        return ["Error: Please provide at least one plugin name."]

    out = []
    plugins_dir = os.path.join(config_dir, "plugins")
    for name in args:
        plugin_path = _resolve_plugin_path(plugins_dir, name)
        if not plugin_path:
            out.append(f"Plugin '{name}' not found.")
            continue
        out.extend(_get_plugin_info(name, plugin_path))
        out.append("")  # blank separator between plugin entries
    if out and out[-1] == "":
        out.pop()
    return out


def meta_data():
    return {
        "name": "info",
        "description": "Display available plugins and metadata.",
        "file_path": __file__,
    }


def _get_all_plugins_info(plugins_dir, plugins):
    """Return a list of strings with short descriptions for all plugins."""
    out = []
    for plugin in sorted(plugins):
        plugin_path = os.path.join(plugins_dir, plugin)
        module = _load_module(plugin[:-3], plugin_path)
        if module and hasattr(module, "meta_data"):
            try:
                meta = module.meta_data()
            except Exception:
                meta = {}
            name = meta.get("name", plugin[:-3])
            description = meta.get("description", "No description.")
            out.append(f"{name}: {description}")
        else:
            out.append(plugin[:-3])
    return out


def _get_plugin_info(name, plugin_path):
    """Return a list of strings with the metadata for a single plugin."""
    out = []
    module = _load_module(name if name.endswith('.py') else name, plugin_path)
    if module and hasattr(module, "meta_data"):
        try:
            meta = module.meta_data()
        except Exception:
            meta = {}
        out.append(f"Name: {meta.get('name', name)}")
        out.append(f"Description: {meta.get('description', 'No description.')}")
        out.append(f"File: {meta.get('file_path', plugin_path)}")
        return out
    out.append(f"Plugin '{name}' has no metadata.")
    return out


def _resolve_plugin_path(plugins_dir, name):
    filename = name if name.endswith(".py") else f"{name}.py"
    plugin_path = os.path.join(plugins_dir, filename)
    if os.path.exists(plugin_path):
        return plugin_path
    return None


def _list_plugins(plugins_dir):
    if not os.path.exists(plugins_dir):
        return []
    return [
        filename
        for filename in os.listdir(plugins_dir)
        if filename.endswith(".py") and not filename.startswith("__")
    ]


def _load_module(name, plugin_path):
    spec = importlib.util.spec_from_file_location(name, plugin_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)  # type: ignore
    try:
        spec.loader.exec_module(module)  # type: ignore
    except Exception:
        return None
    return module
