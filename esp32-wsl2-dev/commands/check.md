---
name: check
description: Check ESP32 development environment (WSL2, usbipd, ESP-IDF, etc.)
argument-hint: "[--json]"
allowed-tools:
  - Bash
  - Read
---

# ESP32 Environment Check Command

Validate the complete ESP32 development environment including WSL2, usbipd, ESP-IDF, and required tools.

## Usage

```
/esp:check          # Interactive check with colored output
/esp:check --json   # JSON output for automation
```

## Implementation

Run the environment check script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check-env.py
```

Or with JSON output:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check-env.py --json
```

## Checks Performed

| Category | What's Checked |
|----------|----------------|
| **WSL2** | Running in WSL2, not WSL1 or native Linux |
| **usbipd-win** | Installed on Windows host |
| **Linux USB Tools** | usbip command available |
| **Dialout Group** | User has serial port permissions |
| **ESP-IDF** | Installed and sourced, version >= 5.5 |
| **System Tools** | git, cmake, ninja, python3 |
| **PySerial** | Python serial library installed |
| **Serial Ports** | USB devices currently attached |

## Interpreting Results

- **✓ Green**: Check passed
- **✗ Red**: Critical failure (must fix)
- **! Yellow**: Warning (should fix but not blocking)

Each failed check includes a suggested fix command.

## Common Issues

### "ESP-IDF found but not sourced"
```bash
source ~/esp/esp-idf/export.sh
```

### "User not in dialout group"
```bash
sudo usermod -aG dialout $USER
# Then log out and back in
```

### "usbipd-win not installed"
In Windows PowerShell (Admin):
```powershell
winget install usbipd
```
