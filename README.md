# drone

##Purpose
This project looks at measuring signal data for mobile broadband network connections at low altitudes, to investigate the possibility of using these networks as communication media for remote drones.   

##Hardware
###Equipment
 - Raspberry Pi B+ with Raspbian OS
 - Netgear 785S mobile broadband wifi modem
 - Turnigy quadcopter
 - usb GPS

###Power Supply Issues
- The RPi was originally getting supplied from the 5V IO pins on the KK2.0 flight controller, but this turned out to be causing problems, possibly due to the inaccurate voltage actually present (6 or so Volts actual, not within Pi specs), or alternatively the current supplied was insufficient. The modem was continually dropping out. The RPi eventually had to be powered from a switching bec running off the LiPo (5.1 V actual) which solved the problem. 
 
##Software
 - Mainly python scripting at this stage to pull signal data from the wifi modem web interface, to operate the usb GPS, and to pull speed data from the python speedtest-cli module. 
 - The main code is in **signalLogger.py**
 - **ping2** and **speedtest_cli2** are slightly altered versions of packages from other authors
