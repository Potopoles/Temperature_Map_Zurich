import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import GPSConverter as GPSConverter
from datetime import datetime,timedelta
from netCDF4 import Dataset
#import os
import pickle
from scipy import interpolate


inp_file = '03_data/01_sensor_data.pkl'
out_file = '03_data/02_spatial_grid.pkl'
ws_path = '../../../Dropbox/aWetter/RP_Upload/ws.nc'

dx = 100
wx2 = 100
minx = 681000
maxx = 687000
miny = 249000
maxy = 255000
min_nEntries = [25,30,50]
i_plot = 1



input = pickle.load(open(inp_file, 'rb'))

# SPATIAL SELECTION 
print('spatial selection')
mask = ( (input['chx'] >= minx) & (input['chx'] <= maxx) ) & \
       ( (input['chy'] >= miny) & (input['chy'] <= maxy) )
mask_inds = np.argwhere(mask).squeeze()
for key,values in input.items():
    if key != 'dt':
        input[key] = input[key][mask]
    else:
        input[key] = [input[key][i] for i in mask_inds]

xs = np.arange(minx,maxx+1,dx) 
ys = np.arange(miny,maxy+1,dx) 
X,Y = np.meshgrid(xs,ys)
nx = len(xs)
ny = len(ys)

vals = np.zeros(np.shape(X))
times = np.zeros(np.shape(X))

data = {}
for i in range(0,nx):
    print(i)
    for j in range(0,ny):
        hash = str(i)+'_'+str(j)

        # PLOTTING CORNERS
        x0 = xs[i] - dx/2
        x1 = xs[i] + dx/2
        y0 = ys[j] - dx/2
        y1 = ys[j] + dx/2

        # WINDOW CORNERS
        wx0 = xs[i] - wx2
        wx1 = xs[i] + wx2
        wy0 = ys[j] - wx2
        wy1 = ys[j] + wx2

        inds = np.argwhere((input['chx'] >= wx0) & (input['chx'] < wx1) & \
                (input['chy'] >= wy0) & (input['chy'] < wy1)).squeeze()
        n_entries = inds.size
        # for size 1 'values' recreate dimension
        if inds.ndim == 0:
            inds = np.expand_dims(inds,axis=0)

        if n_entries > 0:
            data[hash] = {}
            data[hash]['x0'] = x0 
            data[hash]['x1'] = x1 
            data[hash]['y0'] = y0 
            data[hash]['y1'] = y1 
            data[hash]['wx0'] = wx0 
            data[hash]['wx1'] = wx1 
            data[hash]['wy0'] = wy0 
            data[hash]['wy1'] = wy1 

            data[hash]['nEntries'] = n_entries
            data[hash]['diff_T'] = input['diff_T'][inds]
            data[hash]['dts'] = [input['dt'][c] for c in inds]

            # remove minutes and seconds to obtain full hours
            full_hrs = []
            for c,dt in enumerate(data[hash]['dts']):
                dt = dt - timedelta(minutes=dt.minute)
                dt = dt - timedelta(seconds=dt.second)
                full_hrs.append(dt)

            # unique dts
            dts_unique_hrs = np.unique(full_hrs)
            diff_T_hrs = np.zeros(len(dts_unique_hrs))
            # average all diff_T values for each unique hour
            for c,dt_hr in enumerate(dts_unique_hrs):
                mask = [(dt >= dt_hr) & (dt < (dt_hr + timedelta(hours=1))) for dt \
                        in data[hash]['dts']]
                diff_T_hrs[c] = np.mean(data[hash]['diff_T'][mask])

            data[hash]['nEntries'] = len(dts_unique_hrs)
            data[hash]['diff_T'] = diff_T_hrs
            data[hash]['dts'] = dts_unique_hrs

data['nx'] = nx
data['ny'] = ny

pickle.dump(data, open(out_file, 'wb'))


# PLOT
for min_nEntry in min_nEntries:
    Z = np.zeros((nx,ny))
    for i in range(0,nx):
        for j in range(0,ny):
            hash = str(i)+'_'+str(j)
            if hash in data:
                if data[hash]['nEntries'] > min_nEntry:
                    Z[i,j] = data[hash]['nEntries']
                else:
                    Z[i,j] = np.nan
            else:
                Z[i,j] = np.nan
    if i_plot:
        plt.pcolor(X,Y,Z)
        plt.colorbar()
        plt.savefig('03_data/growth/'+str(min_nEntry)+'_'+str(dx)+'_'+
                datetime.now().strftime('%Y%m%d')+'.png')
        plt.close('all')
            

