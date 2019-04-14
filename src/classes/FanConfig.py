from src.classes.Config import Config
from src.classes.EasyLogger import EasyLogger
from src.lib.helpers import is_boolean, is_integer, is_sequence, parse_sequence_str, string_is_empty


class FanConfig:
	config = None
	logconsole = False
	logger = None
	loggername = None
	dbg = False
	gpio = None
	disablefan = False
	interval = None
	fanstartlevel = None
	temp_thresholds = None
	variable_speeds = None
	constant_speed = None
	fan_cooldown_interval = None
	fan_cooldown_time = None

	def __init__(self, configfile, appname):

		self.config = Config(configfile)

		self.logfile = self.config.get_value_bool(False, "general", "logfile")
		self.logconsole = self.config.get_value_bool(False, "general", "logconsole")
		self.loggername = self.config.get_value_string(appname, True, "general", "loggername")
		self.disablefan = self.config.get_value_bool(False, "hardware", "disablefan")

		gpio = self.config.get_value_int(-1, "hardware", "pwmgpio")
		if gpio != -1:
			if gpio < 2 or gpio > 27:
				gpio = -1

		if gpio == -1 and self.disablefan is False:
			raise Exception("PWM-GPIO-Port is invalid")

		self.gpio = gpio

		self.logger = EasyLogger(
			self.logconsole,
			"/tmp/" + self.loggername + ".log" if self.logfile is True else None,
			self.loggername
		)

		profile = self.config.select_profile()
		if profile is None:
			raise Exception("No profile selected or found")

		temp_thresholds = None
		profile_temp_thresholds = self.config.get_profile_value("temp_thresholds")
		if is_sequence(profile_temp_thresholds) and len(profile_temp_thresholds) > 0:
			temp_thresholds = profile_temp_thresholds

		if temp_thresholds is None:
			self.temp_thresholds = parse_sequence_str("[54,59,74,80]", lambda x: int(x))
		else:
			self.temp_thresholds = temp_thresholds

		self.interval = self.config.get_profile_value_int(5, "interval")

		self.fanstartlevel = self.config.get_profile_value_int(2, "fanstartlevel")

		fcd = self.config.get_profile_value("fancooldown")

		if not string_is_empty(fcd):
			pos_sec = fcd.find("sec")
			pos_min = fcd.find("min")
			pos_hrs = fcd.find("hrs")

			if pos_sec > -1:
				self.fan_cooldown_time = int(fcd[0:pos_sec])
			elif pos_min > -1:
				self.fan_cooldown_time = int(fcd[0:pos_min]) * 60
			elif pos_hrs > -1:
				self.fan_cooldown_time = int(fcd[0:pos_hrs]) * 3600
			else:
				self.fan_cooldown_interval = int(fcd)
		elif is_integer(fcd):
			self.fan_cooldown_interval = fcd
		else:
			self.fan_cooldown_time = 10

		self.constant_speed = self.config.get_profile_value("constant_speed")
		self.variable_speeds = self.config.get_profile_value("variable_speeds")

		dbg = self.config.get_profile_value("debug")
		self.dbg = dbg if is_boolean(dbg) else False

	def dbgwrite(self, msg, *args, **kwargs):
		if self.dbg is True and self.logger is not None:
			self.logger.info(msg, *args, **kwargs)
