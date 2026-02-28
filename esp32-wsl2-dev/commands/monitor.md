---
name: monitor
description: Monitor ESP32 serial output with countdown timer
argument-hint: "[port] [duration]"
allowed-tools:
  - Bash
  - Read
---

# ESP32 Serial Monitor Command

Monitor serial output from an ESP32 device with a countdown timer for button press timing.

## Usage

```
/esp:monitor                    # Monitor ttyUSB0 for 15 seconds
/esp:monitor /dev/ttyUSB0       # Monitor specific port for 15 seconds
/esp:monitor /dev/ttyACM0 30    # Monitor native USB for 30 seconds
```

## Implementation

1. Parse arguments:
   - First argument: port (default: `/dev/ttyUSB0`)
   - Second argument: duration in seconds (default: 15)

2. Verify port exists:
   ```bash
   ls -la <port> 2>/dev/null
   ```

3. If port doesn't exist, check USB attachment:
   ```bash
   ${CLAUDE_PLUGIN_ROOT}/scripts/usbip status
   ```

4. **CRITICAL: Button Press Protocol**

   If expecting the user to press RST to see boot messages, provide instructions **in your message text before running the script**:

   > I'll start monitoring now. **Please press the RST button on the board** when you see the countdown timer start.

5. Run the monitor script:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/monitor.py <port> <duration>
   ```

## Button Press Protocol

**DO**: Prompt in message text before running script
**DON'T**: Rely on echo statements inside scripts

The user sees Claude's messages and script output differently. Instructions embedded in script `echo` statements may not be acted upon.

## Interpreting Output

### Successful Output
```
I (1234) app_name: Heartbeat - heap: 8728284
```
- Numbers in parentheses are milliseconds since boot
- "heap" shows free memory (PSRAM + internal)

### No Output
If no output received:
1. Verify console config matches port (UART → ttyUSB0, USB_JTAG → ttyACM0)
2. Press RST to trigger boot messages
3. Check `sdkconfig` for `CONFIG_ESP_CONSOLE_*` setting

### Device Disconnected
If "device disconnected" error:
- Native USB re-enumerates on reset
- Re-attach with `/esp:attach`

## Duration Guidelines

| Scenario | Recommended Duration |
|----------|---------------------|
| Quick check | 10s |
| Capture boot messages | 15s |
| Extended monitoring | 30-60s |
| Debug session | Run `idf.py monitor` in terminal |
