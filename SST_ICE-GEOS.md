# This notes summarizes how [GEOS weather system](https://gmao.gsfc.nasa.gov/weather_prediction/) and [MERRA-2 reanalysis](https://gmao.gsfc.nasa.gov/reanalysis/) handle ocean boundary conditions.

GEOS ocean boundary conditions include:
- Sea Surface Temperature (SST).
- Sea Ice Concentration (SIC).

If the model is an atmosphere (only) model, i.e.., without an ocean and sea ice model the SST and SIC are read in from a dataset to prescribe over:
- Open ocean.
- Certain lakes (in land water).

Chapter 8.A of [Bosilovich et al., 2015](https://gmao.gsfc.nasa.gov/pubs/docs/Bosilovich803.pdf) provides _scientific_ details that apply directly to the MERRA-2 reanalysis.
The same apply to the weather (GEOS-FP) system, instead of $0.25^{\circ}$ SST and SIC, the datsets are prescribed at $0.125^{\circ}= \frac{1}{8}^{\circ}$ resolution.

## Following lists the technical aspects.

1. Download SST and SIC from the [OSTIA system.](https://data.marine.copernicus.eu/product/SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001/description)
   The GEOS-FP system downloads it from [PODAAC](https://podaac.jpl.nasa.gov/dataset/OSTIA-UKMO-L4-GLOB-REP-v2.0), it is upto _you_ to download from whereever and verify that the data is the same regardless of the origin!
   FWIW @sanAkel uses the former.
3. Use [this software](https://github.com/GEOS-ESM/GEOS_Util/tree/main/pre/NSIDC-OSTIA_SST-ICE_blend),
   [this top level script](https://github.com/GEOS-ESM/GEOS_Util/blob/main/pre/NSIDC-OSTIA_SST-ICE_blend/make_ostia_eigth.csh) gives an overview. Essentially steps involved are:
   - [The main program](https://github.com/GEOS-ESM/GEOS_Util/blob/main/pre/NSIDC-OSTIA_SST-ICE_blend/proc_SST_FRACI.F90)
      - [Read inputs](https://github.com/GEOS-ESM/GEOS_Util/blob/5f6a77f5d0b1a6cd9406ef75bea261341bdfd529/pre/NSIDC-OSTIA_SST-ICE_blend/proc_SST_FRACI.F90#L52-L55)
      - [Read OSTIA SST and SIC](https://github.com/GEOS-ESM/GEOS_Util/blob/5f6a77f5d0b1a6cd9406ef75bea261341bdfd529/pre/NSIDC-OSTIA_SST-ICE_blend/proc_SST_FRACI.F90#L80-L81)
      - [Read SST and SIC from _Reynolds_ dataset](https://github.com/GEOS-ESM/GEOS_Util/blob/5f6a77f5d0b1a6cd9406ef75bea261341bdfd529/pre/NSIDC-OSTIA_SST-ICE_blend/proc_SST_FRACI.F90#L71-L73)
        This data is used if and only if there is `NaN` over Great lakes and Caspian sea in the OSTIA dataset, for that to happen it is interpolated to a [common grid](https://github.com/GEOS-ESM/GEOS_Util/blob/5f6a77f5d0b1a6cd9406ef75bea261341bdfd529/pre/NSIDC-OSTIA_SST-ICE_blend/proc_SST_FRACI.F90#L96-L98)
     -  [Bin](https://github.com/GEOS-ESM/GEOS_Util/blob/5f6a77f5d0b1a6cd9406ef75bea261341bdfd529/pre/NSIDC-OSTIA_SST-ICE_blend/proc_SST_FRACI.F90#L106-L107) $0.05^{\circ}$ OSTIA SST and SIC to $0.125^{\circ}$
     -  GEOS modeling infrastructure expects SST and SIC over the entire globe, to satisfy this requirement, [fill land and other non-ocean points](https://github.com/GEOS-ESM/GEOS_Util/blob/5f6a77f5d0b1a6cd9406ef75bea261341bdfd529/pre/NSIDC-OSTIA_SST-ICE_blend/proc_SST_FRACI.F90#L168-L172)
        [Antarctic land mass has to be treated carefully because of ice shelves.](https://github.com/GEOS-ESM/GEOS_Util/blob/5f6a77f5d0b1a6cd9406ef75bea261341bdfd529/pre/NSIDC-OSTIA_SST-ICE_blend/proc_SST_FRACI.F90#L181-L252)
     - [Make adjustments to SIC, using SST thresholds](https://github.com/GEOS-ESM/GEOS_Util/blob/5f6a77f5d0b1a6cd9406ef75bea261341bdfd529/pre/NSIDC-OSTIA_SST-ICE_blend/proc_SST_FRACI.F90#L272-L277)
     - [Write output](https://github.com/GEOS-ESM/GEOS_Util/blob/5f6a77f5d0b1a6cd9406ef75bea261341bdfd529/pre/NSIDC-OSTIA_SST-ICE_blend/proc_SST_FRACI.F90#L305-L313) into a **sequential binary** format. 
4. If _you_ are as sick as @sanAkel is with binary files! Help yourself [with these utilities.](https://github.com/GEOS-ESM/GEOS_Util/tree/main/pre/prepare_ocnExtData) and [notebook example is here.](https://github.com/GEOS-ESM/GEOS_Util/tree/main/pre/prepare_ocnExtData/notebooks)

## [This repo](https://github.com/sanAkel/future_sst_fraci/)
Provides utilties to 
- [Convert ⬆️ mentioned binary files to netcdf format.](https://github.com/sanAkel/future_sst_fraci/blob/main/gen_daily_clim_data/get_daily_clim_or_data.py)
- [Plot the SST and SIC in nc files.](https://github.com/sanAkel/future_sst_fraci/blob/main/gen_daily_clim_data/plot_clim_anom_sst_ice.ipynb)
- [Rest read ...](https://github.com/sanAkel/future_sst_fraci/blob/main/README.md)



