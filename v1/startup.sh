#!/bin/bash
cd /src/skimmer-controller
./pi_pcm -v &
python ./host_files.py &
python ./controller.py &