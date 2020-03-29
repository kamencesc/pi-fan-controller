# This fork is not tested yet, be careful!

# Pi Fan Controller

Raspberry Pi fan controller.

## Description

This repository provides scripts that can be run on the Raspberry Pi that will
monitor the core temperature and start the fan when the temperature reaches
a certain threshold.

To use this code, you'll have to install a fan. The full instructions can be
found on our guide: [Control Your Raspberry Pi Fan (and Temperature) with Python](https://howchoo.com/g/ote2mjkzzta/control-raspberry-pi-fan-temperature-python).

## Terminal commands

This scripts runs on a screen session (so, you need to install screen "sudo apt install screen"), this creates a sesion called "pi-fa-controller".

To enter you need to use this to _redeem_ the session:

```screen -r pi-fan-controller```

And to _detach_ the session only press ctrl+a ctrol+d

The commands availabe are:

- _auto_: It change to standard mode.
- _on_: Allways on
- _off_: Allways off (no fan)
- _min=value_: Change the value for the OFF_THRESHOLD
- _max=value_: Change the value for the ON_THRESHOLD
- _sleep=value_: Change sleep value, interval between temperature reading

Note that the values only change for the active session, when you restart your PI all the configs back to the default values of the script.
