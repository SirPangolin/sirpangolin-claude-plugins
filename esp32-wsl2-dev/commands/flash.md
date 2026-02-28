---
name: flash
description: Flash firmware to ESP32 device
argument-hint: "[port]"
allowed-tools:
  - Bash
  - Read
---

# ESP32 Flash Command

Flash ESP-IDF firmware to an ESP32 device.

## Usage

```
/esp:flash                  # Flash via auto-detected port
/esp:flash /dev/ttyUSB0     # Flash via specific port
/esp:flash /dev/ttyACM0     # Flash via native USB port
```

## Implementation

1. Check environment and ESP-IDF availability:
   ```bash
   ${CLAUDE_PLUGIN_ROOT}/scripts/check-env --quiet
   ```

2. Source ESP-IDF if not already sourced:
   ```bash
   source ~/esp/esp-idf/export.sh 2>/dev/null
   ```

3. Verify we're in a firmware directory (has CMakeLists.txt with idf.py references):
   ```bash
   grep -q "include.*project.cmake" CMakeLists.txt 2>/dev/null
   ```

4. Determine port:
   - If argument provided, use that port
   - Otherwise, prefer `/dev/ttyUSB0` (UART) if available
   - Fall back to `/dev/ttyACM0` (native USB)

5. Flash:
   ```bash
   idf.py -p <port> flash
   ```

## Bootloader Mode

If flash fails with "No serial data received" or connection errors:

**Inform the user** (in message text, not script):

> The device may need to enter bootloader mode manually. Please:
> 1. **Hold the BOOT button**
> 2. **Press and release RST** (while holding BOOT)
> 3. **Release BOOT**
>
> Then let me know when ready.

After bootloader mode, the USB device may re-enumerate. Check if re-attachment is needed:
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/usbip list
```

## Port Recommendations

| Port | Use Case |
|------|----------|
| `/dev/ttyUSB0` | UART bridge (CP2102N) - recommended, survives resets |
| `/dev/ttyACM0` | Native USB - may disconnect on reset |

## Post-Flash

After successful flash, offer to monitor:
```
Would you like to monitor serial output? Use /esp:monitor
```
