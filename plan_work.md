# SA:
1. :white_check_mark: Create daily climatology from _real_ time OSTIA: 2007- 2023, both SST and ICE:
   - Complete years: skip 04/01/2006- 12/31/2006.
   - Use data files that have been created by GMAO OPS, in path:
     `/discover/nobackup/projects/gmao/share/dao_ops/fvInput/g5gcm/bcs/realtime/OSTIA_REYNOLDS/2880x1440/`
     - Using: `dataoceanfile_OSTIA_REYNOLDS_SST.*` and `dataoceanfile_OSTIA_REYNOLDS_ICE.*`
   - Note the data has been _binned_ to 1/8$^\circ$ resolution, _original_ data from OSTIA is at 1/20$^\circ$ resolution, both 
     are on a regular lat-lon dateline, pole edge grid.

   - See script: `get_daily_clim.py`
  
   - Denote by $\bar{x}(t_k)$

2. :negative_squared_cross_mark: Script to create anomaly in SST, ice for any user input day (anomaly with respect to above daily climatology).
 - Denote by $\delta x(t_k).$

 3. :negative_squared_cross_mark: Script to create _future_ SST, ice for 15-days into _future_ from any user input day.

 ## Different approaches:
  - Persist anomaly of today into future (ECMWF, Kristian Mogensen): $x(t_{k+d}) = \bar{x}(t_{k+d}) + \delta x(t_k), $ for $d= 1, 15.$
  - Project from past 15-days anomlaies into future: $x(t_{k+d}) = \bar{x}(t_{k+d}) + \delta x(t_{k-d}), $ for $d= 1, 15.$
  - _Present_ (Dec 2023) GEOS FP: $x(t_{k+d}) = x(t_{k}) + \alpha \, \delta x(t_{k-d}), $ for $d= 1, 15, \, \alpha=0.$ 

# SA and RT: Metric _Test_ above approaches
1. Differences (time-series) RMSE over 15-days $\alpha$ versus RMSE for different choices of (above) methods and $\alpha,$ RMSE is with respect to _real_ SST.

# RT:
1. Control _as usual_ (real SST/ICE). Run experiment for a month, forecasts, etc.
2. Forecast with persisted SST/ICE as in GMAO OPS.
3. Repeat forecats by swapping persisted SST/ICE data with **new options** $\alpha$ (parameter).
4. Repeat above 1 (cycling DA) and 2 by swapping _real_ data with _climatological_ data.

# SA:
1. Coupled set as RT's, relaxing ocean model SST to _real_ and _climatological_ data.
2. ...

