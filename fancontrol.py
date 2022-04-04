#! /usr/bin/python3

# Non-blocking read code from https://repolinux.wordpress.com/2012/10/09/non-blocking-read-from-stdin-in-python/
# Fork from https://github.com/Howchoo/pi-fan-controller
# pi-fan-controller from Howchoo
#
# Modified by Kamencesc
# This script must be run on a screen process:
# $> screen -dmS pi-fan-controller
#
# Then you can enter to the console with:
# $> screen -r pi-fan-controller
#
# There you can interact with the script with commands: start, stop, auto, max=xx, min=xx, sleep=xx
#

"""Check for input every 0.1 seconds. Treat available input
immediately, but the it continues with the control of the fan."""

import sys
import select
import time

import subprocess

# Config from pi-fan-controller

from gpiozero import OutputDevice


ON_THRESHOLD = 65  # (degrees Celsius) Fan kicks on at this temperature.
OFF_THRESHOLD = 55  # (degress Celsius) Fan shuts off at this temperature.
SLEEP_INTERVAL = 5  # (seconds) How often we check the core temperature.
GPIO_PIN = 17  # Which GPIO pin you're using to control the fan.


# New variables

# Mode can be ON, OFF or AUTO
MODE = "AUTO"

# select() should wait for this many seconds for input.
# A smaller number means more cpu usage, but a greater one
# means a more noticeable delay between input becoming
# available and the program starting to work on it.
timeout = 0.1 # seconds
last_work_time = time.time()
read_list = [sys.stdin]

fan = OutputDevice(GPIO_PIN)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def treat_input(linein):
  global last_work_time
  global ON_THRESHOLD
  global OFF_THRESHOLD
  global SLEEP_INTERVAL
  global MODE
  #linein is the string to process
  if type(linein) == str:
    linein = linein.lower()
    linein = linein.rstrip()
    if linein == "on":
      # Force fan to start
      MODE = "ON"
      print(bcolors.WARNING + "Mode set to ON" + bcolors.ENDC)
    elif linein == "off":
      # Force fan to stop
      MODE = "OFF"
      print(bcolors.WARNING + "Mode set to OFF" + bcolors.ENDC)
    elif linein == "auto":
      # Back to auto mode
      MODE = "AUTO"
      print(bcolors.WARNING + "Mode set to AUTO" + bcolors.ENDC)
    elif linein == "temp":
      # Get temperature
      temp = get_temp()
      print(bcolors.WARNING + "Temperature: " + str(temp) + bcolors.ENDC)
    elif "=" in linein:
      # Possible change config on the run
      if "max" in linein:
        # New value for ON_THRESHOLD
        if OFF_THRESHOLD >= ON_THRESHOLD:
          print(bcolors.WARNING + "Value is lower than the off threshold value (" + str(OFF_THRESHOLD)+ ")" + bcolors.ENDC)
        else:
          ON_THRESHOLD = int(linein.split("=")[1].strip())
          print(bcolors.WARNING + "On threshold value changed to " + str(ON_THRESHOLD) + bcolors.ENDC)
    elif "min" in linein:
      # New value for OFF_THRESHOLD
      if OFF_THRESHOLD >= ON_THRESHOLD:
        print(bcolors.WARNING + "Value is more greater than the on threshold value (" + str(OFF_THRESHOLD)+ ")" + bcolors.ENDC)
      else:
        OFF_THRESHOLD = int(linein.split("=")[1].strip())
        print(bcolors.WARNING + "Off threshold value changed to " + str(OFF_THRESHOLD) + bcolors.ENDC)
    elif "sleep" in linein:
      # New value for sleep
      SLEEP_INTERVAL = int(linein.split("=")[1].strip())
      print(bcolors.WARNING + "Sleep interval value changed to " + str(SLEEP_INTERVAL) + bcolors.ENDC)
    elif "help" in linein:
      print("Commands: on (allways on)\n          off (allways off)\n          auto (auto mode, default)")
      print("          max=º (upper threshold, default 65º)\n          min=º (lower threshold, default 55º)")
      print("          sleep=t (time between temperature's check, default 0.1)\n          help (show this text)") 
    else:
      print(bcolors.FAIL + "Unknown command '" + linein + "', type HELP to list commands." + bcolors.ENDC)
  last_work_time = time.time()

def idle_work():
  global last_work_time
  global ON_THRESHOLD
  global OFF_THRESHOLD
  global SLEEP_INTERVAL
  global MODE
  global fan
  now = time.time()
  # Do the main code from pi-fan-controller there
  if now - last_work_time > SLEEP_INTERVAL:
    # Validate the on and off thresholds
    if OFF_THRESHOLD >= ON_THRESHOLD:
      raise RuntimeError('OFF_THRESHOLD must be less than ON_THRESHOLD')
    # fan = OutputDevice(GPIO_PIN)
    temp = get_temp()
    # Start the fan if the temperature has reached the limit and the fan
    # isn't already running.
    # NOTE: `fan.value` returns 1 for "on" and 0 for "off"
    # Do whats MODE says
    if MODE == "AUTO":
      # pi-fan-controller MODE
      if temp > ON_THRESHOLD and not fan.value:
        fan.on()
      # Stop the fan if the fan is running and the temperature has dropped
      # to 10 degrees below the limit.
      elif fan.value and temp < OFF_THRESHOLD:
        fan.off()
    elif MODE == "ON":
      # Allways ON
      if not fan.value:
        fan.on()
    elif MODE == "OFF":
      # Allways OFF
      if fan.value:
        fan.off()
    last_work_time = now

def get_temp():
    """Get the core temperature.
    Run a shell script to get the core temp and parse the output.
    Raises:
        RuntimeError: if response cannot be parsed.
    Returns:
        float: The core temperature in degrees Celsius.
    """
    output = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
    temp_str = output.stdout.decode()
    try:
        return float(temp_str.split('=')[1].split('\'')[0])
    except (IndexError, ValueError):
        raise RuntimeError('Could not parse temperature output.')

def main_loop():
  print("To view this session again type 'screen -r pi-fan-controll'.")
  print("To detach the session an let the script run in the background, press Ctrl+A and then Ctrl+D.")
  print("Ctrl+C will close the script.")
  print("Type 'help' to list commands.")
  while read_list:
    ready = select.select(read_list, [], [], timeout)[0]
    if not ready:
      idle_work()
    else:
      for file in ready:
        line = file.readline()
        if not line: # EOF, remove file from input list
          read_list.remove(file)
        elif line.rstrip(): # optional: skipping empty lines
          treat_input(line)
try:
    main_loop()
except KeyboardInterrupt:
  pass
