"""Example plugin."""

VMAJOR = 0
VMINOR = 4
VPATCH = 0
ID = "com.flench04.hi"


def meta_data():
    return {
        "name": "hi",
        "description": "Example plugin that greets the user.",
        "file_path": __file__,
    }

def main(api, args):
    name = args[0] if args else "there"
    data_dir = api["get_data_local_dir"]()
    return f"Hi, {name}! Data lives in {data_dir}."
