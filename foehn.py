from src.classes.App import App
from daemonize import Daemonize
import signal

globalapp = None


def signal_handler(sig, frame):
	print("You pressed Ctrl+C!'")
	global globalapp
	globalapp.exitapp()


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":

	global globalapp

	globalapp = App("config/config.json", "/tmp/test.log", __name__)

	pid = "/tmp/test.pid"

	daemon = Daemonize(app="PyFoehn", pid=pid, action=app.run)

	daemon.start()