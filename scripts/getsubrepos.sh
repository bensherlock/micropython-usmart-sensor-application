#!/bin/bash

# To git clone into non-empty directory:
# https://stackoverflow.com/a/33695754/209647


# Move out of scripts dir
cd ..

# mainloop
cd main/mainloop
git init .
git remote add origin https://github.com/bensherlock/micropython-usmart-sensor-mainloop.git
git pull origin master
cd ../..

# pybd_expansion
cd main/pybd_expansion
git init .
git remote add origin https://github.com/bensherlock/micropython-pybd-expansion.git
git pull origin master
cd ../..

# sensor_payload
cd main/sensor_payload
git init .
git remote add origin https://github.com/bensherlock/micropython-usmart-sensor-payload.git
git pull origin master
cd ../..

# uac_modem
cd main/uac_modem
git init .
git remote add origin https://github.com/bensherlock/micropython-unm3-pybd.git
git pull origin master
cd ../..
