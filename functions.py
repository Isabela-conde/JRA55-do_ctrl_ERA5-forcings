"""Shared helper functions for this repo.

Auto-extracted from the original ACCESS-OM2-Atmosphere-Perturb notebooks
(funcs_compare.ipynb and others) so the analysis notebooks can simply do:

    from functions import *

instead of redefining these. Edit here once and every notebook benefits.
"""
import numpy as np
import xarray as xr
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
from matplotlib.gridspec import GridSpec
import matplotlib.gridspec as gridspec
import cartopy.crs as ccrs
import scipy
try:
    import xesmf as xe
except Exception:
    xe = None
try:
    from xhistogram.xarray import histogram
except Exception:
    histogram = None
try:
    from mpl_toolkits.basemap import Basemap
except Exception:
    Basemap = None


def regrid_windstress(data):
    
    # Extract 2D coordinates
    TLAT = data["ULAT"]  # (nj, ni)
    TLON = data["ULON"]  # (nj, ni)

    # Create source grid from the natural grid
    ds_src = xr.Dataset(
        {"lat": (["nj", "ni"], TLAT.values),
         "lon": (["nj", "ni"], TLON.values)}
    )
    # Define target regular lat-lon grid
    lat_new = np.linspace(TLAT.min(), TLAT.max(), 300)  # Adjust resolution as needed
    lon_new = np.linspace(TLON.min(), TLON.max(), 360)

    ds_target = xr.Dataset(
        coords={
            "lat": ("lat", lat_new),
            "lon": ("lon", lon_new),
        }
    )
    # Create xESMF regridder (conservative or bilinear)
    regridder = xe.Regridder(ds_src, ds_target, method="bilinear")

    # Apply regridding
    windstress_interp = regridder(data)
    windstress_interp = windstress_interp.assign_coords(
        lon=(("lon",), np.mod(windstress_interp.lon.data , 360))
    )
    # Sort longitudes to maintain increasing order
    windstress_interp = windstress_interp.sortby("lon")
    
    return windstress_interp


def find_trend_values(dt):

    #Input: xarray array with time, lat, lon coordinates and a variable to calculate the trend
    #Output: xarray array with the trend values for each grid point
    
    time, lat, lon = dt['time'].values, dt['lat'].values, dt['lon'].values
    sst_reshaped = dt.values.reshape(len(time), -1)
    degree = 1

    gradient_values = np.empty_like(sst_reshaped[0])
    for i in range(len(sst_reshaped[0])):
        y = sst_reshaped[:, i]
        coefficients = np.polyfit(np.arange(len(time)), y, degree)
        gradient_values[i] = coefficients[-2]  # Coefficient for x term (slope)

    gradient_values = gradient_values.reshape(lat.shape[0], lon.shape[0])
    gradient_da = xr.DataArray(gradient_values, coords={'lat': lat, 'lon': lon}, dims=['lat', 'lon'])
    return gradient_da 


def plot4by4(data, clmap, lab, suptitle,r):
    all_min = r[0]
    all_max = r[1]
    data1 = data[0].sel(lat=slice(-20, 20), lon=slice(110, 291))
    data2 = data[1].sel(lat=slice(-20, 20), lon=slice(110, 291))
    data3 = data[2].sel(lat=slice(-20, 20), lon=slice(110, 291))
    data4 = data[3].sel(lat=slice(-20, 20), lon=slice(110, 291))

    # Create a figure with GridSpec  with 2x2 layout - using basemap
    fig = plt.figure(figsize=(15, 15))
    gs = GridSpec(2, 2, figure=fig)
    gs.update(wspace=0.1, hspace=-0.8)  # reduce the spacing between rows with hspace=0.05


    # Plot for data1
    ax1 = fig.add_subplot(gs[0, 0])
    trend_map = Basemap(ax=ax1, width=6000000, height=12000000, projection='cyl', 
                    llcrnrlat=-20, urcrnrlat=20, llcrnrlon=110, urcrnrlon=291, area_thresh=10000)
    trend_map.drawcoastlines()
    trend_map.drawparallels(np.arange(-20, 20.1, 10.), labels=[1, 0, 0, 0])
    trend_map.drawmeridians(np.arange(-180., 181., 20.), labels=[0, 0, 0, 1])

    trend_map.imshow(data1, cmap=clmap,vmin=all_min, vmax=all_max)
    ax1.set_title('JRA55', fontsize=14)

    # Plot for data2
    ax2 = fig.add_subplot(gs[0, 1])
    trend_map = Basemap(ax=ax2, width=6000000, height=12000000, projection='cyl', 
                    llcrnrlat=-20, urcrnrlat=20, llcrnrlon=110, urcrnrlon=291, area_thresh=10000)
    trend_map.drawcoastlines()
    trend_map.drawparallels(np.arange(-20, 20.1, 10.), labels=[1, 0, 0, 0])
    trend_map.drawmeridians(np.arange(-180., 181., 20.), labels=[0, 0, 0, 1])

    trend_map.imshow(data2, cmap=clmap,vmin=all_min, vmax=all_max)
    ax2.set_title('ERA5', fontsize=14)


    # Plot for data5
    ax3 = fig.add_subplot(gs[1, 0])
    trend_map = Basemap(ax=ax3, width=6000000, height=12000000, projection='cyl', 
                    llcrnrlat=-20, urcrnrlat=20, llcrnrlon=110, urcrnrlon=291, area_thresh=10000)
    trend_map.drawcoastlines()
    trend_map.drawparallels(np.arange(-20, 20.1, 10.), labels=[1, 0, 0, 0])
    trend_map.drawmeridians(np.arange(-180., 181., 20.), labels=[0, 0, 0, 1])

    trend_map.imshow(data3, cmap=clmap, vmin=all_min, vmax=all_max)
    ax3.set_title('ACCESS-CM2', fontsize=14)

    # Plot for data3
    ax4 = fig.add_subplot(gs[1, 1])
    trend_map = Basemap(ax=ax4, width=6000000, height=12000000, projection='cyl', 
                    llcrnrlat=-20, urcrnrlat=20, llcrnrlon=110, urcrnrlon=291, area_thresh=10000)
    trend_map.drawcoastlines()
    trend_map.drawparallels(np.arange(-20, 20.1, 10.), labels=[1, 0, 0, 0])
    trend_map.drawmeridians(np.arange(-180., 181., 20.), labels=[0, 0, 0, 1])

    trend_map.imshow(data4, cmap=clmap, vmin=all_min, vmax=all_max)
    ax4.set_title('MERRA2', fontsize=14)

    plt.tight_layout()

    # Add a common colorbar spanning both rows
    cbar_ax = fig.add_axes([0.92, 0.39, 0.01, 0.2])  # Adjust the position and size to make it smaller
    sm = plt.cm.ScalarMappable(cmap=clmap, norm=plt.Normalize(vmin=all_min, vmax=all_max))
    sm.set_array([])
    fig.colorbar(sm, cax=cbar_ax, label=lab)

    # add super title
    fig.suptitle(suptitle, fontsize=20, y=0.65)
    plt.tight_layout()  # Top of subplots limited to 95% of figure height

    plt.show()


def trend_analysis(jra55, era5, merra2, access_cm2,var_name):
    # if dimensions aren't lat,lon, time regrid with regrid_windstress function - if statement to check jra55, era5, merra2 and access_cm2 dimensions
    def maybe_regrid(ds):
        expected_dims = {'lat', 'lon', 'time'}
        if set(ds.dims) != expected_dims:
            print(f"Regridding {ds.name}")
            return regrid_windstress(ds)
        else:
            return ds
    
    # Regrid the datasets if necessary
    jra55 = maybe_regrid(jra55)
    era5 = maybe_regrid(era5)
    merra2 = maybe_regrid(merra2)
    access_cm2 = maybe_regrid(access_cm2)

    merra2['lon'] = (merra2['lon']) %360
    merra2 = merra2.sortby(['lat','lon']) 

    new_lats = era5.lat.values
    new_lons = era5.lon.values
    merra2_gr = merra2.sel(lat = slice(new_lats[0],new_lats[-1])).interp(lat=new_lats, lon=new_lons)
    print('MERR2 interpolated to match ERA5 grid')

    
    # Calculate the trend for each dataset
    print('Finding trends...')
    jra55_trend = find_trend_values(jra55)*10*12
    era5_trend = find_trend_values(era5)*10*12
    merra2_trend = find_trend_values(merra2_gr)*10*12
    access_cm2_trend = find_trend_values(access_cm2)*10*12
    print('Done')

    # plot all values using plot4by4 function
    print('Plot 1...')
    plot4by4([jra55_trend, era5_trend, access_cm2_trend, merra2_trend], 'BrBG_r' , 'm/s per decade', 'Trend of '+var_name, [-0.6, 0.6])
    # save figure 
    plt.savefig('/Users/isabelaconde/Desktop/trend_fig_abs_vals.png', dpi=300, bbox_inches='tight')
    print('Plot 1 saved on Desktop')

    print('Plot 2...')
    plot4by4([jra55_trend-merra2_trend, era5_trend-merra2_trend, access_cm2_trend-merra2_trend, merra2_trend], 'BrBG_r' , 'm/s per decade', 'Trend of '+var_name+': Differences between MERRA2', [-0.6, 0.6])
    # save figure 
    plt.savefig('/Users/isabelaconde/Desktop/trend_fig_differennces.png', dpi=300, bbox_inches='tight')
    print('Plot 2 saved on Desktop')

    print('all good')
    
    return jra55_trend, era5_trend, merra2_trend, access_cm2_trend


def mean_state_analysis(jra55, era5, merra2, access_cm2,var_name):
    # if dimensions aren't lat,lon, time regrid with regrid_windstress function - if statement to check jra55, era5, merra2 and access_cm2 dimensions
    def maybe_regrid(ds):
        expected_dims = {'lat', 'lon', 'time'}
        if set(ds.dims) != expected_dims:
            print(f"Regridding {ds.name}")
            return regrid_windstress(ds)
        else:
            return ds
    
    # Regrid the datasets if necessary
    jra55 = maybe_regrid(jra55)
    era5 = maybe_regrid(era5)
    merra2 = maybe_regrid(merra2)
    access_cm2 = maybe_regrid(access_cm2)

    merra2['lon'] = (merra2['lon']) %360
    merra2 = merra2.sortby(['lat','lon']) 

    new_lats = era5.lat.values
    new_lons = era5.lon.values
    merra2_gr = merra2.sel(lat = slice(new_lats[0],new_lats[-1])).interp(lat=new_lats, lon=new_lons)
    print('MERR2 interpolated to match ERA5 grid')

    
    # Calculate the mean for each dataset
    print('Finding means...')
    jra55_mean = jra55.mean(dim='time')
    era5_mean = era5.mean(dim='time')
    merra2_mean = merra2_gr.mean(dim='time')
    access_cm2_mean = access_cm2.mean(dim='time')
    print('Done')

    # plot all values using plot4by4 function
    print('Plot 1...')
    plot4by4([jra55_mean, era5_mean, access_cm2_mean, merra2_mean], 'BrBG_r' , 'm/s', 'Mean state of '+var_name, [-10, 10])
    # save figure
    plt.savefig('/Users/isabelaconde/Desktop/mean_fig_abs_vals.png', dpi=300, bbox_inches='tight')
    print('Plot 1 saved on Desktop')
    print('Plot 2...')
    plot4by4([jra55_mean-merra2_mean, era5_mean-merra2_mean, access_cm2_mean-merra2_mean, merra2_mean], 'BrBG_r' , 'm/s', 'Mean state of '+var_name+': Differences between MERRA2', [-2, 2])
    # save figure
    plt.savefig('/Users/isabelaconde/Desktop/mean_fig_differennces.png', dpi=300, bbox_inches='tight')


def pacific_mask(sst):
    LonsPts_pos = [130,120,110,110,110,260,270,270,277,291,291,130] #-np.ones(13)*180
    LatsPts_pos =[-20,-10,-5,10,20,20,15,15,10,5,-20,-20]
    
    x_pixel_pos = LonsPts_pos
    y_pixel_pos = LatsPts_pos
    
    temp_list = []
    for a, b in zip(x_pixel_pos, y_pixel_pos):
        temp_list.append([a, b])
    
    polygon = np.array(temp_list)
    
    xv, yv = sst.lon.values, sst.lat.values
    lon2d, lat2d = np.meshgrid(xv, yv)
    points = np.hstack((lon2d.reshape((-1,1)), lat2d.reshape((-1,1))))
    path = matplotlib.path.Path(polygon)
    mask = path.contains_points(points)
    mask.shape = lon2d.shape
    mask_bit_pos = mask*np.ones_like(lon2d)
    
    mask_mods = mask_bit_pos#+mask_bit_neg
    
    mask_mods[mask_mods==0] = np.nan
    return mask_mods


def quantiles_xhist(data):
    hist_T = data
    weights = np.cos(np.deg2rad(hist_T.lat))
    times = hist_T['time']
    const_area=np.r_[0:1:0.005]
    temps = np.r_[8:34:0.5] # define temperatures for binning 
    
    temps_interp = np.empty([len(times),len(const_area)])
    
    for i in np.r_[0:len(times):1]:  
        h=histogram(hist_T[i],bins=temps,weights=weights).cumsum()
        hh = (h - h[0])/(h[-1]-h[0])
        temps_interp[i]=np.interp(const_area,hh,temps[1:])
    
    
    sst_area= xr.DataArray(temps_interp,coords={'time':times,'area':const_area})

    return(sst_area)


def percentiles_xhist(data): # find percentiles of SST using xhistogram
    hist_T = data.squeeze()
    weights = np.cos(np.deg2rad(hist_T.lat))
    times = hist_T['time']
    const_area=np.r_[0:1:0.01]
    temps = np.r_[12:34:0.5] # define temperatures for binning 
    
    temps_interp = np.empty([len(times),len(const_area)])
    
    for i in np.r_[0:len(times):1]:  
        h=histogram(hist_T[i],bins=temps,weights=weights).cumsum()
        hh = (h - h[0])/(h[-1]-h[0])
        temps_interp[i]=np.interp(const_area,hh,temps[1:])
    
    
    sst_area= xr.DataArray(temps_interp,coords={'time':times,'area':const_area})

    return(sst_area)


def find_trend_percentile(data):
    data = data.sel(time=slice('1982','2017'))
    x_val = np.arange(0, len(data.time))
    slope_array=[np.polyfit(x_val, data.isel(area=j), 1)[0] for j in range(200)]
    da = xr.DataArray(slope_array, coords ={'area':data.area.values},name = 'trend')
    return da


def calculate_confidence_intervals_all(data, n):
    mean = np.empty(n)
    lower = np.empty(n)
    upper = np.empty(n)

    for i in range(data.shape[0]):
        mean[i] = np.mean(data[i])
        lower[i] = scoreatpercentile(data[i],10)
        upper[i] = scoreatpercentile(data[i],90)

    return mean, lower, upper


def mask_models(model_datasets):
    for model, dataset in model_datasets.items():
        print('Masking ' + model)
        dataset['sst'] = dataset['sst'].where(pacific_mask(dataset['sst']) == 1)
        dataset['sst'].attrs['long_name'] = 'Sea Surface Temperature'
        dataset['sst'].attrs['units'] = 'C'
        print(model + ' masked')
    return model_datasets


def shift_lon(da):
    da = da.assign_coords(lon=(((da.lon + 180) % 360) - 180)).sortby('lon')
    return da


def fix_time(ds, prefix):
    src = ds.encoding.get("source", "")
    year = int(re.search(rf"{re.escape(prefix)}_oaflux_(\d{{4}})\.nc$", src).group(1))

    months = [int(m) for m in ds["time"].values]  # 1..12
    new_time = pd.to_datetime([f"{year}-{m:02d}-15" for m in months])

    return ds.assign_coords(time=("time", new_time))


def trend_obs_percentile(data): # find trend of percentile data
    time_axis = np.arange(data.sizes['time'])
    trends = np.empty(data.sizes['area'])
    for i in range(data.sizes['area']):
        y = data[:, i].values
        trends[i] = np.polyfit(time_axis, y, 1)[0]  # slope

    return xr.DataArray(trends, coords={'area': data.area}, dims='area', name='sst_trend')


# ---------------------------------------------------------------------------
# Lightweight save / load of computed variables between notebooks.
#
#   Pattern:  "compute" notebooks save their results to disk; "plotting"
#   notebooks load them, instead of recomputing. Run the compute/loader
#   notebooks first, then the plotting ones.
#
#   At the top of a notebook (after `from functions import *`):
#       load_state(globals())
#   At the bottom of a notebook:
#       save_state(globals())
#
# Variables are stored (accumulating) in  <repo>/processed_data/state.pkl
# Dask-backed xarray objects stay lazy, so this does not force big data
# into memory. Anything unpicklable (modules, functions, regridders) is skipped.
# ---------------------------------------------------------------------------
import os as _os, pickle as _pickle, inspect as _inspect, types as _types
_REPO_DIR = _os.path.dirname(_os.path.abspath(__file__))
STATE_DIR = _os.path.join(_REPO_DIR, "processed_data")
STATE_FILE = _os.path.join(STATE_DIR, "state.pkl")


def save_state(ns, names=None, path=STATE_FILE):
    """Save data variables from a namespace (pass globals()) so other
    notebooks can load them. Accumulates into the existing state file."""
    _os.makedirs(STATE_DIR, exist_ok=True)
    data = {}
    if _os.path.exists(path):
        try:
            with open(path, "rb") as f:
                data = _pickle.load(f)
        except Exception:
            data = {}
    keys = names if names is not None else list(ns.keys())
    saved = []
    for k in keys:
        if k.startswith("_"):
            continue
        v = ns.get(k, None)
        if v is None:
            continue
        if isinstance(v, _types.ModuleType):
            continue
        if _inspect.isfunction(v) or _inspect.isclass(v) or _inspect.isbuiltin(v) or _inspect.ismethod(v):
            continue
        try:
            _pickle.dumps(v)
        except Exception:
            continue
        data[k] = v
        saved.append(k)
    with open(path, "wb") as f:
        _pickle.dump(data, f)
    print(f"[save_state] saved {len(saved)} variables -> {path}")
    return path


def load_state(ns=None, path=STATE_FILE):
    """Load variables saved by earlier notebooks. If a namespace (globals())
    is passed, inject them into it; always returns the dict."""
    if not _os.path.exists(path):
        print(f"[load_state] no saved state yet ({path}). Run the compute/loader notebooks first.")
        return {}
    with open(path, "rb") as f:
        data = _pickle.load(f)
    if ns is not None:
        ns.update(data)
    keys = sorted(data.keys())
    preview = ", ".join(keys[:12]) + (" ..." if len(keys) > 12 else "")
    print(f"[load_state] loaded {len(data)} variables from {path}")
    print(f"[load_state] available: {preview}")
    return data
