# PSU Configuration

See Chapter 5 of [manual](https://www.emea.lambda.tdk.com/de/KB/ZUP-User-Manual.pdf).

You will want to:

1. Setup an address. 01 should be fine.
2. Select RS232
3. Select baud rate (9600 is probably okay)
4. Select remote by pushing REM button (LED should be **on**).
5. Connect the cable from IN on the PSU to the computer.

If you run `sudo dmesg` on the computer, you should see something like:

```
[ 1729.892460] usbcore: registered new interface driver pl2303
[ 1729.902157] usbserial: USB Serial support registered for pl2303
[ 1729.911913] pl2303 1-1.4:1.0: pl2303 converter detected
[ 1729.923912] usb 1-1.4: pl2303 converter now attached to ttyUSB0
```

Note `ttyUSB0`. This means the PSU is available for communication under
`/dev/ttyUSB0`.

## Basic Usage

You can install `picocom` on Linux and use the PSU like this:

```
picocom --baud 9600 --flow x --databits 8 --parity n --stopbits 1 /dev/ttyUSB0
```

Then you can run commands a such (note that anything you type won't be
shown on the output, just the output from the PSU):
```
:ADR01;
:MDL?;
:REV?;
:VOL!;
:VOL?;
```

See Section 5.5 on the manual for the list of commands
