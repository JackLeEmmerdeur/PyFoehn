from src.lib.helpers import file_exists, is_string, is_dict
from json import load


class Config:
	config = None

	def __init__(self, file):
		self.config = Config.config_read(file)

	@staticmethod
	def config_get_profile_value(p, key):
		if is_dict(p) and key in p:
			return p[key]
		return None

	def config_get_profile(self):
		general = self.config["general"]
		profile = general["profile"]
		return self.config[profile]

	@staticmethod
	def config_read(file):
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