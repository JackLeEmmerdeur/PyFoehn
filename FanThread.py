from threading import Thread
from time import time

from funcs import get_soctemp, runs_on_pi
from helpers import is_sequence, string_is_empty


class FanThread(Thread):
	debug = False
	fan = None
	interval = None
	temps = None
	pi = None
	last_dutycycle = -1

	constant_fan_speed = None
	variable_fan_speeds = None

	fan_started = False
	fan_startlevel = None
	fan_started_cooldown = False

	fan_cooldown_interval = None
	fan_cooldown_intervals_ticked = None

	fan_cooldown_time = None
	fan_cooldown_time_started = None

	def __init__(
		self,
		debug, stopevent, fan, interval=10,
			temps=[45, 55, 60, 75],
		fan_startlevel=0,
		fan_cooldown="5",
		constant_fanspeed=None,
		variable_fanspeeds=None
	):
		Thread.__init__(self)
		self.debug = debug
		self.stopevent = stopevent
		self.fan = fan
		self.fan_startlevel = fan_startlevel
		self.interval = interval
		self.temps = temps
		self.pi = runs_on_pi()
		self.constant_fan_speed = constant_fanspeed

		if not is_sequence(temps) or len(temps) == 0:
			raise Exception("Temperature thresholds are screwed")

		has_vf = is_sequence(variable_fanspeeds) and len(variable_fanspeeds) > 0

		if has_vf is True:
			self.variable_fan_speeds = variable_fanspeeds
		else:
			self.variable_fan_speeds = None

		if has_vf is True:
			if len(variable_fanspeeds) != len(temps):
				raise Exception("The number of variable-fan-speeds do not match temperature-thresholds")

		if string_is_empty(fan_cooldown):
			self.fan_cooldown_interval = 5
		else:
			pos_sec = fan_cooldown.find("sec")
			pos_min = fan_cooldown.find("min")
			pos_hrs = fan_cooldown.find("hrs")

			fc = None
			fct = None

			if pos_sec > -1:
				fct = int(fan_cooldown[0:pos_sec])
			elif pos_min > -1:
				fct = int(fan_cooldown[0:pos_min]) * 60
			elif pos_hrs > -1:
				fct = int(fan_cooldown[0:pos_hrs]) * 3600
			else:
				fc = int(fan_cooldown)

			self.fan_cooldown_interval = fc
			self.fan_cooldown_time = fct

	def dbgwrite(self, mess):
		if self.debug is True:
			print(mess)

	def setfandutycycle(self, cycle):
		if self.fan is not None:
			if self.last_dutycycle != cycle:
				self.dbgwrite("Set dutycycle {}".format(cycle))
				self.fan.setdutycycle(cycle)
				self.last_dutycycle = cycle

	def run(self):
		while not self.stopevent.wait(self.interval):
			soctemp = get_soctemp(self.pi)
			has_variablespeeds = False
			has_constantspeed = self.constant_fan_speed is not None

			if has_constantspeed is False:
				vfd = self.variable_fan_speeds
				if vfd is not None:
					has_variablespeeds = True

			self.dbgwrite("Current Socket temperature={}".format(soctemp))

			if soctemp < self.temps[0]:
				# Temperature is below cool so stop fan
				self.dbgwrite("Temperature below cool")
				if self.fan_started is True:
					self.setfandutycycle(0)
					self.fan_started = False

			elif self.fan_started is True:
				# Fan is already running

				if self.fan_started_cooldown is False and soctemp < self.temps[self.fan_startlevel]:
					self.fan_started_cooldown = True
					self.dbgwrite("Back at Defcon 0")
					if self.fan_cooldown_interval is not None:
						self.fan_cooldown_intervals_ticked = 0
					else:
						self.fan_cooldown_time_started = time()

				if self.fan_started_cooldown is True:
					# Back at normal temperature level again

					if self.fan_cooldown_interval is not None:
						# =============================
						# The interval-cooldown is used
						self.dbgwrite("Current interval-cooldown={}".format(self.fan_cooldown_intervals_ticked))
						if self.fan_cooldown_intervals_ticked == self.fan_cooldown_interval:
							# The interval-cooldown-ticker is zero...

							if soctemp < self.temps[self.fan_startlevel]:
								# Stop fan because current temperature is
								# below the fan-startlevel-temperature again
								self.setfandutycycle(0)
								self.fan_started = False
								self.fan_started_cooldown = False

							# Reset interval-cooldown-ticker. So either
							# the fan was stopped above or it runs for
							# another interval-cooldown-ticker round
							self.fan_cooldown_intervals_ticked = 0
						else:
							self.fan_cooldown_intervals_ticked += 1
					else:
						# =============================
						# The timer-cooldown is used
						current_time = time()
						seconds_passed = int(current_time - self.fan_cooldown_time_started)
						self.dbgwrite("Current timer-cooldown seconds passed={}".format(seconds_passed))
						if seconds_passed >= self.fan_cooldown_time:
							# Fan-cooldown-time has elapsed

							if soctemp < self.temps[self.fan_startlevel]:
								# Stop fan because current temperature is
								# below the fan-startlevel-temperature again
								self.setfandutycycle(0)
								self.fan_started = False
								self.fan_started_cooldown = False

							# Reset cooldown-timer. So either
							# the fan was stopped above or it runs for
							# another cooldown-timer-round
							self.fan_cooldown_time_started = current_time
			else:
				# Fan isn't running

				for index, temp in enumerate(self.temps):
					if soctemp >= temp:

						if index >= self.fan_startlevel:
							self.dbgwrite("Fan start level {} reached({}deg)".format(self.fan_startlevel, temp))

							dtindex = index
							if has_variablespeeds:
								speed = self.variable_fan_speeds[dtindex]
							elif has_constantspeed:
								speed = self.constant_fan_speed
							else:
								speed = ((dtindex + 1) * 100) / float(len(self.temps))
							self.setfandutycycle(speed)
							self.fan_started = True
