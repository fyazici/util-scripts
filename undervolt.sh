#!/bin/bash

echo "settings before: "
cd /home/fatih/dev/src/undervolt
python3 undervolt.py --read
echo "undervolting core and cache to -120mV..."
python3 undervolt.py --core -120 --cache -120
echo "settings after:"
python3 undervolt.py --read
