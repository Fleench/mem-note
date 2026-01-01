"""Example plugin."""


def meta_data():
    return {
        "name": "hi",
        "description": "Example plugin that greets the user.",
        "file_path": __file__,
    }

def main(data_dir: str, args: list[str]) -> None:
    name = args[0] if args else "there"
    print(f"Hi, {name}! Notes live in {data_dir}.")
