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