from time import sleep
from src.classes.FanConfig import FanConfig
from src.lib.funcs import runs_on_pi
from src.lib.helpers import is_integer


pi = runs_on_pi()

if pi is True:
	import RPi.GPIO as GPIO


class FanHandler:
	fanconfig = None
	""":type: FanConfig"""

	fanstarted = False
	fan = None
	destroyed = True
	current_dutycycle = None
	runsonpi = None

	def __init__(self, fanconfig):
		self.fanconfig = fanconfig
		self.runsonpi = runs_on_pi()
		self.dbgwrite("Try setup GPIO")
		if self.runsonpi is True:
			freq = self.fanconfig.config.get_profile_value("freq")
			freq = freq if is_integer(freq) else 25
			gpio = self.fanconfig.gpio
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(gpio, GPIO.OUT)
			self.dbgwrite("Fan gpioport set to {}".format(gpio))
			self.fan = GPIO.PWM(gpio, freq)
			self.dbgwrite("Port frequency set to {}".format(freq))
		self.destroyed = False

	def dbgwrite(self, msg, *args, **kwargs):
		self.fanconfig.dbgwrite(msg, *args, **kwargs)

	def startfan(self, default_dutycycle=0):
		if self.runsonpi is True:
			self.fan.start(default_dutycycle)
		sleep(0.5)
		self.dbgwrite("Started PWM with dutycycle {}".format(default_dutycycle))
		self.fanstarted = True

	def setdutycycle(self, dutycycle):
		self.dbgwrite("Changed dutycycle to {}".format(dutycycle))
		if self.runsonpi is True:
			self.fan.ChangeDutyCycle(dutycycle)

	def stopfan(self):
		if self.runsonpi is True:
			self.fan.stop()
		self.fanstarted = False

	def destroy(self):
		if self.runsonpi is True:
			self.dbgwrite("Stopping Fan")
			self.fan.stop()
			self.dbgwrite("GPIO Cleanup")
			GPIO.cleanup()
		self.destroyed = True

