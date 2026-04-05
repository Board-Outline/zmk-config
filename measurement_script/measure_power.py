#pip install ppk2-api

import sys

import time
from ppk2_api.ppk2_api import PPK2_MP as PPK2_API

SAMPLE_RATE = 100000

voltage_min = 3600
voltage_max = 4200
voltage_step = 100

measurement_time_s = 60

delay_after_power_on_s = 60

def main() -> int:
    ppk2s_connected = PPK2_API.list_devices()
    if len(ppk2s_connected) == 0:
        print(f"No connected PPK2's: {ppk2s_connected}")
        return 1
    elif len(ppk2s_connected) == 1:
        ppk2_port = ppk2s_connected[0]
        print(f"Found PPK2 at {ppk2_port}")
    else:
        print(f"Too many connected PPK2's: {ppk2s_connected}")
        return 1
    
    ppk2_test = PPK2_API(ppk2_port, buffer_max_size_seconds=1, buffer_chunk_seconds=0.1, timeout=1, write_timeout=1, exclusive=True)
    ppk2_test.get_modifiers()
    ppk2_test.set_source_voltage(voltage_min)

    ppk2_test.use_source_meter()  # set source meter mode
    ppk2_test.toggle_DUT_power("ON")  # enable DUT power

    print("Pre-start delay")
    time.sleep(delay_after_power_on_s)
    print("Pre-start delay over")

    voltages =[]
    for v in range(voltage_min, voltage_max, voltage_step):
        voltages.append(v)

    if voltage_max not in voltages:
        voltages.append(voltage_max)

    

    measurement_count = measurement_time_s * SAMPLE_RATE
    currents_avr = []

    for v in voltages:
        measurements = []
        ppk2_test.set_source_voltage(v)
        time.sleep(1)
        ppk2_test.start_measuring()
        print(f"Starting measurement at {v}")

        while True:
            read_data = ppk2_test.get_data()
            if read_data != b'':
                samples, raw_digital = ppk2_test.get_samples(read_data)
                measurements.extend(samples)
            time.sleep(0.001)
            if(len(measurements) >= measurement_count):
                break
        
        current_avr = sum(measurements)/len(measurements)
        print(f"Voltage {v} Total Average of {len(measurements)} samples is: {current_avr}uA")
        currents_avr.append(current_avr)
        ppk2_test.stop_measuring()

    print(*currents_avr, sep='\t')
    ppk2_test.toggle_DUT_power("OFF")  # disable DUT power
    ppk2_test.stop_measuring()


    return 0

if __name__ == '__main__':
    sys.exit(main())  
    #sys.exit(test()) 