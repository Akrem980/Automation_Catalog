# Reboot-to-BIOS

A small cross-platform Python utility that restarts your computer straight into the BIOS/UEFI firmware setup screen, so you never have to hammer F2, Del or F10 during boot.

It asks the firmware to open its setup screen on the **next boot** only, then reboots. It does not change any firmware setting and does not touch your boot configuration. After you leave the setup screen, the machine boots normally.

> **Warning:** the reboot is immediate. There is no countdown and no way to cancel once you confirm. Save your work and close your applications first.

## What it does

When you run the script, it:

1. Shows a banner and a short description.
2. Detects the operating system (Windows or Linux).
3. Verifies that it has administrator/root privileges.
4. Verifies that the machine booted in UEFI mode.
5. Asks for confirmation (`y`/`yes` to continue, `n`/`no` to cancel).
6. Reboots into the firmware setup screen.

If any check fails, it stops with a clear message and a non-zero exit status, and nothing is rebooted. Any answer other than a clear yes cancels the run.

## Requirements

- **Windows 8 or newer**, or a **Linux distribution with systemd**
- A machine that booted in **UEFI mode** (not legacy BIOS)
- **Administrator** rights (Windows) or **root** (Linux)
- **Python 3**, tested with 3.10 on Ubuntu and 3.14 on Windows
- The `colorama` package, used for coloured output on Windows terminals:

```
pip install "colorama>=0.4.6" 
```
- If `pip` does not work directly, **try** :

```
python -m pip install "colorama>=0.4.6" 
```

No environment variables or configuration files are needed.

## Usage

**Windows:** open a terminal with *Run as administrator*, then:

```
python script.py
```

**Linux:**

```
sudo python3 script.py
```

Follow the prompt. Answer `y` to reboot into the firmware setup, or `n` to cancel.

## How it works

| Step | Windows | Linux |
|------|---------|-------|
| Admin check | `IsUserAnAdmin()` from `shell32`, called through `ctypes` | `os.geteuid() == 0` |
| UEFI check | `GetFirmwareType()` from `kernel32` (value `2` = UEFI, `1` = legacy BIOS) | the folder `/sys/firmware/efi` exists |
| Reboot command | `shutdown /r /fw /t 0` | `systemctl reboot --firmware-setup` |

Each OS-specific call runs only on its own OS, so the script never calls a Windows function on Linux or the reverse.

## Testing

| Scenario | Result |
|----------|--------|
| Linux (Ubuntu VM in VirtualBox with EFI enabled), run with `sudo`, answer `y` | Reaches the firmware setup screen |
| Linux VM booted in legacy BIOS mode | Refuses to continue and reports that UEFI was not detected |
| Linux without `sudo` | Refuses to continue and asks for root |
| Unsupported OS (simulated with `unittest.mock.patch` on `platform.system`) | Exits with a message listing the supported systems, exit status `1` |
| Windows, UEFI laptop: admin check and UEFI detection | Verified; refuses without admin rights |
| Windows, full reboot into firmware setup | _To be confirmed_ |

## Limitations

- Only **Windows** and **Linux** are supported. Other systems, including macOS, are detected and refused, because the commands used here do not exist there and could not be tested.
- **UEFI only.** Machines in legacy BIOS mode are refused.
- The reboot is **immediate**: there is no countdown on either system. On older systemd versions (before 255) `systemctl reboot` has no `--when` option, so a delay would have to be handled in the script itself.
- The result depends on the firmware. If it does not open the setup screen, the machine simply boots normally and you can fall back to your manufacturer's key.
- Colours and progress bars assume an interactive terminal.