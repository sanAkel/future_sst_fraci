#!/usr/bin/env python3

# Usage:
# source g5_modules
# ./hindcast_data.py
# CHECK FOR OUTPUT, MOVE IT CONVENIENT LOCATION?
# --

from pathlib import Path
import pandas as pd
import sys
import os

# user inputs
start_date, end_date = ['2017-06-01', '2017-06-10']
#start_date, end_date = ['2017-06-01', '2017-10-01']
FVBIN = '/discover/nobackup/sakella/geosMom6/v11.1.1/GEOSgcm/install/bin'

# data files must have been extracted to some path
extracted_files_path = "/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/GMAO_OPS_bin_data/data"

# path where output will be written to
out_dir = '/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/to_gen_new_files/'
# --

ice_pref, sst_pref = ['sst_ice_ice_', 'sst_ice_sst_']
suff = ".bin"

hindcast_dataset_dates = pd.date_range(start_date, end_date, freq='D')

# List all files
list_of_ice_files = []
list_of_sst_files = []
for dd in hindcast_dataset_dates:

  dStr = str(dd.year) + str(dd.month).zfill(2) + str(dd.day).zfill(2)

  ice_file = extracted_files_path+"/"+str(dd.year)+"/" + ice_pref + dStr + suff
  sst_file = extracted_files_path+"/"+str(dd.year)+"/" + sst_pref + dStr + suff

  if(Path(ice_file).is_file()): # check file exists
    list_of_ice_files.append( ice_file)
  else:
    print("File does not exist: {}. Exiting.".format(ice_file))
    sys.exit()

  if(Path(sst_file).is_file()): # check file exists
    list_of_sst_files.append( sst_file)
  else:
    print("File does not exist: {}. Exiting.".format(sst_file))
    sys.exit(1)

# Concatenate them
output_pref = str(hindcast_dataset_dates[0].year) + str(hindcast_dataset_dates[0].month).zfill(2) + str(hindcast_dataset_dates[0].day).zfill(2)+'_'+\
              str(hindcast_dataset_dates[-1].year) + str(hindcast_dataset_dates[-1].month).zfill(2) + str(hindcast_dataset_dates[-1].day).zfill(2)

dir_name = out_dir + 'data_' + output_pref
ice_file_lat_lon = 'real_ice_2880x1440_' + output_pref + suff
sst_file_lat_lon = 'real_sst_2880x1440_' + output_pref + suff

ice_cmd1 = '/usr/bin/cat ' + ' '.join(list_of_ice_files) + ' > ' + ice_file_lat_lon
sst_cmd1 = '/usr/bin/cat ' + ' '.join(list_of_sst_files) + ' > ' + sst_file_lat_lon

ice_cmd2 = out_dir + '/' + 'make_ICE_rcFile.csh ' +\
           ice_file_lat_lon +\
           ' real_ice_C360_'+output_pref+suff + ' ' +\
           ' ' + dir_name + '_ice'

sst_cmd2 = out_dir + '/' + 'make_SST_rcFile.csh ' +\
           sst_file_lat_lon +\
           ' real_sst_C360_'+output_pref+suff + ' ' +\
           ' ' + dir_name + '_sst'

ice_cmd3 = 'sbatch ' + out_dir + '/' + 'ice_cube_bcs.j' 
sst_cmd3 = 'sbatch ' + out_dir + '/' + 'sst_cube_bcs.j'

#-- first ice
# Work in temp dir
if not (os.mkdir(dir_name + '_ice')):
  os.chdir(dir_name + '_ice')
  ice_exit_code1 = os.system( ice_cmd1) # concate bin files
  if ice_exit_code1==0:
    ice_exit_code2 = os.system( ice_cmd2) # transform to lat-lon to cube
  if ice_exit_code2==0:
    ice_exit_code3 = os.system( ice_cmd3) # submit batch job

#-- next sst
if not (os.mkdir(dir_name + '_sst')):
  os.chdir(dir_name + '_sst')
  sst_exit_code1 = os.system( sst_cmd1)
  if sst_exit_code1==0:
    sst_exit_code2 = os.system( sst_cmd2)
  if sst_exit_code2==0:
    sst_exit_code3 = os.system( sst_cmd3)

