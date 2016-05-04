#!/usr/bin/env python
"""
Read antload ice thickness data from mat files to a python class.
Then map to an orca025 grid with monthly frequency to ease comparison
with NEMO model simulations.
"""

import os
import sys
import gzip
import cPickle
from datetime import datetime, timedelta
import numpy as np
from scipy.io import loadmat
import scipy.io.netcdf as nc
import glob
sys.path.append(os.path.join(os.getenv('HOME'),'python/GeoInterpolate/'))
from GeoInterpolate_f90r import geointerpolate_f90r as gi

# global functions
def save_zipped_pickle(obj, filename, protocol=-1):
    with gzip.open(filename, 'wb') as f:
        cPickle.dump(obj, f, protocol)

def load_zipped_pickle(filename):
    with gzip.open(filename, 'rb') as f:
        loaded_object = cPickle.load(f)
        return loaded_object

class Antload(object):
    def __init__(self):
        self.data  = []
        self.dates = []
        self.lat   = []
        self.lon   = []
        self.x     = [] # closest model grid index (ix,iy)
        self.y     = [] # closest model grid index (ix,iy)
        self.vname = 'sit' # sea ice thickness

    def readMatFile(self,filename):
        date0 = datetime(1970,1,1,0) # UTC
        raw  = loadmat(filename)
        # consider ice thicknesses greater than 3m unrealiable
        idx = np.where((raw['Hice'][:]>0.)&(raw['Hice'][:]<=3.))[0]
        self.data = raw['Hice'][idx][:,0]
        self.lat = raw['Latitude'][idx][:,0]
        self.lon = raw['Longitude'][idx][:,0]
        time = raw['Timestamp'][idx][:,0]
        self.dates = [date0 + timedelta(t/86400,t%86400) for t in time]
        min_i = gi.nearest_neighbour_indices(self.lon,self.lat,\
                                       self.grdlon,self.grdlat,\
                                               self.gx,self.gy,\
                                                  len(self.lon))
        self.x, self.y = min_i[:,0]-1, min_i[:,1]-1
        #for c,i in enumerate(idx):
        #    if c%1000.==0:
        #        print "%5.1f percent processed" % \
        #             (100*float(i)/len(raw['Timestamp']))
        #        sys.stdout.flush()
        #    lon, lat = self.lon[c], self.lat[c]
            # f90 should be fast
        #    self.xy.append(min_i)
            # closest model orca025 grid point
            #dst   = self.haversine(self.grdlon,self.grdlat,lon,lat)
            #min_i = np.where(dst==np.min(dst))
            #self.x.append(min_i[0][0])
            #self.y.append(min_i[1][0])

    def readFiles(self,fpat='mittaus*.mat'):
        for fn in sorted(glob.glob(fpat)):
            self.readMatFile(fn)

    def readModelGrid(self,lat_lim=-55.,\
                      grdfile="coordinates_ORCA025.nc"):
        fp = nc.netcdf_file(grdfile)
        lat = np.array(fp.variables['nav_lat'][:])
        idx = np.where(lat<-55.)
        lon = np.array(fp.variables['nav_lon'][:])
        self.grdlat = lat[:idx[0].max()+1,:]
        self.grdlon = lon[:idx[0].max()+1,:]
        fp.close()
        self.gx, self.gy = self.grdlon.shape

if __name__ == "__main__":
    #for fn in sorted(glob.glob('mittaus*.mat')):
    fn = sys.argv[1]
    cgzfile = "%s.cpickle.gz" % fn
    antload = Antload()
    antload.readModelGrid()
    if not os.path.exists(cgzfile):
        sys.stdout.write("Starting %s ...\n" % fn)
        sys.stdout.flush()
        antload.readMatFile(fn)
        # save
        save_zipped_pickle(antload,cgzfile)
    # load
    antload = load_zipped_pickle(cgzfile)
    sys.stdout.write("%s processed!\n" % fn)
    sys.stdout.flush()
    print "Finnished!"
