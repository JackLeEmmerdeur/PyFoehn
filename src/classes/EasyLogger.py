import logging


class EasyLogger:
	fh = None

	def __init__(self, file, name):

		self.logger = logging.getLogger(name)
		self.logger.setLevel(logging.DEBUG)
		self.logger.propagate = False

		self.fh = logging.FileHandler(file, "w")

		self.fh.setLevel(logging.DEBUG)

		self.logger.addHandler(self.fh)
