import os
import sys
import time
import urllib.request
import subprocess
import serial
from intelhex import IntelHex

def hex_to_bin(hex_path, bin_path):
    print(f"Converting {hex_path} to {bin_path}...")
    ih = IntelHex(hex_path)
    ih.tobinfile(bin_path)
    print("Conversion complete.")

def get_firmware(target, version, dest_dir):
    hex_name = f"inav_{version}_{target}.hex"
    hex_path = os.path.join(dest_dir, hex_name)
    bin_name = f"inav_{version}_{target}.bin"
    bin_path = os.path.join(dest_dir, bin_name)
    
    if os.path.exists(bin_path):
        print(f"Binary already exists: {bin_path}")
        return bin_path
        
    if not os.path.exists(hex_path):
        url = f"https://github.com/iNavFlight/inav/releases/download/{version}/{hex_name}"
        print(f"Downloading firmware from {url}...")
        try:
            urllib.request.urlretrieve(url, hex_path)
            print(f"Downloaded to {hex_path}")
        except Exception as e:
            print(f"Failed to download firmware: {e}")
            # Try lowercase release folder name just in case (some releases use RC tags or different formatting)
            print("Retrying with alternative URL formats might be needed if tag is an RC.")
            return None
            
    hex_to_bin(hex_path, bin_path)
    return bin_path

def reboot_to_dfu(port_name):
    print(f"Connecting to {port_name} to reboot into DFU mode...")
    try:
        ser = serial.Serial(port_name, 115200, timeout=1.0)
    except Exception as e:
        print(f"Failed to open port {port_name}: {e}")
        print("Please check if the board is connected and not opened by another application (e.g. Configurator).")
        return False
        
    time.sleep(0.5)
    ser.reset_input_buffer()
    
    # Enter CLI
    ser.write(b'\r\n#\r\n')
    time.sleep(0.5)
    ser.read(2048)
    
    # Send dfu reboot command
    print("Sending 'dfu' command to FC...")
    ser.write(b'dfu\n')
    time.sleep(0.5)
    ser.close()
    print("Reboot command sent.")
    return True

def wait_for_dfu(timeout=15):
    print("Waiting for DFU device to be detected...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Run dfu-util -l to check if device is present
            res = subprocess.run(["dfu-util", "-l"], capture_output=True, text=True)
            if "Found DFU:" in res.stdout or "0483:df11" in res.stdout:
                print("DFU device detected!")
                return True
        except FileNotFoundError:
            print("Error: dfu-util not found in PATH.")
            return False
        time.sleep(1.0)
    print("DFU device not detected. Make sure drivers are correct (WinUSB/libusb via Zadig).")
    return False

def flash_dfu(bin_path):
    print(f"Flashing {bin_path} using dfu-util...")
    # STM32 F405 starts at 0x08000000
    cmd = [
        "dfu-util",
        "-a", "0",
        "-d", "0483:df11",
        "-s", "0x08000000:leave",
        "-D", bin_path
    ]
    print(f"Running command: {' '.join(cmd)}")
    res = subprocess.run(cmd)
    if res.returncode == 0:
        print("Flashing completed successfully!")
        return True
    else:
        print(f"Flashing failed with exit code: {res.returncode}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Automate downloading, DFU-rebooting, and flashing INAV firmware.")
    parser.add_argument("--port", default="COM6", help="Serial port of the FC (default: COM6)")
    parser.add_argument("--target", default="ATOMRCF405NAVI_DELUX", help="INAV hardware target (default: ATOMRCF405NAVI_DELUX)")
    parser.add_argument("--version", default="9.1.0", help="INAV version to flash (default: 9.1.0)")
    parser.add_argument("--dir", default=".", help="Directory to store downloaded firmwares (default: current directory)")
    parser.add_argument("--skip-reboot", action="store_true", help="Skip sending reboot command (if already in DFU mode)")
    
    args = parser.parse_args()
    
    bin_path = get_firmware(args.target, args.version, args.dir)
    if not bin_path:
        print("Error obtaining firmware binary. Aborting.")
        sys.exit(1)
        
    if not args.skip_reboot:
        if not reboot_to_dfu(args.port):
            print("Could not reboot board automatically. Please press the boot button manually while plugging in USB.")
            
    if wait_for_dfu():
        flash_dfu(bin_path)
    else:
        print("Could not flash because DFU device was not found.")

if __name__ == "__main__":
    main()
