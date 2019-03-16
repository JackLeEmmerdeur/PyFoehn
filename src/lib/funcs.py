from platform import machine

import plumbum


def runs_on_pi():
	return machine().find("armv") > -1


def get_soctemp(is_pi=True):

	temp = -1

	if is_pi is True:
		catcmd = plumbum.local["cat"]
		tempval = catcmd.run("/sys/class/thermal/thermal_zone0/temp")

		if tempval[0] == 0:
			temp = round(float(tempval[1]) / 1000, 2)

	else:
		sensors = plumbum.local["sensors"]
		grep = plumbum.local["grep"]
		cut = plumbum.local["cut"]

		tempgetter = sensors | grep["temp2", "-m1"] | cut["-c16-19"]
		tempval = tempgetter.run()

		if tempval[0] == 0:
			temp = float(tempval[1])

	return temp
