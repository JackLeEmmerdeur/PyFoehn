
import sys
from threading import Event
from src.classes.FanHandler import FanHandler
from src.classes.FanThread import FanThread
from src.lib.helpers import is_sequence, is_integer, parse_sequence_str
from src.classes.Config import Config
from src.classes.EasyLogger import EasyLogger


class App:
	config = None
	exited_via_ctrl_c = False
	globalfan = None
	logger = None
	keep_fdhs = None

	def __init__(self, configfile, loggerfile, loggername):
		self.config = Config(configfile)
		self.logger = EasyLogger(loggerfile, loggername)
		self.keep_fds = [self.logger.fh.stream.fileno()]

	def exitapp(self):
		print("Exiting app")
		if self.globalfan is not None:
			self.globalfan.destroy()
		sys.exit(0)

	def dbgwrite(self, msg):
		if self.dbg is True:
			self.logger.info(msg)

	def run(self):
		stopevent = Event()

		try:
			profile = None
			config = App.config_read("config/config.json")
			dbg = True

			if config is not None:
				profile = App.config_get_profile(config)
				if "debug" in profile:
					dbg = profile["debug"]

			gpio = -1

			if config is None or "pwmgpio" not in config["hardware"]:
				raise Exception("No PWM-GPIO-Port found in command line or config-file")
			else:
				if is_integer(config["hardware"]["pwmgpio"]):
					gpio = int(config["hardware"]["pwmgpio"])
					if gpio < 2 or gpio > 27:
						gpio = -1

			if gpio == -1:
				raise Exception("PWM-GPIO-Port is invalid")

			self.globalfan = FanHandler(
				self,
				dbg,
				gpio,
				profile["freq"] if profile is not None else 25
			)
			self.globalfan.startfan()

			tt = None
			if profile is not None and "temp_thresholds" in profile:
				ptt = profile["temp_thresholds"]
				if is_sequence(ptt) and len(ptt) > 0:
					tt = ptt

			if tt is None:
				tt = parse_sequence_str("[54,59,74,80]")

			iv = Config.config_get_profile_value(profile, "interval")
			fs = Config.config_get_profile_value(profile, "fanstartlevel")
			fc = Config.config_get_profile_value(profile, "fancooldown")
			cs = Config.config_get_profile_value(profile, "constant_speed")
			vs = Config.config_get_profile_value(profile, "variable_speeds")

			thread = FanThread(
				self,
				dbg,
				stopevent,
				self.globalfan,
				iv if iv is not None else 5,
				tt,
				fs if fs is not None else 1,
				fc if fc is not None else 10,
				cs if cs is not None else 100,
				vs if vs is not None else None
			)

			thread.run()
		except KeyboardInterrupt as e:
			print("KeyboardInterrupt")
			self.exitapp()
		except Exception as e:
			print(e)
			self.exitapp()
		finally:
			if self.exited_via_ctrl_c is True:
				self.exitapp()


