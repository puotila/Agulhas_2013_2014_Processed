import sys
import os
import numpy as np
from scipy.io import loadmat
import netCDF4 as nc
sys.path.append(os.path.join(os.getenv('HOME'),'python/GeoInterpolate/'))
from GeoInterpolate_f90r import geointerpolate_f90r as gi

raw = loadmat('mittaus18.mat')
fp = nc.Dataset('coordinates_ORCA025.nc')
grdlon = np.array(fp.variables['nav_lon'][:])
grdlat = np.array(fp.variables['nav_lat'][:])
fp.close()
raw = loadmat('mittaus13.mat')
lon = raw['Longitude'].squeeze()
lat = raw['Latitude'].squeeze()
len1 = len(lon)
nx, ny = grdlon.shape
#min_i = gi.nearest_neighbour_index(lon[0],lat[0],grdlon,grdlat,nx,ny)
len1=1000
min_is = gi.nearest_neighbour_indices(lon[:len1],lat[:len1],grdlon,grdlat,nx,ny,len1)
