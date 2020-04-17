from platform import machine
import subprocess


def runs_on_pi():
	test = machine()
	return test.find("armv") > -1 or test.find("aarch") > -1


def get_soctemp(logger, is_pi=True):
	if is_pi is True:
		p = subprocess.Popen(
			["cat", "/sys/class/thermal/thermal_zone0/temp"],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE
		)
		output, err = p.communicate()
		if p.returncode == 0:
			return round(float(output) / 1000, 2)
		else:
			raise Exception(err)
	else:
		from codecs import decode
		p1 = subprocess.Popen(["sensors"], stdout=subprocess.PIPE)
		p2 = subprocess.Popen(["grep", "temp2", "-m1"], stdin=p1.stdout, stdout=subprocess.PIPE)
		p1.stdout.close()
		p3 = subprocess.Popen(["cut", "-c16-19"], stdin=p2.stdout, stdout=subprocess.PIPE)
		p2.stdout.close()
		test = decode(p3.communicate()[0])
		logger.info(test)
		return float(test)
