from daemonize import Daemonize
from watchdog.observers import Observer
import logging
from time import time, sleep



pid = "/tmp/test.pid"

def test():
	while True:
		logger.info(str(time()))
		sleep(10)

daemon = Daemonize(app="test", pid=pid, action=test, keep_fds=keep_fds)


def xoxo(signum, frame):
	logger.info(str(signum))
	daemon.exit()

daemon.sigterm = xoxo



daemon.start()


