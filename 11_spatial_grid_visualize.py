import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import GPSConverter as GPSConverter
from datetime import datetime,timedelta
from netCDF4 import Dataset
#import os
import pickle
from scipy import interpolate


inp_file = '03_data/02_spatial_grid.pkl'
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

min_nEntries = 25
nx = input['nx']
ny = input['ny']

hashes = input.keys()
hashes = [hash for hash in hashes if (hash != 'nx') and (hash != 'ny')]

good_cells = []
for hash in hashes:
    if input[hash]['nEntries'] > min_nEntries:
        good_cells.append(hash)





# PLOT
fig = plt.figure(figsize=(10,10))
dx = 100
minx = 681000
maxx = 687000
miny = 249000
maxy = 255000
xs = np.arange(minx,maxx+1,dx) 
#x = xs[:-1] + dx/2
ys = np.arange(miny,maxy+1,dx) 
#y = ys[:-1] + dy/2
X,Y = np.meshgrid(xs,ys)
Z = np.zeros((nx,ny))
for i in range(0,nx):
    for j in range(0,ny):
        hash = str(i)+'_'+str(j)
        if hash in good_cells:
            Z[i,j] = input[hash]['nEntries']
        else:
            Z[i,j] = np.nan

plt.pcolor(X,Y,Z)
plt.colorbar()
plt.show()
quit()


for hash in good_cells:
    print(hash)
    n_entries = input[hash]['nEntries']
    Z[i,j] = n_entries

    
    print(n_entries)

plt.savefig('03_input/growth/names.png')
plt.close('all')
        

