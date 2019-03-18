from src.classes.App import App
from src.lib.helpers import get_reformatted_exception, file_exists, is_boolean
from daemon import DaemonContext
import signal
import lockfile

appname = "PyFoehn"

app = App("config/config.json", appname)


def signal_handler(sig, frame):
	print("Program exits")
	global app
	app.exitapp()


if __name__ == "__main__":

	foreground = app.config.get_value("general", "foreground")
	foreground = foreground if is_boolean(foreground) else False

	try:

		if foreground is True:
			signal.signal(signal.SIGINT, signal_handler)
			signal.signal(signal.SIGTERM, signal_handler)
			app.run()
		else:
			pidfile = "/tmp/" + appname + ".pid"

			if file_exists(pidfile):
				print("PID-File exists")
				exit(1)

			with DaemonContext(
				signal_map={
					signal.SIGTERM: signal_handler,
					signal.SIGINT: signal_handler
				},
				pidfile=lockfile.FileLock(pidfile),
				files_preserve=[app.logger.getfhf().stream],
				stdout=app.logger.getfhf().stream
			):
				app.run()
	except Exception as e:
		print(get_reformatted_exception("bla", e))
