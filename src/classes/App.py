import sys
from threading import Event
from src.classes.FanThread import FanThread
from src.lib.helpers import get_reformatted_exception
from src.classes.FanConfig import FanConfig


class App:
	stopevent = None
	fanconfig = None
	keep_fdhs = None

	def __init__(self, configfile, appname):

		self.fanconfig = FanConfig(configfile, appname)
		self.stopevent = Event()

		self.keep_fds = [
			self.fanconfig.logger.getfhf().stream.fileno()
		]

		self.thread = FanThread(
			self.fanconfig,
			self.keep_fds,
			self.stopevent
		)

	def exitapp(self):
		self.dbgwrite("Exiting app")
		self.thread.destroy_fan()
		self.logger.close()
		sys.exit(0)

	def dbgwrite(self, msg):
		self.fanconfig.dbgwrite(msg)

	def run(self):
		try:
			self.thread.run()
		except KeyboardInterrupt as e:
			self.exitapp()
		except Exception as e:
			get_reformatted_exception("", e)
			self.exitapp()
		finally:
			pass


