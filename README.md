# Fridump3 for Fix USB Errors and Add Device mod
Fridump is an open source memory dumping tool, primarily aimed to penetration testers and developers. Fridump is using the Frida framework to dump accessible memory addresses from any platform supported. It can be used from a Windows, Linux or Mac OS X system to dump the memory of an iOS, Android or Windows application.

This project is based on the following project:
Origin Fridump: [https://github.com/Nightbringer21/fridump](https://github.com/Nightbringer21/fridump) and Editing Fridump: [([https://github.com/rootbsd/fridump3](https://github.com/rootbsd/fridump3))]([https://github.com/Nightbringer21/fridump](https://github.com/rootbsd/fridump3)) the pending PR concerning the python3 support (especially from [georgepetz](https://github.com/georgepetz) . Additionally I added the network support in addition to the USB support.

FYI: I will destroy this repo is the Fridump author will integrate the pending PR concerning Python3 support.

'+ This code is a fixed version of the code fridump3 specifying the device and a chronic iOS error occurring in Frida 16.1.x and later versions.

**Installation**
---
```
https://github.com/KaiHT-Ladiant/fridump3-Fix-USB-Errors.git
python fridump3e.py -h
```

**Pre-requires**
---
To use fridump3e you need to have frida installed on your python environment and frida-server on the device you are trying to dump the memory from. The easiest way to install frida on your python is using pip:
```python
pip install frida
```

Usage
---

```
usage: fridump [-h] [-o dir] [-u] [-H HOST] [-d device_name] [-v] [-r] [-s] [--max-size bytes] [--launch] [--launch-delay LAUNCH_DELAY] [--retry RETRY] process

positional arguments:
  process               the process that you will be injecting to

optional arguments:
  -h, --help            show this help message and exit
  -o dir, --out dir     Output directory
  -u, --usb             Use USB device
  -H HOST, --host HOST  Remote device IP
  -d device_name, --device device_name
                        Specific USB device
  -v, --verbose         Verbose mode
  -r, --read-only       Dump read-only memory
  -s, --strings         Extract strings
  --max-size bytes      Max dump size
  --launch              Launch app first
  --launch-delay LAUNCH_DELAY
                        Launch delay
  --retry RETRY         Retry attempts
```

Additional features in this code include the dumping function after application execution, the delay function of application execution, the retry function after application dump failure, and the device designation execution function.

**Using Example**
---
```python
python .\fridump3e.py --launch -u -d [DeviceName] -r [YourPackageName] -s
```
- If the s option is difficult to execute, see the following program: (strings2 extension): [Here](https://objects.githubusercontent.com/github-production-release-asset-2e65be/7199192/f38a62d6-4ae7-40ce-851f-4d487861b4b0?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=releaseassetproduction%2F20250224%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250224T064603Z&X-Amz-Expires=300&X-Amz-Signature=f09c3bc48973f959fb3cf2aae2019f28022dd07dfe567de5de2b4addf924771b&X-Amz-SignedHeaders=host&response-content-disposition=attachment%3B%20filename%3Dstrings2.exe&response-content-type=application%2Foctet-stream) - included in this article.
