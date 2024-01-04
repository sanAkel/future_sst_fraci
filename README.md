# Main purpose is to create SST and ice concentration for future

## Ideas are laid out in: [plan_work.md](https://github.com/sanAkel/future_sst_fraci/blob/main/plan_work.md)

## Relies on functional executables built from [GEOS-ESM/GEOS_Util](https://github.com/GEOS-ESM/GEOS_Util/tree/main/pre/prepare_ocnExtData)

# Layout of contents:

- diff_binned_interpolate/

  Because a choice was made (around 2012, MERRA-2 context) to bin 1/20-deg OSTIA datasets to 1/8-deg instead of (conservative: sea ice!) interpolation,
  plot the difference between the two approaches.
  
  - Remarks:
    1. Which of the two approaches is _better_? (We need comparisons with observations: RT)
    2. Given the overall plan of using coupled model (ocean model) and relax to SST, we should switch to interpolated data- that way we use ESMF and
       _some_ day this step can be done on-line (on the fly; Ben connection: when we get there). Relaxation can be interpreted as on _operator_...

- gen_daily_clim/

  - Used for generating daily climatology, see script: get_daily_clim.py
  - You need `cal_daily_clim.x` to be built, available from GEOS-ESM/GEOS_Util, 
    source code: `daily_clim_SST_FRACI_eight.F90`

- GMAO_OPS_bin_data/

  To work with GMAO OPS 1/8-deg files. Path on discover (NCCS):
  `/discover/nobackup/projects/gmao/share/dao_ops/fvInput/g5gcm/bcs/realtime/OSTIA_REYNOLDS/2880x1440/`
  As one can see these
  - Datasets are binary formatted.
  - Are yearly files, whereas we are working with daily data.
 
  Therefore we need `extract_daily_sst_ice.x` to be built, available from GEOS-ESM/GEOS_Util, source code: `extract_day_SST_FRACI_eight.F90`.
  Example usage: `extract_daily_sst_ice.x 2023 2 1`
  When it finishes clean, you will get a single netcdf file containing both SST and Ice concentation for your date of choice (e.g., `sst_ice_20230201.nc`).

  `plot_sst_ice.py`: Apply the [land-sea mask generating using this](https://github.com/sanAkel/future_sst_fraci/blob/main/gen_daily_clim/make_clean_land_sea_mask.ipynb) and calculate
  differences in time-lagged data.

  **Note**: Plot using grads: plot_{xx}.ctl, xx=sst, ice are provided in case you insist on working with binary data. Above `extract_day_SST_FRACI_eight.F90`
            can be modified to write out daily data in binary format, see source code <-- uncomment `CALL write_bin(...)` and recompile.
