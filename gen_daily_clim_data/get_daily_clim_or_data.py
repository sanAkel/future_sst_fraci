#!/usr/bin/env python3

# Usage:
# source g5_modules
# ./get_daily_clim.py
# --

import pandas as pd
import os

#which_exec = 'daily_clim'
which_exec = 'extract_daily'
# --

path_to_bin = "/discover/nobackup/sakella/" + "geosMom6/v11.1.1/GEOSgcm/build/bin/"
#~~~~~~~~~~~~~
if (which_exec == 'daily_clim'):
  to_exec = path_to_bin + "cal_daily_clim.x"
  start_year, end_year = [2007, 2023] # for climatology
# some arbitrary dates
  dummy_dates = pd.date_range(start='1/1/1900', end='12/31/1900', freq='D') # for climatology
else:
  to_exec = path_to_bin + "extract_daily_sst_ice.x"
# x0049 (summer)
  dummy_dates = pd.date_range(start='6/1/2017', end='10/1/2017', freq='D')
#~~~~~~~~~~~~~

if (which_exec == 'daily_clim'):
  for dd in range( len(dummy_dates)):
     mon, day = [dummy_dates[dd].month, dummy_dates[dd].day]
     # print(mon, day)
     cmd = to_exec + ' ' +\
           '{} {}'.format(start_year, end_year) + ' ' +\
           '{} {}'.format(mon, day)
     #print(cmd)
     exit_code = os.system(cmd)
     if (exit_code != 0):
       print("Error running:")
       sys.exit(cmd)
else:
  for dd in range( len(dummy_dates)):
     year, mon, day = [dummy_dates[dd].year, dummy_dates[dd].month, dummy_dates[dd].day]
     # print(year, mon, day)
     cmd = to_exec + ' ' +\
           '{} {} {} .true.'.format(year, mon, day)
     print(cmd)
     exit_code = os.system(cmd)
     if (exit_code != 0):
       print("Error running:")
       sys.exit(cmd)
     else:
       os.system('/bin/mv *.nc  /discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/GMAO_OPS_bin_data/data/{}/'.format(dummy_dates[0].year))
       os.system('/bin/mv *.bin /discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/GMAO_OPS_bin_data/data/{}/'.format(dummy_dates[0].year))
