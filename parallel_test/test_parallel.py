
import ctypes
import sys, os, time
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) #add directory up one level to search path
#import StimToolLib
lib_dll = ctypes.windll.LoadLibrary('inpoutx64.dll')

#print lib_dll.Out32(0x0378, 30)
#print lib_dll.Inp32(0x0378)
#settings_file = #os.path.join(os.path.dirname(__file__), '..', 'Default.params')
parallel_address = 0xD010 #0x4FF8 #0x0378 #StimToolLib.get_var_from_file(settings_file, 'parallel_port_address')

for i in range(256):
    lib_dll.Out32(parallel_address, i)
    read_val = lib_dll.Inp32(parallel_address)
    if not i == read_val:
        print ('Parallel Port ERROR: Tried to write ' + str(i) + ' read back ' + str(read_val))
        print ('Check that inpout32 is installed  and check that parallel_port_address in Default.params is set properly (should match what you find in device manager).')
        sys.exit()
    time.sleep(0.05)
print ('SUCCESS: looks like the parallel port is working properly.  You may want to test the physical values (voltages) using a meter or BIOPAC.')
print ('You can see what the output from BIOPAC should look like in BIOPAC_parallel_output.png (in this directory)')
#print lib_dll.Out32(parallel_address, 5)#0xE010, 1)#0x3000, 3)
#print lib_dll.Inp32(parallel_address)#0x3000)