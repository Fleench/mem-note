"""Example plugin."""


def     :
    return {
        "name": "hi",
        "description": "Example plugin that greets the user.",
        "file_path": __file__,
    }

def main(data_dir, local_data_dir, config_dir, args):
    name = args[0] if args else "there"
    print(f"Hi, {name}! Data lives in {data_dir}.")
