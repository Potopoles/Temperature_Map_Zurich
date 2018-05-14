#!/usr/bin/env python
# # -*- coding: utf-8 -*-

# imports
import numpy as np
import pandas as pd
from netCDF4 import Dataset
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import time
import TimeSelector as TimeSelector
import pickle


ws_path = '../../../../Dropbox/aWetter/RP_Upload/ws.nc'
out_file = '03_data/00_ws_hourly.pkl'

# LOAD WEATHER STATION DATA
ncf = Dataset(ws_path)

#var_names = list(ncf.variables)[1:]
#print(var_names)
var_names = ['Tout', 'wind', 'p']
var_names = ['Td', 'Tout', 'wind', 'p', 'rain']

TS = TimeSelector.TimeSelector(ncf)
TS.selTime('yolo', reset=True)
#TS.selTime('yolo', year=2018, reset=True)

ws_min = {}
for var_name in var_names:
    print(var_name)
    var,dts = TS.getVar(var_name, 'yolo', structure='minute')
    ws_min[var_name] = var

ws_min = pd.DataFrame(ws_min, dts)
resample_mode = 'H'
ws_hr = ws_min.resample(resample_mode).mean()
ws_hr['rain'] = ws_hr['rain']*6


pickle.dump(ws_hr, open(out_file, 'wb'))
