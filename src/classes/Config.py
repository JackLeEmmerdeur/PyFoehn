from src.lib.helpers import file_exists, is_string, get_dict_keychain, is_boolean, is_integer, string_is_empty
from json import load


class Config:
	_config = None
	_profile = None

	def __init__(self, file):
		self._config = Config.read(file)

	@staticmethod
	def _get_value_string(default_string, use_default_if_empty, strval):
		if strval is None:
			return default_string
		elif not is_string(strval):
			return default_string
		elif string_is_empty(strval):
			return default_string if use_default_if_empty else strval
		else:
			return strval

	def get_profile_value(self, *keychain):
		if self._profile is not None:
			return get_dict_keychain(self._profile, *keychain)
		return None

	def get_profile_value_int(self, default_int, *keychain):
		if self._profile is not None:
			i = get_dict_keychain(self._profile, *keychain)
			return i if is_integer(i) else default_int
		return None

	def get_profile_value_bool(self, default_bool, *keychain):
		if self._profile is not None:
			b = get_dict_keychain(self._profile, *keychain)
			return b if is_boolean(b) else default_bool
		return None

	def get_profile_value_string(self, default_string, use_default_if_empty, *keychain):
		if self._profile is not None:
			s = get_dict_keychain(self._profile, *keychain)
			return Config._get_value_string(default_string, use_default_if_empty, s)
		return None

	def get_value(self, *keychain):
		return get_dict_keychain(self._config, *keychain)

	def get_value_bool(self, default_bool, *keychain):
		v = self.get_value(*keychain)
		return v if is_boolean(v) else default_bool

	def get_value_int(self, default_int, *keychain):
		v = self.get_value(*keychain)
		return v if is_integer(v) else default_int

	def get_value_string(self, default_string, use_default_if_empty, *keychain):
		v = self.get_value(*keychain)
		return Config._get_value_string(default_string, use_default_if_empty, v)

	def select_profile(self):
		if "general" in self._config:
			general = self._config["general"]
			if "profile" in general:
				profile = general["profile"]
				if profile in self._config:
					self._profile = self._config[profile]
					return self._profile
		return None

	@staticmethod
	def read(file):
		d = None
		e1 = "Config has to contain key '{}'"
		e2 = "Key '{}' has to contain key '{}'"

		mandatories = ["general", "hardware"]

		if is_string(file) and file_exists(file):
			with open(file, "r") as f:
				d = load(f)
				for mandatory in mandatories:
					if mandatory not in d:
						raise Exception(e1.format(mandatory))

				general = d["general"]
				hardware = d["hardware"]

				if "pwmgpio" not in hardware:
					raise Exception(e2.format("hardware", "pwmgpio"))

				if "profile" not in general:
					raise Exception(e2.format("general", "profile"))

				profile = general["profile"]
				if profile not in d:
					raise Exception("Profile '{}' not found".format(profile))

				sprofile = d[profile]

				if "freq" not in sprofile:
					raise Exception(e2.format(profile, "freq"))
		return d
