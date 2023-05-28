# Sensor-Activated Acoustic Signal acquisition, visualization, and recognition (SAAS)
The SAAS system contains three main components (Hardware, firmware, software). This document=focuses on the firmware component.
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
1. Connect the Lattepanda to a monitor via the HDMI port on the board.
2. Start the device. A login screen should appear.
   - Log in to the admin account using password ```admin```
4. Connect the Lattepanda to your network. If using Wifi ensure that any devices being used to host other components are publically visible on the network.
5. Open a terminal and navigate to ```cd ~/Capstone/Firmware/Server```
6. Do all your funky dunky stuff 

### 2. Connecting to the LattePanda via SSH
This is the preferred method of interfacing with the SAAS firmware. Setting up an SSH server on the Lattepanda will allow any other device on the same network to connect to it via this method if it's IP address is known. 
1. Connect via ethernet
   - On a separate Ubuntu system (WLSL2 on Windows 10/11 is compatible. [Refer to installation guide](https://learn.microsoft.com/en-us/windows/wsl/install)), ensure ssh_client is installed
2. Ensure the LattePanda is turned on.
3. On the separate Ubuntu system, enter the following command: ```ssh -X admin@192.168.1.250```
   - The ```-X``` allows X forwarding to occur between the connected systems so that GUI applications from the LattePanda can run on the ssh client.
   - The ```admin@192.168.1.250``` is referring to the user account being logged into, and the ip address of the device. Note that this IP is static for ethernet connections and non-DHCP wireless connections.
#### Steps from this point on are not required and are only necessary if planning on testing device using wifi.
4. Connect the LattePanda to wifi via SSH
   - Turn on wi-fi using ```nmcli r wifi on```
   - Check that your wireless network of choice is visible to the device using ```nmcli d wifi list```
   - Connect to your network of choice using ```sudo nmcli d wifi connect my_wifi password <password>``` 
#### [Refer to offical guide for more information](https://ubuntu.com/core/docs/networkmanager/configure-wifi-connections)
5. Find IP address of device on wifi network
   - Use the ```ifconfig``` command to find the ip address of the device on the network using the wlan0 interface. It will be listed as "inet addr".
7. Sign out of device using ```exit``` and disconnect ethernet cable from device 
8. Repeat command on step 3 with new ip address
## RUNNING SYSTEM
### Before running the system, please ensure that the MAX9814 microphone is properly connected the the Arduino pins of the Lattepanda.
- A pin diagram with instructions is [shown below](#connecting-to-hardware)
- NOTE: The other scripts (Machine learning, socket server, web-application) *MUST* be running first
1. Navigate to the Client directory ```cd ~/Capstone/Firmware/Client```
2. In line 235 of app.py, change the IP address in the ```SOCKETIO.connect()``` method to the IP address of your socket server.
   ![Lattepanda_ipAddress](https://github.com/SAASAVR/Firmware/assets/59613613/91b6d942-980f-4653-b9fe-739626d35daa)
4. Run the script with ```python app.py```
   - If an error is returned, make sure the socket server is running and it's host machine's IP address is being connected to (Refer to step 2)
## EDITING AND RE-COMPILING ARDUINO SCRIPT
- Arduino sketch is found at '~/Capstone/Firmware/Arduino'
- Open it using the arduino IDE installed on the system by using ```arduino```
- Ensure that the IDE is set to compile for an Arduino Leonardo
- Compile and download to Arduino (if not on port /dev/ttyAM0, try port /dev/ttyAM1)

## CONNECTING TO HARDWARE
- The following image is a pin diagram of the Lattepanda.
- The GND and Vdd pins of the MX9814 microphone should go to GND and 5V pins on the Lattepanda, respectively.
   - The Gain pin on the microphone should also be connected to one of the 5V pins on the Lattepanda.
- The Out pin of the MX9814 microphone should be connected to the **positive** end of a 100µF capacitor.
   - The **negative** end of the same resistor should be connected to pin 16 (A0) on the Lattepanda.
![](https://i.imgur.com/QCrLM6d.png)

