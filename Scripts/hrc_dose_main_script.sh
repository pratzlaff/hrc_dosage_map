#! /bin/sh
cd /data/legs/rpete/flight/hrc_dose/Exc

export SKA=/proj/sot/ska
export PYTHONPATH="/data/mta/Script/Python3.8/envs/ska3-shiny/lib/python3.8/site-packages:/data/mta/Script/Python3.8/lib/python3.8/site-packages/"

/data/legs/rpete/flight/hrc_dose/Scripts/hrc_dose_create_run.py 2000 04
