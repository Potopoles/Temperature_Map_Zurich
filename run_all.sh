#!/bin/bash

#./copy_new_files.sh
python 04_prepare_sensor_data.py
python 05_ws_hourly_mean.py
python 06_spatial_grid.py
python 07_train.py
./upload_model.sh
