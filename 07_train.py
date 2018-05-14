#!/usr/bin/env python
# # -*- coding: utf-8 -*-

# imports
import random
import numpy as np
import pandas as pd
#from sklearn.linear_model import Ridge
#from sklearn.linear_model import Lasso
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
#from sklearn.preprocessing import PolynomialFeatures
#from sklearn.pipeline import make_pipeline
from netCDF4 import Dataset
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pickle
import time
#from pysolar.solar import get_altitude

import TimeSelector as TimeSelector
#from functions import hourly_ts_to_diurnal

#varNames = ['T', 'p', 'Td_diff', 'rain', 'wind', 'hour', 'yday']
#varNames = ['T', 'Td_diff', 'hour', 'wind']
varNames = ['T', 'wind', 'hour', 'yday']
orders = [[3], [3], [3], [2,3]]
n_predictors = 5

inp_file = '../03_data/02_spatial_grid.pkl'
out_file = '../03_data/03_trained.pkl'
ws_hrly_file = '../03_data/00_ws_hourly.pkl'
min_nEntries = 25

# LOAD WS DATA
ws = pickle.load(open(ws_hrly_file, 'rb'))

# LOAD SPATIAL DATA
input = pickle.load(open(inp_file, 'rb'))
nx = input['nx']
ny = input['ny']

hashes = input.keys()
hashes = [hash for hash in hashes if (hash != 'nx') and (hash != 'ny')]

good_cells = []
for hash in hashes:
    if input[hash]['nEntries'] > min_nEntries:
        good_cells.append(hash)


out = {}
for hash in good_cells:

    dts = input[hash]['dts']
    dt_str = [datetime.strftime(dt,'%Y-%m-%d %H') for dt in dts]

    vals = {}
    diff_T = input[hash]['diff_T']
    vals['T'] = np.asarray([ws.loc[dstr]['Tout'] for dstr in dt_str])

    if 'p' in varNames:
        vals['p'] = np.asarray([ws.loc[dstr]['p'] for dstr in dt_str])
    if 'Td_diff' in varNames:
        Td = np.asarray([ws.loc[dstr]['Td'] for dstr in dt_str])
        vals['Td_diff'] = vals['T']-Td
    if 'rain' in varNames:
        rain = np.asarray([ws.loc[dstr]['rain'] for dstr in dt_str])
        rain[rain == 0] = 0.00001
        vals['rain'] = np.log(rain)
    if 'wind' in varNames:
        wind = np.asarray([ws.loc[dstr]['wind'] for dstr in dt_str])
        wind[wind == 0] = 0.00001
        vals['wind'] = np.log(wind)
    if 'hour' in varNames:
        vals['hour'] = [dt.hour for dt in dts]
    if 'yday' in varNames:
        vals['yday'] = [dt.timetuple().tm_yday for dt in dts]

    vals = pd.DataFrame(vals, dts)
    n_entries = len(dts)

    #pd.scatter_matrix(vals)
    #plt.show()


    X = np.zeros((n_entries,n_predictors))
    X[:,0] = vals['T']**3
    X[:,1] = vals['wind']**3
    X[:,2] = vals['hour']**3
    X[:,3] = vals['yday']**2
    X[:,4] = vals['yday']**3
    y = diff_T

    use_inds = np.argwhere(~np.isnan(y)).squeeze()
    removed = X.shape[0]
    y = y[use_inds]
    X = X[use_inds,:]
    removed = removed - X.shape[0]
    print('removed ' + str(removed) + ' entries')
    n_entries = len(y)


    regr = LinearRegression()
    regr.fit(X, y)

    out[hash] = {}
    out[hash]['varNames'] = varNames
    out[hash]['orders'] = orders
    out[hash]['coef'] = regr.coef_
    out[hash]['chx0'] = input[hash]['x0']
    out[hash]['chx1'] = input[hash]['x1']
    out[hash]['chy0'] = input[hash]['y0']
    out[hash]['chy1'] = input[hash]['y1']

pickle.dump(out, open(out_file, 'wb'))
