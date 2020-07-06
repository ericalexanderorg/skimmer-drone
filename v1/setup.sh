#!/bin/bash

# Check if we've already run apt upgrade
if [ ! -f /src/skimmer-drone/apt-upgraded ]; then
    apt update
    apt upgrade
    mkdir -p /src/skimmer-drone
    touch /src/skimmer-drone/apt-upgraded
    shutdown -r now
else

# Install dependencies through apt
# Ran into issues installing through pip
apt -y install python3-opencv python3-numpy 

# Install pi-rc so we can transmit RF
mkdir -p /src/pi-rc
cd /src/pi-rc
wget https://github.com/bskari/pi-rc/archive/master.zip
unzip master.zip
make
# Copy the files we need to our directory
copy host_files.py /src/skimmer-drone/
copy pi_pcm /src/skimmer-drone/
chmod +x /src/skimmer-drone/pi_pcm

# We also need the following files (expected that they're manually transferred here)
# controller.py
# startup.sh
# parameters.json

# Also need to manually add "/src/skimmer-controller/startup.sh" before "exit 0" in /etc/rc.local



