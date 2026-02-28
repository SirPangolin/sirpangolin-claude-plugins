---
name: ESP32-S3-DevKitC-1 WSL2 Flashing
description: This skill should be used when the user asks to "flash ESP32", "monitor ESP32 serial", "attach USB to WSL", "use usbipd", "enter bootloader mode", "press RST button", or is working with ESP32-S3-DevKitC-1-N32R8V board in a Windows 11 + WSL2 environment. Provides ESP-IDF flashing and serial monitoring workflows with usbipd USB passthrough.
version: 1.0.0
---

# ESP32-S3-DevKitC-1 Flashing & Monitoring (WSL2)

Comprehensive guide for flashing and monitoring the ESP32-S3-DevKitC-1-N32R8V development board using ESP-IDF in a Windows 11 Pro + WSL2 Ubuntu environment with usbipd USB passthrough.

## Hardware Overview

**Board**: ESP32-S3-DevKitC-1-N32R8V V1.1
- **Module**: ESP32-S3-WROOM-2
- **Flash**: 32MB
- **PSRAM**: 8MB (Octal SPI)
- **USB Ports**: Two micro-USB ports

### Dual USB Port Configuration

| Port Label | Chip | WSL Device | VID:PID | Purpose |
|------------|------|------------|---------|---------|
| **USB** | Native ESP32-S3 USB | `/dev/ttyACM0` | 303a:1001 | Flashing, JTAG debugging |
| **UART** | CP2102N Bridge | `/dev/ttyUSB0` | 10c4:ea60 | Serial monitoring (recommended) |

**Recommendation**: Use UART port (CP2102N) for serial monitoring. It survives device resets without disconnecting from WSL2.

## Critical: User Button Press Protocol

When requiring the user to press physical buttons (RST, BOOT), follow this protocol:

### DO: Prompt in Message Text

Provide clear instructions **in the message text before running any script**:

```
I'll start monitoring now. **Please press the RST button on the board** when you see the countdown.
```

Then run the monitoring script with a countdown timer.

### DON'T: Embed Instructions in Script Echo

Never rely on `echo` statements inside scripts to communicate button press timing:

```bash
# BAD - User may not realize this is an instruction
echo "Press RST button NOW..."
```

The user sees script output differently from Claude's direct messages and may not act on embedded instructions.

### Countdown Timer Pattern

When monitoring and expecting user button press:

```python
import threading
import time

def countdown():
    for i in range(15, 0, -1):
        print(f'\r[{i:2d}s remaining] Waiting for input...', end='', flush=True)
        time.sleep(1)

t = threading.Thread(target=countdown, daemon=True)
t.start()
```

## USB Passthrough with usbipd

### WSL2 Wrapper Script (Recommended)

Use the bundled `usbip` wrapper script to run usbipd commands from within WSL2:

```bash
# List USB devices
${CLAUDE_PLUGIN_ROOT}/scripts/usbip list

# Attach device to WSL2
${CLAUDE_PLUGIN_ROOT}/scripts/usbip attach 5-10

# Auto-attach by VID:PID
${CLAUDE_PLUGIN_ROOT}/scripts/usbip auto 10c4:ea60

# Show WSL2 serial devices
${CLAUDE_PLUGIN_ROOT}/scripts/usbip status

# Bind device (opens elevated PowerShell prompt)
${CLAUDE_PLUGIN_ROOT}/scripts/usbip bind 5-10
```

This eliminates the need to switch between WSL2 and PowerShell windows.

### Alternative: PowerShell Commands

If the wrapper script is unavailable, use PowerShell directly:

```powershell
# List connected USB devices
usbipd list

# Bind devices (one-time, persists across reboots)
usbipd bind --busid <BUSID>

# Attach to WSL2
usbipd attach --wsl --busid <BUSID>
```

### Typical Device BUSIDs

After `usbipd list`, identify devices by VID:PID:
- `303a:1001` - ESP32-S3 USB JTAG/serial (native USB port)
- `303a:4001` - ESP32-S3 in bootloader mode
- `10c4:ea60` - CP2102N USB to UART Bridge

### Re-attachment After Reset

The native USB port (`303a:1001`) disconnects and re-enumerates when the ESP32 resets. Re-attach in PowerShell:

```powershell
usbipd attach --wsl --busid <BUSID>
```

The UART port (`10c4:ea60`) survives resets because the CP2102N chip stays powered.

## Console Output Configuration

Configure in `sdkconfig.defaults`:

### UART Console (Recommended for WSL2)

```
CONFIG_ESP_CONSOLE_UART_DEFAULT=y
```

- Output on `/dev/ttyUSB0` (CP2102N)
- Survives device resets
- Requires both USB ports connected

### USB JTAG Console

```
CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y
```

- Output on `/dev/ttyACM0` (native USB)
- Works but disconnects on reset
- Requires re-attach after every reset

## Bootloader Mode Sequence

For first-time flashing or recovery when auto-reset fails:

1. **Hold BOOT button**
2. **Press and release RST button** (while holding BOOT)
3. **Release BOOT button**

The device enters bootloader mode. VID:PID changes from `303a:1001` to `303a:4001`.

After entering bootloader mode, re-attach in PowerShell if needed:

```powershell
usbipd attach --wsl --busid <BUSID>
```

## Flashing Workflow

### Prerequisites

Verify ESP-IDF environment:

```bash
source ~/esp/esp-idf/export.sh
```

### Flash via UART (Recommended)

```bash
cd /path/to/firmware
idf.py -p /dev/ttyUSB0 flash
```

### Flash via Native USB

```bash
idf.py -p /dev/ttyACM0 flash
```

Note: May require bootloader mode for first flash.

## Serial Monitoring

### Python Serial Monitor

```python
import serial

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
while True:
    data = ser.read(512)
    if data:
        print(data.decode('utf-8', errors='replace'), end='')
```

### idf.py Monitor

Requires TTY (won't work in non-interactive shells):

```bash
idf.py -p /dev/ttyUSB0 monitor
```

## Troubleshooting

### "No such file or directory: '/dev/ttyUSB0'"

USB device disconnected from WSL2. Re-attach in PowerShell:

```powershell
usbipd attach --wsl --busid <BUSID>
```

### "No serial data received" During Flash

Enter bootloader mode manually (see Bootloader Mode Sequence above).

### Serial Monitor Shows No Output

1. Verify console configuration matches the port being monitored
2. UART console → monitor `/dev/ttyUSB0`
3. USB JTAG console → monitor `/dev/ttyACM0`
4. Press RST to trigger boot messages

### Device VID:PID Changed After Flash

Normal behavior. The ESP32-S3 re-enumerates after reset:
- Bootloader: `303a:4001`
- Running firmware: `303a:1001`

Re-bind and re-attach the new device identity if needed.

## Quick Reference

### PowerShell Commands

```powershell
usbipd list                           # List USB devices
usbipd bind --busid X-Y               # Bind device (admin, once)
usbipd attach --wsl --busid X-Y       # Attach to WSL2
usbipd detach --busid X-Y             # Detach from WSL2
```

### WSL2 Commands

```bash
ls /dev/ttyUSB* /dev/ttyACM*          # List serial ports
dmesg | grep -i tty                   # Check kernel USB messages
```

### ESP-IDF Commands

```bash
source ~/esp/esp-idf/export.sh        # Load ESP-IDF environment
idf.py build                          # Build firmware
idf.py -p /dev/ttyUSB0 flash          # Flash via UART
idf.py -p /dev/ttyUSB0 monitor        # Monitor (needs TTY)
idf.py menuconfig                     # Configure sdkconfig
```

## Bundled Scripts

This plugin includes utility scripts at `${CLAUDE_PLUGIN_ROOT}/scripts/`.

### scripts/usbip

WSL2 wrapper for usbipd-win. Run usbipd commands without switching to PowerShell:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/usbip list
${CLAUDE_PLUGIN_ROOT}/scripts/usbip attach <BUSID>
${CLAUDE_PLUGIN_ROOT}/scripts/usbip auto <VID:PID>
${CLAUDE_PLUGIN_ROOT}/scripts/usbip status
```

### scripts/monitor.py

Serial monitor with countdown timer for button press timing:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/monitor.py /dev/ttyUSB0 15
```

Arguments: `[port] [duration_seconds]`

## Additional Resources

- **`references/hardware-specs.md`** - Detailed board specifications, pinout, memory configuration
