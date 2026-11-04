import argparse
import ctypes
import os
import platform
import subprocess
import sys
from ctypes import wintypes
import random
from colorama import just_fix_windows_console
import time

just_fix_windows_console()


OS_List = ["Windows", "Linux"]
uefi_path = "/sys/firmware/efi"
command_win = ["shutdown", "/r", "/fw", '/t', '0']
command_linux = ["systemctl", "reboot", "--firmware-setup"]
vocabulary_p = {"yes", "y"}
vocabulary_n = {"no", "n"}

banner = [
"""
██████╗ ███████╗██████╗  ██████╗  ██████╗ ████████╗         ██╗      ██████╗ ██╗ ██████╗ ███████╗
██╔══██╗██╔════╝██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝         ╚██╗     ██╔══██╗██║██╔═══██╗██╔════╝
██████╔╝█████╗  ██████╔╝██║   ██║██║   ██║   ██║       █████╗╚██╗    ██████╔╝██║██║   ██║███████╗
██╔══██╗██╔══╝  ██╔══██╗██║   ██║██║   ██║   ██║       ╚════╝██╔╝    ██╔══██╗██║██║   ██║╚════██║
██║  ██║███████╗██████╔╝╚██████╔╝╚██████╔╝   ██║            ██╔╝     ██████╔╝██║╚██████╔╝███████║
╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝  ╚═════╝    ╚═╝            ╚═╝      ╚═════╝ ╚═╝ ╚═════╝ ╚══════╝
"""                                                                                                                                                                                                                                                                                                                                                                    
]

def gradient_banner(banner_lines):
    # Generate random start and end RGB colors for the horizontal gradient
    r1, g1, b1 = random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)
    r2, g2, b2 = random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)
    
    max_width = max(len(line) for line in banner_lines)
    
    for line in banner_lines:
        colored_line = []
        for x, char in enumerate(line):
            if char.isspace():
                colored_line.append(char)
                continue
            
            # Calculate horizontal position ratio (0.0 to 1.0)
            t = x / max(max_width - 1, 1)
            
            # Interpolate RGB values across the width
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            
            # Apply ANSI 24-bit Truecolor escape sequence
            colored_line.append(f"\033[38;2;{r};{g};{b}m{char}")
            
        print("".join(colored_line) + "\033[0m") # Print a separator line in gray

def description():
    desc = (
        "\033[90m[+] A cross-platform utility designed to verify UEFI compatibility,\n"
        "    verify administrator/root privileges, and securely reboot your\n"
        "    system directly into BIOS/UEFI firmware settings.\033[0m\n"
    )
    print(desc)

def show_progress_bar(total=50, prefix='', length=30, fill='█'):
    for i in range(total + 1):
        percent = f"{100 * (i / float(total)):.1f}"
        filled_length = int(length * i // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        sys.stdout.write(f'\r{prefix} |{bar}| {percent}')
        sys.stdout.flush()
        time.sleep(0.02)
    print()


def os_detect():
    show_progress_bar(total=50, prefix='Detecting OS:', length=30, fill='█')
    platform_system = platform.system()
    if platform_system in OS_List:
        print(f"\033[32m>> Operating System Verified:\033[0m {platform_system}\n")
        return platform_system
    else:
        sys.exit(
            "\033[31m>> Unsupported OS :\033[0m "
            + platform_system
            + "\n\033[32mSupported :\033[0m "
            + ", ".join(OS_List)
        )


def is_admin(os_name):
    show_progress_bar(total=50, prefix='Checking Admin Privileges:', length=30, fill='█')
    if os_name == "Windows":
        win_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if win_admin:
            return "\033[32m>> Privilege Status:\033[0m Administrator Access Confirmed\n"
        else:
            sys.exit("\n\033[31m>> Insufficient Privileges (False):\033[0m Please run as Administrator")

    elif os_name == "Linux":
        linux_admin = os.geteuid() == 0
        if linux_admin:
            return "\033[32m>> Privilege Status:\033[0m Root Access Confirmed\n"
        else:
            sys.exit("\n\033[31m>> Insufficient Privileges (False):\033[0m Please run as root")


def uefi_check(os_name):
    show_progress_bar(total=50, prefix='Checking UEFI Compatibility:', length=30, fill='█')
    if os_name == "Windows":
        bios_mode = ctypes.windll.kernel32
        firmware_type_val = ctypes.c_int()
        bios_mode.GetFirmwareType.argtypes = [ctypes.POINTER(ctypes.c_int)]
        bios_mode.GetFirmwareType.restype = wintypes.BOOL
        success = bios_mode.GetFirmwareType(ctypes.byref(firmware_type_val))
        if success and firmware_type_val.value == 2:
            return "\033[32m>> UEFI Compatibility:\033[0m UEFI detected\n"
        elif success and firmware_type_val.value == 1:
            sys.exit("\033[31m>> Legacy BIOS detected\033[0m, please boot in UEFI mode")
        else:
            sys.exit("\033[31m>> Unable to determine firmware type\033[0m")

    if os_name == "Linux":
        if os.path.exists(uefi_path):
            return "\033[32m>> UEFI Compatibility:\033[0m UEFI detected\n"
        else:
            sys.exit("\033[31m>> UEFI not detected\033[0m, please boot in UEFI mode")


def reboot(os_name):
    confirm = input("Are you sure you want to reboot into BIOS/UEFI? (y/n): ").lower().strip()
    if confirm in vocabulary_n:
        sys.exit("\033[31m>> Reboot cancelled.\033[0m")
    elif confirm not in vocabulary_p and confirm not in vocabulary_n:
         sys.exit("\033[31m>> Invalid input. Please enter 'y'/'yes' or 'n'/'no'.\033[0m")
    else:
        print("\033[32m>> Rebooting into BIOS/UEFI...\033[0m")
        if os_name == "Windows":
                    show_progress_bar(total=50, length=30, fill='█')
                    #subprocess.run(command_win, check=True)
                    pass
        if os_name == "Linux":
                    show_progress_bar(total=50, length=30, fill='█')
                    #subprocess.run(command_linux, check=True)
                    pass


def main():
    gradient_banner(banner)
    description()
    os_name = os_detect()
    print(is_admin(os_name))
    print(uefi_check(os_name))
    reboot(os_name)



if __name__ == "__main__":
    main()

                                                                               
