# from distutils.core import setup
# from sys import platform
from setuptools import setup

ir = [
	'RPi.GPIO >= 0.7.0',
	'python-daemon >= 2.2.4'
]

setup(
	name='PyFoehn',
	version='0.0.1',
	description='Raspberry Pi Service for controlling a fan via PWM',
	long_description='Service runs under Raspberry Pi System D via python-daemon library and ' +
	'controls a fan via Pulsewidth-modulation using thresholds.',
	author='Daniel Hilker',
	author_email='jackleemmerdeur@googlemail.com',
	url='https://github.com/JackLeEmmerdeur/PyFoehn',
	install_requires=ir,
	download_url='',
	keywords=['raspberry', 'pi', 'fan', 'pwm', 'service', 'systemd'],
	packages=[
		'classes',
		'lib',
	],
	classifiers=[
		'Development Status :: 0.5.0 - Beta',
		'Environment :: Console',
		'Intended Audience :: System Administrators ',
		'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)'
		'Programming Language :: Python :: 3'
	]
)
