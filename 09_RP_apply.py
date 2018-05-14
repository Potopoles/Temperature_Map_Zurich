#!/usr/bin/env python
# # -*- coding: utf-8 -*-

# imports
import numpy as np
from netCDF4 import Dataset
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from matplotlib import cm
from matplotlib.colors import Normalize
import TimeSelector as TimeSelector
import pickle
import time
import os

inp_file = '03_data/03_trained.pkl'
ws_path = '../../../Dropbox/aWetter/RP_Upload/ws.nc'
maps_path = 'maps/lowQuality'
i_save_fig = 1
img_out_path = 'test_images/current_heat_map.png'

now = datetime.now()
now = now - timedelta(hours=1)
sel_dt_str = now.strftime('%Y-%m-%d %H')
sel_dt = datetime.strptime(sel_dt_str, '%Y-%m-%d %H')

# LOAD WS DATA
ncf = Dataset(ws_path)
TS = TimeSelector.TimeSelector(ncf)
TS.selTime('yolo',year=now.year, month=now.month, day=now.day, hour=now.hour, reset=True)
Tout,dts = TS.getVar('Tout', 'yolo', structure='minute')
wind,dts = TS.getVar('wind', 'yolo', structure='minute')
Tout = np.nanmean(Tout)
wind = np.nanmean(wind)

# LOAD SPATIAL DATA
model = pickle.load(open(inp_file, 'rb'))
hashes = list(model)

# FIND SPATIAL EXTENT
minx = np.Inf
maxx = -np.Inf
miny = np.Inf
maxy = -np.Inf
for hash in hashes:
    if model[hash]['chx0'] <= minx:
        minx = model[hash]['chx0']
    if model[hash]['chx1'] >= maxx:
        maxx = model[hash]['chx1']
    if model[hash]['chy0'] <= miny:
        miny = model[hash]['chy0']
    if model[hash]['chy1'] >= maxy:
        maxy = model[hash]['chy1']

# COMBINE MODEL WITH WS DATA
for hash in hashes:
    values = []
    for i,var in enumerate(model[hash]['varNames']):
        for order in model[hash]['orders'][i]:
            if var == 'T':
                value = Tout**order
            if var == 'wind':
                value = wind
                if value < 1E-10:
                    value = 0.00001
                value = np.log(value)**order
            if var == 'hour':
                value = sel_dt.hour**order
            if var == 'yday':
                value = sel_dt.timetuple().tm_yday**order
            values.append(value)
    predict = np.sum(model[hash]['coef']*values)
    model[hash]['pred_diffT'] = predict
    model[hash]['pred_absT'] = predict + Tout


######################## PLOTTING
fig,ax = plt.subplots()
img_files = os.listdir(maps_path)
for img_file in img_files:

    img_x0 = int(img_file[0:3])*1000
    img_y0 = int(img_file[4:7])*1000
    img_x1 = int(img_file[8:11])*1000
    img_y1 = int(img_file[12:15])*1000
    
    
    if ((img_x0 < maxx) & (img_x1 > minx)) & \
            ((img_y0 <= maxy) & (img_y1 >= miny)):
        img = mpimg.imread(maps_path + '/' + img_file)
        imgplot = ax.imshow(img, extent=(img_x0,img_x1,img_y0,img_y1), origin='upper')

ax.set_xlim((minx,maxx))
ax.set_ylim((miny,maxy))

# GET LIMITS
predictions = []
for hash in hashes:
    predictions.append(model[hash]['pred_absT'])
zlim0 = np.min(predictions)
zlim1 = np.max(predictions)

# color normalization
cmap = cm.get_cmap('YlOrRd')
norm = Normalize(vmin=zlim0, vmax=zlim1)

cells = []
colors = []
#predictions = []
for hash in hashes:
    x0 = model[hash]['chx0']
    x1 = model[hash]['chx1']
    y0 = model[hash]['chy0']
    y1 = model[hash]['chy1']

    cell = Rectangle((x0, y0), x1-x0, y1-y0)
    cells.append(cell)

    col = cmap(norm(model[hash]['pred_absT']))
    colors.append(col)

pc = PatchCollection(cells, facecolor=colors, alpha=0.3)

ax.add_collection(pc)
mappable = cm.ScalarMappable(cmap=cmap)
mappable.set_array([zlim0,zlim1])
fig.colorbar(mappable)

factor = 400
fig.set_size_inches((maxx-minx)/factor,(maxy-miny)/factor)
fig.tight_layout()

ax.set_title(sel_dt_str)

if i_save_fig:
    plt.savefig(img_out_path)
else:
    plt.show()
