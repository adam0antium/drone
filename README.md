# drone

##Purpose
This project looks at measuring signal data for mobile broadband network connections at low altitudes, to investigate the possibility of using these networks as communication media for remote drones.   

##Hardware
 - Raspberry Pi B+ with Raspbian OS
 - Netgear 785S mobile broadband wifi modem
 - MPL3115A2 altitude/pressure sensor
 - Turnigy SK450 quadcopter
 
 ##Software
 - Mainly python scripting with some embedded shell commands, to pull signal data from the wifi modem web interface, test the upload and download speeds and latency, and get the altitude from an MPL3115A2 sensor via I2C. 
 - The main code is in [signalLogger.py](https://github.com/adam0antium/drone/blob/master/signalLogger.py)**
