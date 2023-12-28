#!/usr/bin/env python3

import xarray as xr
import xesmf as xe

import matplotlib.pyplot as plt

# Pick a 1/20 grid OSTIA (original grid) file
ostia_path = "/discover/nobackup/sakella/projects/bcs_pert/data/data_OSTIA/"
ostia_fl = ostia_path + "20230101-UKMO-L4HRfnd-GLOB-v01-fv02-OSTIA.nc"

# Pick a binned 1/8 deg grid file
geos_grid_path = "/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/data/ncFiles/"
geos_grid_file = geos_grid_path + "daily_clim_mean_sst_fraci_00010101.nc"

# Below file was created using `diff_binned_interpolate/gen_wts_regrid_ostia_geos.py`
wts_fl = "/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/diff_binned_interpolate/data/wts_cons_ostia_to_geos_eight.nc"

ds_in  = xr.open_dataset(ostia_fl).squeeze()
ds_geos_grid = xr.open_dataset(geos_grid_file, decode_times=False).squeeze()

# regrid OSTIA data, including `mask` to 1/8 GEOS grid
regridder = xe.Regridder(ds_in, ds_geos_grid, 'conservative', weights=wts_fl)
ds_out = regridder(ds_in, keep_attrs=True)

# extract and write out mask
mask_in = ds_in.mask
mask_out = ds_out.mask

# write out mask
mask_in.to_netcdf('mask_ostia.nc')
mask_out.to_netcdf('mask_geos_bcs.nc')
