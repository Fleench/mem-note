# Memory Note

A basic memory/note CLI tool.

## Usage

```sh
mem-note new shopping "Milk and bread"
mem-note list
mem-note recall shopping
mem-note delete shopping
```

## Plugins

Plugins are loaded from the user config directory. The example plugin in
`src/mem/plugins/hi.py` shows the expected `main(data_dir, args)` entry point.
