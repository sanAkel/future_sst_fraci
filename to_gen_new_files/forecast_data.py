#!/usr/bin/env python3

# Usage:
# 1. source g5_modules
# 2. Edit: start_date, fcst_nDays
# 3. ./forecast_data.py
#
# todo: 
# - Input args to to_cube_bcs.j
# - CHECK FOR FINAL OUTPUT, MOVE TO CONVENIENT LOCATION?
# --

import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import sys
import os
# --

def make_file_name(d_string, workDir, ice_pref, sst_pref):
  dStr = str(d_string.year) + str(d_string.month).zfill(2) + str(d_string.day).zfill(2)
  print(dStr)
  ice_file = workDir+"/"+ ice_pref + dStr + suff
  sst_file = workDir+"/"+ sst_pref + dStr + suff
  return ice_file, sst_file
# --

# user inputs
get_inputs = argparse.ArgumentParser(prog='\nforecast_data.py',\
description='Generate SST and Ice concentration lower boundary\
             condition for atmospheric forecasting.', usage='%(prog)s [options]')

get_inputs.add_argument('--sdate', type=str,\
                        metavar='date in yyyymmdd format (str)', required=True)

get_inputs.add_argument('--fcst_nDays', type=int,\
                        metavar='number of days (int)', default=15, help='default to 15 days')

get_inputs.add_argument('--method', type=str,\
                        metavar='which method of generating future data: persistence OR persist_anomaly', required=True)

args = get_inputs.parse_args()

start_date = datetime.strptime(str(args.sdate), '%Y%m%d')
fcst_nDays = args.fcst_nDays
method = args.method

FVBIN = '/discover/nobackup/sakella/geosMom6/develop_20Feb2024/install/bin'
EXEC  = 'gen_forecast_bcs.x'
EXEC2x= 'extract_daily_sst_ice.x'

# path where output will be written to-- a sub dir in this path will be created
out_dir = '/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/to_gen_new_files/'

ice_pref, sst_pref = ["bcs_2880x1440_ice_", "bcs_2880x1440_sst_"]
suff = ".bin"

ncFile_pref, ncFile_suff = ["sst_ice_", ".nc"]
# --

# Forecast dates
fcst_dates = pd.date_range(start_date, periods=fcst_nDays, freq='D')

# Past date - A single day from past is needed for GEOS ReadForcing and its interpolation/date bracketing to work
last_date = pd.date_range(end=fcst_dates[0], periods=2, freq='D')[0]
# --

print("\nGenerate fcst data for:\n\n",fcst_dates)

output_pref = str( fcst_dates[0].year) + str( fcst_dates[0].month).zfill(2) + str( fcst_dates[0].day).zfill(2)+'_'+\
              str(fcst_dates[-1].year) + str(fcst_dates[-1].month).zfill(2) + str(fcst_dates[-1].day).zfill(2)

# if workDir exists, delete it and create a fresh one.
workDir = out_dir + 'fcst_data_' + output_pref
if os.path.exists(workDir):
  print("\nOutput {}\nalready exists. Deleting it.".format(workDir))
  cmd1 = '/usr/bin/rm -rf ' + workDir
  exit_code1 = os.system(cmd1)

try:
  print("Creating..", workDir, "\n")
  os.mkdir(workDir)
  print("\n\nDone.")
except OSError as error:
  print(error) 

# Generate lat-lon files
os.chdir(workDir)
# Generate lat-lon output
cmd2x = FVBIN + '/' + EXEC2x +\
      ' -year {} -month {} -day {} -save_bin'.format(last_date.year, last_date.month, last_date.day)
exit_code2x = os.system(cmd2x) # past (one) day

cmd2 = FVBIN + '/' + EXEC +\
      ' -year {} -month {} -day {} -fcst_nDays {} -method {}'.format(fcst_dates[0].year, fcst_dates[0].month, fcst_dates[0].day, fcst_nDays, method)
exit_code2 = os.system(cmd2)   # Present and future days

# List all output files
list_of_ice_files = []
list_of_sst_files = []

# Start with past date
[ice_file, sst_file] = make_file_name(last_date, workDir, ice_pref, sst_pref)

if(Path(ice_file).is_file()): # check file exists
  list_of_ice_files.append( ice_file)
else:
  print("File does not exist: {}. Exiting.".format(ice_file))
  sys.exit()

if(Path(sst_file).is_file()): # check file exists
  list_of_sst_files.append( sst_file)
else:
  print("File does not exist: {}. Exiting.".format(sst_file))
  sys.exit()
#
# Next forecast dates
for dd in fcst_dates:
  dStr = str(dd.year) + str(dd.month).zfill(2) + str(dd.day).zfill(2)
  #print(dStr)
  [ice_file, sst_file] = make_file_name(dd, workDir, ice_pref, sst_pref)

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

# Generate commands: 1. concatenate daily files, 2. make rc file for Ben's lat-lon to cube util, 3. sbatch Ben's regridForcing
#
# 1. Command to concatenate into a single file

ice_file_lat_lon = 'ice_2880x1440_' + output_pref + suff
sst_file_lat_lon = 'sst_2880x1440_' + output_pref + suff

ice_cmd1 = '/usr/bin/cat ' + ' '.join(list_of_ice_files) + ' > ' + ice_file_lat_lon
sst_cmd1 = '/usr/bin/cat ' + ' '.join(list_of_sst_files) + ' > ' + sst_file_lat_lon

print(ice_cmd1)
print(sst_cmd1)

# 2. Commands to create rc file for lat-lon -> cube
ice_cmd2 = out_dir + '/' + 'make_ICE_rcFile.csh ' +\
           ice_file_lat_lon +\
           ' fcst_ice_C360_'+output_pref+suff + ' ' +\
           ' ' + workDir + '_ice'

sst_cmd2 = out_dir + '/' + 'make_SST_rcFile.csh ' +\
           sst_file_lat_lon +\
           ' fcst_sst_C360_'+output_pref+suff + ' ' +\
           ' ' + workDir + '_sst'

# 3. Command to sbatch
ice_cmd3 = 'sbatch ' + '--export=date_range={} '.format(output_pref) + out_dir + '/' + 'ice_cube_bcs.j' 
sst_cmd3 = 'sbatch ' + '--export=date_range={} '.format(output_pref) + out_dir + '/' + 'sst_cube_bcs.j'

#-- first ice
output_dir = workDir + '_ice'
if os.path.exists(output_dir):
  print("\nOutput {}\nalready exists. Deleting it.".format(output_dir))
  cmd1 = '/usr/bin/rm -rf ' + output_dir
  exit_code = os.system(cmd1)
os.mkdir(output_dir)
os.chdir(output_dir)
ice_exit_code1 = os.system( ice_cmd1) # concate bin files
if ice_exit_code1==0:
  ice_exit_code2 = os.system( ice_cmd2) # transform lat-lon to cube
if ice_exit_code2==0:
  ice_exit_code3 = os.system( ice_cmd3) # submit batch job

#-- next sst
output_dir = workDir + '_sst'
if os.path.exists(output_dir):
  print("\nOutput {}\nalready exists. Deleting it.".format(output_dir))
  cmd1 = '/usr/bin/rm -rf ' + output_dir
  exit_code = os.system(cmd1)
os.mkdir(output_dir)
os.chdir(output_dir)
sst_exit_code1 = os.system( sst_cmd1)
if sst_exit_code1==0:
  sst_exit_code2 = os.system( sst_cmd2)
if sst_exit_code2==0:
  sst_exit_code3 = os.system( sst_cmd3)
