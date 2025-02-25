import textwrap
import frida
import os
import sys
import time
import dumper
import utils
import argparse
import logging

logo = """
        ______    _     _
        |  ___|  (_)   | |
        | |_ _ __ _  __| |_   _ _ __ ___  _ __
        |  _| '__| |/ _` | | | | '_ ` _ \| '_ \\
        | | | |  | | (_| | |_| | | | | | | |_) |
        \_| |_|  |_|\__,_|\__,_|_| |_| |_| .__/
                                         | |
                                         |_|
        """

def MENU():
    parser = argparse.ArgumentParser(
        prog='fridump',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(""))
    
    parser.add_argument('process', help='Process name/PID to inject')
    parser.add_argument('-o', '--out', type=str, help='Output directory', metavar="dir")
    parser.add_argument('-u', '--usb', action='store_true', help='Use USB device')
    parser.add_argument('-H', '--host', type=str, help='Remote device IP')
    parser.add_argument('-d', '--device', type=str, help='Specific USB device', metavar="device_name")
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    parser.add_argument('-r', '--read-only', action='store_true', help='Dump read-only memory')
    parser.add_argument('-s', '--strings', action='store_true', help='Extract strings')
    parser.add_argument('--max-size', type=int, help='Max dump size', metavar="bytes")
    parser.add_argument('--launch', action='store_true', help='Launch app first')
    parser.add_argument('--launch-delay', type=float, default=3.0, help='Launch delay')
    parser.add_argument('--retry', type=int, default=5, help='Retry attempts')
    return parser.parse_args()

print(logo)

arguments = MENU()

# Configuration
APP_NAME = arguments.process
DIRECTORY = arguments.out if arguments.out else os.path.join(os.getcwd(), "dump")
USB = arguments.usb
NETWORK = bool(arguments.host)
IP = arguments.host if arguments.host else None
PERMS = 'r--' if arguments.read_only else 'rw-'
MAX_SIZE = arguments.max_size or 20971520

# Logging setup
logging.basicConfig(
    format='%(levelname)s:%(message)s',
    level=logging.DEBUG if arguments.verbose else logging.INFO
)

def get_target_device():
    try:
        device_manager = frida.get_device_manager()
        
        if USB:
            devices = [d for d in device_manager.enumerate_devices() if d.type == 'usb']
            
            if arguments.verbose:
                print("Available USB devices:")
                for idx, dev in enumerate(devices):
                    print(f"  {idx+1}. {dev.id} | {dev.name}")

            if arguments.device:
                device = next((d for d in devices if d.id == arguments.device or d.id.endswith(arguments.device)), None)
                if not device:
                    print("Available devices:")
                    for d in devices:
                        print(f"  - {d.id} ({d.name})")
                    raise ValueError(f"Device '{arguments.device}' not found")
                return device
                
            if len(devices) == 1:
                return devices[0]
            
            print("Multiple devices detected. Use -d option:")
            for d in devices:
                print(f"  -d {d.id}")
            sys.exit(1)
            
        elif NETWORK:
            return device_manager.add_remote_device(IP)
            
        return frida.get_local_device()
        
    except Exception as e:
        print(f"[!] Device Error: {str(e)}")
        sys.exit(1)

def attach_to_process(device, app_name):
    pid = None
    session = None
    
    try:
        if arguments.launch:
            print(f"Launching {app_name}...")
            pid = device.spawn(app_name)
            device.resume(pid)
            time.sleep(arguments.launch_delay)

        for attempt in range(1, arguments.retry + 1):
            try:
                if pid:
                    session = device.attach(pid)
                    print(f"Attached to PID: {pid}")
                    return session
                else:
                    processes = device.enumerate_processes()
                    process = next((p for p in processes if p.name == app_name or str(p.pid) == app_name), None)
                    if process:
                        session = device.attach(process.pid)
                        print(f"Attached to process: {app_name} (PID: {process.pid})")
                        return session
                    else:
                        raise frida.ProcessNotFoundError(f"Process '{app_name}' not found")

            except frida.ProcessNotFoundError:
                if attempt < arguments.retry:
                    wait = 2 ** attempt
                    print(f"Retrying in {wait}s... ({attempt}/{arguments.retry})")
                    time.sleep(wait)
                    processes = device.enumerate_processes()
                    print("Current processes:")
                    for p in processes:
                        print(f"  - {p.pid}: {p.name}")
                else:
                    raise
                    
    except Exception as e:
        print(f"[!] Attachment Error: {str(e)}")
        if pid:
            try:
                device.kill(pid)
            except:
                pass
        sys.exit(1)

# Main execution
session = None
try:
    device = get_target_device()
    print(f"Connected to: {device.name}")
    
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)
        print(f"Created output dir: {DIRECTORY}")
        
    session = attach_to_process(device, APP_NAME)
    
    # Memory dumping logic
    script = session.create_script("""'use strict';
    rpc.exports = {
        enumerateRanges: function(prot) { return Process.enumerateRangesSync(prot); },
        readMemory: function(address, size) { return Memory.readByteArray(ptr(address), size); }
    };""")
    script.load()
    agent = script.exports_sync
    
    ranges = agent.enumerate_ranges(PERMS)
    mem_access_viol = ""
    
    for idx, range in enumerate(ranges):
        try:
            mem_access_viol = dumper.splitter(agent, range["base"], range["size"], MAX_SIZE, mem_access_viol, DIRECTORY) if range["size"] > MAX_SIZE else dumper.dump_to_file(agent, range["base"], range["size"], mem_access_viol, DIRECTORY)
            utils.printProgress(idx+1, len(ranges), prefix='Progress:', suffix='Complete', bar=50)
        except Exception as e:
            print(f"\n[!] Failed to dump range {range['base']}: {str(e)}")
            continue

    if arguments.strings:
        print("\nRunning strings analysis...")
        file_list = [f for f in os.listdir(DIRECTORY) if f.endswith('.dump')]
        for file_idx, filename in enumerate(file_list):
            utils.strings(filename, DIRECTORY)
            utils.printProgress(file_idx+1, len(file_list), prefix='Strings:', suffix='Complete', bar=50)

except Exception as e:
    print(f"[!] Fatal Error: {str(e)}")
    sys.exit(1)
finally:
    if session:
        session.detach()
        print("Operation completed")
    else:
        print("Operation failed")
