# Message Handler

This package is meant to be a one-stop-shop for handling commands sent via mesh nodes (Meshtastic, Meshcore, Reticulum). It's desinged to be short, simple, and useful.

Some examples of commands include:
- `!w`: Get, Set waypoints
- `!i`: Get service information (version, repo URL)
- `!h`: Get a list of commands

More commands are on the way, so check back.

## JSON CLI Commands

This package allows for you to define and execute select CLI commands from the mesh.

An example JSON configuration exists in the `commands.json` file.

You can only execute commands as defined in the JSON file keys. So if someone sends you a `sudo rm -rf /` command and it's *not* defined in the JSON file, it won't execute. Also only designated admin IDs can execute commands. You can define the `admins` upon initializing the `MeshCommandHandler()`. By default it's disabled.

> [!CAUTION]
> Don't be stupid with the commands you define. Remember, the mesh is public. This is an ease of use feature. Use at your own risk, especially if you don't have physical or SSH access to your node.

### How it Works

1. Define a JSON file with a set of CLI commands with an associated shorthand alias. For example:

```json
{
    "docker": "docker compose pull && docker compose up -d --force-recreate"

}
```

2. User sends a `!cmd list` text message. If their node ID is in the `admins` list, we return a list of shorthand commands they can use.

3. Whitelisted admin user sends `!cmd docker` and we execute the defined CLI command.


### Examples

- Turn on / off WiFi ad-hoc hotspots on Raspberry Pi Nodes
- Trigger remote updates without logging in to SSH (at your own risk)
- Trigger shell commands such as `rsync` backups

## Contributing

Ruff formatting:

```bash
uvx ruff format .
```

Running pytest:

```bash
uv run pytest -s
```
