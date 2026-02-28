#!/usr/bin/env python3
"""
Serial monitor for ESP32-S3-DevKitC-1 with countdown timer.

Usage:
    python monitor.py [port] [duration]

    port: Serial port (default: /dev/ttyUSB0)
    duration: Monitoring duration in seconds (default: 15)

Examples:
    python monitor.py                      # Monitor ttyUSB0 for 15s
    python monitor.py /dev/ttyACM0         # Monitor native USB
    python monitor.py /dev/ttyUSB0 30      # Monitor for 30 seconds
"""

import sys
import time
import threading
import argparse

try:
    import serial
except ImportError:
    print("Error: pyserial module not found.", file=sys.stderr)
    print("Install it with: pip install pyserial", file=sys.stderr)
    sys.exit(1)


def countdown_timer(duration: int, stop_event: threading.Event):
    """Display countdown timer until stop_event is set or duration expires."""
    for remaining in range(duration, 0, -1):
        if stop_event.is_set():
            break
        print(f'\r[{remaining:2d}s remaining] Waiting for data...', end='', flush=True)
        time.sleep(1)
    if not stop_event.is_set():
        print('\r[TIMEOUT]                              ')


def monitor_serial(port: str, baud: int, duration: int):
    """Monitor serial port with countdown timer."""
    try:
        ser = serial.Serial(port, baud, timeout=0.5)
    except serial.SerialException as e:
        print(f"Error opening {port}: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if device is attached: ls /dev/tty*")
        print("  2. Re-attach in PowerShell: usbipd attach --wsl --busid <BUSID>")
        return False

    print(f"=== Monitoring {port} at {baud} baud ===")
    print(f"Duration: {duration} seconds")
    print("")

    # Start countdown in background
    stop_event = threading.Event()
    countdown_thread = threading.Thread(
        target=countdown_timer,
        args=(duration, stop_event),
        daemon=True
    )
    countdown_thread.start()

    output_received = False
    start_time = time.time()

    try:
        while time.time() - start_time < duration:
            data = ser.read(512)
            if data:
                if not output_received:
                    stop_event.set()  # Stop countdown
                    print('\r' + ' ' * 40 + '\r', end='')  # Clear countdown line
                    print("=== OUTPUT RECEIVED ===")
                    output_received = True
                print(data.decode('utf-8', errors='replace'), end='', flush=True)
    except serial.SerialException as e:
        print(f"\nSerial error: {e}")
        print("Device may have disconnected (reset triggered)")
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    finally:
        stop_event.set()
        ser.close()

    print("")
    if output_received:
        print("=== MONITORING COMPLETE ===")
    else:
        print("=== NO OUTPUT RECEIVED ===")
        print("\nPossible causes:")
        print("  1. Wrong port (UART console on ttyUSB0, USB JTAG on ttyACM0)")
        print("  2. Console not configured for this port in sdkconfig")
        print("  3. Device not running (try pressing RST)")

    return output_received


def main():
    parser = argparse.ArgumentParser(
        description='Serial monitor for ESP32-S3-DevKitC-1 with countdown timer'
    )
    parser.add_argument(
        'port',
        nargs='?',
        default='/dev/ttyUSB0',
        help='Serial port (default: /dev/ttyUSB0)'
    )
    parser.add_argument(
        'duration',
        nargs='?',
        type=int,
        default=15,
        help='Monitoring duration in seconds (default: 15)'
    )
    parser.add_argument(
        '-b', '--baud',
        type=int,
        default=115200,
        help='Baud rate (default: 115200)'
    )

    args = parser.parse_args()

    success = monitor_serial(args.port, args.baud, args.duration)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
