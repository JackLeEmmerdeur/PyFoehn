## PyFoehn

#### Application use case

A 2-pin fan for a Raspberry Pi can be put on the ground and the 5V pin to let it run constantly.

The PyFoehn service allows to use PWM with a [2-pin fan](https://www.amazon.com/-/de/dp/B07RZF5W75) instead of a [4-pin smart fan](https://www.amazon.com/dp/B07DXRNYNX).

The service needs a small circut containing a resistor, transistor and a capacitator which fit on a 1x2cm breadboard.

I may upload the layout for the circuit when someone opens an respective issue, though...

...all in all this solution is outdated and I'd advise to just invest a few bucks more and buy a 4-pin fan and use [smaRSt-fan](https://medium.com/@olilay/how-to-keep-your-raspberry-pi-cool-and-quiet-with-a-smart-fan-ecd15f4dbf7b) / (github: [link](https://github.com/OliLay/smaRSt-fan)) without needing any extra breadboard or pcb circuit. 


## Installation

#### Copy the script folder to the Raspberry
In my case it was a retropie-system, so I copied the  
foehn.py-file, the config-folder and the src-folder  
via SFTP to the folder "/home/pi/RetroPie/retropiemenu/PyFoehn"

#### How to install the service
Adjust the file pyfoehn.service to your needs
* "WorkingDirectory" needs to be the path to the where you copied the script and additional folders
* Modify the "WantedBy" according to your needs  
e.g. if you only want to start the service in a graphical login use "graphical.target"
* Otherwise have fun with the [docs](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

Modify the config.json in the config-folder:
* Set general->foreground to false
* Set general->logconsole to false
* Set general->logfile to false  
This will ensure that /tmp/PyFoehn.log won't grow indefinitely, because it is only meant for debugging the service

Install the service-file:  
* Copy pyfoehn.service to /etc/systemd/system
* cd /etc/systemd/system
* sudo systemctl enable pyfoehn.service
* If the service won't start consult the file /var/log/daemon.log

The service will be started on every boot.

If you want to stop it execute "sudo systemctl stop pyfoehn.service"