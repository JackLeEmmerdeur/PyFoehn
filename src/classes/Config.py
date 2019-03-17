from src.lib.helpers import file_exists, is_string, is_dict
from json import load


class Config:
	_config = None

	def __init__(self, file):
		self._config = Config.read(file)

	@staticmethod
	def get_profile_value(p, key):
		if is_dict(p) and key in p:
			return p[key]
		return None

	def get_value(self, *keychain):
		last_item = None
		if self._config:
			for key in keychain:
				if last_item is None:
					if key in self._config:
						last_item = self._config[key]
					else:
						break
				else:
					last_item = last_item[key]
		return last_item

	def get_profile(self):
		general = self._config["general"]
		profile = general["profile"]
		return self._config[profile]

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
