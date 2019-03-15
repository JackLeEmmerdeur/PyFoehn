import signal
import sys
from json import load
from threading import Event

import click

from FanHandler import FanHandler
from FanThread import FanThread
from helpers import file_exists, is_string, is_sequence, is_dict, is_integer

exited_via_ctrl_c = False

globalfan = None


def config_get_profile_value(p, key):
	if is_dict(p) and key in p:
		return p[key]
	return None


def config_get_profile(d):
	general = d["general"]
	profile = general["profile"]
	return d[profile]


def config_read(fn):
	d = None
	e1 = "Config has to contain key '{}'"
	e2 = "Key '{}' has to contain key '{}'"

	mandatories = ["general", "hardware"]

	if is_string(fn) and file_exists(fn):
		with open(fn, "r") as f:
			d = load(f)
			for mandatory in mandatories:
				if mandatory not in d:
					raise Exception(e1.format(mandatory))

			general = d["general"]
			hardware = d["hardware"]

			if "pwmgpio" not in hardware:
				raise Exception(e2.format("hardware", "pwmgpio"))

			if "profile" not in general:
				raise Exception(e2.format("general", "profile"))

			profile = general["profile"]
			if profile not in d:
				raise Exception("Profile '{}' not found".format(profile))

			sprofile = d[profile]

			if "freq" not in sprofile:
				raise Exception(e2.format(profile, "freq"))
	return d


def exitapp(fan=None):
	print("Exiting app")
	if fan is not None:
		fan.destroy()
	sys.exit(0)


def signal_handler(sig, frame):
	print("You pressed Ctrl+C!'")
	exitapp(globalfan)


signal.signal(signal.SIGINT, signal_handler)


@click.command()
@click.option(
	"--temp_tresholds", type=click.STRING, default="[54,59,74,80]", required=False,
	help=
	"Variable length list of temperature thresholds. Use e.g. [50,60,70,80] "
	"for spinning at 0% speed from 0-50deg, 33% from 50-60deg, 66% from "
	"60-70deg and 100% from 70-80deg. Without static_speed the fan will "
	"spread at relative procentage.")
@click.option(
	"--interval", type=click.IntRange(2, 20), default=5, required=False,
	help="Measure interval (default 5 secs)")
@click.option(
	"--freq", type=click.IntRange(2, 300), default=25, required=False,
	help="PWM Frequency (default 25)")
@click.option(
	"--pwmgpio", type=click.IntRange(-1, 27), required=False, default=-1,
	help="PWM-Output GPIO-Port (default 25)")
@click.option(
	"--constant_speed", type=click.IntRange(0, 100), default=None, required=False,
	help=
	"Sets the fans dutycycle to a static percentage on every range from the "
	"above temp_threshold list.")
@click.option(
	"--variable_speeds", type=click.STRING, default=None, required=False,
	help=
	"Sets individual fan speeds for every temp_threshold passed. "
	"Has to correspond with the temp_thresholds-argument, "
	"e.g. temp_thresholds='[45,55,70,80] and variable_speeds='[20,30,50,90]' "
	"means spin at 0% speed at 0-45deg, 20% at 45-55deg, 30% at 55-70, "
	"50% at 70-80deg and 90% when over 80deg the")
@click.option(
	"--fanstartlevel", type=click.INT, default=1, required=False,
	help=
	"The level at which to start the fan. If e.g [45,50,60,70,80] was "
	"passed to temp_thresholds a stoplevel of 2 will indicate that the "
	"fan has to start when 60deg is reached")
@click.option(
	"--fancooldown", type=click.STRING, default="10sek", required=False,
	help=
	"Either a number-string, e.g. '10' which means to cool for another 10 "
	"interval turns after temperature dropping below fanstartlevel or a "
	"time-string, e.g. '10sec' or '10min' means cool for another "
	"10 seconds or 10 minutes"
)
@click.option(
	"--debug", type=click.BOOL, default=False, required=False,
	help="Print debug messages (1 or 0, true or false)")
@click.option(
	"--fan/--nofan", is_flag=True, default=True,
	help="Use the fan (--fan) or don't (--nofan)")
def run(
		temp_tresholds, interval, freq, pwmgpio,
		constant_speed, variable_speeds, fanstartlevel,
		fancooldown, debug, fan
):

	import re
	global globalfan

	stopevent = Event()

	try:
		profile = None
		config = config_read("config.json")
		dbg = debug

		if config is not None:
			profile = config_get_profile(config)
			if "debug" in profile:
				dbg = profile["debug"]

		gpio = -1

		if pwmgpio == -1:
			print(config)
			if config is None or "pwmgpio" not in config["hardware"]:
				raise Exception("No PWM-GPIO-Port found in command line or config-file")
			else:
				if is_integer(config["hardware"]["pwmgpio"]):
					gpio = int(config["hardware"]["pwmgpio"])
					if gpio < 2 or gpio > 27:
						gpio = -1
		else:
			gpio = pwmgpio

		if gpio == -1:
			raise Exception("PWM-GPIO-Port is invalid")

		if fan is True:
			if dbg is True:
				print("Creating Fan")
			globalfan = FanHandler(
				dbg,
				gpio,
				profile["freq"] if profile is not None else freq
			)
			globalfan.startfan()

		tt = None
		if profile is not None and "temp_thresholds" in profile:
			ptt = profile["temp_thresholds"]
			if is_sequence(ptt) and len(ptt) > 0:
				tt = ptt

		if tt is None:
			tt = list(map(lambda x: int(x), re.findall('\d+', temp_tresholds)))

		iv = config_get_profile_value(profile, "interval")
		fs = config_get_profile_value(profile, "fanstartlevel")
		fc = config_get_profile_value(profile, "fancooldown")
		cs = config_get_profile_value(profile, "constant_speed")
		vs = config_get_profile_value(profile, "variable_speeds")

		thread = FanThread(
			dbg,
			stopevent,
			None if fan is False else globalfan,
			iv if iv is not None else interval,
			tt,
			fs if fs is not None else fanstartlevel,
			fc if fc is not None else fancooldown,
			cs if cs is not None else constant_speed,
			vs if vs is not None else variable_speeds
		)

		thread.run()
	except KeyboardInterrupt as e:
		print("KeyboardInterrupt")
		exitapp()
	except Exception as e:
		print(e)
		exitapp(globalfan)
	finally:
		pass
		if exited_via_ctrl_c is True:
			exitapp(globalfan)


if __name__ == "__main__":
	run()
