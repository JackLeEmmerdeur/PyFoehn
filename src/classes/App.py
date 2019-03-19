from threading import Event
from src.classes.FanThread import FanThread
from src.lib.helpers import get_reformatted_exception
from src.classes.FanConfig import FanConfig


class App:
	stopevent = None
	fanconfig = None

	def __init__(self, configfile, appname):

		self.fanconfig = FanConfig(configfile, appname)
		self.stopevent = Event()

		self.thread = FanThread(
			self.fanconfig,
			self.stopevent
		)

	def dbgwrite(self, msg):
		self.fanconfig.dbgwrite(msg)

	def run(self):
		try:
			self.thread.run()
		except KeyboardInterrupt as e:
			self.stopevent.set()
		except Exception as e:
			get_reformatted_exception("", e)
			self.stopevent.set()
		finally:
			pass


