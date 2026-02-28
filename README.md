# SirPangolin Claude Plugins

A personal marketplace of Claude Code plugins.

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [esp32-wsl2-dev](./esp32-wsl2-dev/) | ESP32 development toolkit for Windows 11 + WSL2 environments |

## Installation

### Option 1: Add as Marketplace (Recommended)

Add this repository as a marketplace source in your Claude Code configuration. This enables automatic updates and discovery.

### Option 2: Direct Plugin Load

Load a specific plugin directly:

```bash
claude --plugin-dir /path/to/sirpangolin-claude-plugins/esp32-wsl2-dev
```

### Option 3: Clone to Plugins Directory

```bash
git clone https://github.com/SirPangolin/sirpangolin-claude-plugins.git
cd sirpangolin-claude-plugins
cp -r esp32-wsl2-dev ~/.claude/plugins/
```

## Plugin Development

Each plugin follows the standard Claude Code plugin structure:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # Plugin manifest
├── README.md            # Plugin documentation
├── commands/            # Slash commands
├── agents/              # Autonomous agents
├── skills/              # Knowledge & workflows
└── scripts/             # Utility scripts
```

## License

MIT
