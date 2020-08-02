# labctl.hw.tdklambda

A basic library for interacting with the ZUP Series of power supplies by
TDK-Lambda.

## Power Supply Configuration

See Chapter 5 of [manual](https://www.emea.lambda.tdk.com/de/KB/ZUP-User-Manual.pdf).

You will want to:

1. Setup an address on the power supply. `01` should be fine.
2. Select RS232
3. Select baud rate (`9600` is probably okay)
4. Select remote by pushing REM button (LED should be **on**).
5. Connect the cable from IN on the power supply to the computer.

If you run `sudo dmesg` on the computer, you should see something like:

```
[ 1729.892460] usbcore: registered new interface driver pl2303
[ 1729.902157] usbserial: USB Serial support registered for pl2303
[ 1729.911913] pl2303 1-1.4:1.0: pl2303 converter detected
[ 1729.923912] usb 1-1.4: pl2303 converter now attached to ttyUSB0
```

Note `ttyUSB0`. This means the power supply is available for communication under
`/dev/ttyUSB0`.

### Basic Usage

```python
from labctl.hw.tdklambda import power_supply as tdklambda_power_supply

with tdklambda_power_supply.ZUP("/dev/ttyUSB0", 9600) as power_supply:
    power_supply.set_voltage(6.0)
    power_supply.set_current(1.5)
    power_supply.set_output_on(True)

    print(f"Model: {power_supply.get_model()}")
    print(f"Software Version: {power_supply.get_software_version()}")
    print(f"Set Voltage: {power_supply.get_set_voltage():.3f} V")
    print(f"Actual Voltage: {power_supply.get_actual_voltage():.3f} V")
    print(f"Set Current: {power_supply.get_set_current():.3f} A")
    print(f"Actual Current: {power_supply.get_actual_current():.3f} A")
    print(f"Mode: {power_supply.get_mode()}")
    print(f"Output: {'ON' if power_supply.is_output_on() else 'OFF'}")
```
