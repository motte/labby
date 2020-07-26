from serial import Serial

serial = Serial("/dev/ttyUSB0", 9600, xonxoff=True)
serial.write(b":ADR01;")
print(f"Returned: {serial.readline()}")
