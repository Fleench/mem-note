'''
Plugin to manage repositories of plugins.
'''
import os
import shutil
import json
import requests

VMAJOR = 0
VMINOR = 4
VPATCH = 0
ID = "com.flench04.repo"

def meta_data():
    return {
        "name": "repo",
        "description": "Manage plugin repositories: add, remove, list.",
        "file_path": __file__,
    }
def catalog(data_dir, local_data_dir, config_dir, args):
    '''
    List all configured plugin repositories. Returns list of lines.
    '''
    out = []
    config_dir_self = _get_config_dir_self(config_dir)
    for filename in os.listdir(config_dir_self):
        if not filename.endswith(".json"):
            continue
        repo_path = os.path.join(config_dir_self, filename)
        with open(repo_path, "r") as f:
            repo = json.load(f)
            out.append(f"{repo['repo-info']['name']}: {repo['repo-info']['description']}")
    return out
def add(data_dir, local_data_dir, config_dir, args):
    '''
    Add a new plugin repository. Returns a status message.
    '''
    config_dir_self = _get_config_dir_self(config_dir)
    source = args[0]
    if args[0].startswith("http://") or args[0].startswith("https://"):
        response = requests.get(source)
        if response.status_code != 200:
            return f"Failed to download plugin from {source}."
        plugin_name = source.split("/")[-1]
        destination_path = os.path.join(config_dir_self, response.url.split("/")[-1])
        with open(destination_path, "wb") as f:
            f.write(response.content)
        return f"Installed repo from {source} to {destination_path}"
    else:
        destination_path = os.path.join(config_dir_self, source.split("/")[-1])
        shutil.copy2(source, destination_path)
        return f"Added repo from {source} to {destination_path}"
    pass
def remove(data_dir, local_data_dir, config_dir, args):
    '''
    Remove an existing plugin repository. Returns a status message.
    '''
    config_dir_self = _get_config_dir_self(config_dir)
    repo_name = args[0]
    repo_path = os.path.join(config_dir_self, repo_name + ".json")
    if os.path.exists(repo_path):
        os.remove(repo_path)
        return f"Removed repo '{repo_name}'."
    else:
        return f"Repo '{repo_name}' not found."
def update(data_dir, local_data_dir, config_dir, args):
    '''
    Update plugin repositories. Returns list of status messages.
    '''
    out = []
    config_dir_self = _get_config_dir_self(config_dir)
    for filename in os.listdir(config_dir_self):
        if not filename.endswith(".json"):
            continue
        repo_path = os.path.join(config_dir_self, filename)
        with open(repo_path, "r") as f:
            repo = json.load(f)
            repo_url = repo["repo-info"]["url"]
            response = requests.get(repo_url)
            if response.status_code != 200:
                out.append(f"Failed to update repo from {repo_url}.")
                continue
            with open(repo_path, "wb") as repo_file:
                repo_file.write(response.content)
            out.append(f"Updated repo '{repo['repo-info']['name']}' from {repo_url}.")
    return out
def search(data_dir, local_data_dir, config_dir, args):
    '''
    Search for plugins in configured repositories. Returns list of matches.
    '''
    out = []
    config_dir_self = _get_config_dir_self(config_dir)
    for filename in os.listdir(config_dir_self):
        if not filename.endswith(".json"):
            continue
        repo_path = os.path.join(config_dir_self, filename)
        with open(repo_path, "r") as f:
            repo = json.load(f)
            for plugin in repo.get("plugins", []):
                if any(arg.lower() in plugin["name"].lower() or arg.lower() in plugin.get("description", "").lower() for arg in args):
                    out.append(f"{plugin['name']}: {plugin.get('description', 'No description.')}")
    return out
def build(data_dir, local_data_dir, config_dir, args):
    '''
    Build the plugin index from configured repositories.
    Produces a mapping of plugin name -> metadata similar to the default index used by pkg.install.
    '''
    config_dir_pkg = _get_config_dir_pkg(config_dir)
    config_dir_self = _get_config_dir_self(config_dir)
    index = {}
    for filename in os.listdir(config_dir_self):
        if not filename.endswith(".json"):
            continue
        repo_path = os.path.join(config_dir_self, filename)
        with open(repo_path, "r") as f:
            repo = json.load(f)
            plugins = repo.get("plugins", [])
            # Support both dict and list formats
            if isinstance(plugins, dict):
                for name, plugin in plugins.items():
                    if isinstance(plugin, dict):
                        index[name] = plugin
                    else:
                        index[name] = {"url": str(plugin)}
            elif isinstance(plugins, list):
                for plugin in plugins:
                    if not isinstance(plugin, dict):
                        continue
                    name = plugin.get("name") or plugin.get("id") or plugin.get("url", "").split("/")[-1].replace(".py", "")
                    index[name] = plugin
    index_path = os.path.join(config_dir_pkg, "index.json")
    with open(index_path, "w") as f:
        json.dump(index, f, indent=4)
    return f"Built plugin index with {len(index)} plugins at {index_path}."
def _get_config_dir_pkg(config_dir):
    pkg_config_dir = os.path.join(config_dir, "pkg")
    if not os.path.exists(pkg_config_dir):
        os.makedirs(pkg_config_dir)
    return pkg_config_dir
def _get_config_dir_self(config_dir):
    self_config_dir = os.path.join(config_dir, "repo")
    if not os.path.exists(self_config_dir):
        os.makedirs(self_config_dir)
    return self_config_dir