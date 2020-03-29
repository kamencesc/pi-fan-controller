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
MODE="AUTO"

# select() should wait for this many seconds for input.
# A smaller number means more cpu usage, but a greater one
# means a more noticeable delay between input becoming
# available and the program starting to work on it.
timeout = 0.1 # seconds
last_work_time = time.time()

def treat_input(linein):
  global last_work_time
  global ON_THRESHOLD
  global OFF_THRESHOLD
  global SLEEP_INTERVAL
  global MODE
  #linein is the string to process
  if type(linein) == str:
    linein = linein.lower
	if linein == "start":
		# Force fan to start
		MODE = "ON"
	elif linein == "stop":
		# Force fan to stop
		MODE = "OFF"
	elif linein == "auto":
		# Back to auto mode
		MODE = "AUTO"
	elif "=" in linein:
		# Possible change config on the run
		if "top" in linein:
			# New value for ON_THRESHOLD
			if OFF_THRESHOLD >= ON_THRESHOLD:
				print("Value is lower than the off threshold value (" + str(OFF_THRESHOLD)+ ")")
			else
				ON_THRESHOLD = int(linein.split("=").strip())
		print("On threshold value changed to " + str(ON_THRESHOLD))
		elif "bottom" in linein:
			# New value for OFF_THRESHOLD
			if OFF_THRESHOLD >= ON_THRESHOLD:
				print("Value is more greater than the on threshold value (" + str(OFF_THRESHOLD)+ ")")
			else
				OFF_THRESHOLD = int(linein.split("=").strip())
			print(Off threshold value changed to " + str(OFF_THRESHOLD))
		elif "sleep" in linein:
			# New value for sleep
			SLEEP_INTERVAL = int(linein.split("=").strip())
			print("Sleep interval value changed to " + str(SLEEP_INTERVAL))
  last_work_time = time.time()

def idle_work():
  global last_work_time
  global ON_THRESHOLD
  global OFF_THRESHOLD
  global SLEEP_INTERVAL
  global MODE
  now = time.time()
  # Do the main code from pi-fan-controller there
  if now - last_work_time > SLEEP_INTERVAL:
    # Validate the on and off thresholds
    if OFF_THRESHOLD >= ON_THRESHOLD:
        raise RuntimeError('OFF_THRESHOLD must be less than ON_THRESHOLD')
    fan = OutputDevice(GPIO_PIN)
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
    idle_work()

try:
    main_loop()
except KeyboardInterrupt:
  pass
