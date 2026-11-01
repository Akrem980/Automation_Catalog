import platform
import sys
import ctypes
import os
from ctypes import wintypes

OS_List=["Windows","Linux"]
uefi_path = "/sys/firmware/efi"

def os_detect():
    platform_system = platform.system()
    if platform_system in OS_List:
        return platform_system
    else:
        sys.exit("Unsupported OS : " + platform_system + "\nSupported : " + ", ".join(OS_List))

def is_admin(os_name):
    if os_name == "Windows":
        win_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if win_admin:
            return "admin privileges -> True"
        else:
            sys.exit(str(bool(win_admin)) + " -> Insufficient privileges, please run as administrator")

    elif os_name == "Linux":
        linux_admin = os.geteuid() == 0
        if linux_admin:
           return "admin privileges -> True"
        else:
            sys.exit(str(bool(linux_admin)) + " -> Insufficient privileges, please run as root")

def uefi_check(os_name):
    if os_name == "Windows":
        bios_mode = ctypes.windll.kernel32
        firmware_type_val = ctypes.c_int()
        bios_mode.GetFirmwareType.argtypes = [ctypes.POINTER(ctypes.c_int)]
        bios_mode.GetFirmwareType.restype = wintypes.BOOL
        success = bios_mode.GetFirmwareType(ctypes.byref(firmware_type_val))
        if success and firmware_type_val.value == 2:
            return "UEFI detected"
        elif success and firmware_type_val.value == 1:
            sys.exit("Legacy BIOS detected, please boot in UEFI mode")
        else:
            sys.exit("Unable to determine firmware type")


    if os_name == "Linux":
        if os.path.exists(uefi_path):
            return "UEFI detected"
        else:
            sys.exit("UEFI not detected, please boot in UEFI mode")

def main():
    os_name = os_detect()
    print(os_name)
    print(is_admin(os_name))
    print(uefi_check(os_name))

if __name__ == "__main__":
    main()