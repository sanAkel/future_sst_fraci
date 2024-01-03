#!/usr/bin/env python3

# Usage:
# source g5_modules
# ./get_daily_clim.py
# --

import pandas as pd
import os

path_to_bin = "/discover/nobackup/sakella/" + "geosMom6/v11.1.1/GEOSgcm/build/bin/"
to_exec = path_to_bin + "cal_daily_clim.x"

start_year, end_year = [2007, 2023]

# some arbitrary year
dummy_dates = pd.date_range(start='12/2/1900', end='12/31/1900', freq='D')
#dummy_dates = pd.date_range(start='1/1/1900', end='12/31/1900', freq='D')

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
