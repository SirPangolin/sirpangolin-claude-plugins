---
name: attach
description: Attach USB device to WSL2 via usbipd
argument-hint: "<BUSID|VID:PID>"
allowed-tools:
  - Bash
  - Read
---

# ESP32 USB Attach Command

Attach a USB device to WSL2 using the usbipd wrapper script.

## Usage

```
/esp:attach 5-10           # Attach by BUSID
/esp:attach 10c4:ea60      # Attach by VID:PID (auto-find BUSID)
/esp:attach                 # List available devices
```

## Implementation

1. First, check the environment:
   ```bash
   ${CLAUDE_PLUGIN_ROOT}/scripts/check-env --quiet || echo "Environment issues detected"
   ```

2. If no argument provided, list devices:
   ```bash
   ${CLAUDE_PLUGIN_ROOT}/scripts/usbip list
   ```

3. If argument contains `:` (VID:PID format), use auto-attach:
   ```bash
   ${CLAUDE_PLUGIN_ROOT}/scripts/usbip auto <VID:PID>
   ```

4. Otherwise, attach by BUSID:
   ```bash
   ${CLAUDE_PLUGIN_ROOT}/scripts/usbip attach <BUSID>
   ```

5. Verify attachment:
   ```bash
   ls -la /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
   ```

## Common VID:PID Values

| VID:PID | Device |
|---------|--------|
| 303a:1001 | ESP32-S3 USB JTAG/serial (running) |
| 303a:4001 | ESP32-S3 bootloader mode |
| 10c4:ea60 | CP2102N USB-to-UART bridge |
| 1a86:7523 | CH340 USB-to-UART bridge |

## Error Handling

If "not shared" error occurs, inform user to run bind first:
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/usbip bind <BUSID>
```

Note: Bind requires Windows administrator privileges and will open an elevated PowerShell prompt.
