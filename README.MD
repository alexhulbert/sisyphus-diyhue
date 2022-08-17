Steps to make this work:
 1. Add your ssh pubkey to /root/.ssh/authorized_keys in the sd card plugged into the sisyphus
 2. ssh into the sisyphus
 3. edit /etc/apt/sources.list to use legacy.raspbian.org instead of the deprecated mirror
 4. run the following commands as root:
```
rw
rwhome
apt update
apt install python-flask
```
 5. go to settings -> advanced -> advanced lighting in the sisyphus web interface and upload hue.py
 6. add `<sisyphus ip>:8801`, `<sisyphus ip>:8802`, and `<sisyphus ip>:8803` to diyhue
 7. restart the diyhue systemd service
