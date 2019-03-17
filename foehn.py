from src.classes.App import App
from daemonize import Daemonize
import signal
from src.lib.helpers import is_boolean, get_reformatted_exception

appname = "PyFoehn"

app = App("config/config.json", appname)


def signal_handler(sig, frame):
	print("You pressed Ctrl+C!'")
	global app
	app.exitapp()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":

	foreground = app.config.get_value("general", "foreground")

	try:
		daemon = Daemonize(
			app=appname,
			foreground=foreground if is_boolean(foreground) else False,
			logger=app.logger, pid="/tmp/" + appname + ".pid", action=lambda: app.run()
		)
		daemon.start()
	except Exception as e:
		print(get_reformatted_exception("bla", e))
