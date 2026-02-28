# ESP32 WSL2 Development Plugin

ESP32 development toolkit for Windows 11 Pro + WSL2 Ubuntu environments using ESP-IDF.

## Features

- **Environment Validation**: Comprehensive checks for WSL2, usbipd, ESP-IDF, and dependencies
- **USB Passthrough**: Wrapper scripts for usbipd-win to manage USB devices from WSL2
- **Board-Specific Skills**: Knowledge about ESP32 development boards
- **Hardware Onboarding**: Agent-guided process to add new boards to the plugin
- **Flashing & Monitoring**: Commands for common ESP-IDF workflows
- **Button Press Protocol**: Clear guidance for physical device interactions

## Supported Boards

| Board | Status | Skill |
|-------|--------|-------|
| ESP32-S3-DevKitC-1-N32R8V | Tested | `esp32-s3-devkitc` |

**Adding New Hardware**: Use the `add-hardware` agent to onboard new ESP32 boards. It guides through specification research, USB testing, and skill creation.

## Commands

| Command | Description |
|---------|-------------|
| `/esp:check` | Validate development environment |
| `/esp:attach` | Attach USB device to WSL2 via usbipd |
| `/esp:flash` | Flash firmware to ESP32 |
| `/esp:monitor` | Monitor serial output with countdown timer |

## Agents

| Agent | Description |
|-------|-------------|
| `add-hardware` | Onboard new ESP32 boards to the plugin |

## Prerequisites

- Windows 11 Pro with WSL2
- Ubuntu 24.04 (or compatible distro) in WSL2
- [usbipd-win](https://github.com/dorssel/usbipd-win) installed on Windows
- ESP-IDF v5.5+ installed in WSL2
- Python 3.x with `pyserial` package

Run `/esp:check` to validate your environment.

## Installation

1. Enable the plugin in Claude Code settings
2. Verify usbipd-win is installed on Windows:
   ```powershell
   winget install usbipd
   ```
3. Install pyserial in WSL2:
   ```bash
   pip install pyserial
   ```
4. Run environment check:
   ```
   /esp:check
   ```

## Quick Start

### 1. Check Environment
```
/esp:check
```

### 2. Attach USB Device
```
/esp:attach 5-10           # By BUSID
/esp:attach 10c4:ea60      # By VID:PID (auto-find)
```

### 3. Flash Firmware
```
/esp:flash                 # Auto-detect port
/esp:flash /dev/ttyUSB0    # Specific port
```

### 4. Monitor Serial
```
/esp:monitor               # Default: ttyUSB0, 15 seconds
/esp:monitor /dev/ttyUSB0 30
```

## Scripts

Utility scripts in `scripts/`:

| Script | Purpose |
|--------|---------|
| `check-env.py` | Comprehensive environment validation |
| `usbip` | WSL2 wrapper for usbipd-win |
| `monitor.py` | Serial monitor with countdown timer |

## Button Press Protocol

When commands require physical button presses (RST, BOOT), instructions appear in Claude's message text **before** scripts run.

**DO**: Watch for prompts like:
> "Please press the **RST** button when you see the countdown."

**DON'T**: Rely on `echo` statements inside script output for timing.

## Adding New Hardware

When you receive new ESP32 hardware:

1. Ask Claude to "add new hardware" or "onboard this board"
2. The `add-hardware` agent guides you through:
   - Specification research
   - USB enumeration testing
   - Flash/monitor testing
   - Skill creation

## Common VID:PID Values

| VID:PID | Device |
|---------|--------|
| 303a:1001 | ESP32-S3 USB JTAG/serial (running) |
| 303a:4001 | ESP32-S3 bootloader mode |
| 10c4:ea60 | CP2102N USB-to-UART bridge |
| 1a86:7523 | CH340 USB-to-UART bridge |
| 0403:6001 | FTDI FT232R |

## License

MIT
