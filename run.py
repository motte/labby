from tdklambda import TDKLambdaPSU

with TDKLambdaPSU("/dev/ttyUSB0", 9600) as psu:
    psu.set_voltage(0.0)
    psu.set_current(0.0)
    print(f"Model: {psu.get_model()}")
    print(f"Software Version: {psu.get_software_version()}")
    print(f"Set Voltage: {psu.get_set_voltage():.3f} V")
    print(f"Actual Voltage: {psu.get_actual_voltage():.3f} V")
    print(f"Set Current: {psu.get_set_current():.3f} A")
    print(f"Actual Current: {psu.get_actual_current():.3f} A")
    print(f"Output: {'ON' if psu.is_output_on() else 'OFF'}")
    psu.close()
