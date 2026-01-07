# Plugin development for hub 🔌

This short guide explains how to write plugins for `hub`.

## Plugin basics

- Plugins are simple Python files placed in the configuration directory (e.g., `$XDG_CONFIG_HOME/hub`). Packaged example plugins live in `src/hub/plugins/` and will be copied to the config dir on first run.
- Each plugin exposes one or more functions that correspond to commands. Each command function should have the signature:

```py
def command(data_dir, local_data_dir, config_dir, args):
    """Implement the command behavior."""
```

- Plugins can optionally provide a `meta_data()` function returning a dict with `name`, `description`, and `file_path`.

## Example

```py
# myplugin.py

def meta_data():
    return {"name": "myplugin", "description": "Do something useful", "file_path": __file__}


def greet(data_dir, local_data_dir, config_dir, args):
    name = args[0] if args else "there"
    print(f"Hello, {name}!")
```

## Discovery & info

Use the built-in `info` plugin to list available plugins and view metadata:

```sh
hub info        # lists plugins
hub info myplugin  # shows metadata for myplugin
```

## Tips

- Keep plugins small and stateless where possible (simple file-based storage is fine).
- Use relative imports only when packaging complex plugin packages.
- Test plugins by copying them into your config dir or running with `PYTHONPATH=src python -m hub.main <plugin>.<command>`.
