#!/usr/bin/env python3
"""
ESP32 Development Environment Checker

Validates all requirements for ESP-IDF development in a WSL2 environment:
- Windows: usbipd-win installation
- WSL2: USB tools, user permissions
- ESP-IDF: Installation, version, toolchain
- Python: Required packages

Usage:
    python3 check-env.py          # Full interactive check
    python3 check-env.py --json   # JSON output for automation
    python3 check-env.py --quiet  # Exit code only (0=pass, 1=fail)
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class CheckResult:
    """Result of a single environment check."""
    name: str
    passed: bool
    message: str
    fix: Optional[str] = None
    critical: bool = True


@dataclass
class EnvironmentReport:
    """Complete environment check report."""
    environment: str = "unknown"
    os_name: str = ""
    is_wsl2: bool = False
    checks: list = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks if c.critical)

    @property
    def critical_failures(self) -> list:
        return [c for c in self.checks if c.critical and not c.passed]

    @property
    def warnings(self) -> list:
        return [c for c in self.checks if not c.critical and not c.passed]


def run_command(cmd: list, timeout: int = 10) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return -1, "", str(e)


def check_wsl2() -> CheckResult:
    """Check if running in WSL2."""
    try:
        with open("/proc/version", "r") as f:
            version = f.read().lower()

        if "microsoft" in version:
            if "wsl2" in version or "microsoft-standard" in version:
                return CheckResult(
                    "WSL2 Environment",
                    True,
                    "Running in WSL2"
                )
            else:
                return CheckResult(
                    "WSL2 Environment",
                    False,
                    "Running in WSL1 (WSL2 required for USB passthrough)",
                    "Upgrade to WSL2: wsl --set-version <distro> 2"
                )
        else:
            return CheckResult(
                "WSL2 Environment",
                False,
                "Not running in WSL",
                "This plugin requires WSL2 on Windows"
            )
    except Exception as e:
        return CheckResult(
            "WSL2 Environment",
            False,
            f"Could not detect environment: {e}"
        )


def check_usbipd() -> CheckResult:
    """Check if usbipd-win is installed on Windows host."""
    ps_paths = [
        "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
        "/mnt/c/Windows/SysWOW64/WindowsPowerShell/v1.0/powershell.exe",
    ]

    ps_path = None
    for p in ps_paths:
        if os.path.exists(p):
            ps_path = p
            break

    if not ps_path:
        return CheckResult(
            "usbipd-win",
            False,
            "Cannot find PowerShell to check usbipd",
            critical=False
        )

    code, out, err = run_command([
        ps_path, "-Command",
        "Get-Command usbipd -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source"
    ])

    if code == 0 and out:
        # Get version
        code2, ver, _ = run_command([ps_path, "-Command", "usbipd --version"])
        version = ver if code2 == 0 else "unknown"
        return CheckResult(
            "usbipd-win",
            True,
            f"Installed (version {version})"
        )
    else:
        return CheckResult(
            "usbipd-win",
            False,
            "usbipd-win not installed on Windows",
            "Install: winget install usbipd"
        )


def check_linux_tools() -> CheckResult:
    """Check if linux-tools-generic is installed (provides usbip)."""
    code, out, err = run_command(["which", "usbip"])

    if code == 0:
        return CheckResult(
            "Linux USB Tools",
            True,
            f"usbip found at {out}"
        )
    else:
        return CheckResult(
            "Linux USB Tools",
            False,
            "usbip command not found",
            "Install: sudo apt install linux-tools-generic hwdata"
        )


def check_dialout_group() -> CheckResult:
    """Check if user is in dialout group."""
    code, out, err = run_command(["groups"])

    if code == 0 and "dialout" in out:
        return CheckResult(
            "Dialout Group",
            True,
            "User is in dialout group"
        )
    else:
        return CheckResult(
            "Dialout Group",
            False,
            "User not in dialout group (may have serial port permission issues)",
            "Fix: sudo usermod -aG dialout $USER (then log out and back in)",
            critical=False
        )


def check_esp_idf() -> CheckResult:
    """Check ESP-IDF installation and version."""
    idf_path = os.environ.get("IDF_PATH")

    if not idf_path:
        # Check if ESP-IDF exists but isn't sourced
        default_path = os.path.expanduser("~/esp/esp-idf")
        if os.path.isdir(default_path):
            return CheckResult(
                "ESP-IDF",
                False,
                "ESP-IDF found but not sourced",
                "Run: source ~/esp/esp-idf/export.sh"
            )
        else:
            return CheckResult(
                "ESP-IDF",
                False,
                "ESP-IDF not installed",
                "Install: See https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/get-started/"
            )

    # Get version
    version_file = Path(idf_path) / "version.txt"
    if version_file.exists():
        version = version_file.read_text().strip()
    else:
        code, out, err = run_command(["idf.py", "--version"])
        version = out if code == 0 else "unknown"

    # Check if version is >= 5.5
    version_match = re.search(r'v?(\d+)\.(\d+)', version)
    if version_match:
        major, minor = int(version_match.group(1)), int(version_match.group(2))
        if major < 5 or (major == 5 and minor < 5):
            return CheckResult(
                "ESP-IDF",
                False,
                f"ESP-IDF {version} is outdated",
                "Upgrade to v5.5.3 or later for ESP32-S3 support"
            )

    return CheckResult(
        "ESP-IDF",
        True,
        f"Version {version}"
    )


def check_idf_tools() -> CheckResult:
    """Check if ESP-IDF tools are available (idf.py)."""
    code, out, err = run_command(["which", "idf.py"])

    if code == 0:
        return CheckResult(
            "ESP-IDF Tools",
            True,
            "idf.py is available in PATH"
        )
    else:
        return CheckResult(
            "ESP-IDF Tools",
            False,
            "idf.py not found in PATH",
            "Run: source ~/esp/esp-idf/export.sh"
        )


def check_system_tools() -> CheckResult:
    """Check required system tools (git, cmake, ninja, python3)."""
    tools = ["git", "cmake", "ninja", "python3"]
    missing = []
    versions = {}

    for tool in tools:
        code, out, err = run_command([tool, "--version"])
        if code != 0:
            missing.append(tool)
        else:
            # Extract version from first line
            versions[tool] = out.split('\n')[0]

    if missing:
        return CheckResult(
            "System Tools",
            False,
            f"Missing: {', '.join(missing)}",
            "Install: sudo apt install git cmake ninja-build python3"
        )

    # Check cmake version >= 3.16
    cmake_ver = versions.get("cmake", "")
    cmake_match = re.search(r'(\d+)\.(\d+)', cmake_ver)
    if cmake_match:
        major, minor = int(cmake_match.group(1)), int(cmake_match.group(2))
        if major < 3 or (major == 3 and minor < 16):
            return CheckResult(
                "System Tools",
                False,
                f"CMake {major}.{minor} is too old (need >= 3.16)",
                "Upgrade cmake: sudo apt install cmake"
            )

    return CheckResult(
        "System Tools",
        True,
        "git, cmake, ninja, python3 available"
    )


def check_pyserial() -> CheckResult:
    """Check if pyserial is installed."""
    try:
        import serial
        return CheckResult(
            "PySerial",
            True,
            f"Version {serial.__version__}"
        )
    except ImportError:
        return CheckResult(
            "PySerial",
            False,
            "pyserial not installed",
            "Install: pip install pyserial",
            critical=False
        )


def check_serial_ports() -> CheckResult:
    """Check for available serial ports."""
    ports = []

    for pattern in ["/dev/ttyUSB*", "/dev/ttyACM*"]:
        import glob
        ports.extend(glob.glob(pattern))

    if ports:
        return CheckResult(
            "Serial Ports",
            True,
            f"Found: {', '.join(ports)}",
            critical=False
        )
    else:
        return CheckResult(
            "Serial Ports",
            False,
            "No serial ports found",
            "Attach USB device: Use /esp:attach or usbipd attach --wsl --busid <BUSID>",
            critical=False
        )


def run_all_checks() -> EnvironmentReport:
    """Run all environment checks and return report."""
    report = EnvironmentReport()

    # Detect environment
    wsl_check = check_wsl2()
    report.checks.append(wsl_check)
    report.is_wsl2 = wsl_check.passed

    if report.is_wsl2:
        report.environment = "wsl2"
        report.os_name = "Windows 11 + WSL2"

        # WSL2-specific checks
        report.checks.append(check_usbipd())
        report.checks.append(check_linux_tools())
        report.checks.append(check_dialout_group())
    else:
        report.environment = "linux" if "linux" in sys.platform else sys.platform
        report.os_name = sys.platform

    # ESP-IDF checks
    report.checks.append(check_esp_idf())
    report.checks.append(check_idf_tools())

    # System tools
    report.checks.append(check_system_tools())
    report.checks.append(check_pyserial())

    # Serial ports (non-critical)
    report.checks.append(check_serial_ports())

    return report


def print_report(report: EnvironmentReport):
    """Print formatted report to console."""
    COLORS = {
        'GREEN': '\033[0;32m',
        'RED': '\033[0;31m',
        'YELLOW': '\033[1;33m',
        'BLUE': '\033[0;34m',
        'NC': '\033[0m'
    }

    print(f"\n{COLORS['BLUE']}{'=' * 50}")
    print("ESP32 Development Environment Check")
    print(f"{'=' * 50}{COLORS['NC']}\n")

    print(f"Environment: {COLORS['GREEN']}{report.environment}{COLORS['NC']}")
    print(f"OS: {report.os_name}")
    print()

    print(f"{COLORS['BLUE']}--- Checks ---{COLORS['NC']}\n")

    for check in report.checks:
        if check.passed:
            status = f"{COLORS['GREEN']}✓{COLORS['NC']}"
        elif check.critical:
            status = f"{COLORS['RED']}✗{COLORS['NC']}"
        else:
            status = f"{COLORS['YELLOW']}!{COLORS['NC']}"

        print(f"{status} {check.name}: {check.message}")
        if not check.passed and check.fix:
            print(f"    → Fix: {check.fix}")

    print()

    if report.passed:
        print(f"{COLORS['GREEN']}Environment is ready for ESP32 development!{COLORS['NC']}")
    else:
        failures = report.critical_failures
        print(f"{COLORS['RED']}Environment has {len(failures)} critical issue(s) to resolve.{COLORS['NC']}")

    if report.warnings:
        print(f"{COLORS['YELLOW']}Additionally, {len(report.warnings)} warning(s) noted.{COLORS['NC']}")

    print()


def main():
    args = sys.argv[1:]

    report = run_all_checks()

    if "--json" in args:
        # JSON output
        output = {
            "environment": report.environment,
            "os": report.os_name,
            "is_wsl2": report.is_wsl2,
            "passed": report.passed,
            "checks": [asdict(c) for c in report.checks],
            "critical_failures": len(report.critical_failures),
            "warnings": len(report.warnings)
        }
        print(json.dumps(output, indent=2))
    elif "--quiet" in args:
        # Exit code only
        pass
    else:
        # Interactive output
        print_report(report)

    sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
