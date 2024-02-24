#!/usr/bin/env python3

import os
import pandas as pd

date_s, date_e = ['20230717', '20230917']
#method = 'persistence'
method = 'persist_anomaly'

for d in pd.date_range(date_s, date_e):
# print( d.strftime('%Y%m%d'))
  cmd = "./forecast_data.py --sdate {} --method {}".format(d.strftime('%Y%m%d'), method)
  print(cmd)
  exit_code = os.system(cmd)
