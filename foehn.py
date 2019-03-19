from src.classes.App import App
from src.lib.helpers import get_reformatted_exception, file_exists, is_boolean
from daemon import DaemonContext
import signal
import lockfile
from os import getcwd
from os.path import join

appname = "PyFoehn"

cfgfile = join(getcwd(), "config/config.json")

app = App(cfgfile, appname)


def signal_handler(sig, frame):
	print("Program exits")
	global app
	# app.exitapp()
	app.stopevent.set()


if __name__ == "__main__":

	foreground = app.fanconfig.config.get_value_bool(False, "general", "foreground")

	try:
		if foreground is True:
			signal.signal(signal.SIGINT, signal_handler)
			signal.signal(signal.SIGTERM, signal_handler)
			app.run()
		else:
			pidfile = "/tmp/" + appname + ".pid"

			if file_exists(pidfile + ".lock"):
				print("PID-File exists")
				exit(1)

			keep_fds = None
			fdf = app.fanconfig.logger.getfhf()
			if fdf is not None:
				keep_fds = [fdf.stream]

			consoleout = None
			fdc = app.fanconfig.logger.getfhc()
			if fdc is not None:
				consoleout = fdc.stream

			with DaemonContext(
				signal_map={
					signal.SIGTERM: signal_handler,
					signal.SIGINT: signal_handler
				},
				pidfile=lockfile.FileLock(pidfile),
				files_preserve=keep_fds,
				stdout=consoleout
			):
				app.run()
	except Exception as e:
		print(get_reformatted_exception("bla", e))
