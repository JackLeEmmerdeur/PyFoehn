from platform import machine
import subprocess


def runs_on_pi():
	return machine().find("armv") > -1


def get_soctemp(is_pi=True):
	if is_pi is True:
		p1 = subprocess.call(["cat", "/sys/class/thermal/thermal_zone0/temp"])

		# if tempval[0] == 0:
		# 	temp = round(float(tempval[1]) / 1000, 2)
		return 0
	else:
		from codecs import decode
		p1 = subprocess.Popen(["sensors"], stdout=subprocess.PIPE)
		p2 = subprocess.Popen(["grep", "temp2", "-m1"], stdin=p1.stdout, stdout=subprocess.PIPE)
		p1.stdout.close()
		p3 = subprocess.Popen(["cut", "-c16-19"], stdin=p2.stdout, stdout=subprocess.PIPE)
		p2.stdout.close()
		return float(decode(p3.communicate()[0]))
