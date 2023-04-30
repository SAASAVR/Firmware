# Sensor-Activated Acoustic Signal acquisition, visualization, and recognition (SAAS)
The SAAS system contains three main components (Hardware, firmware, software). This repository focuses on the firmware component.
Within the firmware, there are two sub-systems.
- Arduino sketch (C++)
- Client (Python 3.8.10 on an Ubuntu 16.4 OS)
## Requirements
Ensure that the operating system being used is Ubuntu 16.4. If the lattepanda does not currently has Ubuntu installed please [refer to the OS installation instructions.](https://docs.lattepanda.com/content/1st_edition/os/)
Ensure that python 3.8.10 is installed before running scripts

## WORKING ON THE LATTEPANDA
The Lattepanda is currently running Ubuntu Desktop 16.4. There are multiple ways to interface with it, each with their own advantages and disadvantages.
### 1. Connecting to a monitor via HDMI
This is the easiest way to interface with the SAAS firmware, as it allows for full access to the operating system in a visual manner. 
Some issues may arise using this method however, as there seems to be a problem with graphical elements creating trails when moving around the screen. 
This can overwhelm the user and make the device difficult to configure.
### 2. Connecting to the LattePanda via SSH
This is the preferred method of interfacing with the SAAS firmware. Setting up an SSH server on the Lattepanda will allow any other device on the same network to connect to it via this method if it's IP address is known.

## NETWORK SETUP
### 1. Connect via ethernet
#### - On a separate Ubuntu device (WLSL2 on Windows 10/11 is compatible), ensure ssh_client is installed
## SETUP FOR CONFIGURED DEVICE
- Arduino sketch is found under ~/Capstone/Firmware/Arduino
- Open it using the arduino IDE installed on the system.
- Compile and download to Arduino (if not on port /dev/ttyAM0, try port /dev/ttyAM1)

