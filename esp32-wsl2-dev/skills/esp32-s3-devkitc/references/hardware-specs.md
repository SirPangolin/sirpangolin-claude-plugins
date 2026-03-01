# ESP32-S3-DevKitC-1-N32R8V Hardware Specifications

## Board Identification

- **Full Name**: ESP32-S3-DevKitC-1-N32R8V V1.1
- **Module**: ESP32-S3-WROOM-2
- **Manufacturer**: Espressif Systems

## Memory Configuration

| Type | Size | Interface | Speed |
|------|------|-----------|-------|
| Flash | 32MB | Quad SPI | 80MHz |
| PSRAM | 8MB | Octal SPI | 80MHz |

### PSRAM Configuration (sdkconfig.defaults)

```
CONFIG_SPIRAM=y
CONFIG_SPIRAM_MODE_OCT=y
CONFIG_SPIRAM_SPEED_80M=y
CONFIG_SPIRAM_BOOT_INIT=y
CONFIG_SPIRAM_USE_MALLOC=y
CONFIG_SPIRAM_MALLOC_ALWAYSINTERNAL=4096
CONFIG_SPIRAM_MALLOC_RESERVE_INTERNAL=32768
```

### Verifying PSRAM in Code

```c
#include "esp_heap_caps.h"

// Get free PSRAM (should be ~8MB on boot)
size_t psram_free = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
ESP_LOGI(TAG, "Free PSRAM: %lu bytes", psram_free);

// Get total heap (internal + PSRAM)
size_t heap_free = esp_get_free_heap_size();
ESP_LOGI(TAG, "Free heap: %lu bytes", heap_free);
```

## USB Ports

The board has **two micro-USB ports**:

### Native USB Port (labeled "USB")

- **Controller**: ESP32-S3 internal USB OTG
- **Chip**: Direct to ESP32-S3 GPIO19 (D-) and GPIO20 (D+)
- **VID:PID (running)**: 303a:1001
- **VID:PID (bootloader)**: 303a:4001
- **WSL2 Device**: `/dev/ttyACM0`
- **Capabilities**:
  - USB CDC (serial)
  - USB JTAG debugging
  - DFU firmware upload
- **Limitation**: Disconnects from WSL2 on device reset (re-enumeration)

### UART Port (labeled "UART")

- **Controller**: CP2102N USB-to-UART bridge
- **Chip**: Silicon Labs CP2102N
- **VID:PID**: 10c4:ea60
- **WSL2 Device**: `/dev/ttyUSB0`
- **Baud Rate**: Up to 3 Mbps (typically 115200)
- **Capabilities**:
  - Serial communication
  - Auto-reset via RTS/DTR
- **Advantage**: Survives device resets (bridge chip stays powered)

## Buttons

### BOOT Button (GPIO0)

- **Function**: Force bootloader mode when held during reset
- **GPIO**: GPIO0 directly to ground when pressed
- **Usage**: Hold during power-on or RST to enter download mode

### RST Button

- **Function**: Hardware reset (EN pin to ground)
- **Effect**: Resets ESP32-S3, triggers USB re-enumeration
- **WSL2 Impact**: Native USB port disconnects, requires re-attach

## Power

- **Input Voltage**: 5V via either USB port
- **Regulator**: AMS1117-3.3 (3.3V LDO)
- **Current**: Up to 500mA typical, peaks higher during WiFi TX

## GPIO Pinout Highlights

| GPIO | Function | Notes |
|------|----------|-------|
| GPIO0 | BOOT button | Strapping pin, directly connected to ground when pressed |
| GPIO19 | USB_D- | Native USB data minus |
| GPIO20 | USB_D+ | Native USB data plus |
| GPIO35-37 | Reserved | Internal Octal SPI for PSRAM (do not use on N32R8V) |
| GPIO38 | RGB LED | WS2812 on v1.1 boards (silkscreen: "RGB@IO38") |
| GPIO43 | U0TXD | UART0 TX (to CP2102N RX) |
| GPIO44 | U0RXD | UART0 RX (from CP2102N TX) |
| GPIO48 | General GPIO | Was RGB LED on v1.0; available for other use on v1.1 |

## LED

- **RGB LED**: WS2812 addressable LED
  - **v1.1 boards**: GPIO38 (silkscreen shows "RGB@IO38")
  - **v1.0 boards**: GPIO48
- **Power LED (SYS)**: Red, always on when powered

## Crystal

- **Frequency**: 40MHz
- **Type**: External crystal oscillator

## Antenna

- **Type**: PCB trace antenna (onboard)
- **Frequency**: 2.4GHz (WiFi/BLE)

## Links

- [Official User Guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html)
- [ESP32-S3 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)
- [ESP32-S3 Technical Reference](https://www.espressif.com/sites/default/files/documentation/esp32-s3_technical_reference_manual_en.pdf)
