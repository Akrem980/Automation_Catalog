import platform
import sys

OS_List=["Windows","Linux"]

def os_detect():
    platform_system = platform.system()
    if platform_system in OS_List:
        return platform_system
    else:
        sys.exit("Unsupported OS : " + platform_system + "\nSupported : " + ", ".join(OS_List))

def main():
    print(os_detect())
    
if __name__ == "__main__":
    main()


