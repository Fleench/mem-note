"""Example plugin."""

def main(data_dir: str, args: list[str]) -> None:
    name = args[0] if args else "there"
    print(f"Hi, {name}! Notes live in {data_dir}.")
