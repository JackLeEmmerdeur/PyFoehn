
import sys
from threading import Event
from src.classes.FanHandler import FanHandler
from src.classes.FanThread import FanThread
from src.lib.helpers import is_sequence, is_integer, parse_sequence_str, is_boolean, get_reformatted_exception
from src.classes.Config import Config
from src.classes.EasyLogger import EasyLogger


class App:
	config = None
	exited_via_ctrl_c = False
	fan = None
	logger = None
	keep_fdhs = None
	stopevent = None
	disablefan = False

	def __init__(self, configfile, loggername):
		self.config = Config(configfile)

		logconsole = self.config.get_value("general", "logconsole")

		self.logger = EasyLogger(
			logconsole if is_boolean(logconsole) else False,
			"/tmp/" + loggername + ".log",
			loggername
		)

		self.keep_fds = [
			self.logger.getfhf().stream.fileno()
		]

		self.stopevent = Event()
		profile = None

		dbg = True

		if self.config is not None:
			profile = self.config.get_profile()
			if "debug" in profile:
				self.dbg = profile["debug"]

		gpio = -1

		if self.config is None or "pwmgpio" not in self.config.get_value("hardware"):
			raise Exception("No PWM-GPIO-Port found in command line or config-file")
		else:
			if is_integer(self.config.get_value("hardware", "pwmgpio")):
				gpio = int(self.config.get_value("hardware", "pwmgpio"))
				if gpio < 2 or gpio > 27:
					gpio = -1

		if gpio == -1:
			raise Exception("PWM-GPIO-Port is invalid")

		disablefan = self.config.get_value("hardware", "disablefan")

		self.disablefan = False if disablefan is None or not is_boolean(disablefan) else disablefan

		if self.disablefan is False:
			self.fan = FanHandler(
				self,
				dbg,
				gpio,
				profile["freq"] if profile is not None else 25
			)
			self.fan.startfan()

		tt = None
		if profile is not None and "temp_thresholds" in profile:
			ptt = profile["temp_thresholds"]
			if is_sequence(ptt) and len(ptt) > 0:
				tt = ptt

		if tt is None:
			tt = parse_sequence_str("[54,59,74,80]")

		iv = Config.get_profile_value(profile, "interval")
		fs = Config.get_profile_value(profile, "fanstartlevel")
		fc = Config.get_profile_value(profile, "fancooldown")
		cs = Config.get_profile_value(profile, "constant_speed")
		vs = Config.get_profile_value(profile, "variable_speeds")

		self.thread = FanThread(
			self,
			dbg,
			self.stopevent,
			self.fan,
			iv if iv is not None else 5,
			tt,
			fs if fs is not None else 1,
			fc if fc is not None else 10,
			cs if cs is not None else 100,
			vs if vs is not None else None
		)

	def exitapp(self):
		self.dbgwrite("Exiting app")
		if self.fan is not None:
			self.fan.destroy()
		sys.exit(0)

	def dbgwrite(self, msg):
		if self.dbg is True:
			self.logger.info(msg)

	def run(self):
		try:
			self.thread.run()
		except KeyboardInterrupt as e:
			print("KeyboardInterrupt")
			self.exitapp()
		except Exception as e:
			print("1")
			get_reformatted_exception("", e)
			self.exitapp()
		finally:
			print("2")
			if self.exited_via_ctrl_c is True:
				self.exitapp()


