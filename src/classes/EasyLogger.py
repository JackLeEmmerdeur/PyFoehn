import logging
from sys import stdout


class EasyLogger:
	_fhf = None
	_fhc = None
	_logger = None

	def __init__(self, use_console_too, file, name):
		self._logger = logging.getLogger(name)
		self._logger.setLevel(logging.DEBUG)
		self._logger.propagate = False

		if file is not None:
			self._fhf = logging.FileHandler(file, "w")
			self._fhf.setLevel(logging.DEBUG)
			self._logger.addHandler(self._fhf)

		if use_console_too is True:
			self._fhc = logging.StreamHandler(stdout)
			self._fhc.setLevel(logging.DEBUG)
			self._logger.addHandler(self._fhc)

	def close(self):
		handlers = self._logger.handlers[:]
		for handler in handlers:
			handler.close()

	def getfhf(self):
		return self._fhf

	def getfhc(self):
		return self._fhc

	def info(self, msg, *args, **kwargs):
		self._logger.info(msg, *args, **kwargs)

	def warning(self, msg, *args, **kwargs):
		self._logger.warning(msg, *args, **kwargs)

	def error(self, msg, *args, **kwargs):
		self._logger.error(msg, *args, **kwargs)
