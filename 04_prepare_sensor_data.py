import numpy as np
from datetime import datetime
import GPSConverter as GPSConverter
from netCDF4 import Dataset
from scipy import interpolate
import pickle
import os
import subprocess
from dateutil import tz
#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt

input = {'chx':[],'chy':[],'T':[],'dt':[]}

input_folder = 'thermoloc_out'
archive_folder = 'thermoloc_archive'
out_file = '03_data/01_sensor_data.pkl'
ws_path = '../../../Dropbox/aWetter/RP_Upload/ws.nc'
cet_tz = tz.gettz('Europe/Berlin')
utc_tz = tz.gettz('UTC')

converter = GPSConverter.GPSConverter()

print('load files')
files = os.listdir(input_folder)
for filename in files:
    print(filename)
    filepath = input_folder+'/'+filename
    success = 0
    while not success:
        # TRY TO LOAD THE FILE
        try:
            inp = np.genfromtxt(filepath, delimiter=';',
                    skip_header=1,dtype=np.str)[:,:]
            success = 1
        except: # ERROR --> REMOVE CORRUPTED LINES
            print('FILE CORRUPTED. FIX IT')
            #raise NotImplementedError('A FILE COULD NOT BE READ')
            good_lines = []
            with open(filepath, 'r') as f:
                for line in f:
                    if line.count(';') == 10:
                        good_lines.append(line)

            with open(filepath, 'w+') as f:
                for line in good_lines:
                    f.write(line)

    dt = [datetime.strptime(dt_str,'%Y-%m-%d %H:%M:%S') for dt_str in inp[:,0]]
    dt_utc = [this_dt.replace(tzinfo=utc_tz) for this_dt in dt]
    dt_cet = [this_dt.astimezone(cet_tz) for this_dt in dt_utc]

    lon = inp[:,1].astype(np.float)
    lat = inp[:,2].astype(np.float)
    alt_gps = inp[:,3].astype(np.float)
    temp = inp[:,8].astype(np.float)

    # Calculate chx and chy
    nEntries = len(lat)
    chx = np.full(nEntries,np.nan)
    chy = np.full(nEntries,np.nan)
    for i in range(0,nEntries):
        try:
            out = converter.WGS84toLV03(lat[i], lon[i], alt_gps[i])
            chx[i] = out[0]
            chy[i] = out[1]
        except:
            pass

    for i in range(0,nEntries):
        if (temp[i] < -20) | (temp[i] > 50):
            chx[i] = np.nan
            chy[i] = np.nan
            temp[i] = np.nan


    input['chx'].extend(list(chx)) 
    input['chy'].extend(list(chy)) 
    input['T'].extend(list(temp)) 
    input['dt'].extend(list(dt_cet)) 

plt.plot(input['chx'],input['chy'])
print('Proceed..?')
plt.show()

plt.plot(input['dt'],input['T'])
print('Proceed..?')
plt.show()

if len(input['chx']) > 0:
    ## INTERPOLATE WS TEMPERATURE
    print('interpolate ws temperature')
    chx = input['chx']
    chy = input['chy']
    T = input['T']
    dts = input['dt']
    tstmp = [int(dt.timestamp()) for dt in dts]

    # WS DB
    ncf = Dataset(ws_path, 'r')
    ws_tstmp = ncf['time'][:].astype(np.int)
    ws_T = ncf['Tout'][:]

    print('entries: '+str(datetime.fromtimestamp(np.max(tstmp))))
    print('ws:      '+str(datetime.fromtimestamp(np.max(ws_tstmp))))

    # ACTUALISE WS DB IF NECESSARY
    if np.max(tstmp) > np.max(ws_tstmp):
        ncf.close()
        print('COPY NEW WS DB')
        subprocess.call(['scp', 'pi@192.168.178.139:/home/pi/ws.nc',
            '../../../Dropbox/aWetter/RP_Upload/ws.nc'])
        # try loading ws again
        ncf = Dataset(ws_path, 'r')
        ws_tstmp = ncf['time'][:].astype(np.int)
        # raise error if scp did not work.
        if np.max(tstmp) > np.max(ws_tstmp):
            ncf.close()
            raise RuntimeError('Could not connect to WS DB with scp!')
        ws_T = ncf['Tout'][:]

    interp = interpolate.interp1d(ws_tstmp, ws_T)
    ws_T_interp = interp(tstmp)

    input['ws_T'] = ws_T_interp
    input['diff_T'] = input['T'] - input['ws_T']

    print('#########')
    print('Mean abs diff:')
    print(np.nanmean(np.abs(input['diff_T'])))
    print('#########')

    plt.plot(input['dt'],input['diff_T'])
    print('Proceed..?')
    plt.show()

    ## REMOVE NAN ENTRIES
    print('remove NAN entries')
    mask = np.isnan(input['chx']) == False
    mask[np.isnan(input['chy'])] = False
    mask[np.isnan(input['T'])] = False
    mask[np.isnan(input['ws_T'])] = False
    mask_inds = np.argwhere(mask).squeeze()

    input['chx'] = np.asarray(input['chx'])
    input['chy'] = np.asarray(input['chy'])
    input['T'] = np.asarray(input['T'])

    for key,values in input.items():
        if key != 'dt':
            input[key] = input[key][mask]
        else:
            input[key] = [input[key][i] for i in mask_inds]

    # ADD TO EXISTING DB
    if os.path.exists(out_file):
        existing_db = pickle.load(open(out_file, 'rb'))
        nEntries_old = existing_db['chx'].shape[0]
        for key in existing_db.keys():
            field_ex = existing_db[key]
            if key != 'dt':
                field_ex = np.append(field_ex, input[key])
            else:
                field_ex.extend(input[key])
            existing_db[key] = field_ex
        nEntries_new = existing_db['chx'].shape[0]
        rel_increase = nEntries_new/nEntries_old - 1
        print("DB grows by {:4.2f} % :-)".format(100*rel_increase))
    else:
        existing_db = input

    #quit()
    # SAVE
    pickle.dump(existing_db, open(out_file, 'wb'))

    # MOVE RAW DATA TO ARCHIVE
    subprocess.call(['mv '+input_folder+'/* '+archive_folder], shell=True)

else:
    print('NO NEW DATA IN "files_new_toProcess" FOLDER!')

