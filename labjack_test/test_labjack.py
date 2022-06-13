from labjack import ljm
import sys, time

# Open first found LabJack
try:
    handle = ljm.openS("ANY", "ANY", "ANY")
except:
    print('not labjack plugged int?')
    sys.exit(0)


def test_wn():
    """
    """
    value = 2.5
    pin_name = 'DAC0'
    # Write to Register pin name
    ljm.eWriteName(handle, pin_name, value)
    # Read the Register pin Name
    print('%s Voltage: %s' % (pin_name, ljm.eReadName(handle, pin_name)))
    time.sleep(0.04) # waite 40 ms
    value = 1
    pin_name = 'DAC0'
    # Write to Register pin name
    ljm.eWriteName(handle, pin_name, value)
    # Read the Register pin Name
    print('%s Voltage: %s' % (pin_name, ljm.eReadName(handle, pin_name)))

def test_shock():
    # Pulse Rise every 2ms, since DIGITMER has a limit duration of 2ms

    for stim in range(20):
        ljm.eWriteName(handle, 'DAC1', 5) # rise up 
        #print('%s Voltage: %s' % ('DAC1', ljm.eReadName(handle, 'DAC1')))
        time.sleep(.002)
        ljm.eWriteName(handle, 'DAC1', 1) # rise down
        #print('%s Voltage: %s' % ('DAC1', ljm.eReadName(handle, 'DAC1')))
        time.sleep(.003)

#print("\neReadName result: ")
#print("    %s = %f" % (name, result))

if __name__ == '__main__':
    ljm.eWriteName(handle, 'DAC1', 0)
    ljm.eWriteName(handle, 'DAC0', 0)
    test_shock()
    #test_wn()