from threading import Thread
from time import time
from threading import Event
from src.classes.FanConfig import FanConfig
from src.classes.FanHandler import FanHandler
from src.lib.funcs import get_soctemp, runs_on_pi
from src.lib.helpers import is_sequence, string_is_empty, is_integer, get_reformatted_exception
from sys import exit


class FanThread(Thread):
	fan = None

	fanconfig = None
	""":type: FanConfig"""

	stopevent = None
	""":type: Event"""

	stopevent_signaled = True
	""":type: boolean"""

	pi = None

	fan_last_dutycycle = -1
	fan_started = False
	fan_started_cooldown = False
	fan_cooldown_intervals_ticked = None
	fan_cooldown_time_started = None

	def __init__(
		self,
		fanconfig,
		stopevent
	):
		Thread.__init__(self)
		self.fanconfig = fanconfig
		self.stopevent = stopevent
		self.pi = runs_on_pi()

		vfs = self.fanconfig.variable_speeds
		has_vfs = is_sequence(vfs) and len(vfs) > 0

		if has_vfs is True:
			if len(vfs) != len(vfs):
				raise Exception("The number of variable-fan-speeds do not match temperature-thresholds")

	def dbgwrite(self, msg, *args, **kwargs):
		self.fanconfig.dbgwrite(msg, *args, **kwargs)

	def setfandutycycle(self, cycle):
		if self.fan is not None:
			if self.fan_last_dutycycle != cycle:
				self.dbgwrite("Set dutycycle {}".format(cycle))
				self.fan.setdutycycle(cycle)
				self.fan_last_dutycycle = cycle

	def destroy_fan(self):
		if self.fan is not None:
			self.fan.destroy()

	def run(self):

		if self.fan is None and self.fanconfig.disablefan is False:
			self.fan = FanHandler(self.fanconfig)
			self.fan.startfan()

		constant_fan_speed = self.fanconfig.config.get_profile_value_int(None, "constant_speed")
		variable_fan_speeds = self.fanconfig.config.get_profile_value("variable_speeds")
		has_constantspeed = is_integer(constant_fan_speed)
		has_variablespeeds = False

		if has_constantspeed is False:
			# Not using constant-fan-cycle,
			# so check for variable-fan-speeds
			if variable_fan_speeds is not None:
				# using variable-fan-speeds. jay.
				has_variablespeeds = True

		try:
			while not self.stopevent.wait(self.fanconfig.interval):
				# Stop-Signal was not send yet, e.g. via CTRL-C
				soctemp = get_soctemp(self.fanconfig.logger, self.pi)

				self.dbgwrite("Current Socket temperature={}".format(soctemp))

				if soctemp < self.fanconfig.temp_thresholds[0]:
					# Temperature fell below the first
					# temperature-control-point, which
					# probably means that the socket
					# doesn't need cooling so stop the fan
					self.dbgwrite("Temperature below cool")
					if self.fan_started is True:
						self.setfandutycycle(0)
						self.fan_started = False

				elif self.fan_started is True:
					# Fan is already running

					if self.fan_started_cooldown is False and \
							soctemp < self.fanconfig.temp_thresholds[self.fanconfig.fanstartlevel]:
						# We're not in the cooldown phase (CP),
						# but socket temperature has normalized,
						# so start CP

						self.fan_started_cooldown = True
						self.dbgwrite("Back at Defcon 0")

						if self.fanconfig.fan_cooldown_interval is not None:
							# CP will use interval-mode
							self.fan_cooldown_intervals_ticked = 0
						else:
							# CP will use time-period-mode
							self.fan_cooldown_time_started = time()

					if self.fan_started_cooldown is True:
						# CP was started so check its stop-condition

						if self.fanconfig.fan_cooldown_interval is not None:
							# ---------- CP-Interval-Mode

							self.dbgwrite("Current interval-cooldown-ticker={}".format(self.fan_cooldown_intervals_ticked))

							# Check stop-condition:
							# Ticks of check-interval reached max interval config-value
							if self.fan_cooldown_intervals_ticked == self.fanconfig.fan_cooldown_interval:
								# The interval-cooldown-ticker is zero...

								if soctemp < self.fanconfig.temp_thresholds[self.fanconfig.fanstartlevel]:
									# Stop fan because current temperature is
									# below the fan-startlevel-temperature again

									self.setfandutycycle(0)
									self.fan_started = False
									self.fan_started_cooldown = False

								# Reset CP-cooldown-ticker. So either
								# the fan was stopped above or it runs for
								# another CP-cooldown-ticker round
								self.fan_cooldown_intervals_ticked = 0
							else:
								# Advance the CP-interval
								self.fan_cooldown_intervals_ticked += 1
						else:
							# ---------- CP-Cooldown-Mode is used

							current_time = time()
							seconds_passed = int(current_time - self.fan_cooldown_time_started)
							self.dbgwrite("Current timer-cooldown seconds passed={}".format(seconds_passed))

							if seconds_passed >= self.fanconfig.fan_cooldown_time:
								# Fan-cooldown-time has elapsed

								if soctemp < self.fanconfig.temp_thresholds[self.fanconfig.fanstartlevel]:
									# Stop fan because current temperature is
									# below the fan-startlevel-temperature again
									self.setfandutycycle(0)
									self.fan_started = False
									self.fan_started_cooldown = False

								# Reset cooldown-timer. So either the fan
								# was stopped above or it runs for another
								# cooldown-timer-round
								self.fan_cooldown_time_started = current_time
				else:
					# Fan isn't running so determine if the
					# socket temperature reached one of the
					# temperature-control-points
					for index, temp in enumerate(self.fanconfig.temp_thresholds):
						if soctemp >= temp:
							if index >= self.fanconfig.fanstartlevel:
								# The fan should be started if the
								# socket-temperature exeeds the
								# temperature-control-point
								self.dbgwrite("Fan start level {} reached({}deg)".format(
									self.fanconfig.fanstartlevel,
									temp
								))
								dtindex = index

								if has_variablespeeds:
									# Set the speed to the corresponding
									# variable-fan-speed of the current
									# temperature-control-point
									speed = self.fanconfig.variable_speeds[dtindex]
								elif has_constantspeed:
									# Set the fan-speed to constant
									speed = self.fanconfig.constant_speed
								else:
									# Set speed to the corresponding
									# procentual value of the
									# temperature-control-point
									speed = ((dtindex + 1) * 100) / float(len(self.fanconfig.temp_thresholds))

								self.setfandutycycle(speed)
								self.fan_started = True
		except:
			import traceback
			self.dbgwrite(traceback.format_exc())
		finally:
			try:
				# self.thread.stopevent.set()
				self.dbgwrite("Exiting app")
				self.destroy_fan()
				self.fanconfig.logger.close()
			except:
				import traceback
				self.dbgwrite(traceback.format_exc())
				exit(1)
			else:
				exit(0)
