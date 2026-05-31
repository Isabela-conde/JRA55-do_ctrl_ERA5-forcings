# JRA55-do_ctrl_ERA5-forcings

Analysis of **ACCESS-OM2 forcing-perturbation experiments** — JRA55-do control vs.
ERA5-derived forcings — focused on SST responses, percentile / cold-warm metrics, and
the observational input trends that drive the perturbations.

Carved out of the original `ACCESS-OM2-Atmosphere-Perturb` folder and reorganised into
focused notebooks. The original folder is left untouched as the source of truth.

## Structure

- `omip_comparison/`
  - `omip_trend_maps_and_quivers.ipynb` — SST trend maps + wind quivers across OMIP models
  - `omip_percentiles.ipynb` — percentile method & perturbation-SST percentiles
  - `omip_global_mean.ipynb` — global means & wind-stress perturbation
- `cold_warm_metric/`
  - `cw_load_and_percentile_plots.ipynb` — load data, percentiles, difference plots
  - `cw_warm_cold_fractions_and_gradient.ipynb` — temp gradient, warmest/coldest 50%/20%
  - `cw_mean_and_basin_warming.ipynb` — CW mean & basin warming
  - `cw_trend_load_and_compute.ipynb` / `cw_trend_plots.ipynb` — cold-warm trend
- `cm2_om2_compare/`
  - `cm2_om2_trends.ipynb` / `cm2_om2_means.ipynb` — CM2 vs OM2 comparisons
- `sst/era5_sst_vs_cobe.ipynb` — ERA5 SST vs COBE
- `trends/trend_maps.ipynb` — trend maps
- `inputs/`
  - `obs_tas_huss_trends.ipynb` — OAFlux tas/huss input trends
  - `obs_wind_uas_vas_trends.ipynb` — NOAA blended-wind uas/vas input trends
- `tutorial/` — *pending* (see note)
- `functions.py` — shared helpers (`find_trend_values`, `pacific_mask`, `quantiles_xhist`, `find_trend_percentile`, `calculate_confidence_intervals_all`, …). Notebooks start with `from functions import *`.

## Notes

- **Outputs were stripped** — re-run to regenerate figures.
- Split out of long linear notebooks, so a focused notebook may need a data-loading cell
  added if it references a variable computed in another section.
- Data paths currently point at `…/Desktop/data/…` (local). Update for Gadi as needed.

## Pending
`ACCESS-OM2_forcing_perturbation_tutorial.ipynb` could not be copied because the source
file was open/locked during processing. Close it in Jupyter/VS Code and it can be added.
