import platform
import sys
import ctypes
import os

OS_List=["Windows","Linux"]

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
            return True
        else:
            sys.exit(str(bool(win_admin)) + " -> Insufficient privileges, please run as administrator")

    elif os_name == "Linux":
        linux_admin = os.geteuid() == 0
        if linux_admin:
           return True
        else:
            sys.exit(str(bool(linux_admin)) + " -> Insufficient privileges, please run as root")

def main():
    os_name = os_detect()
    print(os_name)
    print(is_admin(os_name))

if __name__ == "__main__":
    main()


