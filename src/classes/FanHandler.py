from time import sleep

from src.lib.funcs import runs_on_pi

pi = runs_on_pi()

if pi is True:
	import RPi.GPIO as GPIO


class FanHandler:
	fanstarted = False
	fan = None
	destroyed = True
	dbg = False
	gpioport = None
	current_dutycycle = None
	runsonpi = None

	def __init__(self, dbg, gpioport, freq):
		self.runsonpi = runs_on_pi()
		self.gpioport = gpioport
		self.dbg = dbg
		self.dbgwrite("Try setup GPIO")
		if self.runsonpi is True:
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(gpioport, GPIO.OUT)
			self.dbgwrite("Fan gpioport set to {}".format(gpioport))
			self.fan = GPIO.PWM(gpioport, freq)
		self.dbgwrite("Port frequency set to {}".format(freq))
		self.destroyed = False

	def dbgwrite(self, msg):
		if self.dbg is True:
			print(msg)

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

