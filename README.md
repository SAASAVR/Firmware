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
Please note that any method will require a login. The default admin user can be accessed with the password 'admin'.
### 1. Connecting to a monitor via HDMI
This is the easiest way to interface with the SAAS firmware, as it allows for full access to the operating system in a visual manner. 
Some issues may arise using this method however, as there seems to be a problem with graphical elements creating trails when moving around the screen. 
This can make configuration difficult.
#### Steps:
1. Connect the Lattepanda to your network. If using Wifi ensure that any devices being used to host other components are publically visible on the network.
2. 

### 2. Connecting to the LattePanda via SSH
This is the preferred method of interfacing with the SAAS firmware. Setting up an SSH server on the Lattepanda will allow any other device on the same network to connect to it via this method if it's IP address is known.

## NETWORK SETUP
### 1. Connect via ethernet
#### - On a separate Ubuntu system (WLSL2 on Windows 10/11 is compatible. [Refer to installation guide](https://learn.microsoft.com/en-us/windows/wsl/install)), ensure ssh_client is installed
### 2. Ensure the LattePanda is turned on.
### 3. On the separate Ubuntu system, enter the following command: ```ssh -X admin@192.168.1.250```
#### - The ```-X``` allows X forwarding to occur between the connected systems so that GUI applications from the LattePanda can run on the ssh client.
#### - The ```admin@192.168.1.250``` is referring to the user account being logged into, and the ip address of the device. Note that this IP is static for ethernet connections and non-DHCP wireless connections.
### 4. Connect the LattePanda to wifi via SSH
#### - Turn on wi-fi using ```nmcli r wifi on```
#### - Check that your wireless network of choice is visible to the device using ```nmcli d wifi list```
#### - Connect to your network of choice using ```nmcli d wifi connect my_wifi password <password>``` 
#### [Refer to offical guide for more information](https://ubuntu.com/core/docs/networkmanager/configure-wifi-connections)
## SETUP FOR CONFIGURED DEVICE
- Arduino sketch is found at '~/Capstone/Firmware/Arduino'
- Open it using the arduino IDE installed on the system by using ```arduino```
- Compile and download to Arduino (if not on port /dev/ttyAM0, try port /dev/ttyAM1)

