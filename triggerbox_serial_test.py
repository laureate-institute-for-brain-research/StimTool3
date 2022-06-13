

import serial

import time


port = serial.Serial('COM3')

time.sleep(5)
# Set the port to an initial state
#port.write([0x00])
# Set Bit 0, Pin 2 of the Output(to Amp) connector

port.write([0x00])
time.sleep(0.5)
#port.write([0x02])
#time.sleep(0.5)
#port.write([0x04])
#time.sleep(0.5)
#port.write([0x06])
#time.sleep(0.5)
#port.write([0x05])
#time.sleep(0.5)
# Reset Bit 0, Pin 2 of the Output(to Amp) connector
#port.write([0x00])


#time.sleep(0.5)
# Reset the port to its default state
port.write([0xFF])


# Close the serial port
port.close()




port = serial.Serial('COM3')
port.write([0x02])
time.sleep(0.5)
# Reset the port to its default state
port.write([0xFF])
port.close()
